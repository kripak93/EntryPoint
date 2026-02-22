#!/usr/bin/env python3
"""
Test recency-aware ReAct agent
"""

import pandas as pd
from react_cricket_agent import create_react_agent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_recency_awareness():
    """Test that AI properly handles active vs retired players"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("🧪 Testing Recency-Aware ReAct Agent")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, model)
    
    # Find players with different recency statuses
    from react_cricket_agent import CricketDataAnalyzer
    analyzer = CricketDataAnalyzer(df)
    
    # Get some sample players
    all_players = df['Player'].unique()[:20]
    
    test_players = []
    for player in all_players:
        stats = analyzer.get_player_stats(player)
        if stats:
            test_players.append({
                'name': stats['name'],
                'recency_status': stats['recency_status'],
                'most_recent_year': stats['most_recent_year'],
                'recency_score': stats['recency_score']
            })
    
    # Sort by recency score
    test_players.sort(key=lambda x: x['recency_score'], reverse=True)
    
    print("📊 Sample Players by Recency:")
    for p in test_players[:10]:
        print(f"  - {p['name']}: {p['recency_status']} (Last: {p['most_recent_year']})")
    
    # Test with active and historical players
    test_cases = [
        (test_players[0]['name'], "ACTIVE"),  # Most recent
        (test_players[-1]['name'], "HISTORICAL"),  # Oldest
    ]
    
    for player_name, expected_status in test_cases:
        print(f"\n{'='*80}")
        print(f"❓ Testing: {player_name} (Expected: {expected_status})")
        print("─" * 80)
        
        question = f"Should I use {player_name} for middle overs batting?"
        
        # Get player stats directly
        stats = analyzer.get_player_stats(player_name)
        if stats:
            print(f"📊 Player Info:")
            print(f"   - Years: {stats['years_span']}")
            print(f"   - Most Recent: {stats['most_recent_year']}")
            print(f"   - Status: {stats['recency_status']}")
            print(f"   - Recency Score: {stats['recency_score']}")
            
            if 'recent_performance' in stats:
                print(f"   - Recent Performance: {stats['recent_performance']}")
            if 'historical_performance' in stats:
                print(f"   - Historical Performance: {stats['historical_performance']}")
        
        # Get AI response
        print(f"\n🤖 AI Response:")
        print("─" * 80)
        answer = agent.answer_question(question)
        print(answer[:500] + "..." if len(answer) > 500 else answer)
        
        # Check if AI mentions recency
        answer_lower = answer.lower()
        mentions_recency = any(word in answer_lower for word in ['active', 'recent', 'historical', 'retired', 'current', 'past', 'last played'])
        mentions_year = stats['most_recent_year'] in answer
        
        print(f"\n✅ Validation:")
        print(f"   - Mentions recency status: {'✅' if mentions_recency else '❌'}")
        print(f"   - Mentions year: {'✅' if mentions_year else '❌'}")
        
        if stats['recency_score'] < 0.5 and not mentions_recency:
            print(f"   ⚠️  WARNING: Historical player but AI didn't mention recency!")

def test_david_warner():
    """Specific test for David Warner (likely retired)"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print(f"\n{'='*80}")
    print("🧪 Specific Test: David Warner")
    print("=" * 80)
    
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, model)
    
    question = "Should I use David Warner for powerplay batting?"
    
    print(f"❓ Question: {question}")
    print("─" * 80)
    
    # Get response
    answer = agent.answer_question(question)
    
    print(f"🤖 AI Response:")
    print(answer)
    
    # Check for recency awareness
    answer_lower = answer.lower()
    has_recency_warning = any(word in answer_lower for word in ['historical', 'retired', 'past', 'no longer', 'last played'])
    
    print(f"\n✅ Recency Awareness: {'✅ Properly noted' if has_recency_warning else '⚠️  Should mention if historical'}")

if __name__ == "__main__":
    test_recency_awareness()
    test_david_warner()
    
    print(f"\n{'='*80}")
    print("🎉 Recency-Aware ReAct Testing Complete!")
    print("   The agent now considers player activity status and data relevance.")