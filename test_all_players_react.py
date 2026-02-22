#!/usr/bin/env python3
"""
Test ReAct agent with multiple players to ensure it ALWAYS uses actual data
"""

import pandas as pd
from react_cricket_agent import create_react_agent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_multiple_players():
    """Test that AI uses actual data for various players"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("🧪 Testing ReAct with Multiple Players")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, model)
    
    # Get list of available players
    players_in_data = df['Player'].unique()[:10]  # Test first 10
    
    print(f"📊 Testing with {len(players_in_data)} different players")
    print(f"Players: {', '.join(players_in_data[:5])}...\n")
    
    # Test questions for different players
    test_cases = [
        ("When should I play Virat Kohli in powerplay?", "Kohli"),
        ("Is MS Dhoni good for death overs?", "Dhoni"),
        ("How does Rohit Sharma perform against spin?", "Rohit"),
        ("Should I use KL Rahul in middle overs?", "Rahul"),
        ("What about David Warner for powerplay?", "Warner")
    ]
    
    results = []
    
    for question, player_keyword in test_cases:
        print(f"\n{'='*80}")
        print(f"❓ Question: {question}")
        print(f"🎯 Expected: Data for player containing '{player_keyword}'")
        print("─" * 80)
        
        # Get entities and actions
        entities = agent._extract_entities(question)
        actions = agent._reason_and_plan(question, entities)
        
        # Execute actions
        action_results = {}
        for action in actions:
            result = agent._execute_action(action)
            action_results[action] = result
        
        # Check if player data was retrieved
        player_data_found = False
        player_name = None
        
        for action, result in action_results.items():
            if 'get_player_stats' in action and result and isinstance(result, dict):
                player_data_found = True
                player_name = result.get('name', 'Unknown')
                print(f"✅ Player data retrieved: {player_name}")
                print(f"   - Matches: {result.get('total_matches', 'N/A')}")
                print(f"   - Avg Entry: {result.get('avg_entry_over', 'N/A')}")
                print(f"   - Avg SR: {result.get('avg_strike_rate', 'N/A')}")
                break
        
        if not player_data_found:
            print(f"❌ No player data found for '{player_keyword}'")
            results.append({
                'question': question,
                'player': player_keyword,
                'data_found': False,
                'player_name': None
            })
            continue
        
        # Get observations
        observations = agent._analyze_results(action_results, entities)
        
        # Check if observations contain player's actual stats
        has_player_stats = player_name in observations if player_name else False
        has_specific_numbers = any(str(x) in observations for x in ['Total Matches', 'Average Entry', 'Strike Rate'])
        
        print(f"\n📊 Observations Quality:")
        print(f"   - Contains player name: {'✅' if has_player_stats else '❌'}")
        print(f"   - Contains specific stats: {'✅' if has_specific_numbers else '❌'}")
        
        # Get AI response
        answer = agent.answer_question(question)
        
        # Verify AI used the actual data
        uses_player_name = player_name in answer if player_name else False
        uses_specific_numbers = any(str(result.get(key, '')) in answer for key in ['total_matches', 'avg_strike_rate', 'avg_entry_over'])
        avoids_generic_response = "not in the top" not in answer.lower() or player_name in answer
        
        print(f"\n🤖 AI Response Quality:")
        print(f"   - Uses player name: {'✅' if uses_player_name else '❌'}")
        print(f"   - Uses specific numbers: {'✅' if uses_specific_numbers else '❌'}")
        print(f"   - Avoids generic 'not in top' response: {'✅' if avoids_generic_response else '❌'}")
        
        # Show snippet of response
        print(f"\n📝 Response snippet:")
        print(f"   {answer[:200]}...")
        
        results.append({
            'question': question,
            'player': player_keyword,
            'data_found': player_data_found,
            'player_name': player_name,
            'uses_actual_data': uses_player_name and uses_specific_numbers,
            'quality_score': sum([uses_player_name, uses_specific_numbers, avoids_generic_response])
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    data_found_count = sum(1 for r in results if r['data_found'])
    quality_count = sum(1 for r in results if r.get('uses_actual_data', False))
    
    print(f"Total tests: {total_tests}")
    print(f"Player data retrieved: {data_found_count}/{total_tests} ({'✅' if data_found_count == total_tests else '❌'})")
    print(f"AI used actual data: {quality_count}/{total_tests} ({'✅' if quality_count == total_tests else '❌'})")
    
    print(f"\n{'='*80}")
    if quality_count == total_tests:
        print("🎉 SUCCESS! ReAct agent consistently uses actual player data!")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Some responses don't use actual player data")
        print("\nFailed cases:")
        for r in results:
            if not r.get('uses_actual_data', False):
                print(f"  - {r['question']} (Player: {r.get('player_name', 'Not found')})")

def test_edge_cases():
    """Test edge cases like player not found, multiple players, etc."""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print(f"\n{'='*80}")
    print("🧪 Testing Edge Cases")
    print("=" * 80)
    
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, model)
    
    edge_cases = [
        "Compare Virat Kohli vs MS Dhoni",  # Multiple players
        "Who is better: Rohit or Rahul?",   # Multiple players, informal
        "Best death over batsmen",          # No specific player
    ]
    
    for question in edge_cases:
        print(f"\n❓ Edge Case: {question}")
        
        entities = agent._extract_entities(question)
        actions = agent._reason_and_plan(question, entities)
        
        print(f"   🧠 Entities: {entities['players']}")
        print(f"   🔍 Actions: {len(actions)} planned")
        
        # Execute
        action_results = {}
        for action in actions:
            result = agent._execute_action(action)
            action_results[action] = result
        
        # Count player data retrieved
        player_count = sum(1 for action, result in action_results.items() 
                          if 'get_player_stats' in action and result and isinstance(result, dict))
        
        print(f"   📊 Player data retrieved: {player_count}")
        
        if player_count > 0:
            print(f"   ✅ Correctly retrieved data for mentioned players")
        elif not entities['players']:
            print(f"   ✅ Correctly handled question without specific players")
        else:
            print(f"   ⚠️  Expected player data but none retrieved")

if __name__ == "__main__":
    test_multiple_players()
    test_edge_cases()
    
    print(f"\n{'='*80}")
    print("🚀 ReAct Agent Testing Complete!")
    print("   The agent should now consistently use actual player data")
    print("   for ANY player mentioned in questions.")