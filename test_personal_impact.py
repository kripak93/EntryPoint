"""
Test Personal Impact metric with known chase specialists
"""
import pandas as pd

df = pd.read_csv('processed_entry_points_ballbyball.csv')

# Filter to entries with RRR data
chase_df = df[df['Personal_Impact'].notna()].copy()

print("=" * 80)
print("PERSONAL IMPACT ANALYSIS - CHASE SPECIALISTS")
print("=" * 80)

# Known chase specialists to check
specialists = ['HH Pandya', 'MS Dhoni', 'V Kohli', 'AB de Villiers', 'RG Sharma', 
               'KL Rahul', 'S Iyer', 'RD Gaikwad']

print(f"\nAnalyzing {len(chase_df)} chase entries across {chase_df['Player'].nunique()} players")

# Get top performers by Personal Impact
print("\n" + "=" * 80)
print("TOP 15 PLAYERS BY PERSONAL IMPACT (Min 3 chase entries)")
print("=" * 80)

player_stats = chase_df.groupby('Player').agg({
    'Personal_Impact': ['mean', 'count'],
    'Impact_Runs': 'mean',
    'Final_Strike_Rate': 'mean',
    'Entry_RR_Required': 'mean',
    'Runs': 'mean'
}).reset_index()

player_stats.columns = ['Player', 'Avg Personal Impact', 'Entries', 'Avg Impact Runs', 
                        'Avg SR', 'Avg Entry RRR', 'Avg Runs']
player_stats = player_stats[player_stats['Entries'] >= 3]
player_stats = player_stats.sort_values('Avg Personal Impact', ascending=False)

print(player_stats.head(15).round(2).to_string(index=False))

# Check specific specialists
print("\n" + "=" * 80)
print("KNOWN CHASE SPECIALISTS IN DATASET")
print("=" * 80)

for player in specialists:
    player_data = chase_df[chase_df['Player'] == player]
    if len(player_data) > 0:
        print(f"\n{player}:")
        print(f"  Chase entries: {len(player_data)}")
        print(f"  Avg Personal Impact: {player_data['Personal_Impact'].mean():.2f} RPO")
        print(f"  Positive impacts: {(player_data['Personal_Impact'] > 0).sum()}")
        print(f"  Negative impacts: {(player_data['Personal_Impact'] < 0).sum()}")
        print(f"  Avg Strike Rate: {player_data['Final_Strike_Rate'].mean():.1f}")
        print(f"  Avg Entry RRR: {player_data['Entry_RR_Required'].mean():.2f}")
        print(f"  Avg Impact Runs: {player_data['Impact_Runs'].mean():.2f}")

# Bottom performers
print("\n" + "=" * 80)
print("BOTTOM 10 PLAYERS BY PERSONAL IMPACT (Min 3 chase entries)")
print("=" * 80)

bottom = player_stats.sort_values('Avg Personal Impact', ascending=True).head(10)
print(bottom.round(2).to_string(index=False))

# High pressure scenarios (RRR > 12)
print("\n" + "=" * 80)
print("HIGH PRESSURE CHASES (Entry RRR > 12)")
print("=" * 80)

high_pressure = chase_df[chase_df['Entry_RR_Required'] > 12].copy()
print(f"\nTotal high pressure entries: {len(high_pressure)}")

hp_stats = high_pressure.groupby('Player').agg({
    'Personal_Impact': ['mean', 'count'],
    'Final_Strike_Rate': 'mean',
    'Entry_RR_Required': 'mean'
}).reset_index()

hp_stats.columns = ['Player', 'Avg Personal Impact', 'Entries', 'Avg SR', 'Avg Entry RRR']
hp_stats = hp_stats[hp_stats['Entries'] >= 2]
hp_stats = hp_stats.sort_values('Avg Personal Impact', ascending=False)

print("\nTop 10 in high pressure:")
print(hp_stats.head(10).round(2).to_string(index=False))

print("\n" + "=" * 80)
print("INSIGHTS")
print("=" * 80)
print(f"• Overall avg Personal Impact: {chase_df['Personal_Impact'].mean():.2f} RPO")
print(f"• Players scoring faster than required: {(chase_df['Personal_Impact'] > 0).sum()} entries")
print(f"• Players scoring slower than required: {(chase_df['Personal_Impact'] < 0).sum()} entries")
print(f"• Success rate (positive impact): {(chase_df['Personal_Impact'] > 0).sum() / len(chase_df) * 100:.1f}%")
print("\nPersonal Impact isolates individual performance from team context.")
print("Positive values indicate the player scored faster than the required rate.")
