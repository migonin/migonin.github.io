import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# === Configuration ===
SERVICE_ACCOUNT_FILE = "secrets/service_account.json"
SPREADSHEET_ID = "1nw23BQ_VzFLdcWoii12Sb1GEutMrVSRLIs3ISyinZNQ"
SHEET_NAMES = ["Places", "Categories", "Curators"]

# Save JSON directly to repo root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_PATH = os.path.join(ROOT_DIR, "output.json")

# === Auth & API setup ===
scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
service = build("sheets", "v4", credentials=creds)
sheet_api = service.spreadsheets().values()

# === Fetch all sheets in one call ===
response = sheet_api.batchGet(
    spreadsheetId=SPREADSHEET_ID,
    ranges=SHEET_NAMES
).execute()

data = {}

for value_range in response.get("valueRanges", []):
    name = value_range["range"].split("!")[0].strip("'")
    values = value_range.get("values", [])

    if not values:
        data[name] = []
        continue

    headers = values[0]
    rows = [dict(zip(headers, row)) for row in values[1:]]
    data[name] = rows

# === Write output file safely ===
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Exported {len(SHEET_NAMES)} sheets to {OUTPUT_PATH}")
