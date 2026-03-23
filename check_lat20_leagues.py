import pandas as pd
df = pd.read_csv('cricviz_all_pages_combined.csv', low_memory=False)

# Filter to LAT20 only
lat20 = df[df['Match⬆'].str.startswith('LAT20', na=False)]

# Try to identify leagues by team names / ground / opposition
# The best indicator is likely the teams (Opposition column) or Ground
print("=== LAT20 Leagues by Team Names ===\n")

teams = lat20['Opposition'].dropna().unique()
print(f"Total unique teams: {len(teams)}")

# Group by ground country to identify leagues
print("\n=== By Country ===")
countries = lat20['Country'].value_counts()
print(countries)

print("\n=== By Ground ===")
grounds = lat20['Ground Name'].value_counts().head(30)
print(grounds)

print("\n=== All Teams ===")
for t in sorted(teams):
    count = len(lat20[lat20['Opposition'] == t])
    print(f"  {t}: {count:,} balls")
