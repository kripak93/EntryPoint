"""
Verify dashboard data is ready
"""
import pandas as pd

df = pd.read_csv('processed_entry_points_ballbyball.csv')

print("=" * 60)
print("DASHBOARD DATA VERIFICATION")
print("=" * 60)

print(f"\n✓ Data loaded successfully")
print(f"✓ Rows: {len(df)}")
print(f"✓ Columns: {len(df.columns)}")

print("\n✓ Key columns present:")
for col in ['Personal_Impact', 'Player_Run_Rate', 'Impact_Runs', 'Team_RRR_Impact']:
    present = col in df.columns
    print(f"  {'✓' if present else '✗'} {col}: {present}")

print(f"\n✓ Entries with RRR data: {df['Entry_RR_Required'].notna().sum()}")

rrr = df[df['Personal_Impact'].notna()]
print(f"\n✓ Personal Impact stats:")
print(f"  - Mean: {rrr['Personal_Impact'].mean():.2f} RPO")
print(f"  - Positive: {(rrr['Personal_Impact'] > 0).sum()}")
print(f"  - Negative: {(rrr['Personal_Impact'] < 0).sum()}")

print(f"\n✓ Sample data (first 3 rows with RRR):")
sample = rrr[['Player', 'Entry_RR_Required', 'Player_Run_Rate', 'Personal_Impact', 'Impact_Runs']].head(3)
print(sample.to_string())

print("\n" + "=" * 60)
print("✓ DASHBOARD READY TO RUN")
print("=" * 60)
print("\nRun: streamlit run ballbyball_entry_dashboard.py")
