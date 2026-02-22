"""
Test script to verify Gemini API key and model access
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_api():
    """Test the Gemini API connection"""
    
    print("🔑 Testing Gemini API Connection...")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ API key not found or not set properly")
        print("📝 Please edit .env file and add your actual API key")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Configure API
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Available models:")
        models = genai.list_models()
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"  - {model.name}")
        
        # Test with gemini-2.5-flash
        print(f"\n🧪 Testing gemini-2.5-flash model...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content("Hello! Can you help me analyze cricket data?")
        print(f"✅ Model response: {response.text[:100]}...")
        
        print(f"\n🎉 API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        
        # Suggest alternative models
        print(f"\n💡 Try these models instead:")
        print(f"  - gemini-2.5-flash-lite")
        print(f"  - gemini-2.5-flash")
        
        return False

if __name__ == "__main__":
    test_api()