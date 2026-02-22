"""
Production-Ready IPL Analytics App
Clean interface without debug messages
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics

# Load environment variables
load_dotenv(override=True)

st.set_page_config(
    page_title="IPL Analytics Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏏 IPL Analytics Pro</h1>
    <p>AI-Powered Cricket Intelligence & Scouting Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Season selection
season_options = {
    "All Seasons": None,
    "2024 Season": 2024,
    "2025 Season": 2025
}
selected_season_name = st.sidebar.selectbox(
    "📅 Choose Season:",
    options=list(season_options.keys()),
    index=0
)
selected_season = season_options[selected_season_name]

@st.cache_resource
def load_analytics(season_filter=None):
    """Load analytics engine with proper error handling"""
    
    # Try to get API key from multiple sources
    api_key = None
    
    # Method 1: Environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Method 2: Streamlit secrets (for cloud deployment)
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    
    # Method 3: Local .env file
    if not api_key and os.path.exists('.env'):
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not api_key or api_key in ['your_gemini_api_key_here', 'your_actual_api_key_here']:
        st.error("🔑 API Key Required")
        st.info("Please configure your Gemini API key:")
        st.code("For local: Add GEMINI_API_KEY to .env file\nFor cloud: Add to Streamlit secrets")
        st.stop()
    
    try:
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv', api_key=api_key, season_filter=season_filter)
        return analytics
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        st.stop()

# Load analytics
try:
    analytics = load_analytics(selected_season)
    st.sidebar.success(f"✅ {analytics.model_name}")
    st.sidebar.info(f"📊 {analytics.season}")
except Exception as e:
    st.error(f"Initialization error: {e}")
    st.stop()

# Load data for UI
@st.cache_data
def load_data():
    return pd.read_csv('ipl_data.csv')

df = load_data()

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Smart Analysis",
    "👤 Player Insights", 
    "🏟️ Team Reports",
    "🎯 Game Prep",
    "📊 Data Explorer"
])

# TAB 1: Smart Analysis
with tab1:
    st.header("💬 AI-Powered Cricket Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### Ask any cricket question:")
        
        # Example questions
        examples = [
            "Who has the best economy rate in 2025?",
            "Compare Bumrah vs Starc bowling performance",
            "Which team has the strongest bowling attack?",
            "Analyze ball position performance trends",
            "Who performs best in powerplay overs?"
        ]
        
        example_query = st.selectbox("💡 Try these examples:", [""] + examples)
        
        query = st.text_area(
            "Your Question:",
            value=example_query,
            placeholder="E.g., Who is the most economical bowler in death overs?",
            height=100
        )
    
    with col2:
        st.markdown("#### Quick Stats")
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Players", df['Player'].nunique())
        st.metric("Teams", df['Team'].nunique())
    
    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        if query.strip():
            with st.spinner("🤖 AI is analyzing..."):
                try:
                    result = analytics.smart_analyze(query)
                    
                    st.markdown("### 📋 Analysis Result")
                    st.markdown("---")
                    st.markdown(result['gemini_response'])
                    
                    # Show intent for transparency
                    if result['intent']:
                        st.caption(f"🎯 Analysis type: {', '.join(result['intent'])}")
                        
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
        else:
            st.warning("Please enter a question to analyze")

# TAB 2: Player Insights
with tab2:
    st.header("👤 Player Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        all_players = sorted(set(
            list(df['Player'].dropna().unique()) + 
            list(df['Batsman'].dropna().unique())
        ))
        
        selected_player = st.selectbox("🏏 Select Player:", all_players)
        
        # Show player stats preview
        if selected_player:
            bowling_data = df[df['Player'] == selected_player]
            batting_data = df[df['Batsman'] == selected_player]
            
            st.markdown("#### Quick Stats")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Bowling Records", len(bowling_data))
            with col_b:
                st.metric("Batting Records", len(batting_data))
    
    with col2:
        if selected_player:
            if st.button("📊 Generate Player Report", type="primary"):
                with st.spinner(f"Analyzing {selected_player}..."):
                    try:
                        insights = analytics.get_player_insights(selected_player)
                        
                        if 'error' not in insights:
                            st.markdown(f"### 📋 {selected_player} Analysis")
                            st.markdown("---")
                            st.markdown(insights['gemini_insights'])
                        else:
                            st.error(insights['error'])
                            
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

# TAB 3: Team Reports
with tab3:
    st.header("🏟️ Team Analysis")
    
    teams = sorted(df['Team'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_team = st.selectbox("🏟️ Select Team:", teams)
        
        if selected_team:
            team_data = df[df['Team'] == selected_team]
            
            st.markdown("#### Team Overview")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Players", team_data['Player'].nunique())
            with col_b:
                st.metric("Matches", team_data['Match⬆'].nunique())
            with col_c:
                st.metric("Total Balls", len(team_data))
    
    with col2:
        if selected_team:
            if st.button("⚡ Generate Team Report", type="primary"):
                with st.spinner(f"Analyzing {selected_team}..."):
                    try:
                        analysis = analytics.analyze_team(selected_team)
                        
                        if 'error' not in analysis:
                            st.markdown(f"### 📋 {selected_team} Team Analysis")
                            st.markdown("---")
                            st.markdown(analysis['gemini_analysis'])
                        else:
                            st.error(analysis['error'])
                            
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

# TAB 4: Game Prep
with tab4:
    st.header("🎯 Professional Scouting & Game Prep")
    
    # Load cricket analytics data if available
    @st.cache_resource
    def load_cricket_analytics():
        try:
            import json
            with open('cricket_analytics_data (1).json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    cricket_data = load_cricket_analytics()
    
    if cricket_data:
        # Enhanced game prep with cricket analytics
        prep_type = st.radio("📋 Analysis Type:", 
                           ["IPL Batsman Scouting", "Cricket Team Analysis", "Matchup Intelligence"], 
                           horizontal=True)
        
        if prep_type == "Cricket Team Analysis":
            st.markdown("#### Professional Team Intelligence")
            
            teams = cricket_data.get('metadata', {}).get('teams', {})
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if teams:
                    selected_team = st.selectbox(
                        "🏟️ Select Team:",
                        list(teams.keys()),
                        format_func=lambda x: f"{x} - {teams[x]}"
                    )
                    
                    phase = st.selectbox(
                        "📊 Analysis Phase:",
                        ["Overall", "PP", "Post PP"],
                        help="PP = Powerplay, Post PP = Middle/Death overs"
                    )
                    
                    if st.button("🔍 Generate Team Intelligence", type="primary"):
                        st.session_state.show_team_analysis = True
                else:
                    st.error("No team data available")
            
            with col2:
                if hasattr(st.session_state, 'show_team_analysis') and teams:
                    st.markdown(f"### 📋 {teams[selected_team]} - {phase} Analysis")
                    
                    # Get insights for selected team and phase
                    insights = cricket_data.get('insights', [])
                    team_insights = [
                        insight for insight in insights 
                        if selected_team in insight.get('matchup', '') and 
                        phase.replace(' ', '_') in insight.get('matchup', '')
                    ]
                    
                    if team_insights:
                        for insight in team_insights:
                            icon = insight.get('icon', '•')
                            priority = insight.get('priority', 'medium').upper()
                            insight_type = insight.get('type', 'info')
                            
                            if insight_type == 'strength':
                                st.success(f"{icon} **[{priority}] {insight['title']}**\n\n{insight['description']}")
                            elif insight_type == 'opportunity':
                                st.info(f"{icon} **[{priority}] {insight['title']}**\n\n{insight['description']}")
                            elif insight_type == 'weakness':
                                st.warning(f"{icon} **[{priority}] {insight['title']}**\n\n{insight['description']}")
                    
                    # Show batting analysis if available
                    matchups = cricket_data.get('matchups', {})
                    team_matchup_key = None
                    
                    for key in matchups.keys():
                        if selected_team in key and phase.replace(' ', '_') in key:
                            team_matchup_key = key
                            break
                    
                    if team_matchup_key and 'batsmen' in matchups[team_matchup_key]:
                        st.markdown("---")
                        st.markdown("#### 🏏 Key Batsmen Performance")
                        
                        batsmen = matchups[team_matchup_key]['batsmen'][:5]  # Top 5
                        
                        for batsman in batsmen:
                            col_a, col_b, col_c, col_d = st.columns(4)
                            
                            with col_a:
                                st.metric("Player", batsman['player'])
                            with col_b:
                                st.metric("Strike Rate", f"{batsman.get('sr', 0):.1f}")
                            with col_c:
                                st.metric("Average", f"{batsman.get('avg', 'N/A')}")
                            with col_d:
                                st.metric("Boundary %", f"{batsman.get('bnd', 0):.1f}%")
        
        elif prep_type == "Matchup Intelligence":
            st.markdown("#### Advanced Matchup Analysis")
            
            teams = cricket_data.get('metadata', {}).get('teams', {})
            
            if teams:
                selected_team = st.selectbox(
                    "🏟️ Team:",
                    list(teams.keys()),
                    format_func=lambda x: f"{x} - {teams[x]}",
                    key="matchup_team"
                )
                
                phase = st.selectbox(
                    "📊 Phase:",
                    ["Overall", "PP", "Post PP"],
                    key="matchup_phase"
                )
                
                if st.button("⚔️ Analyze Matchups", type="primary"):
                    # Find matchup data
                    matchups = cricket_data.get('matchups', {})
                    team_matchup_key = None
                    
                    for key in matchups.keys():
                        if selected_team in key and phase.replace(' ', '_') in key:
                            team_matchup_key = key
                            break
                    
                    if team_matchup_key and 'matchups' in matchups[team_matchup_key]:
                        st.markdown(f"### ⚔️ {teams[selected_team]} Matchup Intelligence")
                        
                        matchup_data = matchups[team_matchup_key]['matchups']
                        
                        # Separate favorable and challenging
                        favorable = [m for m in matchup_data if m['advantage'] == 'batsman'][:5]
                        challenging = [m for m in matchup_data if m['advantage'] == 'bowler'][:5]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### ✅ Exploit These Matchups")
                            for matchup in favorable:
                                st.success(
                                    f"**{matchup['batsman']}** vs {matchup['bowler']}\n"
                                    f"Strike Rate: {matchup['sr']:.1f} | Runs: {matchup['runs']}"
                                )
                        
                        with col2:
                            st.markdown("#### ⚠️ Avoid These Matchups")
                            for matchup in challenging:
                                st.error(
                                    f"**{matchup['batsman']}** vs {matchup['bowler']}\n"
                                    f"Wickets: {matchup['wks']} | Strike Rate: {matchup['sr']:.1f}"
                                )
                    else:
                        st.info("No matchup data available for selected team and phase")
        
        else:  # IPL Batsman Scouting
            st.markdown("#### IPL Batsman Scouting Brief")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                available_batsmen = sorted(df['Batsman'].dropna().unique())
                selected_batsman = st.selectbox("🏏 Batsman:", available_batsmen)
            
            with col2:
                bowler_types = ["RAF", "LAF", "Off Break", "Leg Spin", "LAO"]
                selected_bowler_type = st.selectbox("🎳 vs Bowler Type:", bowler_types)
            
            with col3:
                min_balls = st.slider("📊 Min Balls:", 20, 100, 30, help="Minimum balls for reliable analysis")
            
            if st.button("🎯 Generate Scouting Brief", type="primary", use_container_width=True):
                with st.spinner("🔍 Generating professional scouting brief..."):
                    try:
                        from corrected_strategy_engine import CorrectedIPLStrategyEngine
                        
                        filters = {}
                        if selected_season:
                            filters['season'] = selected_season
                        
                        engine = CorrectedIPLStrategyEngine(filters)
                        brief = engine.generate_scouting_brief(selected_batsman, selected_bowler_type, min_balls)
                        
                        if brief.startswith("❌"):
                            st.error(brief)
                            st.info("💡 Try: Reduce minimum balls, change season, or select different player")
                        else:
                            st.markdown("### 📋 Professional Scouting Brief")
                            st.markdown("---")
                            st.markdown(brief)
                            
                            st.download_button(
                                "📥 Download Brief",
                                brief,
                                f"scouting_{selected_batsman}_{selected_bowler_type}.md",
                                "text/markdown",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Brief generation failed: {e}")
    
    else:
        # Fallback to original IPL scouting only
        st.markdown("#### IPL Batsman Scouting Brief")
        st.info("💡 Add 'cricket_analytics_data (1).json' for enhanced team analysis features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            available_batsmen = sorted(df['Batsman'].dropna().unique())
            selected_batsman = st.selectbox("🏏 Batsman:", available_batsmen)
        
        with col2:
            bowler_types = ["RAF", "LAF", "Off Break", "Leg Spin", "LAO"]
            selected_bowler_type = st.selectbox("🎳 vs Bowler Type:", bowler_types)
        
        with col3:
            min_balls = st.slider("📊 Min Balls:", 20, 100, 30, help="Minimum balls for reliable analysis")
        
        if st.button("🎯 Generate Scouting Brief", type="primary", use_container_width=True):
            with st.spinner("🔍 Generating professional scouting brief..."):
                try:
                    from corrected_strategy_engine import CorrectedIPLStrategyEngine
                    
                    filters = {}
                    if selected_season:
                        filters['season'] = selected_season
                    
                    engine = CorrectedIPLStrategyEngine(filters)
                    brief = engine.generate_scouting_brief(selected_batsman, selected_bowler_type, min_balls)
                    
                    if brief.startswith("❌"):
                        st.error(brief)
                        st.info("💡 Try: Reduce minimum balls, change season, or select different player")
                    else:
                        st.markdown("### 📋 Professional Scouting Brief")
                        st.markdown("---")
                        st.markdown(brief)
                        
                        st.download_button(
                            "📥 Download Brief",
                            brief,
                            f"scouting_{selected_batsman}_{selected_bowler_type}.md",
                            "text/markdown",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Brief generation failed: {e}")

# TAB 5: Data Explorer
with tab5:
    st.header("📊 Interactive Data Explorer")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### Filters")
        
        # Team filter
        teams_filter = st.multiselect("Teams:", sorted(df['Team'].unique()))
        
        # Player filter
        players_filter = st.multiselect("Players:", sorted(df['Player'].dropna().unique())[:20])
        
        # Date filter
        if 'Date⬆' in df.columns:
            df['date_parsed'] = pd.to_datetime(df['Date⬆'])
            date_range = st.date_input(
                "Date Range:",
                value=(df['date_parsed'].min(), df['date_parsed'].max()),
                min_value=df['date_parsed'].min(),
                max_value=df['date_parsed'].max()
            )
    
    with col2:
        # Apply filters
        filtered_df = df.copy()
        
        if teams_filter:
            filtered_df = filtered_df[filtered_df['Team'].isin(teams_filter)]
        
        if players_filter:
            filtered_df = filtered_df[filtered_df['Player'].isin(players_filter)]
        
        st.markdown(f"#### Data Preview ({len(filtered_df):,} records)")
        
        # Display options
        display_cols = st.multiselect(
            "Columns to display:",
            df.columns.tolist(),
            default=['Player', 'Team', 'Batsman', 'O', 'W', 'R', 'Econ', 'Date⬆'][:8]
        )
        
        if display_cols:
            st.dataframe(
                filtered_df[display_cols].head(100),
                use_container_width=True,
                height=400
            )
            
            # Download option
            csv = filtered_df[display_cols].to_csv(index=False)
            st.download_button(
                "📥 Download Filtered Data",
                csv,
                "ipl_filtered_data.csv",
                "text/csv",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🏏 IPL Analytics Pro | Powered by AI | Built for Cricket Intelligence"
    "</div>",
    unsafe_allow_html=True
)