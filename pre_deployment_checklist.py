"""
Pre-Deployment Checklist - Verify everything is ready
"""

import os
import sys

def check_file_exists(filename):
    """Check if a file exists"""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    size = f"({os.path.getsize(filename) / 1024:.1f} KB)" if exists else ""
    print(f"{status} {filename} {size}")
    return exists

def check_deployment_readiness():
    """Check if all files are ready for deployment"""
    
    print("🚀 IPL Analytics - Pre-Deployment Checklist")
    print("=" * 50)
    
    # Essential files
    print("\n📁 Essential Files:")
    essential_files = [
        'enhanced_gemini_ipl_backend.py',
        'enhanced_gemini_streamlit_app.py',
        'corrected_strategy_engine.py',
        'ipl_data.csv',
        'requirements.txt',
        'README.md',
        '.gitignore'
    ]
    
    all_essential = all(check_file_exists(f) for f in essential_files)
    
    # Configuration files
    print("\n⚙️ Configuration Files:")
    config_files = [
        'Procfile',
        '.env'
    ]
    
    for f in config_files:
        check_file_exists(f)
    
    # Check data file size
    print("\n📊 Data File Check:")
    if os.path.exists('ipl_data.csv'):
        size_mb = os.path.getsize('ipl_data.csv') / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
        if size_mb < 100:
            print(f"   ✅ Under GitHub limit (100 MB)")
        else:
            print(f"   ❌ Over GitHub limit! Consider splitting the file")
    
    # Check requirements
    print("\n📦 Dependencies Check:")
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            required_packages = ['streamlit', 'pandas', 'google-generativeai', 'python-dotenv', 'numpy']
            
            for package in required_packages:
                if package in requirements:
                    print(f"   ✅ {package}")
                else:
                    print(f"   ❌ {package} missing")
    except:
        print("   ❌ Could not read requirements.txt")
    
    # Check API key
    print("\n🔑 API Key Check:")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'GEMINI_API_KEY=' in env_content and 'AIzaSy' in env_content:
                print("   ✅ API key found in .env")
                print("   ⚠️  Remember: Don't commit .env to GitHub!")
                print("   ⚠️  Add API key to Streamlit secrets instead")
            else:
                print("   ❌ API key not properly set in .env")
    else:
        print("   ⚠️  .env file not found (will use Streamlit secrets)")
    
    # Check .gitignore
    print("\n🔒 Security Check:")
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
            if '.env' in gitignore:
                print("   ✅ .env is in .gitignore")
            else:
                print("   ❌ .env should be in .gitignore!")
            
            if 'secrets.toml' in gitignore:
                print("   ✅ secrets.toml is in .gitignore")
            else:
                print("   ⚠️  secrets.toml should be in .gitignore")
    
    # Final summary
    print("\n" + "=" * 50)
    if all_essential:
        print("🎉 All essential files present!")
        print("\n📋 Next Steps:")
        print("1. Create GitHub repository")
        print("2. Upload files (excluding .env)")
        print("3. Deploy to Streamlit Cloud")
        print("4. Add API key to Streamlit secrets")
        print("\n📖 See deploy_instructions.md for detailed steps")
    else:
        print("❌ Some essential files are missing!")
        print("Please ensure all required files are present before deploying")
    
    # Show what NOT to upload
    print("\n⚠️  DO NOT Upload to GitHub:")
    print("   - .env (contains API key)")
    print("   - .streamlit/secrets.toml (local secrets)")
    print("   - __pycache__/ (Python cache)")
    print("   - *.pyc (compiled Python)")
    
    print("\n✅ Safe to Upload:")
    print("   - All .py files")
    print("   - ipl_data.csv")
    print("   - requirements.txt")
    print("   - README.md")
    print("   - .gitignore")
    print("   - Procfile")

if __name__ == "__main__":
    check_deployment_readiness()