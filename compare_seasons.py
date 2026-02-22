"""
Compare IPL 2024 vs 2025 seasons
"""

import pandas as pd
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import os
from dotenv import load_dotenv

def compare_seasons():
    """Compare 2024 vs 2025 IPL seasons"""
    
    load_dotenv()
    
    print("🏏 Comparing IPL 2024 vs 2025 Seasons")
    print("=" * 50)
    
    try:
        # Load both seasons
        analytics_2024 = EnhancedGeminiIPLAnalytics('ipl_data.csv', season_filter=2024)
        analytics_2025 = EnhancedGeminiIPLAnalytics('ipl_data.csv', season_filter=2025)
        
        print(f"\n📊 Data Summary:")
        print(f"  2024: {len(analytics_2024.df):,} records")
        print(f"  2025: {len(analytics_2025.df):,} records")
        
        # Compare top bowlers
        print(f"\n🎯 Top Economy Rates (min 2 overs):")
        
        for year, analytics in [(2024, analytics_2024), (2025, analytics_2025)]:
            valid_bowlers = analytics.df[analytics.df['O'] >= 2.0]
            valid_bowlers = valid_bowlers[valid_bowlers['Econ'] != '-']
            valid_bowlers['Econ'] = pd.to_numeric(valid_bowlers['Econ'], errors='coerce')
            top_economy = valid_bowlers.nsmallest(5, 'Econ')[['Player', 'Team', 'O', 'W', 'Econ']]
            
            print(f"\n  📈 {year} Season:")
            if not top_economy.empty:
                print(top_economy.to_string(index=False))
            else:
                print("    No qualifying data")
        
        # AI comparison
        print(f"\n🤖 AI Analysis:")
        comparison_query = "Compare the bowling performances between what appears to be different time periods in this dataset"
        
        # Use 2024 data for comparison
        result = analytics_2024.smart_analyze(comparison_query)
        print(f"\n2024 Season Analysis:")
        print(result['gemini_response'][:500] + "..." if len(result['gemini_response']) > 500 else result['gemini_response'])
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    compare_seasons()