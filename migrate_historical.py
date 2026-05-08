import json

# Lee data.json actual (tiene historical embebido)
with open('C:/Users/jquirno/proyecto-claude/campaign_tracker/docs/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

historical = data.get('historical', [])
print(f"Entradas historicas encontradas: {len(historical)}")
for h in historical:
    print(f"  - {h['name']} ({h['start']} → {h['end']}): ms={len(h['ms'])}, landing={len(h['landing'])}, container={len(h['container'])}")

# Escribe historical.json separado
with open('C:/Users/jquirno/proyecto-claude/campaign_tracker/docs/historical.json', 'w', encoding='utf-8') as f:
    json.dump(historical, f, ensure_ascii=False, indent=2)
print("\nhistorical.json creado OK")

# Limpia data.json (saca el campo historical)
data.pop('historical', None)
with open('C:/Users/jquirno/proyecto-claude/campaign_tracker/docs/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("data.json actualizado (sin historical)")
