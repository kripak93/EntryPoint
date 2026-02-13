"""
Process ball-by-ball data with ball position in over
Analyze performance by: Ball Number in Over + RRR Range
"""
import pandas as pd
import numpy as np

def process_ball_position_analysis(csv_path='ipl_data_mens_only.csv'):
    """
    Create ball-by-ball analysis showing:
    - Which ball of the over (1-6)
    - RRR at that ball
    - Entry over phase (Powerplay, Middle, Death)
    - Outcome (runs scored, boundary, dot)
    - Player performance by ball position
    """
    print("Loading ball-by-ball data...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} balls")
    
    # Clean and prepare data
    df['Batsman'] = df['Batsman'].fillna('Unknown')
    df['Team'] = df['Opposition'].fillna('Unknown')
    df['Match'] = df['Match⬆'].fillna('Unknown')
    
    # Extract over and ball number
    df['Over_Ball'] = df['Overs'].astype(str)
    df['Over_Num'] = df['Over_Ball'].str.split('.').str[0].astype(float)
    df['Ball_Num'] = df['Over_Ball'].str.split('.').str[1].astype(float)
    
    # Get ball outcome - R.1 is cumulative runs, need to calculate runs per ball
    df['Cumulative_Runs'] = pd.to_numeric(df['R.1'], errors='coerce').fillna(0)
    
    # Calculate runs scored on this ball (difference from previous ball)
    # Group by match and batsman to handle innings properly
    df = df.sort_values(['Match', 'Batsman', 'Overs'])
    df['Runs_This_Ball'] = df.groupby(['Match', 'Batsman'])['Cumulative_Runs'].diff().fillna(df['Cumulative_Runs'])
    
    # Handle negative values (shouldn't happen but just in case)
    df['Runs_This_Ball'] = df['Runs_This_Ball'].clip(lower=0)
    
    df['Is_Dot'] = (df['Runs_This_Ball'] == 0).astype(int)
    df['Is_Boundary'] = ((df['Runs_This_Ball'] == 4) | (df['Runs_This_Ball'] == 6)).astype(int)
    df['Is_Four'] = (df['Runs_This_Ball'] == 4).astype(int)
    df['Is_Six'] = (df['Runs_This_Ball'] == 6).astype(int)
    
    # Match situation
    df['RRreq'] = pd.to_numeric(df['RRreq'], errors='coerce')
    df['Runs_Required'] = pd.to_numeric(df['RReq'], errors='coerce')
    df['Balls_Remaining'] = pd.to_numeric(df['BRem'], errors='coerce')
    df['Innings'] = df['Bat']
    
    # Extract year
    df['Date'] = pd.to_datetime(df['Date⬆'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    
    # Filter to valid balls (1-6 in over)
    df = df[(df['Ball_Num'] >= 1) & (df['Ball_Num'] <= 6)]
    
    # Calculate entry over for each batsman in each match
    print("Calculating entry overs...")
    entry_overs = df.groupby(['Match', 'Batsman'])['Over_Num'].min().reset_index()
    entry_overs.columns = ['Match', 'Batsman', 'Entry_Over']
    df = df.merge(entry_overs, on=['Match', 'Batsman'], how='left')
    
    # Categorize entry over phase
    def categorize_entry_phase(over):
        if pd.isna(over):
            return 'Unknown'
        elif over < 6:
            return 'Powerplay (0-6)'
        elif over < 16:
            return 'Middle (7-15)'
        else:
            return 'Death (16-20)'
    
    df['Entry_Phase'] = df['Entry_Over'].apply(categorize_entry_phase)
    
    # Create RRR ranges
    def categorize_rrr(rrr):
        if pd.isna(rrr):
            return 'No RRR'
        elif rrr < 6:
            return '0-6 RPO'
        elif rrr < 9:
            return '6-9 RPO'
        elif rrr < 12:
            return '9-12 RPO'
        elif rrr < 15:
            return '12-15 RPO'
        else:
            return '15+ RPO'
    
    df['RRR_Range'] = df['RRreq'].apply(categorize_rrr)
    
    # Create ball position categories
    def categorize_ball_position(ball_num):
        if ball_num <= 2:
            return 'Early (1-2)'
        elif ball_num <= 4:
            return 'Middle (3-4)'
        else:
            return 'Late (5-6)'
    
    df['Ball_Position'] = df['Ball_Num'].apply(categorize_ball_position)
    
    print(f"\nProcessed {len(df)} balls")
    print(f"Unique players: {df['Batsman'].nunique()}")
    print(f"Unique matches: {df['Match'].nunique()}")
    
    # Save detailed ball-by-ball data
    ball_cols = ['Batsman', 'Team', 'Match', 'Year', 'Innings', 'Over_Num', 'Ball_Num',
                 'Ball_Position', 'Entry_Over', 'Entry_Phase', 'Runs_This_Ball', 'Is_Dot', 
                 'Is_Boundary', 'Is_Four', 'Is_Six', 'RRreq', 'RRR_Range', 'Runs_Required', 
                 'Balls_Remaining']
    
    ball_df = df[ball_cols].copy()
    ball_df.to_csv('ball_position_analysis.csv', index=False)
    print(f"\n✅ Saved detailed data to ball_position_analysis.csv")
    
    return ball_df

def analyze_player_by_ball_position(ball_df, player_name=None):
    """
    Analyze player performance by ball position and RRR
    """
    if player_name:
        player_df = ball_df[ball_df['Batsman'] == player_name].copy()
    else:
        player_df = ball_df.copy()
    
    # Filter to chase scenarios only
    chase_df = player_df[player_df['RRR_Range'] != 'No RRR'].copy()
    
    if chase_df.empty:
        return pd.DataFrame()
    
    # Aggregate by player, ball position, and RRR range
    analysis = chase_df.groupby(['Batsman', 'Ball_Position', 'RRR_Range']).agg({
        'Runs_This_Ball': ['count', 'sum', 'mean'],
        'Is_Dot': 'sum',
        'Is_Boundary': 'sum',
        'Is_Four': 'sum',
        'Is_Six': 'sum'
    }).reset_index()
    
    analysis.columns = ['Player', 'Ball_Position', 'RRR_Range', 'Balls_Faced', 
                       'Total_Runs', 'Avg_Runs', 'Dots', 'Boundaries', 'Fours', 'Sixes']
    
    # Calculate percentages
    analysis['Strike_Rate'] = (analysis['Total_Runs'] / analysis['Balls_Faced'] * 100).round(1)
    analysis['Dot_Pct'] = (analysis['Dots'] / analysis['Balls_Faced'] * 100).round(1)
    analysis['Boundary_Pct'] = (analysis['Boundaries'] / analysis['Balls_Faced'] * 100).round(1)
    
    # Filter minimum sample size
    analysis = analysis[analysis['Balls_Faced'] >= 5]
    
    return analysis

if __name__ == "__main__":
    # Process ball-by-ball data
    ball_df = process_ball_position_analysis()
    
    # Show distribution
    print("\n" + "=" * 80)
    print("BALL POSITION DISTRIBUTION")
    print("=" * 80)
    print("\nBalls by position:")
    print(ball_df['Ball_Position'].value_counts())
    
    print("\nBalls by RRR range:")
    print(ball_df['RRR_Range'].value_counts())
    
    # Analyze Hardik Pandya
    print("\n" + "=" * 80)
    print("HARDIK PANDYA - BALL POSITION ANALYSIS")
    print("=" * 80)
    
    hh_analysis = analyze_player_by_ball_position(ball_df, 'HH Pandya')
    
    if not hh_analysis.empty:
        print("\nPerformance by Ball Position and RRR:")
        print(hh_analysis.sort_values(['RRR_Range', 'Ball_Position']).to_string(index=False))
    
    # Overall analysis (top performers)
    print("\n" + "=" * 80)
    print("TOP PERFORMERS - LATE OVER BALLS (5-6) AT HIGH RRR (12+)")
    print("=" * 80)
    
    all_analysis = analyze_player_by_ball_position(ball_df)
    
    high_pressure = all_analysis[
        (all_analysis['Ball_Position'] == 'Late (5-6)') &
        (all_analysis['RRR_Range'].isin(['12-15 RPO', '15+ RPO']))
    ].copy()
    
    high_pressure = high_pressure.sort_values('Strike_Rate', ascending=False)
    print(high_pressure.head(15).to_string(index=False))
    
    print("\n" + "=" * 80)
    print("INSIGHTS")
    print("=" * 80)
    print("This analysis shows:")
    print("  - Player performance by ball position in over (1-2, 3-4, 5-6)")
    print("  - Performance at different RRR ranges")
    print("  - Strike rate and boundary % by situation")
    print("  - Identifies specialists for specific ball positions")
