#!/usr/bin/env python3
"""
Demo: ReAct Cricket Strategy Agent
Shows how the Reasoning + Acting methodology works for cricket analysis
"""

import pandas as pd
from react_cricket_agent import create_react_agent
import json

def demo_react_process():
    """Demonstrate the ReAct process step by step"""
    print("🏏 ReAct Cricket Strategy Agent Demo")
    print("=" * 50)
    
    # Load data
    print("📊 Loading cricket data...")
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    print(f"✅ Loaded {len(df)} records")
    
    # Create mock AI for demo
    class DemoAI:
        def generate_content(self, prompt):
            class DemoResponse:
                def __init__(self, prompt):
                    # Extract key info from prompt for demo
                    if "Hardik" in prompt:
                        self.text = """
                        Based on my ReAct analysis of Hardik Pandya's data:
                        
                        **Data Observations:**
                        - Hardik averages entry at over 11.0 with a strike rate of 6.7
                        - He has played multiple matches across different phases
                        - His performance shows adaptability to various match situations
                        
                        **Strategic Recommendation:**
                        Deploy Hardik Pandya against spin in the middle overs (7-15) when:
                        1. You need to accelerate the scoring rate
                        2. The required run rate is manageable (6-8 per over)
                        3. You have wickets in hand for his aggressive approach
                        
                        **Tactical Considerations:**
                        - His entry timing data suggests he's effective when coming in during transition phases
                        - Against spin, his strike rate indicates he can rotate strike and find boundaries
                        - Best deployed when the team needs 40-60 runs in 6-8 overs
                        """
                    else:
                        self.text = "Based on the ReAct analysis, here are the data-driven recommendations..."
            return DemoResponse(prompt)
    
    # Create ReAct agent
    print("🤖 Creating ReAct agent...")
    agent = create_react_agent(df, DemoAI())
    print("✅ ReAct agent ready!")
    
    # Demo question
    question = "When should I play Hardik Pandya against spin bowling?"
    print(f"\n❓ Demo Question: {question}")
    print("\n🔄 ReAct Process:")
    
    # Step 1: Show reasoning
    print("\n1️⃣ REASONING - Extracting entities and planning actions:")
    entities = agent._extract_entities(question)
    print(f"   🧠 Identified entities: {json.dumps(entities, indent=6)}")
    
    actions = agent._reason_and_plan(question, entities)
    print(f"   📋 Planned actions: {actions}")
    
    # Step 2: Show acting
    print("\n2️⃣ ACTING - Executing data queries:")
    for action in actions:
        result = agent._execute_action(action)
        if result:
            print(f"   🔍 {action}:")
            if isinstance(result, dict) and 'name' in result:
                print(f"      - Player: {result['name']}")
                print(f"      - Avg Entry Over: {result['avg_entry_over']}")
                print(f"      - Avg Strike Rate: {result['avg_strike_rate']}")
                print(f"      - Total Matches: {result['total_matches']}")
            elif isinstance(result, list) and result:
                print(f"      - Top performer: {result[0]['player']} (SR: {result[0]['avg_strike_rate']})")
    
    # Step 3: Show observing
    print("\n3️⃣ OBSERVING - Analyzing results:")
    print("   👀 Key observations from data:")
    print("      - Hardik Pandya's entry patterns identified")
    print("      - Performance metrics against spin scenarios calculated")
    print("      - Strategic deployment windows determined")
    
    # Step 4: Show final reasoning and response
    print("\n4️⃣ REASONING & RESPONDING - Generating strategic advice:")
    answer = agent.answer_question(question)
    print("   💡 Final strategic recommendation:")
    print("   " + "─" * 60)
    print(f"   {answer}")
    print("   " + "─" * 60)
    
    print("\n🎉 ReAct Process Complete!")
    print("\n📈 Benefits of ReAct Approach:")
    print("   ✅ Data-driven decisions (not just general cricket knowledge)")
    print("   ✅ Specific player analysis based on actual performance")
    print("   ✅ Transparent reasoning process")
    print("   ✅ Actionable tactical recommendations")
    print("   ✅ Adaptable to any cricket strategy question")

def demo_multiple_questions():
    """Demo multiple types of questions"""
    print("\n" + "=" * 60)
    print("🎯 Multiple Question Types Demo")
    print("=" * 60)
    
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    
    class QuickAI:
        def generate_content(self, prompt):
            class QuickResponse:
                def __init__(self):
                    self.text = "Strategic recommendation based on ReAct data analysis..."
            return QuickResponse()
    
    agent = create_react_agent(df, QuickAI())
    
    questions = [
        "Who are the best death over batsmen?",
        "Compare Virat Kohli vs MS Dhoni for middle overs",
        "What's the optimal powerplay strategy?",
        "Which players perform best against pace bowling?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        
        # Show what ReAct would analyze
        entities = agent._extract_entities(question)
        actions = agent._reason_and_plan(question, entities)
        
        print(f"   🧠 ReAct would analyze: {entities['intent']}")
        print(f"   🔍 Data queries: {len(actions)} specific database lookups")
        print(f"   📊 Result: Data-driven strategic recommendation")

if __name__ == "__main__":
    demo_react_process()
    demo_multiple_questions()
    
    print("\n🚀 Ready to deploy ReAct-powered cricket dashboard!")
    print("   The AI will now reason about questions, query data, and provide")
    print("   evidence-based strategic recommendations for any cricket scenario!")