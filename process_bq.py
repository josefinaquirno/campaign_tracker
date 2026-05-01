import json
import sys

# Read the BQ results file
with open('C:/Users/jquirno/Downloads/bq-results-20260417-143838-1776436845982.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

# Handle both array and object forms
if isinstance(raw, list):
    data_json_str = raw[0]['data_json']
else:
    data_json_str = raw['data_json']

# Parse the inner JSON
inner = json.loads(data_json_str)

print("Keys in inner JSON:", list(inner.keys()))
print("ms rows:", len(inner.get('ms', [])))
print("landing rows:", len(inner.get('landing', [])))
print("container rows:", len(inner.get('container', [])))
print("First ms row:", json.dumps(inner['ms'][0]) if inner.get('ms') else 'empty')

# Read current historical.json
HISTORICAL_PATH = 'C:/Users/jquirno/proyecto-claude/campaign_tracker/docs/historical.json'
try:
    with open(HISTORICAL_PATH, 'r', encoding='utf-8') as f:
        historical = json.load(f)
except FileNotFoundError:
    historical = []

# Build historical entry
historical_entry = {
    "name": "DOUBLE DATES 04/04",
    "start": "2026-03-23",
    "end": "2026-04-07",
    "ms": inner.get('ms', []),
    "landing": inner.get('landing', []),
    "container": inner.get('container', [])
}

# Push into historical array
historical.append(historical_entry)

# Write updated historical.json
with open(HISTORICAL_PATH, 'w', encoding='utf-8') as f:
    json.dump(historical, f, ensure_ascii=False, indent=2)

print("\nDone! Updated historical.json successfully.")
print("historical entries now:", len(historical))
