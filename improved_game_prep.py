"""
Improved Game Prep Interface with Matchup Availability
"""

print("=== STARTING IMPROVED GAME PREP ===")
print("Step 1: Importing streamlit...")
import streamlit as st
print("Step 2: Importing pandas...")
import pandas as pd
print("Step 3: Importing strategy engine...")
from corrected_strategy_engine import CorrectedIPLStrategyEngine
print("Step 4: All imports successful!")
print("=" * 40)

def show_game_prep_interface():
    """Enhanced Game Prep interface with matchup availability"""
    
    st.header("🎯 Professional Scouting & Game Prep")
    
    # Load data
    df = pd.read_csv('ipl_data.csv')
    
    # Season selection (from sidebar)
    season_options = {
        "All Seasons": None,
        "2024 Season": 2024,
        "2025 Season": 2025
    }
    selected_season_name = st.sidebar.selectbox("Season:", list(season_options.keys()))
    selected_season = season_options[selected_season_name]
    
    prep_type = st.radio("📋 Analysis Type:", ["Batsman Scouting", "Team Brief"], horizontal=True)
    
    if prep_type == "Batsman Scouting":
        st.markdown("#### Generate Professional Scouting Brief")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            available_batsmen = sorted(df['Batsman'].dropna().unique())
            selected_batsman = st.selectbox("🏏 Batsman:", available_batsmen)
        
        with col2:
            bowler_types = ["RAF", "LAF", "Off Break", "Leg Spin", "LAO"]
            selected_bowler_type = st.selectbox("🎳 vs Bowler Type:", bowler_types)
        
        with col3:
            min_balls = st.slider("📊 Min Balls:", 10, 100, 20, help="Minimum balls for reliable analysis")
        
        # Enhanced data availability check
        if selected_batsman:
            try:
                # Initialize engine with filters
                filters = {}
                if selected_season:
                    filters['season'] = selected_season
                
                engine = CorrectedIPLStrategyEngine(filters)
                
                # Get all data for this batsman
                batsman_data = engine.df[engine.df['Batsman'] == selected_batsman]
                
                if not batsman_data.empty:
                    total_balls = len(batsman_data)
                    
                    # Get bowler type breakdown
                    bowler_breakdown = batsman_data['bowler_category'].value_counts()
                    
                    # Display availability
                    st.markdown("#### 📊 Matchup Availability")
                    
                    col_a, col_b = st.columns([1, 2])
                    
                    with col_a:
                        st.metric("Total Balls", f"{total_balls:,}")
                        st.metric("Matches", batsman_data['Match⬆'].nunique())
                        
                        # Check specific selection
                        available_balls = bowler_breakdown.get(selected_bowler_type, 0)
                        
                        if available_balls >= min_balls:
                            st.success(f"✅ Ready for analysis")
                        elif available_balls > 0:
                            st.warning(f"⚠️ Limited data ({available_balls} balls)")
                        else:
                            st.error(f"❌ No data vs {selected_bowler_type}")
                    
                    with col_b:
                        st.markdown("**Available Bowler Matchups:**")
                        
                        # Create a nice table of available matchups
                        matchup_data = []
                        for bowler_cat, balls in bowler_breakdown.items():
                            status = "✅ Ready" if balls >= min_balls else "⚠️ Limited" if balls > 0 else "❌ None"
                            matchup_data.append({
                                "Bowler Type": bowler_cat,
                                "Balls": balls,
                                "Status": status
                            })
                        
                        matchup_df = pd.DataFrame(matchup_data)
                        st.dataframe(matchup_df, use_container_width=True, hide_index=True)
                        
                        # Suggest best alternative if current selection has no data
                        if available_balls == 0 and len(bowler_breakdown) > 0:
                            best_matchup = bowler_breakdown.index[0]
                            st.info(f"💡 **Suggestion:** Try **{best_matchup}** ({bowler_breakdown.iloc[0]} balls)")
                
                else:
                    st.error(f"❌ No data found for {selected_batsman} in {selected_season_name}")
                    
            except Exception as e:
                st.error(f"Error checking data availability: {e}")
        
        # Generate brief button
        if st.button("🎯 Generate Scouting Brief", type="primary", use_container_width=True):
            if not selected_batsman:
                st.error("Please select a batsman")
                return
            
            with st.spinner("🔍 Generating professional scouting brief..."):
                try:
                    filters = {}
                    if selected_season:
                        filters['season'] = selected_season
                    
                    engine = CorrectedIPLStrategyEngine(filters)
                    brief = engine.generate_scouting_brief(selected_batsman, selected_bowler_type, min_balls)
                    
                    if brief.startswith("❌"):
                        st.error(brief)
                        
                        # Show helpful suggestions
                        batsman_data = engine.df[engine.df['Batsman'] == selected_batsman]
                        if not batsman_data.empty:
                            bowler_breakdown = batsman_data['bowler_category'].value_counts()
                            valid_options = bowler_breakdown[bowler_breakdown >= min_balls]
                            
                            if len(valid_options) > 0:
                                st.info("💡 **Try these alternatives:**")
                                for bowler_type, balls in valid_options.items():
                                    st.write(f"• **{bowler_type}**: {balls} balls available")
                            else:
                                st.info(f"💡 Try reducing minimum balls to {min_balls//2} or select a different season")
                    else:
                        st.markdown("### 📋 Professional Scouting Brief")
                        st.markdown("---")
                        st.markdown(brief)
                        
                        # Download option
                        st.download_button(
                            "📥 Download Brief",
                            brief,
                            f"scouting_{selected_batsman}_{selected_bowler_type}_{selected_season or 'all'}.md",
                            "text/markdown",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"Brief generation failed: {e}")
                    st.info("Please check your data and try again")

def main():
    """Test the improved interface"""
    st.set_page_config(page_title="Game Prep Test", layout="wide")
    show_game_prep_interface()

if __name__ == "__main__":
    main()