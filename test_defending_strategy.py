#!/usr/bin/env python3
"""
Test how the agent handles defensive strategy questions
"""

import pandas as pd
from react_cricket_agent import create_react_agent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_defensive_strategy():
    """Test defensive strategy question"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("🧪 Testing Defensive Strategy Question")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, model)
    
    question = "How should I defend a low total in death overs?"
    
    print(f"❓ Question: {question}")
    print("─" * 80)
    
    # Show what the agent reasons
    entities = agent._extract_entities(question)
    print(f"\n🧠 Entities Extracted:")
    print(f"   - Players: {entities['players']}")
    print(f"   - Phases: {entities['phases']}")
    print(f"   - Intent: {entities['intent']}")
    
    # Show what actions it plans
    actions = agent._reason_and_plan(question, entities)
    print(f"\n🔍 Actions Planned:")
    for action in actions:
        print(f"   - {action}")
    
    # Execute actions
    print(f"\n📊 Data Retrieved:")
    action_results = {}
    for action in actions:
        result = agent._execute_action(action)
        action_results[action] = result
        
        if result and isinstance(result, list):
            print(f"   ✅ {action}: {len(result)} players")
            if result:
                top_3 = result[:3]
                for i, p in enumerate(top_3, 1):
                    print(f"      {i}. {p['player']} - SR: {p['avg_strike_rate']}, Matches: {p['matches']}")
    
    # Get observations
    observations = agent._analyze_results(action_results, entities)
    print(f"\n👀 Observations Generated:")
    print(observations[:500] + "..." if len(observations) > 500 else observations)
    
    # Get AI response
    print(f"\n🤖 AI Response:")
    print("─" * 80)
    answer = agent.answer_question(question)
    print(answer)
    
    print(f"\n{'='*80}")
    print("📊 Analysis:")
    print("   The agent uses BATTING data (death over batsmen) to inform")
    print("   defensive strategy by identifying:")
    print("   - Which batsmen are most dangerous in death overs")
    print("   - Their strike rates and scoring patterns")
    print("   - How to bowl to limit their effectiveness")

if __name__ == "__main__":
    test_defensive_strategy()
    
    print(f"\n{'='*80}")
    print("💡 Current Approach:")
    print("   ✅ Uses batting data to identify threats")
    print("   ✅ AI provides tactical bowling recommendations")
    print("   ⚠️  No direct bowling performance data available")
    print("\n🔮 Future Enhancement:")
    print("   - Add bowling data (economy rates, wickets, yorker %)")
    print("   - Track bowler vs batsman matchups")
    print("   - Analyze field placements and bowling variations")