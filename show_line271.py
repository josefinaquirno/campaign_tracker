import json

with open('verdi_targets.json', 'r', encoding='utf-8') as f:
    flow = json.load(f)

sql = flow['nodes'][1]['parameters']['sqlQuery']
lines = sql.split('\n')
print(f"Total lines: {len(lines)}")
for i in range(265, min(280, len(lines))):
    print(f"{i+1}: {lines[i][:120]}")
