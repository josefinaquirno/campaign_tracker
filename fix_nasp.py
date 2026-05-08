with open('verdi_targets.json', 'r', encoding='utf-8-sig') as f:
    c = f.read()

# Find exact nasp string
idx = c.find('CAST(nasp AS STRING)')
print(f'CAST(nasp AS STRING) at index: {idx}')
if idx > 0:
    print(repr(c[idx-30:idx+60]))

# Replace CAST(nasp AS STRING) with TO_JSON_STRING approach
old = 'CAST(nasp AS STRING)'
new = 'IFNULL(TO_JSON_STRING(nasp),\'null\')'
if old in c:
    c = c.replace(old, new)
    print('Fixed!')
else:
    print('Not found - check encoding')

with open('verdi_targets.json', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
with open('verdi_targets.json', 'r', encoding='utf-8') as f:
    c2 = f.read()
print(f'TO_JSON_STRING in file: {c2.count("TO_JSON_STRING")}')
