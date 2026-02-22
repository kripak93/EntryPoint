"""
Filter the dataset to keep only Men's IPL data
Remove Women's T20 (WT20) and Minor T20 data
"""

import pandas as pd

def filter_mens_ipl():
    """Filter dataset to keep only men's IPL data"""
    
    print("🏏 Filtering dataset for Men's IPL only...")
    
    # Load original data
    df = pd.read_csv('ipl_data.csv')
    print(f"📊 Original dataset: {len(df)} rows")
    
    # Show current match types
    print(f"\n📋 Current match types:")
    print(df['Match⬆'].value_counts())
    
    # Filter for men's IPL (LAT20 appears to be men's IPL)
    mens_ipl = df[df['Match⬆'].str.startswith('LAT20', na=False)]
    print(f"\n✅ Men's IPL data: {len(mens_ipl)} rows")
    
    # Show teams in filtered data
    print(f"\n🏟️  Teams in Men's IPL data:")
    teams = sorted(mens_ipl['Team'].unique())
    print(teams)
    
    # Show sample players
    print(f"\n👤 Sample players in Men's IPL:")
    sample_players = sorted(mens_ipl['Player'].unique())[:15]
    print(sample_players)
    
    # Save filtered data
    mens_ipl.to_csv('ipl_data_mens_only.csv', index=False)
    print(f"\n💾 Saved filtered data as 'ipl_data_mens_only.csv'")
    
    # Show some stats
    print(f"\n📈 Quick stats:")
    print(f"  - Total players: {mens_ipl['Player'].nunique()}")
    print(f"  - Total teams: {mens_ipl['Team'].nunique()}")
    print(f"  - Date range: {mens_ipl['Date⬆'].min()} to {mens_ipl['Date⬆'].max()}")
    
    # Show top bowlers from filtered data
    print(f"\n🎯 Top bowlers by wickets (Men's IPL only):")
    valid_bowlers = mens_ipl[mens_ipl['O'] >= 2.0]  # Min 2 overs
    top_bowlers = valid_bowlers.nlargest(10, 'W')[['Player', 'Team', 'W', 'O', 'Econ']]
    print(top_bowlers.to_string())
    
    return True

if __name__ == "__main__":
    filter_mens_ipl()