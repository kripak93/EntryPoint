#!/usr/bin/env python3
"""
Test Cricket Analytics Integration
"""

import json
import os

def test_cricket_data_loading():
    """Test loading cricket analytics data"""
    try:
        with open('cricket_analytics_data (1).json', 'r') as f:
            data = json.load(f)
        
        print("✅ Cricket analytics data loaded successfully")
        
        # Check structure
        teams = data.get('metadata', {}).get('teams', {})
        matchups = data.get('matchups', {})
        insights = data.get('insights', [])
        
        print(f"📊 Teams available: {len(teams)}")
        print(f"⚔️ Matchup datasets: {len(matchups)}")
        print(f"💡 Strategic insights: {len(insights)}")
        
        # Show team list
        print("\n🏟️ Available Teams:")
        for code, name in teams.items():
            print(f"  {code}: {name}")
        
        # Show sample insights
        print(f"\n💡 Sample Insights:")
        for insight in insights[:3]:
            print(f"  {insight['type'].upper()}: {insight['title']}")
        
        return True
        
    except FileNotFoundError:
        print("❌ Cricket analytics data file not found")
        print("   Expected: cricket_analytics_data (1).json")
        return False
    except Exception as e:
        print(f"❌ Error loading cricket data: {e}")
        return False

def test_ipl_data_loading():
    """Test loading IPL data"""
    try:
        import pandas as pd
        df = pd.read_csv('ipl_data.csv')
        
        print("✅ IPL data loaded successfully")
        print(f"📊 Records: {len(df):,}")
        print(f"👥 Players: {df['Player'].nunique()}")
        print(f"🏟️ Teams: {df['Team'].nunique()}")
        
        return True
        
    except FileNotFoundError:
        print("❌ IPL data file not found")
        print("   Expected: ipl_data.csv")
        return False
    except Exception as e:
        print(f"❌ Error loading IPL data: {e}")
        return False

def main():
    print("🏏 Testing Cricket Analytics Integration")
    print("=" * 50)
    
    cricket_ok = test_cricket_data_loading()
    print()
    ipl_ok = test_ipl_data_loading()
    
    print("\n" + "=" * 50)
    
    if cricket_ok and ipl_ok:
        print("✅ All data sources available - Full integration ready!")
        print("\n🚀 Run: streamlit run production_app.py")
    elif cricket_ok:
        print("✅ Cricket analytics available - Enhanced game prep ready!")
        print("⚠️ IPL data missing - Some features limited")
    elif ipl_ok:
        print("✅ IPL data available - Basic analytics ready!")
        print("⚠️ Cricket analytics missing - Game prep features limited")
    else:
        print("❌ No data sources available")
        print("   Please ensure data files are in the current directory")

if __name__ == "__main__":
    main()