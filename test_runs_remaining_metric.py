"""
Test the % of Runs Remaining metric
"""
import pandas as pd

df = pd.read_csv('processed_entry_points_ballbyball.csv')

print("=" * 80)
print("% OF RUNS REMAINING METRIC TEST")
print("=" * 80)

# Test with Hardik Pandya
hh = df[df['Player'] == 'HH Pandya'].copy()
chase = hh[hh['Pct_of_Runs_Remaining'].notna()]

print("\nHardik Pandya Analysis:")
print(f"  Total chase entries: {len(chase)}")
print(f"  Avg % of Runs Remaining: {chase['Pct_of_Runs_Remaining'].mean():.1f}%")
print(f"  Avg Contribution per Over: {chase['Contribution_Per_Over'].mean():.1f} RPO")
print(f"  Avg % of Target: {chase['Pct_of_Target'].mean():.1f}%")
print(f"  Avg SR: {chase['Final_Strike_Rate'].mean():.1f}")
print(f"  Avg Entry RRR: {chase['Entry_RR_Required'].mean():.2f}")
print(f"  Avg Runs Required at Entry: {chase['Entry_Runs_Required'].mean():.0f}")
print(f"  Total Runs: {chase['Runs'].sum()}")

print("\n  Top 5 by % of Runs Remaining:")
cols = ['Entry_Over', 'Entry_Runs_Required', 'Runs', 'BF', 'Pct_of_Runs_Remaining', 
        'Contribution_Per_Over', 'Entry_RR_Required']
print(chase[cols].nlargest(5, 'Pct_of_Runs_Remaining').round(1).to_string())

# Overall stats
chase_df = df[df['Pct_of_Runs_Remaining'].notna()]

print("\n" + "=" * 80)
print("OVERALL STATS")
print("=" * 80)
print(f"Total chase entries: {len(chase_df)}")
print(f"Avg % of Runs Remaining: {chase_df['Pct_of_Runs_Remaining'].mean():.1f}%")
print(f"Avg Contribution per Over: {chase_df['Contribution_Per_Over'].mean():.1f} RPO")
print(f"Avg % of Target: {chase_df['Pct_of_Target'].mean():.1f}%")

# Top performers by % of Runs Remaining
print("\n" + "=" * 80)
print("TOP 15 PLAYERS BY % OF RUNS REMAINING (Min 3 entries)")
print("=" * 80)

player_stats = chase_df.groupby('Player').agg({
    'Pct_of_Runs_Remaining': 'mean',
    'Contribution_Per_Over': 'mean',
    'Pct_of_Target': 'mean',
    'Runs': ['sum', 'mean'],
    'Final_Strike_Rate': 'mean',
    'Entry_RR_Required': 'mean',
    'Entry_Runs_Required': 'mean',
    'BF': 'count'
}).reset_index()

player_stats.columns = ['Player', 'Avg % Remaining', 'Avg Contrib/Over', 'Avg % Target',
                        'Total Runs', 'Avg Runs', 'Avg SR', 'Avg Entry RRR', 'Avg Runs Req', 'Entries']
player_stats = player_stats[player_stats['Entries'] >= 3]
player_stats = player_stats.sort_values('Avg % Remaining', ascending=False)

print(player_stats.head(15).round(1).to_string(index=False))

# Example calculation
print("\n" + "=" * 80)
print("EXAMPLE CALCULATION")
print("=" * 80)
example = chase_df[chase_df['Entry_Runs_Required'].notna()].iloc[0]
print(f"Player: {example['Player']}")
print(f"Entry RRR: {example['Entry_RR_Required']:.2f} runs per over")
print(f"Runs Required at Entry: {example['Entry_Runs_Required']:.0f}")
print(f"Player Runs: {example['Runs']:.0f}")
print(f"Balls Faced: {example['BF']:.0f}")
print(f"\n% of Runs Remaining: ({example['Runs']:.0f} / {example['Entry_Runs_Required']:.0f}) × 100 = {example['Pct_of_Runs_Remaining']:.1f}%")
print(f"Contribution per Over: {example['Runs']:.0f} / ({example['BF']:.0f} / 6) = {example['Contribution_Per_Over']:.1f} RPO")
print(f"\nInterpretation:")
print(f"  - When player entered, team needed {example['Entry_Runs_Required']:.0f} more runs")
print(f"  - Player contributed {example['Runs']:.0f} runs = {example['Pct_of_Runs_Remaining']:.1f}% of what was needed")
print(f"  - Player scored at {example['Contribution_Per_Over']:.1f} RPO")
print(f"  - Entry RRR was {example['Entry_RR_Required']:.2f}, so player {'exceeded' if example['Contribution_Per_Over'] > example['Entry_RR_Required'] else 'fell short of'} requirement")
