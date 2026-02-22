"""
Test the new Contribution % metric
"""
import pandas as pd

df = pd.read_csv('processed_entry_points_ballbyball.csv')

print("=" * 80)
print("CONTRIBUTION % METRIC TEST")
print("=" * 80)

# Test with Hardik Pandya
hh = df[df['Player'] == 'HH Pandya'].copy()
chase = hh[hh['Contribution_Pct'].notna()]

print("\nHardik Pandya Contribution Analysis:")
print(f"  Total chase entries: {len(chase)}")
print(f"  Avg Contribution: {chase['Contribution_Pct'].mean():.1f}%")
print(f"  Exceeded requirement (>100%): {(chase['Contribution_Pct'] > 100).sum()}")
print(f"  Fell short (<100%): {(chase['Contribution_Pct'] < 100).sum()}")
print(f"  Avg SR: {chase['Final_Strike_Rate'].mean():.1f}")
print(f"  Avg Entry RRR: {chase['Entry_RR_Required'].mean():.2f}")

print("\n  Top 5 contributions:")
cols = ['Entry_Over', 'Entry_RR_Required', 'Runs', 'BF', 'Required_Runs_For_Balls', 
        'Contribution_Pct', 'Final_Strike_Rate']
print(chase[cols].nlargest(5, 'Contribution_Pct').round(1).to_string())

print("\n  Bottom 5 contributions:")
print(chase[cols].nsmallest(5, 'Contribution_Pct').round(1).to_string())

# Overall stats
chase_df = df[df['Contribution_Pct'].notna()]

print("\n" + "=" * 80)
print("OVERALL CONTRIBUTION STATS")
print("=" * 80)
print(f"Total chase entries: {len(chase_df)}")
print(f"Avg Contribution: {chase_df['Contribution_Pct'].mean():.1f}%")
print(f"Exceeded requirement (>100%): {(chase_df['Contribution_Pct'] > 100).sum()} ({(chase_df['Contribution_Pct'] > 100).sum() / len(chase_df) * 100:.1f}%)")
print(f"Fell short (<100%): {(chase_df['Contribution_Pct'] < 100).sum()} ({(chase_df['Contribution_Pct'] < 100).sum() / len(chase_df) * 100:.1f}%)")

# Top performers
print("\n" + "=" * 80)
print("TOP 15 PLAYERS BY CONTRIBUTION % (Min 3 entries)")
print("=" * 80)

player_stats = chase_df.groupby('Player').agg({
    'Contribution_Pct': ['mean', 'count'],
    'Impact_Runs': 'sum',
    'Final_Strike_Rate': 'mean',
    'Entry_RR_Required': 'mean',
    'Runs': 'mean'
}).reset_index()

player_stats.columns = ['Player', 'Avg Contribution %', 'Entries', 'Total Impact Runs',
                        'Avg SR', 'Avg Entry RRR', 'Avg Runs']
player_stats = player_stats[player_stats['Entries'] >= 3]
player_stats = player_stats.sort_values('Avg Contribution %', ascending=False)

print(player_stats.head(15).round(1).to_string(index=False))

# Example calculation
print("\n" + "=" * 80)
print("EXAMPLE CALCULATION")
print("=" * 80)
example = chase_df.iloc[0]
print(f"Player: {example['Player']}")
print(f"Entry RRR: {example['Entry_RR_Required']:.2f} runs per over")
print(f"Balls Faced: {example['BF']:.0f}")
print(f"Required Runs for those balls: {example['Entry_RR_Required']:.2f} × {example['BF']:.0f} / 6 = {example['Required_Runs_For_Balls']:.2f}")
print(f"Actual Runs Scored: {example['Runs']:.0f}")
print(f"Contribution %: ({example['Runs']:.0f} / {example['Required_Runs_For_Balls']:.2f}) × 100 = {example['Contribution_Pct']:.1f}%")
print(f"Impact Runs: {example['Runs']:.0f} - {example['Required_Runs_For_Balls']:.2f} = {example['Impact_Runs']:.2f}")
print(f"\nInterpretation: Player scored {example['Contribution_Pct']:.1f}% of their required share")
if example['Contribution_Pct'] > 100:
    print(f"  ✓ EXCEEDED requirement by {example['Contribution_Pct'] - 100:.1f}%")
else:
    print(f"  ✗ FELL SHORT by {100 - example['Contribution_Pct']:.1f}%")
