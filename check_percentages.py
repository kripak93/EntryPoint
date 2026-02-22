import pandas as pd

# Check entry points data
print("=== ENTRY POINTS DATA ===")
df = pd.read_csv('processed_entry_points_ballbyball.csv')

print("Sample data:")
print(df[['Player', 'Dots', 'BF', 'Dot_Pct', 'Fours', 'Sixes', 'Bnd_Pct']].head(10))

print("\nDot_Pct over 100:")
over_100_dot = df[df['Dot_Pct'] > 100]
print(f"Count: {len(over_100_dot)}")
if len(over_100_dot) > 0:
    print(over_100_dot[['Player', 'Dots', 'BF', 'Dot_Pct']].head(5))

print("\nBnd_Pct over 100:")
over_100_bnd = df[df['Bnd_Pct'] > 100]
print(f"Count: {len(over_100_bnd)}")
if len(over_100_bnd) > 0:
    print(over_100_bnd[['Player', 'Fours', 'Sixes', 'BF', 'Bnd_Pct']].head(5))

# Verify calculations
print("\n=== VERIFICATION ===")
sample = df.iloc[0]
print(f"Player: {sample['Player']}")
print(f"Dots: {sample['Dots']}, BF: {sample['BF']}")
print(f"Stored Dot_Pct: {sample['Dot_Pct']}")
print(f"Calculated Dot_Pct: {(sample['Dots'] / sample['BF'] * 100):.1f}")

print(f"Boundaries: {sample['Fours'] + sample['Sixes']}, BF: {sample['BF']}")
print(f"Stored Bnd_Pct: {sample['Bnd_Pct']}")
print(f"Calculated Bnd_Pct: {((sample['Fours'] + sample['Sixes']) / sample['BF'] * 100):.1f}")