with open('verdi_targets.json', 'r', encoding='utf-8-sig') as f:
    c = f.read()

# Fix 1: NASP - the inner IFNULL doesn't help when subquery returns 0 rows
# Wrap the whole subquery: IFNULL((SELECT ...), 'null')
old_nasp = "(SELECT IFNULL(TO_JSON_STRING(nasp),'null') FROM NASP)"
new_nasp = "IFNULL((SELECT TO_JSON_STRING(nasp) FROM NASP),'null')"
if old_nasp in c:
    c = c.replace(old_nasp, new_nasp)
    print("Fixed NASP")
else:
    idx = c.find('FROM NASP')
    print(f"NASP not found, context: {repr(c[max(0,idx-60):idx+20])}")

# Fix 2: MS CTR ALL - CAST(NULL AS STRING) = NULL breaks CONCAT
# Wrap in IFNULL: IFNULL(CAST(...), '0')
old_start = "CAST((SELECT ROUND(SAFE_DIVIDE(SUM(CLICKS_QTY),NULLIF(SUM(IMPRESSION_VIEWS_QTY),0)),4)"
new_start = "IFNULL(CAST((SELECT ROUND(SAFE_DIVIDE(SUM(CLICKS_QTY),NULLIF(SUM(IMPRESSION_VIEWS_QTY),0)),4)"
if old_start in c:
    c = c.replace(old_start, new_start)
    # Fix closing bracket: ) AS STRING), -> ) AS STRING),'0'),
    c = c.replace("NOT LIKE '%FD%') AS STRING),", "NOT LIKE '%FD%') AS STRING),'0'),", 1)
    print("Fixed MS CTR ALL")
else:
    print("MS CTR ALL not found")

with open('verdi_targets.json', 'w', encoding='utf-8') as f:
    f.write(c)

c2 = open('verdi_targets.json', encoding='utf-8').read()
print("IFNULL nasp count:", c2.count("IFNULL((SELECT TO_JSON_STRING(nasp)"))
print("IFNULL ctr_all count:", c2.count("IFNULL(CAST((SELECT ROUND"))
print("Done")
