import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "secrets/service_account.json"
SPREADSHEET_ID = "1nw23BQ_VzFLdcWoii12Sb1GEutMrVSRLIs3ISyinZNQ"
OUTPUT_PATH = "./something.json"
SHEET_NAMES = ["Places", "Categories", "Curators"]

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

service = build("sheets", "v4", credentials=creds)
sheet_api = service.spreadsheets().values()

# Batch get all sheets in one call
response = sheet_api.batchGet(
    spreadsheetId=SPREADSHEET_ID,
    ranges=SHEET_NAMES
).execute()

data = {}

# Convert each sheet's range to structured dicts
for value_range in response.get("valueRanges", []):
    name = value_range["range"].split("!")[0].strip("'")  # extract sheet name
    values = value_range.get("values", [])

    if not values:
        data[name] = []
        continue

    headers = values[0]
    rows = [dict(zip(headers, row)) for row in values[1:]]
    data[name] = rows

# Save JSON
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Exported {len(SHEET_NAMES)} sheets → {OUTPUT_PATH}")
