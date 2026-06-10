# test_elt_columns.py — Check exact column names in ELT response

from touchstone_client import get_all_loss_data

print("Fetching ELT for Analysis SID 63...")
results = get_all_loss_data(63)

df_elt = results.get('ELT')
if df_elt is not None and not df_elt.empty:
    print(f"\nColumns ({len(df_elt.columns)}):")
    for col in df_elt.columns:
        print(f"  '{col}'")
    print(f"\nFirst row:")
    print(df_elt.iloc[0].to_dict())
else:
    print("No ELT data returned")