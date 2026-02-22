"""
Create over-by-over progression data for player innings
"""
import pandas as pd
import numpy as np

def get_player_over_progression(player_name, match_id=None):
    """
    Get over-by-over data for a player's innings showing:
    - Cumulative runs
    - Cumulative balls
    - Strike rate at each over
    - RRR at each over
    """
    df = pd.read_csv('ipl_data_mens_only.csv')
    
    # Filter to player
    player_df = df[df['Batsman'] == player_name].copy()
    
    if match_id:
        player_df = player_df[player_df['Match⬆'] == match_id]
    
    if player_df.empty:
        return pd.DataFrame()
    
    # Get match details
    player_df['Over_Num'] = player_df['Overs'].astype(str).str.split('.').str[0].astype(float)
    player_df['Runs_Cumulative'] = pd.to_numeric(player_df['R.1'], errors='coerce').fillna(0)
    player_df['Balls_Cumulative'] = pd.to_numeric(player_df['B'], errors='coerce').fillna(0)
    player_df['RRreq'] = pd.to_numeric(player_df['RRreq'], errors='coerce')
    
    # Sort by over
    player_df = player_df.sort_values('Over_Num')
    
    # Get data at the END of each over (last ball of each over)
    over_data = []
    
    for over in sorted(player_df['Over_Num'].unique()):
        over_balls = player_df[player_df['Over_Num'] == over]
        last_ball = over_balls.iloc[-1]
        
        runs = last_ball['Runs_Cumulative']
        balls = last_ball['Balls_Cumulative']
        sr = (runs / balls * 100) if balls > 0 else 0
        rrr = last_ball['RRreq']
        
        over_data.append({
            'Over': int(over),
            'Cumulative_Runs': runs,
            'Cumulative_Balls': balls,
            'Strike_Rate': sr,
            'RRR': rrr,
            'Balls_This_Over': len(over_balls)
        })
    
    return pd.DataFrame(over_data)

# Test with Hardik Pandya
print("=" * 80)
print("OVER-BY-OVER PROGRESSION TEST")
print("=" * 80)

# Get all Hardik matches
df = pd.read_csv('ipl_data_mens_only.csv')
hardik_matches = df[df['Batsman'] == 'HH Pandya']['Match⬆'].unique()

print(f"\nHH Pandya has {len(hardik_matches)} matches in dataset")
print("\nSample match progression:")

# Show first match with RRR data
for match in hardik_matches[:3]:
    print(f"\n{'='*60}")
    print(f"Match: {match}")
    print(f"{'='*60}")
    
    progression = get_player_over_progression('HH Pandya', match)
    
    if not progression.empty and progression['RRR'].notna().any():
        print(progression.to_string(index=False))
        print(f"\nEntry Over: {progression['Over'].min()}")
        print(f"Exit Over: {progression['Over'].max()}")
        print(f"Duration: {len(progression)} overs")
        print(f"Final SR: {progression['Strike_Rate'].iloc[-1]:.1f}")
        print(f"Entry RRR: {progression['RRR'].iloc[0]:.2f}")
        print(f"Exit RRR: {progression['RRR'].iloc[-1]:.2f}")
        break

print("\n" + "=" * 80)
print("This data can be used to create a line chart showing:")
print("  - Player SR progression (line)")
print("  - RRR progression (line)")
print("  - Over-by-over comparison")
print("=" * 80)
