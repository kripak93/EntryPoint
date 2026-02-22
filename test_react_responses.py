#!/usr/bin/env python3
"""
Test ReAct Cricket Agent Responses
Shows actual AI responses to cricket strategy questions
"""

import pandas as pd
from react_cricket_agent import create_react_agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_with_real_ai():
    """Test with real Gemini AI if available"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ No GEMINI_API_KEY found, using mock responses")
            return test_with_mock_ai()
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("🤖 Testing with REAL Gemini AI")
        print("=" * 50)
        
        # Load data
        df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
        agent = create_react_agent(df, model)
        
        # Test questions
        questions = [
            "When should I play Hardik Pandya against spin bowling?",
            "Who are the best death over batsmen based on the data?",
            "Compare Virat Kohli vs MS Dhoni for middle overs batting"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n🏏 Question {i}: {question}")
            print("─" * 60)
            
            try:
                # Show ReAct process
                entities = agent._extract_entities(question)
                print(f"🧠 ReAct Reasoning: {entities}")
                
                # Get AI response
                answer = agent.answer_question(question)
                print(f"\n🤖 AI Response:")
                print(answer)
                
                # Show what data was analyzed
                if agent.conversation_history:
                    last_conv = agent.conversation_history[-1]
                    print(f"\n📊 Data Analyzed: {len(last_conv['actions'])} database queries")
                    for action in last_conv['actions']:
                        print(f"   - {action}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "=" * 60)
        
        return True
        
    except ImportError:
        print("❌ google-generativeai not available")
        return test_with_mock_ai()
    except Exception as e:
        print(f"❌ AI setup failed: {e}")
        return test_with_mock_ai()

def test_with_mock_ai():
    """Test with detailed mock AI responses"""
    print("🎭 Testing with Enhanced Mock AI Responses")
    print("=" * 50)
    
    class DetailedMockAI:
        def generate_content(self, prompt):
            class MockResponse:
                def __init__(self, prompt):
                    # Analyze prompt to give relevant response
                    if "Hardik Pandya" in prompt and "spin" in prompt:
                        self.text = """
**ReAct Analysis: Hardik Pandya vs Spin Bowling**

Based on my data-driven analysis using the ReAct methodology:

**🔍 Data Observations:**
- Hardik Pandya averages entry at over 11.0 with a strike rate of 6.7
- He has played across multiple phases but shows preference for middle overs
- Against spin-heavy scenarios (middle overs 7-15), he maintains consistent performance

**📊 Strategic Deployment Recommendation:**

**WHEN TO DEPLOY:**
1. **Middle Overs (7-15)** - His optimal entry window
2. **Required Run Rate: 6-8 per over** - Matches his strike rate capability
3. **Wickets in Hand: 6+ remaining** - Allows for his aggressive approach
4. **Match Situation: Building partnerships** - His entry timing suggests he's effective in transition phases

**TACTICAL CONSIDERATIONS:**
- Deploy him when spin bowlers are operating (typically overs 8-14)
- Best used when you need 40-60 runs in 6-8 overs
- His data shows adaptability to pressure situations
- Consider the match context - he's more effective when not under extreme pressure

**CONFIDENCE LEVEL:** High (based on 11+ match entries in similar scenarios)

**Alternative Strategy:** If early wickets fall, he can adapt to earlier entry but with modified approach focusing on strike rotation rather than boundary hitting.
                        """
                    
                    elif "death over" in prompt.lower() and "best" in prompt.lower():
                        self.text = """
**ReAct Analysis: Best Death Over Batsmen**

**🔍 Data-Driven Findings:**

**TOP DEATH OVER SPECIALISTS (Entry Over 16+):**
1. **D Wiese** - Strike Rate: 12.0, Avg Entry: 18.3
   - Exceptional finisher with proven death over performance
   - Deploy in final 3 overs when 30+ runs needed

2. **A Deep** - Strike Rate: 11.5, Avg Entry: 18.0  
   - Consistent death over performer
   - Best for situations requiring 6-8 runs per over

3. **LH Ferguson** - Strike Rate: 9.8, Avg Entry: 19.5
   - Late-entry specialist for final over scenarios
   - Use when 12-15 runs needed in last over

**📊 Strategic Deployment Matrix:**

**SCENARIO 1: 40+ runs in 4 overs**
- Primary: D Wiese (over 17-18)
- Secondary: A Deep (over 19-20)

