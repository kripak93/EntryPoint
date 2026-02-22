#!/usr/bin/env python3
"""
Test general "who is best" questions
"""

import pandas as pd
from react_cricket_agent import create_react_agent

def test_general_questions():
    """Test that general questions work properly"""
    
    print("🧪 Testing General 'Who is Best' Questions")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    
    # Filter for MI, 2023 and 2025
    df_filtered = df[
        (df['Team'] == 'MI') & 
        (df['Span⬇'].str.contains('2023|2025'))
    ]
    
    print(f"📊 Filtered data: {len(df_filtered)} records (MI, 2023+2025)")
    
    # Create agent with filtered data
    from react_cricket_agent import CricketDataAnalyzer
    
    class MockAI:
        def generate_content(self, prompt):
            class MockResponse:
                def __init__(self):
                    self.text = "Based on the data analysis, here are the recommendations..."
            return MockResponse()
    
    agent = create_react_agent(df_filtered, MockAI())
    
    # Test questions
    test_questions = [
        "Who is best at death overs?",
        "Who are the best death over batsmen?",
        "Best players for death overs",
        "Top performers in death overs"
    ]
    
    for question in test_questions:
        print(f"\n{'='*80}")
        print(f"❓ Question: {question}")
        print("─" * 80)
        
        # Extract entities
        entities = agent._extract_entities(question)
        print(f"🧠 Entities: {entities}")
        
        # Plan actions
        actions = agent._reason_and_plan(question, entities)
        print(f"🔍 Actions: {actions}")
        
        # Execute actions
        action_results = {}
        for action in actions:
            result = agent._execute_action(action)
            action_results[action] = result
            
            if result and isinstance(result, list):
                print(f"✅ Retrieved {len(result)} players for {action}")
                if result:
                    print(f"   Top 3: {[p['player'] for p in result[:3]]}")
        
        # Check observations
        observations = agent._analyze_results(action_results, entities)
        has_data = "TOP PERFORMERS" in observations
        
        print(f"📊 Has player data: {'✅' if has_data else '❌'}")
        
        if not has_data:
            print("⚠️  WARNING: No player data retrieved for general question!")

if __name__ == "__main__":
    test_general_questions()
    
    print(f"\n{'='*80}")
    print("🎉 General question testing complete!")
    print("   The agent should now properly handle 'who is best' questions.")