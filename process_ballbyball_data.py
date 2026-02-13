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
    df['Runs'] = pd.to_numeric(df['R.1'], errors='coerce').fillna(0)
    df['Balls'] = pd.to_numeric(df['B'], errors='coerce').fillna(0)
    df['Dots'] = pd.to_numeric(df['0'], errors='coerce').fillna(0)
    df['Fours'] = pd.to_numeric(df['4'], errors='coerce').fillna(0)
    df['Sixes'] = pd.to_numeric(df['6'], errors='coerce').fillna(0)
    df['Bowling_Type'] = df['Technique'].fillna('Unknown')
    
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
    
    print("\nGrouping by batsman-match...")
    
    # For each batsman-match, get entry and exit situation
    entry_exit_data = []
    
    for (batsman, team, match, year), group in df.groupby(['Batsman', 'Team', 'Match', 'Year']):
        # Sort by over to get chronological order
        group = group.sort_values('Over_Num')
        
        # Entry point (first ball)
        entry_row = group.iloc[0]
        exit_row = group.iloc[-1]
        
        entry_exit_data.append({
            'Player': batsman,
            'Team': team,
            'Match': match,
            'Year': year,
            'Innings': entry_row['Innings'],  # 1st or 2nd
            'Chase_Target': entry_row['Chase_Target'],  # Total target (only for 1st innings/chasing)
            'Entry_Over': entry_row['Over_Num'],
            'Exit_Over': exit_row['Over_Num'],
            'Runs': exit_row['Runs'],  # Final cumulative runs
            'BF': exit_row['Balls'],   # Final cumulative balls
            'Dots': group['Dots'].sum(),
            'Fours': group['Fours'].sum(),
            'Sixes': group['Sixes'].sum(),
            # Match situation at entry
            'Entry_RR_Required': entry_row['Required_RR'],
            'Entry_Runs_Required': entry_row['Runs_Required'],
            'Entry_Balls_Remaining': entry_row['Balls_Remaining'],
            # Match situation at exit
            'Exit_RR_Required': exit_row['Required_RR'],
            'Exit_Runs_Required': exit_row['Runs_Required'],
            'Exit_Balls_Remaining': exit_row['Balls_Remaining']
        })
    
    entry_points = pd.DataFrame(entry_exit_data)
    
    # Calculate metrics
    entry_points['Strike_Rate'] = (entry_points['Runs'] / entry_points['BF'] * 100).fillna(0)
    entry_points['Dot_Pct'] = (entry_points['Dots'] / entry_points['BF'] * 100).fillna(0)
    entry_points['Bnd_Pct'] = ((entry_points['Fours'] + entry_points['Sixes']) / entry_points['BF'] * 100).fillna(0)
    
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
    # Process entry points
    entry_df = process_ballbyball_to_entry_points()
    
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
