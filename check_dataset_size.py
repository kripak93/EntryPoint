import pandas as pd
from react_cricket_agent import CricketDataAnalyzer

# Load data
df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
print(f"Total rows in CSV: {len(df)}")
print(f"Unique players in CSV: {df['Player'].nunique()}")

# Create analyzer (processes entry points)
analyzer = CricketDataAnalyzer(df)
print(f"\nAfter entry point calculation:")
print(f"Total entry points: {len(analyzer.entry_points)}")
print(f"Unique players: {analyzer.entry_points['Player'].nunique()}")

# Check powerplay specifically
powerplay = analyzer.entry_points[analyzer.entry_points['Entry_Phase'] == 'Powerplay']
print(f"\nPowerplay entries: {len(powerplay)}")
print(f"Unique powerplay players: {powerplay['Player'].nunique()}")

# Check with min 3 matches filter
powerplay_grouped = powerplay.groupby('Player').size()
powerplay_3plus = powerplay_grouped[powerplay_grouped >= 3]
print(f"Powerplay players with 3+ matches: {len(powerplay_3plus)}")

# Show top 20 by count
print(f"\nTop 20 players by powerplay entries:")
print(powerplay_grouped.sort_values(ascending=False).head(20))

# Test diverse players function
diverse = analyzer.get_diverse_players_for_phase('powerplay', min_matches=3)
print(f"\nDiverse player categories:")
for category, players in diverse.items():
    print(f"  {category}: {len(players)} players")
