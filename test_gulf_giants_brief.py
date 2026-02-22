"""
Test Gulf Giants style scouting brief generation
"""

from ipl_strategy_engine import IPLStrategyEngine
import pandas as pd

def test_brief_format():
    """Test if the brief matches Gulf Giants requirements"""
    
    print("🏏 Testing Gulf Giants Brief Format")
    print("=" * 50)
    
    # Initialize engine
    engine = IPLStrategyEngine()
    
    # Check available data
    print("📊 Data check:")
    print(f"Total records: {len(engine.df)}")
    print(f"Available batsmen: {engine.df['batsman'].nunique()}")
    print(f"Bowler categories: {engine.df['bowler_category'].value_counts().to_dict()}")
    
    # Test with a known batsman
    available_batsmen = engine.df['batsman'].dropna().unique()
    test_batsman = available_batsmen[0] if len(available_batsmen) > 0 else None
    
    if test_batsman:
        print(f"\n🎯 Testing brief for: {test_batsman}")
        
        # Generate brief
        brief = engine.generate_scouting_brief(test_batsman, 'RAF')
        
        print("\n📋 Brief Preview:")
        print("=" * 30)
        print(brief[:800] + "..." if len(brief) > 800 else brief)
        
        # Check if it has all required sections
        required_sections = [
            "OVERVIEW",
            "POWERPLAY",
            "POST POWERPLAY", 
            "TACTICAL SUMMARY",
            "Strike Rate by Length",
            "Strike Rate by Zone",
            "Boundary Analysis"
        ]
        
        print(f"\n✅ Section Check:")
        for section in required_sections:
            if section in brief:
                print(f"  ✅ {section}")
            else:
                print(f"  ❌ {section}")
    
    else:
        print("❌ No batsmen found in dataset")

if __name__ == "__main__":
    test_brief_format()