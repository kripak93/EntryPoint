"""
Process ball-by-ball IPL data to create entry point analysis
"""
import pandas as pd
import numpy as np

def process_ballbyball_to_entry_points(csv_path='ipl_data_mens_only.csv'):
    """
    Convert ball-by-ball data to entry point format with match situation metrics
    """
    print("Loading ball-by-ball data...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} balls")
    
    # Clean and prepare data
    df['Batsman'] = df['Batsman'].fillna('Unknown')
    df['Team'] = df['Opposition'].fillna('Unknown')  # Opposition = batting team
    df['Match'] = df['Match⬆'].fillna('Unknown')
    df['Over_Num'] = df['Overs'].astype(str).str.split('.').str[0].astype(float)
    df['Ball_In_Over'] = df['Overs'].astype(str).str.split('.').str[1].apply(
        lambda x: int(x) if str(x).isdigit() else 0
    )
    df['Runs'] = pd.to_numeric(df['R.1'], errors='coerce').fillna(0)  # Cumulative runs
    df['Balls'] = pd.to_numeric(df['B'], errors='coerce').fillna(0)  # Cumulative balls
    df['R'] = pd.to_numeric(df['R'], errors='coerce').fillna(0)  # Runs on THIS ball
    df['Bowling_Type'] = df['Technique'].fillna('Unknown')
    df['Bowling_Variation'] = df['Variation'].fillna('Unknown')
    df['Venue'] = df['Ground Name'].fillna('Unknown')
    df['Bowler'] = df['Player'].fillna('Unknown')
    if 'Competition' not in df.columns:
        df['Competition'] = 'IPL'

    # Match situation metrics
    df['Runs_Required'] = pd.to_numeric(df['RReq'], errors='coerce')
    df['Required_RR'] = pd.to_numeric(df['RRreq'], errors='coerce')
    df['Balls_Remaining'] = pd.to_numeric(df['BRem'], errors='coerce')
    df['Team_Score'] = df['Score'].astype(str)
    df['Innings'] = df['Bat']  # 1st or 2nd innings
    df['Chase_Target'] = pd.to_numeric(df['Target'], errors='coerce')  # Total target to chase

    # Extract year from date
    df['Date'] = pd.to_datetime(df['Date⬆'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Date_Str'] = df['Date'].dt.strftime('%Y-%m-%d')

    # Batting partner: for each ball, find the other batsman at the crease in the same match/over
    # We identify the non-striker by finding other batsmen who faced balls in the same match
    # Simple approach: for each batsman-match, record all other batsmen who batted in same match
    match_batsmen = df.groupby('Match')['Batsman'].apply(lambda x: list(x.unique())).to_dict()
    
    print("\nGrouping by batsman-match...")
    
    # For each batsman-match, get entry and exit situation
    entry_exit_data = []
    
    for (batsman, team, match, year), group in df.groupby(['Batsman', 'Team', 'Match', 'Year']):
        # Sort by over to get chronological order
        group = group.sort_values('Over_Num')
        
        # Entry point (first ball faced by this batsman in this match)
        entry_row = group.iloc[0]
        # Exit point (last ball faced by this batsman in this match)
        exit_row = group.iloc[-1]
        
        # The cumulative columns (R.1, B) show the batsman's stats UP TO that ball
        # So the exit_row contains the final totals for this batsman in this match
        player_runs = exit_row['Runs']
        player_balls = exit_row['Balls']
        
        # Calculate dots, fours, sixes from the R column (runs on each ball)
        player_dots = (group['R'] == 0).sum()  # Count balls where R = 0
        player_fours = (group['R'] == 4).sum()  # Count balls where R = 4
        player_sixes = (group['R'] == 6).sum()  # Count balls where R = 6

        # SR by each ball in over (ball 1-6)
        sr_by_ball = {}
        for ball_num in range(1, 7):
            ball_group = group[group['Ball_In_Over'] == ball_num]
            if len(ball_group) > 0:
                sr_by_ball[f'SR_Ball_{ball_num}'] = round(ball_group['R'].sum() / len(ball_group) * 100, 1)
            else:
                sr_by_ball[f'SR_Ball_{ball_num}'] = None

        # SR by each over
        sr_by_over = {}
        for over_num in range(1, 21):
            over_group = group[group['Over_Num'] == over_num]
            if len(over_group) > 0:
                sr_by_over[f'SR_Over_{over_num}'] = round(over_group['R'].sum() / len(over_group) * 100, 1)
            else:
                sr_by_over[f'SR_Over_{over_num}'] = None

        # Batting partners: other batsmen in same match (excluding self)
        partners = [b for b in match_batsmen.get(match, []) if b != batsman and b != 'Unknown']
        batting_partners = ', '.join(partners[:5]) if partners else 'None'

        # Bowling specs faced
        bowling_specs = group['Bowling_Variation'].dropna().unique()
        bowling_specs_str = ', '.join([s for s in bowling_specs if s not in ['-', 'Unknown']])

        # Dominant bowling type faced
        bowling_types_faced = group['Bowling_Type'].value_counts()
        dominant_bowling = bowling_types_faced.index[0] if len(bowling_types_faced) > 0 else 'Unknown'

        # Over slab for entry
        entry_over_int = int(entry_row['Over_Num'])
        if entry_over_int <= 3:
            over_slab = '1-3'
        elif entry_over_int <= 6:
            over_slab = '4-6'
        elif entry_over_int <= 10:
            over_slab = '7-10'
        elif entry_over_int <= 14:
            over_slab = '11-14'
        elif entry_over_int <= 17:
            over_slab = '15-17'
        else:
            over_slab = '18-20'

        # Skip invalid entries
        if player_balls <= 0:
            continue

        row = {
            'Player': batsman,
            'Team': team,
            'Match': match,
            'Year': year,
            'Competition': group['Competition'].iloc[0],
            'Date': entry_row['Date_Str'],
            'Venue': entry_row['Venue'],
            'Innings': entry_row['Innings'],
            'Chase_Target': entry_row['Chase_Target'],
            'Entry_Over': entry_row['Over_Num'],
            'Entry_Over_Slab': over_slab,
            'Exit_Over': exit_row['Over_Num'],
            'Runs': player_runs,
            'BF': player_balls,
            'Dots': player_dots,
            'Fours': player_fours,
            'Sixes': player_sixes,
            'Batting_Partners': batting_partners,
            'Bowling_Specs': bowling_specs_str,
            'Dominant_Bowling_Type': dominant_bowling,
            # Match situation at entry
            'Entry_RR_Required': entry_row['Required_RR'],
            'Entry_Runs_Required': entry_row['Runs_Required'],
            'Entry_Balls_Remaining': entry_row['Balls_Remaining'],
            # Match situation at exit
            'Exit_RR_Required': exit_row['Required_RR'],
            'Exit_Runs_Required': exit_row['Runs_Required'],
            'Exit_Balls_Remaining': exit_row['Balls_Remaining']
        }
        row.update(sr_by_ball)
        row.update(sr_by_over)
        entry_exit_data.append(row)

    entry_points = pd.DataFrame(entry_exit_data)
    
    # Calculate metrics
    entry_points['Strike_Rate'] = (entry_points['Runs'] / entry_points['BF'] * 100).fillna(0)
    entry_points['Dot_Pct'] = (entry_points['Dots'] / entry_points['BF'] * 100).fillna(0)
    entry_points['Bnd_Pct'] = ((entry_points['Fours'] + entry_points['Sixes']) / entry_points['BF'] * 100).fillna(0)

    # New metrics
    boundaries = entry_points['Fours'] + entry_points['Sixes']
    entry_points['Balls_Per_Boundary'] = (entry_points['BF'] / boundaries.replace(0, np.nan)).round(1)
    rotating = entry_points['BF'] - entry_points['Dots'] - boundaries
    entry_points['Strike_Rotation_Pct'] = (rotating.clip(lower=0) / entry_points['BF'] * 100).round(1)

    # Calculate overs played and innings duration
    entry_points['Overs_Played'] = (entry_points['BF'] / 6).round(1)
    entry_points['Exit_Over'] = (entry_points['Exit_Over']).round(0).astype(int)
    entry_points['Exit_Over'] = entry_points['Exit_Over'].clip(upper=20)
    entry_points['Innings_Duration'] = entry_points['Exit_Over'] - entry_points['Entry_Over'] + 1
    
    # Calculate RRR impact (TEAM metric - how much team RR changed)
    entry_points['Team_RRR_Impact'] = entry_points['Entry_RR_Required'] - entry_points['Exit_RR_Required']
    # Positive = team reduced required RR, Negative = team increased required RR
    
    # Calculate CONTRIBUTION METRICS
    # 1. % of Runs Remaining at Entry = (Player Runs / Runs Required at Entry) * 100
    #    This shows what % of the remaining chase the player contributed
    entry_points['Pct_of_Runs_Remaining'] = (entry_points['Runs'] / entry_points['Entry_Runs_Required'] * 100).fillna(0)
    entry_points['Pct_of_Runs_Remaining'] = entry_points['Pct_of_Runs_Remaining'].replace([float('inf'), -float('inf')], 0)
    
    # 2. Contribution per Over = Player Runs / Overs Played
    entry_points['Contribution_Per_Over'] = (entry_points['Runs'] / (entry_points['BF'] / 6)).fillna(0)
    entry_points['Contribution_Per_Over'] = entry_points['Contribution_Per_Over'].replace([float('inf'), -float('inf')], 0)
    
    # 3. % of Chase Target (for reference)
    entry_points['Pct_of_Target'] = (entry_points['Runs'] / entry_points['Chase_Target'] * 100).fillna(0)
    entry_points['Pct_of_Target'] = entry_points['Pct_of_Target'].replace([float('inf'), -float('inf')], 0)
    
    # ALSO keep the RRR-based calculation for comparison
    # Required runs for the overs this player batted = RRR * (balls_faced / 6)
    entry_points['Required_Runs_For_Balls'] = entry_points['Entry_RR_Required'] * entry_points['BF'] / 6
    
    # Contribution % = (Actual Runs / Required Runs) * 100
    # >100% = exceeded requirement, <100% = fell short
    entry_points['Contribution_Pct'] = (entry_points['Runs'] / entry_points['Required_Runs_For_Balls'] * 100).fillna(0)
    entry_points['Contribution_Pct'] = entry_points['Contribution_Pct'].replace([float('inf'), -float('inf')], 0)
    
    # Impact Runs = Actual - Required (how many runs above/below requirement)
    entry_points['Impact_Runs'] = (entry_points['Runs'] - entry_points['Required_Runs_For_Balls']).fillna(0)
    
    # For reference, also calculate player's run rate
    entry_points['Player_Run_Rate'] = entry_points['Strike_Rate'] / 100 * 6  # Convert SR to runs per over
    
    # Create entry phase
    entry_points['Entry_Phase'] = entry_points['Entry_Over'].apply(
        lambda x: 'Powerplay' if x <= 6 else 'Middle' if x <= 15 else 'Death'
    )
    
    # Rename Strike_Rate to Final_Strike_Rate for consistency
    entry_points['Final_Strike_Rate'] = entry_points['Strike_Rate']
    
    # Filter out invalid entries
    entry_points = entry_points[
        (entry_points['BF'] > 0) &
        (entry_points['Entry_Over'] > 0) &
        (entry_points['Entry_Over'] <= 20)
    ]
    
    print(f"\nProcessed {len(entry_points)} entry points")
    print(f"Unique players: {entry_points['Player'].nunique()}")
    print(f"Unique matches: {entry_points['Match'].nunique()}")
    print(f"Years: {sorted(entry_points['Year'].dropna().unique())}")
    
    # Show phase distribution
    print("\nEntry phase distribution:")
    print(entry_points['Entry_Phase'].value_counts())
    
    # Show impact stats (only for entries with RRR data)
    rrr_entries = entry_points[entry_points['Entry_RR_Required'].notna()]
    if len(rrr_entries) > 0:
        print("\nMatch Impact stats (entries with RRR data):")
        print(f"  Entries with RRR: {len(rrr_entries)}")
        print(f"  Avg % of Runs Remaining: {rrr_entries['Pct_of_Runs_Remaining'].mean():.2f}%")
        print(f"  Avg Contribution per Over: {rrr_entries['Contribution_Per_Over'].mean():.2f} RPO")
        print(f"  Avg % of Target: {rrr_entries['Pct_of_Target'].mean():.2f}%")
        print(f"  Avg RRR Contribution %: {rrr_entries['Contribution_Pct'].mean():.1f}%")
    
    return entry_points

def get_bowling_type_stats(csv_path='ipl_data_mens_only.csv'):
    """
    Get batsman performance vs different bowling types
    """
    print("\nCalculating bowling type matchups...")
    df = pd.read_csv(csv_path)
    
    # Clean data
    df['Batsman'] = df['Batsman'].fillna('Unknown')
    df['Bowling_Type'] = df['Technique'].fillna('Unknown')
    
    # Categorize bowling types
    def categorize_bowling(technique):
        technique = str(technique).lower()
        if 'pace' in technique or 'fast' in technique or 'seam' in technique:
            return 'Pace'
        elif 'spin' in technique or 'orthodox' in technique or 'break' in technique or 'leg' in technique:
            return 'Spin'
        else:
            return 'Other'
    
    df['Bowling_Category'] = df['Bowling_Type'].apply(categorize_bowling)
    
    # For each batsman-match-bowling_category, get the FINAL cumulative values
    # R.1 and B are cumulative, so we take max per match
    df['Match'] = df['Match⬆'].fillna('Unknown')
    df['Runs_Cumulative'] = pd.to_numeric(df['R.1'], errors='coerce').fillna(0)
    df['Balls_Cumulative'] = pd.to_numeric(df['B'], errors='coerce').fillna(0)
    
    # Group by batsman, match, and bowling category to get final values
    match_stats = df.groupby(['Batsman', 'Match', 'Bowling_Category']).agg({
        'Runs_Cumulative': 'max',  # Final runs against this bowling type in this match
        'Balls_Cumulative': 'max'  # Final balls against this bowling type in this match
    }).reset_index()
    
    # Now aggregate across all matches
    bowling_stats = match_stats.groupby(['Batsman', 'Bowling_Category']).agg({
        'Runs_Cumulative': 'sum',
        'Balls_Cumulative': 'sum'
    }).reset_index()
    
    bowling_stats.columns = ['Batsman', 'Bowling_Category', 'Runs', 'Balls']
    bowling_stats['Strike_Rate'] = (bowling_stats['Runs'] / bowling_stats['Balls'] * 100).round(1)
    
    # Filter out entries with no balls
    bowling_stats = bowling_stats[bowling_stats['Balls'] > 0]
    
    print(f"Calculated stats for {bowling_stats['Batsman'].nunique()} batsmen")
    print("\nBowling type distribution:")
    print(match_stats['Bowling_Category'].value_counts())
    
    return bowling_stats

if __name__ == "__main__":
    # Process entry points from multi-league source
    entry_df = process_ballbyball_to_entry_points(csv_path='multi_league_data.csv')
    
    # Save to CSV
    output_file = 'processed_entry_points_ballbyball.csv'
    entry_df.to_csv(output_file, index=False)
    print(f"\n✅ Saved to {output_file}")
    
    # Show sample
    print("\nSample data:")
    print(entry_df.head(10))
    
    # Get bowling type stats
    bowling_df = get_bowling_type_stats()
    bowling_output = 'bowling_type_matchups.csv'
    bowling_df.to_csv(bowling_output, index=False)
    print(f"\n✅ Saved bowling matchups to {bowling_output}")
    
    print("\nSample bowling matchups:")
    print(bowling_df[bowling_df['Batsman'] == 'V Kohli'])
