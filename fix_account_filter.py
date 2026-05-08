with open('verdi_targets.json', 'r', encoding='utf-8-sig') as f:
    c = f.read()

# Remove ACCOUNT_TYPE filter (field is in joined table LK_ADS_ACCOUNTS, not in BT_ADS_DISP_METRICS_DAILY)
# The remaining filters (MAIN-SLIDER, NOT SPLINTER, NOT FD) are sufficient
old = "AND ACCOUNT_TYPE LIKE '%MARKETING%'\n"
if old in c:
    c = c.replace(old, '')
    print("Removed ACCOUNT_TYPE filter")
else:
    old2 = "AND ACCOUNT_TYPE LIKE '%MARKETING%'"
    if old2 in c:
        c = c.replace(old2, '')
        print("Removed ACCOUNT_TYPE filter (no trailing newline)")
    else:
        print("Pattern not found, searching...")
        idx = c.find('ACCOUNT_TYPE')
        print(f"ACCOUNT_TYPE at: {idx}")
        if idx > 0:
            print(repr(c[idx-5:idx+50]))

with open('verdi_targets.json', 'w', encoding='utf-8') as f:
    f.write(c)

c2 = open('verdi_targets.json', encoding='utf-8').read()
print(f"ACCOUNT_TYPE remaining: {c2.count('ACCOUNT_TYPE')}")
print("Done")
