"""
Main application file for deployment
Renamed from ai_cricket_manager_dashboard.py for deployment compatibility
"""

# Import the main dashboard
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import and run the dashboard
if __name__ == "__main__":
    import subprocess
    subprocess.run(["streamlit", "run", "ai_cricket_manager_dashboard.py", "--server.port", "8501"])