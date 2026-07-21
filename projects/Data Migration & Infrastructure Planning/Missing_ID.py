import pandas as pd

# Read the Excel file
file_path = r'./sample_data/loan_ids.xlsx'  # set your own path
df = pd.read_excel(file_path)

# Get unique IDs, sort them, and convert to integers (handling any float/decimal values)
ids = sorted(df['id'].dropna().unique().astype(int))

# Find the range of IDs (min to max)
min_id = min(ids)
max_id = max(ids)

# Create a set of all IDs in the range
all_ids = set(range(min_id, max_id + 1))
existing_ids = set(ids)

# Find missing IDs
missing_ids = sorted(all_ids - existing_ids)

print(f"Total rows in file: {len(df)}")
print(f"Unique IDs present: {len(ids)}")
print(f"ID range: {min_id} to {max_id}")
print(f"\nMissing ID numbers: {missing_ids}")
print(f"\nTotal missing IDs: {len(missing_ids)}")

# Optional: Display first 20 missing IDs if the list is long
if len(missing_ids) > 20:
    print(f"\nFirst 20 missing IDs: {missing_ids[:20]}")