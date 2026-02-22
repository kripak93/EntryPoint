"""
Check HH Pandya's performance in match LAT20 # 14977
"""
import pandas as pd

match_id = 'LAT20 # 14977'
player = 'HH Pandya'

print("=" * 80)
print(f"HARDIK PANDYA - {match_id}")
print("=" * 80)

# Load ball-by-ball data
df = pd.read_csv('ipl_data_mens_only.csv')

# Filter to this player and match
match_df = df[(df['Batsman'] == player) & (df['Match⬆'] == match_id)].copy()

if match_df.empty:
    print(f"\nNo data found for {player} in {match_id}")
else:
    print(f"\nFound {len(match_df)} balls for {player}")
    
    # Process data
    match_df['Over_Num'] = match_df['Overs'].astype(str).str.split('.').str[0].astype(int)
    match_df['Ball_Num'] = match_df['Overs'].astype(str).str.split('.').str[1].astype(int)
    match_df['Runs_Cum'] = pd.to_numeric(match_df['R.1'], errors='coerce').fillna(0)
    match_df['Balls_Cum'] = pd.to_numeric(match_df['B'], errors='coerce').fillna(0)
    match_df['RRreq'] = pd.to_numeric(match_df['RRreq'], errors='coerce')
    match_df['Runs_Req'] = pd.to_numeric(match_df['RReq'], errors='coerce')
    match_df['Balls_Rem'] = pd.to_numeric(match_df['BRem'], errors='coerce')
    
    # Sort by over and ball
    match_df = match_df.sort_values(['Over_Num', 'Ball_Num'])
    
    # Summary stats
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    final_ball = match_df.iloc[-1]
    print(f"Entry Over: {match_df['Over_Num'].min()}")
    print(f"Exit Over: {match_df['Over_Num'].max()}")
    print(f"Total Runs: {final_ball['Runs_Cum']:.0f}")
    print(f"Total Balls: {final_ball['Balls_Cum']:.0f}")
    print(f"Strike Rate: {(final_ball['Runs_Cum'] / final_ball['Balls_Cum'] * 100):.1f}")
    print(f"Entry RRR: {match_df['RRreq'].iloc[0]:.2f}" if pd.notna(match_df['RRreq'].iloc[0]) else "Entry RRR: N/A")
    print(f"Exit RRR: {final_ball['RRreq']:.2f}" if pd.notna(final_ball['RRreq']) else "Exit RRR: N/A")
    
    # Over-by-over progression
    print("\n" + "=" * 80)
    print("OVER-BY-OVER PROGRESSION")
    print("=" * 80)
    
    over_data = []
    for over in sorted(match_df['Over_Num'].unique()):
        over_balls = match_df[match_df['Over_Num'] == over]
        last_ball = over_balls.iloc[-1]
        
        runs = last_ball['Runs_Cum']
        balls = last_ball['Balls_Cum']
        sr = (runs / balls * 100) if balls > 0 else 0
        rrr = last_ball['RRreq']
        rrr_as_sr = rrr * 100 / 6 if pd.notna(rrr) else None
        runs_req = last_ball['Runs_Req']
        balls_rem = last_ball['Balls_Rem']
        
        over_data.append({
            'Over': over,
            'Runs': int(runs),
            'Balls': int(balls),
            'SR': sr,
            'RRR': rrr,
            'RRR_as_SR': rrr_as_sr,
            'Runs_Req': runs_req,
            'Balls_Rem': balls_rem
        })
    
    prog_df = pd.DataFrame(over_data)
    print(prog_df.to_string(index=False))
    
    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    if prog_df['RRR_as_SR'].notna().any():
        avg_sr = prog_df['SR'].mean()
        avg_rrr_sr = prog_df['RRR_as_SR'].mean()
        
        print(f"Average Player SR: {avg_sr:.1f}")
        print(f"Average Required SR: {avg_rrr_sr:.1f}")
        print(f"Difference: {avg_sr - avg_rrr_sr:+.1f}")
        
        if avg_sr > avg_rrr_sr:
            print(f"\n✓ Player scored FASTER than required on average")
        else:
            print(f"\n✗ Player scored SLOWER than required on average")
        
        # Check if player kept pace
        above_req = (prog_df['SR'] > prog_df['RRR_as_SR']).sum()
        total_overs = len(prog_df[prog_df['RRR_as_SR'].notna()])
        print(f"\nOvers above requirement: {above_req}/{total_overs}")
    
    # Ball-by-ball details
    print("\n" + "=" * 80)
    print("BALL-BY-BALL DETAILS (First 10 balls)")
    print("=" * 80)
    
    ball_cols = ['Overs', 'Score', 'Runs_Cum', 'Balls_Cum', 'RRreq', 'Runs_Req', 'Balls_Rem']
    print(match_df[ball_cols].head(10).to_string(index=False))
