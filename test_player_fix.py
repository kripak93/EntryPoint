"""
Test the fixed player insights functionality
"""

from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import pandas as pd

def test_player_insights():
    """Test player insights with full data"""
    
    print("🏏 Testing Fixed Player Insights")
    print("=" * 50)
    
    # Load raw data for comparison
    df = pd.read_csv('ipl_data.csv')
    
    # Test players with different data amounts
    test_players = ['A Mhatre', 'V Kohli', 'JJ Bumrah']
    
    for player in test_players:
        print(f"\n📊 Testing: {player}")
        print("-" * 30)
        
        # Raw data check
        raw_batting = df[df['Batsman'] == player]
        raw_bowling = df[df['Player'] == player]
        
        print(f"Raw data - Batting: {len(raw_batting)}, Bowling: {len(raw_bowling)}")
        
        # Analytics check (2025 season)
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv', season_filter=2025)
        result = analytics.get_player_insights(player)
        
        print(f"Analytics - Batting: {result['batting_matches']}, Bowling: {result['bowling_matches']}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            # Check if AI mentions the correct number of records
            insights = result['gemini_insights']
            if str(result['batting_matches']) in insights or str(result['bowling_matches']) in insights:
                print("✅ AI correctly references full dataset")
            else:
                print("⚠️ AI might not be using full dataset info")
            
            print(f"Response preview: {insights[:200]}...")

if __name__ == "__main__":
    test_player_insights()