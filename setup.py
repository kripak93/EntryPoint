"""
Setup script for Gemini IPL Analytics
Run this to check dependencies and setup
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("📝 Please copy .env.template to .env and add your API key")
        return False

def check_data_file():
    """Check if data file exists"""
    if os.path.exists('ipl_data.csv'):
        print("✅ ipl_data.csv found")
        return True
    else:
        print("❌ ipl_data.csv not found")
        print("📝 Please add your IPL dataset as 'ipl_data.csv'")
        return False

def main():
    print("🏏 Gemini IPL Analytics Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check files
    env_ok = check_env_file()
    data_ok = check_data_file()
    
    print("\n" + "=" * 40)
    if env_ok and data_ok:
        print("🎉 Setup complete! Run: streamlit run enhanced_gemini_streamlit_app.py")
    else:
        print("⚠️  Setup incomplete. Please fix the issues above.")

if __name__ == "__main__":
    main()