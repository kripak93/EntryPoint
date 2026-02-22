"""
Command-Line Game Prep Tool - Works without Streamlit
"""

from corrected_strategy_engine import CorrectedIPLStrategyEngine
import pandas as pd

def main():
    print("\n" + "="*60)
    print("🎯 IPL GAME PREP - SCOUTING TOOL")
    print("="*60 + "\n")
    
    # Load available data
    df = pd.read_csv('ipl_data.csv')
    
    print("Available Batsmen:")
    batsmen = sorted(df['Batsman'].dropna().unique())[:20]  # Show first 20
    for i, bat in enumerate(batsmen, 1):
        print(f"  {i}. {bat}")
    print(f"  ... and {len(df['Batsman'].dropna().unique()) - 20} more\n")
    
    # Get user input
    batsman = input("Enter batsman name: ").strip()
    
    print("\nBowler Types:")
    print("  1. RAF (Right Arm Fast)")
    print("  2. LAF (Left Arm Fast)")
    print("  3. Off Break")
    print("  4. Leg Spin")
    print("  5. LAO (Left Arm Orthodox)")
    
    bowler_map = {
        "1": "RAF", "2": "LAF", "3": "Off Break", 
        "4": "Leg Spin", "5": "LAO"
    }
    bowler_choice = input("\nSelect bowler type (1-5): ").strip()
    bowler_type = bowler_map.get(bowler_choice, "RAF")
    
    min_balls = int(input("Minimum balls for analysis (default 20): ").strip() or "20")
    
    # Generate brief
    print("\n" + "="*60)
    print("GENERATING SCOUTING BRIEF...")
    print("="*60 + "\n")
    
    engine = CorrectedIPLStrategyEngine()
    engine._ensure_data_loaded()
    brief = engine.generate_scouting_brief(batsman, bowler_type, min_balls)
    
    print("\n" + "="*60)
    print("✓ BRIEF GENERATED")
    print("="*60)

if __name__ == "__main__":
    main()
