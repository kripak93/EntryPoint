"""
Analyze RRR Impact calculation issue
"""
import pandas as pd

# Load data
df = pd.read_csv('processed_entry_points_ballbyball.csv')

print("=== RRR Data Summary ===")
print(f"Total entries: {len(df)}")
print(f"\nEntries with RRR data: {df['Entry_RR_Required'].notna().sum()}")

print(f"\n=== Innings Breakdown ===")
print(df['Innings'].value_counts())

print(f"\n=== RRR by Innings ===")
rrr_by_innings = df.groupby('Innings')['Entry_RR_Required'].agg(['count', 'mean'])
print(rrr_by_innings)

print(f"\n=== Hardik Pandya Sample (Sorted by RRR Impact) ===")
hh = df[df['Player'] == 'HH Pandya'].copy()
if not hh.empty:
    hh = hh.sort_values('RRR_Impact')
    cols = ['Player', 'Innings', 'Entry_Over', 'Entry_RR_Required', 'Exit_RR_Required', 
            'RRR_Impact', 'Runs', 'BF', 'Final_Strike_Rate']
    print(hh[cols].head(10).to_string())
    
    print(f"\n=== Hardik Pandya RRR Impact Stats ===")
    print(f"Total chases with RRR data: {hh['Entry_RR_Required'].notna().sum()}")
    print(f"Avg RRR Impact: {hh['RRR_Impact'].mean():.2f}")
    print(f"Positive impacts: {(hh['RRR_Impact'] > 0).sum()}")
    print(f"Negative impacts: {(hh['RRR_Impact'] < 0).sum()}")
    print(f"Avg Strike Rate: {hh['Final_Strike_Rate'].mean():.1f}")
else:
    print("No data found for HH Pandya")

print(f"\n=== Sample Entry with Negative Impact ===")
negative = df[(df['RRR_Impact'] < 0) & (df['Final_Strike_Rate'] > 150)].head(1)
if not negative.empty:
    print(negative[['Player', 'Innings', 'Entry_Over', 'Entry_RR_Required', 'Exit_RR_Required',
                   'RRR_Impact', 'Runs', 'BF', 'Final_Strike_Rate']].to_string())

print(f"\n=== Check: Are we looking at 2nd innings? ===")
second_innings = df[df['Innings'] == '2nd innings']
print(f"2nd innings entries: {len(second_innings)}")
print(f"2nd innings with RRR: {second_innings['Entry_RR_Required'].notna().sum()}")
