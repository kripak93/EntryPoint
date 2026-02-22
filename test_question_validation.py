"""
Test question validation for out-of-bounds queries
"""
import pandas as pd
from react_cricket_agent import CricketDataAnalyzer, ReActCricketAgent
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Load data
df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')

# Create analyzer
analyzer = CricketDataAnalyzer(df)

# Create mock AI model (won't be used for validation)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
ai_model = genai.GenerativeModel('gemini-2.5-flash')

# Create agent
agent = ReActCricketAgent(analyzer, ai_model)

# Test cases
test_questions = [
    # Should be REJECTED
    ("Which players perform best against spin?", False),
    ("How does Virat Kohli perform against pace bowling?", False),
    ("Who is the best bowler in death overs?", False),
    ("What is the economy rate of Bumrah?", False),
    ("Which team wins most matches at Wankhede?", False),
    ("How does the pitch affect batting?", False),
    
    # Should be ACCEPTED
    ("Which players perform best in middle overs?", True),
    ("How does Virat Kohli perform in the powerplay?", True),
    ("Who are the best death-overs finishers?", True),
    ("What is Hardik Pandya's strike rate?", True),
    ("Which MI players have the highest boundary percentage?", True),
    ("Compare Rohit Sharma vs Virat Kohli", True),
]

print("=" * 80)
print("QUESTION VALIDATION TEST")
print("=" * 80)

for question, should_be_valid in test_questions:
    result = agent._validate_question(question)
    is_valid = result['is_valid']
    
    status = "✅ PASS" if (is_valid == should_be_valid) else "❌ FAIL"
    
    print(f"\n{status}")
    print(f"Question: {question}")
    print(f"Expected: {'VALID' if should_be_valid else 'INVALID'}")
    print(f"Got: {'VALID' if is_valid else 'INVALID'}")
    
    if not is_valid:
        print(f"\nMessage shown to user:")
        print(result['message'][:200] + "..." if len(result['message']) > 200 else result['message'])

print("\n" + "=" * 80)
