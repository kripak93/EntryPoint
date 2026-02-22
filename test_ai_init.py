"""Test AI initialization"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv(override=True)

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {bool(api_key)}")
print(f"API Key starts with: {api_key[:20] if api_key else 'None'}...")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test the model
        response = model.generate_content("Say 'AI is working!'")
        print(f"\nModel response: {response.text}")
        print("\n✅ AI initialization successful!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
else:
    print("\n❌ No API key found")
