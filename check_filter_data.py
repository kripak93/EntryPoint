import pandas as pd

# Load original data
orig = pd.read_csv('ipl_data_mens_only.csv')

print("=== Available Columns ===")
print([col for col in orig.columns if 'Date' in col or 'Ground' in col or 'Variation' in col])

print("\n=== Date Info ===")
date_col = 'Date⬆'
print(f"Date range: {orig[date_col].min()} to {orig[date_col].max()}")
print(f"Sample dates: {orig[date_col].head(3).tolist()}")

print("\n=== Ground Names ===")
print(orig['Ground Name'].value_counts().head(5))

print("\n=== Bowling Variations ===")
print(orig['Variation'].value_counts().head(10))

print("\n=== Other Useful Columns ===")
useful_cols = ['Line', 'Length', 'Shot Type', 'Shot', 'Zone']
for col in useful_cols:
    if col in orig.columns:
        print(f"{col}: {orig[col].nunique()} unique values")
        print(f"  Sample: {orig[col].value_counts().head(3).index.tolist()}")