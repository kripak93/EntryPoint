"""
Analyze player performance by ball position within an over
Example: Bumrah's performance on 1st ball vs last ball of an over
"""

import pandas as pd
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import os
from dotenv import load_dotenv

def analyze_ball_position(player_name="JJ Bumrah"):
    """Analyze player performance by ball position in over"""
    
    load_dotenv()
    
    print(f"🏏 Analyzing {player_name}'s Performance by Ball Position")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv('ipl_data.csv')
    
    # Filter for the player
    player_data = df[df['Player'] == player_name].copy()
    
    if player_data.empty:
        print(f"❌ No data found for {player_name}")
        return
    
    print(f"📊 Total balls bowled by {player_name}: {len(player_data)}")
    
    # Extract ball position from Overs column
    player_data['Over_Number'] = player_data['Overs'].astype(str).str.split('.').str[0].astype(int)
    player_data['Ball_Position'] = player_data['Overs'].astype(str).str.split('.').str[1].astype(int)
    
    # Analyze by ball position
    print(f"\n🎯 Ball Position Analysis:")
    
    ball_stats = []
    for ball_pos in sorted(player_data['Ball_Position'].unique()):
        ball_data = player_data[player_data['Ball_Position'] == ball_pos]
        
        # Calculate stats
        total_balls = len(ball_data)
        runs_conceded = ball_data['R'].sum() if 'R' in ball_data.columns else 0
        wickets = len(ball_data[ball_data['Wkt'] != '-']) if 'Wkt' in ball_data.columns else 0
        dots = len(ball_data[ball_data['0'] == 1]) if '0' in ball_data.columns else 0
        fours = len(ball_data[ball_data['4'] == 1]) if '4' in ball_data.columns else 0
        sixes = len(ball_data[ball_data['6'] == 1]) if '6' in ball_data.columns else 0
        
        ball_name = "1st ball" if ball_pos == 1 else f"{ball_pos}th ball" if ball_pos <= 6 else f"Extra ball ({ball_pos})"
        
        ball_stats.append({
            'Ball_Position': ball_name,
            'Total_Balls': total_balls,
            'Runs_Conceded': runs_conceded,
            'Wickets': wickets,
            'Dots': dots,
            'Fours': fours,
            'Sixes': sixes,
            'Avg_Runs_Per_Ball': round(runs_conceded / total_balls, 2) if total_balls > 0 else 0,
            'Dot_Percentage': round((dots / total_balls) * 100, 1) if total_balls > 0 else 0
        })
    
    # Display results
    stats_df = pd.DataFrame(ball_stats)
    print(stats_df.to_string(index=False))
    
    # Specific comparison: 1st ball vs 6th ball
    print(f"\n⚡ Key Comparison: 1st Ball vs 6th Ball (Last Ball)")
    print("=" * 50)
    
    first_ball = player_data[player_data['Ball_Position'] == 1]
    last_ball = player_data[player_data['Ball_Position'] == 6]
    
    if not first_ball.empty and not last_ball.empty:
        print(f"1st Ball of Over:")
        print(f"  • Total balls: {len(first_ball)}")
        print(f"  • Runs conceded: {first_ball['R'].sum()}")
        print(f"  • Wickets: {len(first_ball[first_ball['Wkt'] != '-'])}")
        print(f"  • Dot balls: {len(first_ball[first_ball['0'] == 1])}")
        print(f"  • Average runs per ball: {round(first_ball['R'].sum() / len(first_ball), 2)}")
        
        print(f"\n6th Ball of Over (Last Ball):")
        print(f"  • Total balls: {len(last_ball)}")
        print(f"  • Runs conceded: {last_ball['R'].sum()}")
        print(f"  • Wickets: {len(last_ball[last_ball['Wkt'] != '-'])}")
        print(f"  • Dot balls: {len(last_ball[last_ball['0'] == 1])}")
        print(f"  • Average runs per ball: {round(last_ball['R'].sum() / len(last_ball), 2)}")
        
        # AI Analysis
        print(f"\n🤖 AI Analysis:")
        try:
            analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv')
            
            # Create a custom prompt for ball position analysis
            prompt = f"""
Analyze {player_name}'s bowling performance based on ball position within an over:

1ST BALL DATA:
- Total balls: {len(first_ball)}
- Runs conceded: {first_ball['R'].sum()}
- Wickets taken: {len(first_ball[first_ball['Wkt'] != '-'])}
- Dot balls: {len(first_ball[first_ball['0'] == 1])}

6TH BALL (LAST BALL) DATA:
- Total balls: {len(last_ball)}
- Runs conceded: {last_ball['R'].sum()}
- Wickets taken: {len(last_ball[last_ball['Wkt'] != '-'])}
- Dot balls: {len(last_ball[last_ball['0'] == 1])}

Please analyze:
1. Which ball position is more effective for {player_name}?
2. What patterns do you see?
3. Strategic insights about his bowling approach
4. Comparison of pressure situations (1st vs last ball)
"""
            
            response = analytics.model.generate_content(prompt)
            print(response.text)
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
    
    else:
        print("❌ Insufficient data for 1st vs 6th ball comparison")

def analyze_multiple_players():
    """Analyze multiple players for ball position performance"""
    
    players = ["JJ Bumrah", "YR Thakur", "MA Starc", "HH Pandya"]
    
    print("🏏 Multi-Player Ball Position Analysis")
    print("=" * 50)
    
    df = pd.read_csv('ipl_data.csv')
    
    for player in players:
        player_data = df[df['Player'] == player]
        if not player_data.empty:
            player_data = player_data.copy()
            player_data['Ball_Position'] = player_data['Overs'].astype(str).str.split('.').str[1].astype(int)
            
            first_ball = player_data[player_data['Ball_Position'] == 1]
            last_ball = player_data[player_data['Ball_Position'] == 6]
            
            if not first_ball.empty and not last_ball.empty:
                first_avg = round(first_ball['R'].sum() / len(first_ball), 2)
                last_avg = round(last_ball['R'].sum() / len(last_ball), 2)
                
                print(f"\n{player}:")
                print(f"  1st ball avg: {first_avg} | 6th ball avg: {last_avg}")
                print(f"  Better on: {'1st ball' if first_avg < last_avg else '6th ball'}")

if __name__ == "__main__":
    # Single player detailed analysis
    analyze_ball_position("JJ Bumrah")
    
    print("\n" + "="*60)
    
    # Multi-player comparison
    analyze_multiple_players()