"""Fix NASP column ambiguity and ACCOUNT_NAME → ACCOUNT_TYPE."""

with open('verdi_targets.json', 'r', encoding='utf-8-sig') as f:
    c = f.read()

# Fix 1: Rename nasp column to nasp_val in NASP CTE to avoid STRUCT ambiguity
# CTE definition: AS nasp -> AS nasp_val
c = c.replace(
    'ROUND(SAFE_DIVIDE(SUM(NMV_LAST_30DAYS), SUM(NSI_LAST_30DAYS)), 2) AS nasp',
    'ROUND(SAFE_DIVIDE(SUM(NMV_LAST_30DAYS), SUM(NSI_LAST_30DAYS)), 2) AS nasp_val'
)
# Subquery reference: TO_JSON_STRING(nasp) -> TO_JSON_STRING(nasp_val)
c = c.replace(
    'IFNULL((SELECT TO_JSON_STRING(nasp) FROM NASP)',
    'IFNULL((SELECT TO_JSON_STRING(nasp_val) FROM NASP)'
)
print(f"nasp_val in file: {c.count('nasp_val')}")

# Fix 2: ACCOUNT_NAME → ACCOUNT_TYPE (same as verdi_flow.json)
c = c.replace(
    "AND ACCOUNT_NAME LIKE '%MARKETING%'",
    "AND ACCOUNT_TYPE LIKE '%MARKETING%'"
)
print(f"ACCOUNT_TYPE occurrences: {c.count('ACCOUNT_TYPE')}")
print(f"ACCOUNT_NAME remaining: {c.count('ACCOUNT_NAME')}")

with open('verdi_targets.json', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done")
