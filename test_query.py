"""
Test script to verify the AI only uses actual dataset players
"""

import os
from dotenv import load_dotenv
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics

def test_query():
    """Test that AI only uses actual dataset players"""
    
    load_dotenv()
    
    try:
        # Initialize analytics
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv')
        print(f"✅ Using model: {analytics.model_name}")
        
        # Test query that previously gave retired players
        print("\n🧪 Testing query: 'Who has the best economy rate?'")
        result = analytics.smart_analyze("Who has the best economy rate?")
        
        print(f"\nIntent detected: {result['intent']}")
        print(f"Data extracted: {result['data_extracted']} records")
        print("\n" + "="*50)
        print("AI Response:")
        print("="*50)
        print(result['gemini_response'])
        
        # Show actual top bowlers from data for comparison
        print("\n" + "="*50)
        print("Actual top bowlers by economy (for verification):")
        print("="*50)
        
        import pandas as pd
        df = pd.read_csv('ipl_data.csv')
        
        # Filter valid economy rates and minimum overs
        valid_econ = df[df['Econ'] != '-'].copy()
        valid_econ['Econ'] = pd.to_numeric(valid_econ['Econ'], errors='coerce')
        valid_econ = valid_econ[valid_econ['O'] >= 2.0]  # Minimum 2 overs
        
        top_bowlers = valid_econ.nsmallest(10, 'Econ')[['Player', 'Team', 'O', 'W', 'Econ']]
        print(top_bowlers.to_string())
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_query()