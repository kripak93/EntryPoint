import pandas as pd
df = pd.read_csv('cricviz_all_pages_combined.csv', low_memory=False)

# Extract tournament prefix from Match column
df['Tournament'] = df['Match⬆'].str.split(' # ').str[0].str.strip()
tournaments = df.groupby('Tournament').agg(
    Balls=('Match⬆', 'count'),
    Matches=('Match⬆', 'nunique'),
    Players=('Batsman', 'nunique'),
    Date_Min=('Date⬆', 'min'),
    Date_Max=('Date⬆', 'max')
).sort_values('Balls', ascending=False)

print("Tournaments in cricviz_all_pages_combined.csv:\n")
for idx, row in tournaments.iterrows():
    print(f"  {idx}: {row['Balls']:,} balls | {row['Matches']} matches | {row['Players']} players | {row['Date_Min']} to {row['Date_Max']}")
