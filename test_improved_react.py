#!/usr/bin/env python3
"""
Test improved ReAct reasoning with actual player data
"""

import pandas as pd
from react_cricket_agent import create_react_agent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_improved_reasoning():
    """Test that AI uses actual player data, not just top performer lists"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key, skipping test")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("🧪 Testing Improved ReAct Reasoning")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, model)
    
    # Test question about Hardik Pandya
    question = "When should I play Hardik Pandya against spin bowling?"
    
    print(f"\n❓ Question: {question}")
    print("─" * 70)
    
    # Get entities and actions
    entities = agent._extract_entities(question)
    actions = agent._reason_and_plan(question, entities)
    
    print(f"🧠 Entities: {entities}")
    print(f"🔍 Actions: {actions}")
    
    # Execute actions and show observations
    action_results = {}
    for action in actions:
        result = agent._execute_action(action)
        action_results[action] = result
    
    observations = agent._analyze_results(action_results, entities)
    
    print(f"\n📊 DATA OBSERVATIONS:")
    print(observations)
    
    # Get AI response
    print(f"\n🤖 AI RESPONSE:")
    print("─" * 70)
    answer = agent.answer_question(question)
    print(answer)
    
    print("\n" + "=" * 70)
    print("✅ Check if the response:")
    print("   1. Uses Hardik Pandya's ACTUAL stats (not just 'not in top 3')")
    print("   2. Provides specific numbers from his data")
    print("   3. Gives nuanced analysis based on his performance")
    print("   4. Compares to benchmarks, not just top performers")

if __name__ == "__main__":
    test_improved_reasoning()