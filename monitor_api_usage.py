"""
Monitor API usage to track when credits are being consumed
"""

import os
from datetime import datetime
from dotenv import load_dotenv

def log_api_call(function_name, query=""):
    """Log when an API call is made"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - API CALL: {function_name} - Query: {query}\n"
    
    with open("api_usage_log.txt", "a") as f:
        f.write(log_entry)
    
    print(f"🔔 API Call Logged: {function_name}")

def check_api_status():
    """Check if API key is active"""
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    print("🔑 API Status Check")
    print("=" * 30)
    
    if not api_key:
        print("✅ No API key found - No charges possible")
    elif api_key == 'disabled_to_prevent_usage':
        print("✅ API key disabled - No charges possible")
    elif api_key == 'your_gemini_api_key_here':
        print("✅ API key not set - No charges possible")
    else:
        print(f"⚠️  API key active: {api_key[:10]}...")
        print("💰 Credits may be used if scripts run")
    
    # Check for recent usage log
    if os.path.exists("api_usage_log.txt"):
        print(f"\n📋 Recent API calls:")
        with open("api_usage_log.txt", "r") as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Show last 5 calls
                print(f"  {line.strip()}")
    else:
        print(f"\n📋 No API usage log found")

if __name__ == "__main__":
    check_api_status()