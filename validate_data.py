"""
Data validation script for IPL dataset
Run this to check if your data file is compatible
"""

import pandas as pd
import os

def validate_ipl_data():
    """Validate the IPL data file"""
    
    if not os.path.exists('ipl_data.csv'):
        print("❌ ipl_data.csv not found")
        print("📝 Please add your IPL dataset as 'ipl_data.csv'")
        return False
    
    try:
        df = pd.read_csv('ipl_data.csv')
        print(f"✅ Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        
        # Check essential columns
        essential_cols = {
            'bowling': ['Player', 'Team', 'O', 'W', 'R', 'Econ'],
            'batting': ['Batsman', 'Team.1', 'R.1', 'B'],
            'match': ['Date↑', 'Ground Name']
        }
        
        missing_cols = []
        for category, cols in essential_cols.items():
            for col in cols:
                if col not in df.columns:
                    missing_cols.append(f"{col} ({category})")
        
        if missing_cols:
            print(f"⚠️  Missing columns: {', '.join(missing_cols)}")
            print("📝 Your data might still work, but some features may be limited")
        else:
            print("✅ All essential columns found")
        
        # Show sample data
        print(f"\n📊 Sample data preview:")
        print(df.head(3).to_string())
        
        # Show teams
        if 'Team' in df.columns:
            teams = sorted(df['Team'].unique())
            print(f"\n🏟️  Teams found: {', '.join(teams)}")
        
        # Show players count
        if 'Player' in df.columns:
            player_count = df['Player'].nunique()
            print(f"👤 Unique players: {player_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading data: {e}")
        return False

if __name__ == "__main__":
    print("🏏 IPL Data Validation")
    print("=" * 30)
    validate_ipl_data()