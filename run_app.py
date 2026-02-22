"""
Simple launcher for the Gemini IPL Analytics app
"""

import subprocess
import sys
import os

def main():
    print("🏏 Starting Gemini IPL Analytics...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please copy .env.template to .env and add your API key")
        print("   Then run this script again")
        return
    
    # Check if data exists
    if not os.path.exists('ipl_data.csv'):
        print("❌ ipl_data.csv not found!")
        print("📝 Please add your IPL dataset as 'ipl_data.csv'")
        print("   You can run 'python validate_data.py' to check your data")
        return
    
    print("✅ Files found, starting Streamlit app...")
    print("🌐 App will open in your browser automatically")
    print("⏹️  Press Ctrl+C to stop the app")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "enhanced_gemini_streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 App stopped")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

if __name__ == "__main__":
    main()