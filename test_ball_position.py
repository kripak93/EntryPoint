"""
Test ball position analysis functionality
"""

from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
from dotenv import load_dotenv

load_dotenv()

def test_ball_position():
    """Test ball position analysis"""
    
    print("🏏 Testing Ball Position Analysis")
    print("=" * 50)
    
    # Initialize analytics
    analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv')
    
    # Test 1: General query about ball position
    print("\n1️⃣ Testing general ball position query:")
    result = analytics.smart_analyze("Who has the best strike rate in the first ball of the over compared to the last ball?")
    print(f"Intent detected: {result['intent']}")
    print(f"Response preview: {result['gemini_response'][:300]}...")
    
    # Test 2: Specific player ball position analysis
    print("\n2️⃣ Testing player-specific ball position analysis:")
    player_result = analytics.analyze_ball_position("JJ Bumrah")
    print(f"Player: {player_result['player']}")
    print(f"\nBall Position Stats:")
    for stat in player_result['ball_analysis']:
        print(f"  {stat['Ball_Name']}: {stat['Avg_Runs_Per_Ball']} runs/ball, {stat['Dot_Percentage']}% dots")
    print(f"\nAI Insights preview: {player_result['ai_insights'][:300]}...")
    
    # Test 3: All players ball position
    print("\n3️⃣ Testing overall ball position analysis:")
    overall_result = analytics.analyze_ball_position()
    print(f"Analysis for: {overall_result['player']}")
    print(f"\nFirst ball vs Last ball:")
    first = overall_result['ball_analysis'][0]
    last = overall_result['ball_analysis'][5]
    print(f"  1st ball: {first['Avg_Runs_Per_Ball']} runs/ball")
    print(f"  6th ball: {last['Avg_Runs_Per_Ball']} runs/ball")
    print(f"  Difference: {abs(first['Avg_Runs_Per_Ball'] - last['Avg_Runs_Per_Ball']):.3f}")

if __name__ == "__main__":
    test_ball_position()