"""Fix STRUCT/FLOAT cast errors in verdi_targets.json CONCAT section."""

path = 'verdi_targets.json'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find ctr_all and replace inline subquery with CAST wrapper
OLD_ALL = (
    "'\\\"ctr_all\\\":\\',       "
    "(SELECT ROUND(SAFE_DIVIDE(SUM(CLICKS_QTY),NULLIF(SUM(IMPRESSION_VIEWS_QTY),0)),4) "
    "FROM `meli-bi-data.WHOWNER.BT_ADS_DISP_METRICS_DAILY` "
    "WHERE EVENT_LOCAL_DT BETWEEN '2026-01-01' AND CURRENT_DATE() "
    "AND SIT_SITE_ID IN ('MLA') AND PLACEMENT LIKE '%MAIN-SLIDER%' "
    "AND ACCOUNT_NAME LIKE '%MARKETING%' "
    "AND LINE_ITEM_NAME NOT LIKE '%SPLINTER%' AND CAMPAIGN_NAME NOT LIKE '%FD%'),"
)

NEW_ALL = (
    "'\\\"ctr_all\\\":\\',       "
    "CAST((SELECT ROUND(SAFE_DIVIDE(SUM(CLICKS_QTY),NULLIF(SUM(IMPRESSION_VIEWS_QTY),0)),4) "
    "FROM `meli-bi-data.WHOWNER.BT_ADS_DISP_METRICS_DAILY` "
    "WHERE EVENT_LOCAL_DT BETWEEN '2026-01-01' AND CURRENT_DATE() "
    "AND SIT_SITE_ID IN ('MLA') AND PLACEMENT LIKE '%MAIN-SLIDER%' "
    "AND ACCOUNT_NAME LIKE '%MARKETING%' "
    "AND LINE_ITEM_NAME NOT LIKE '%SPLINTER%' AND CAMPAIGN_NAME NOT LIKE '%FD%') AS STRING),"
)

# Use the exact bytes found in the file
# From debug: '\\'\\\"ctr_all\\\":\\', ...'
# Actual string starts with: '\"ctr_all\":',
old_fragment = "'\\\"ctr_all\\\":',"
new_fragment  = "'\\\"ctr_all\\\":',"  # same — just find position

idx = c.find(old_fragment)
print(f"Fragment found at: {idx}")
print(f"Context: {repr(c[idx:idx+300])}")

# Build exact old and new strings based on what we see in file
# The subquery ends with: AND CAMPAIGN_NAME NOT LIKE '%FD%'),
end_marker = "AND CAMPAIGN_NAME NOT LIKE '%FD%'),"
end_idx = c.find(end_marker, idx)
print(f"End marker at: {end_idx}")

if end_idx > 0:
    old_str = c[idx:end_idx + len(end_marker)]
    new_str = old_str.replace(
        "(SELECT ROUND(SAFE_DIVIDE",
        "CAST((SELECT ROUND(SAFE_DIVIDE"
    ).replace(
        "NOT LIKE '%FD%'),",
        "NOT LIKE '%FD%') AS STRING),"
    )
    c = c[:idx] + new_str + c[end_idx + len(end_marker):]
    print("ctr_all CAST applied")
else:
    print("ERROR: end marker not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

# Verify all 4 CTRs are now wrapped
import re
matches = re.findall(r'CAST\(.*?AS STRING\)', c[10000:12000])
print(f"CAST wrappers found near ctr section: {len(matches)}")
print("Done")