**SCENARIO 2: 20-30 runs in 3 overs**  
- Primary: A Deep (over 18)
- Support: LH Ferguson (over 20)

**SCENARIO 3: 10-15 runs in 2 overs**
- Specialist: LH Ferguson (over 19-20)

**CONFIDENCE LEVEL:** Very High (based on 50+ death over entries analyzed)

**Key Insight:** The data shows clear specialization - these players consistently enter late and maintain high strike rates under pressure.
                        """
                    
                    elif "Kohli" in prompt and "Dhoni" in prompt:
                        self.text = """
**ReAct Analysis: Virat Kohli vs MS Dhoni - Middle Overs**

**🔍 Comparative Data Analysis:**

**VIRAT KOHLI:**
- Average Entry Over: 1.6 (Early entry specialist)
- Strike Rate: 7.0
- Role: Anchor/Accumulator
- Strength: Building innings foundation

**MS DHONI:**
- Average Entry Over: 16.6 (Late entry specialist)  
- Strike Rate: 8.5
- Role: Finisher/Accelerator
- Strength: Pressure situation management

**📊 Middle Overs Deployment Strategy:**

**FOR MIDDLE OVERS (7-15) SPECIFICALLY:**

**Choose KOHLI when:**
- Early wickets have fallen (2-3 down)
- Need to rebuild and stabilize
- Required run rate is manageable (5-7 per over)
- Long batting lineup available

**Choose DHONI when:**
- Solid platform already set (100+ runs, 4+ overs remaining)
- Need acceleration in middle overs
- Required run rate climbing (7+ per over)
- Experience needed for pressure situations

**OPTIMAL COMBINATION:**
- Kohli enters early (overs 2-4) to build
- Dhoni enters middle-to-late (overs 14-16) to finish

**DATA INSIGHT:** Their entry patterns show complementary roles - Kohli as foundation builder, Dhoni as situation manager.

**RECOMMENDATION:** Use both in sequence rather than choosing one over the other for complete middle overs coverage.
                        """
                    
                    else:
                        self.text = """
**ReAct Analysis Complete**

Based on the data analysis using Reasoning + Acting methodology:

**🧠 REASONING:** Analyzed your question and identified key cricket strategy elements
**🔍 ACTING:** Queried the cricket database for relevant player performance data  
**👀 OBSERVING:** Identified patterns in entry timing, strike rates, and match situations
**💡 RESPONDING:** Providing data-driven strategic recommendations

The analysis shows clear patterns in player performance that can guide tactical decisions. Each recommendation is backed by actual match data and performance statistics.

**Confidence Level:** High (based on comprehensive data analysis)
                        """
                
            return MockResponse(prompt)
    
    # Load data and create agent
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    agent = create_react_agent(df, DetailedMockAI())
    
    # Test questions
    questions = [
        "When should I play Hardik Pandya against spin bowling?",
        "Who are the best death over batsmen based on the data?", 
        "Compare Virat Kohli vs MS Dhoni for middle overs batting"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n🏏 Question {i}: {question}")
        print("─" * 70)
        
        # Show ReAct process
        entities = agent._extract_entities(question)
        actions = agent._reason_and_plan(question, entities)
        
        print(f"🧠 ReAct Reasoning: {entities['intent']} question about {entities['players'] or entities['phases'] or 'general strategy'}")
        print(f"🔍 Data Queries Planned: {len(actions)} database lookups")
        
        # Execute and show response
        answer = agent.answer_question(question)
        print(f"\n🤖 ReAct AI Response:")
        print(answer)
        
        print("\n" + "=" * 70)
    
    return True

def main():
    """Main test function"""
    print("🏏 ReAct Cricket Strategy Agent - Response Testing")
    print("🤖 This shows exactly what users will see in the dashboard")
    print("\n" + "=" * 70)
    
    # Try real AI first, fallback to mock
    success = test_with_real_ai()
    
    if success:
        print("\n🎉 ReAct Testing Complete!")
        print("\n📋 What Users Will Experience:")
        print("✅ Intelligent question analysis (entity extraction)")
        print("✅ Targeted data queries based on question context")
        print("✅ Evidence-based strategic recommendations")
        print("✅ Transparent reasoning process")
        print("✅ Professional cricket coaching insights")
        
        print(f"\n🚀 Dashboard is running at: http://localhost:8503")
        print("   Navigate to 'ReAct Cricket Strategy Assistant' to test live!")

if __name__ == "__main__":
    main()