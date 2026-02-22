"""
Integrated Cricket Analytics Dashboard
Combines IPL data with comprehensive cricket game preparation
"""

import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

# Load environment variables
load_dotenv(override=True)

st.set_page_config(
    page_title="Cricket Analytics Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .insight-card {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .strength-card {
        background: #e8f5e8;
        border-left-color: #28a745;
    }
    .weakness-card {
        background: #fdf2e8;
        border-left-color: #fd7e14;
    }
    .opportunity-card {
        background: #e8f4fd;
        border-left-color: #007bff;
    }
</style>
""", unsafe_allow_html=True)

class CricketGamePrep:
    """Cricket Game Preparation System"""
    
    def __init__(self, data_file: str):
        try:
            with open(data_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            st.error(f"Cricket analytics data file '{data_file}' not found!")
            self.data = {}
        
        self.teams = self.data.get('metadata', {}).get('teams', {})
        self.matchups = self.data.get('matchups', {})
        self.insights = self.data.get('insights', [])
    
    def get_team_analysis(self, team_code: str, phase: str = "Overall") -> Dict[str, Any]:
        """Get comprehensive team analysis"""
        team_data = {}
        for matchup_key, matchup_data in self.matchups.items():
            if team_code in matchup_key and phase.replace(' ', '_') in matchup_key:
                team_data[matchup_key] = matchup_data
        return team_data
    
    def get_batting_insights(self, team_code: str, phase: str = "Overall") -> List[Dict]:
        """Get batting insights for team"""
        insights = []
        team_data = self.get_team_analysis(team_code, phase)
        
        for matchup_key, data in team_data.items():
            if 'batsmen' in data:
                for batsman in data['batsmen'][:10]:  # Top 10
                    insights.append({
                        'player': batsman['player'],
                        'strike_rate': batsman.get('sr', 0),
                        'average': batsman.get('avg', 0),
                        'runs': batsman.get('runs', 0),
                        'balls_faced': batsman.get('bf', 0),
                        'wickets': batsman.get('wks', 0),
                        'dot_percentage': batsman.get('dot', 0),
                        'boundary_percentage': batsman.get('bnd', 0)
                    })
                break
        
        return sorted(insights, key=lambda x: x['strike_rate'], reverse=True)
    
    def get_key_matchups(self, team_code: str, phase: str = "Overall") -> List[Dict]:
        """Get key matchups for team"""
        matchups = []
        team_data = self.get_team_analysis(team_code, phase)
        
        for matchup_key, data in team_data.items():
            if 'matchups' in data:
                for matchup in data['matchups'][:15]:  # Top 15
                    matchups.append({
                        'batsman': matchup['batsman'],
                        'bowler': matchup['bowler'],
                        'runs': matchup['runs'],
                        'balls_faced': matchup['bf'],
                        'strike_rate': matchup['sr'],
                        'wickets': matchup['wks'],
                        'advantage': matchup['advantage']
                    })
                break
        
        return matchups
    
    def get_strategic_insights(self, team_code: str, phase: str = "Overall") -> Dict[str, List]:
        """Get strategic insights categorized by type"""
        insights = {
            'strengths': [],
            'opportunities': [],
            'weaknesses': []
        }
        
        phase_key = phase.replace(' ', '_')
        team_insights = [insight for insight in self.insights 
                        if team_code in insight.get('matchup', '') and 
                        phase_key in insight.get('matchup', '')]
        
        for insight in team_insights:
            insight_type = insight['type']
            if insight_type in insights:
                insights[insight_type].append({
                    'title': insight['title'],
                    'description': insight['description'],
                    'priority': insight['priority'],
                    'icon': insight.get('icon', '•')
                })
        
        return insights

# Header
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricket Analytics Pro</h1>
    <p>AI-Powered Cricket Intelligence & Game Preparation Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Data source selection
data_source = st.sidebar.radio(
    "📊 Data Source:",
    ["IPL Historical Data", "Cricket Analytics Data", "Both"],
    index=2
)

# Season selection for IPL data
if data_source in ["IPL Historical Data", "Both"]:
    season_options = {
        "All Seasons": None,
        "2024 Season": 2024,
        "2025 Season": 2025
    }
    selected_season_name = st.sidebar.selectbox(
        "📅 IPL Season:",
        options=list(season_options.keys()),
        index=0
    )
    selected_season = season_options[selected_season_name]

@st.cache_resource
def load_analytics(season_filter=None):
    """Load IPL analytics engine"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    
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
        st.sidebar.error("🔑 IPL Analytics requires API key")
        return None
    
    try:
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv', api_key=api_key, season_filter=season_filter)
        return analytics
    except Exception as e:
        st.sidebar.error(f"IPL Analytics failed: {str(e)}")
        return None

@st.cache_resource
def load_cricket_prep():
    """Load cricket game prep system"""
    try:
        return CricketGamePrep('cricket_analytics_data (1).json')
    except Exception as e:
        st.sidebar.error(f"Cricket prep failed: {str(e)}")
        return None

# Load systems based on selection
analytics = None
cricket_prep = None

if data_source in ["IPL Historical Data", "Both"]:
    analytics = load_analytics(selected_season)
    if analytics:
        st.sidebar.success(f"✅ IPL: {analytics.model_name}")

if data_source in ["Cricket Analytics Data", "Both"]:
    cricket_prep = load_cricket_prep()
    if cricket_prep:
        st.sidebar.success(f"✅ Cricket Prep: {len(cricket_prep.teams)} teams")

# Main tabs
if data_source == "IPL Historical Data":
    tabs = ["💬 Smart Analysis", "👤 Player Insights", "🏟️ Team Reports", "📊 Data Explorer"]
elif data_source == "Cricket Analytics Data":
    tabs = ["🎯 Game Preparation", "⚔️ Matchup Analysis", "📈 Team Intelligence", "🔍 Strategic Insights"]
else:  # Both
    tabs = ["💬 Smart Analysis", "🎯 Game Preparation", "⚔️ Matchup Analysis", "👤 Player Insights", "📊 Data Explorer"]

tab_objects = st.tabs(tabs)

# TAB: Smart Analysis (IPL)
if "💬 Smart Analysis" in tabs:
    tab_idx = tabs.index("💬 Smart Analysis")
    with tab_objects[tab_idx]:
        if analytics:
            st.header("💬 AI-Powered Cricket Analysis")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
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
                df = pd.read_csv('ipl_data.csv')
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
                            
                            if result['intent']:
                                st.caption(f"🎯 Analysis type: {', '.join(result['intent'])}")
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")
                else:
                    st.warning("Please enter a question to analyze")
        else:
            st.error("IPL Analytics not available")

# TAB: Game Preparation
if "🎯 Game Preparation" in tabs:
    tab_idx = tabs.index("🎯 Game Preparation")
    with tab_objects[tab_idx]:
        if cricket_prep:
            st.header("🎯 Professional Game Preparation")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Team Selection")
                
                teams = cricket_prep.teams
                selected_team = st.selectbox(
                    "Select Team:",
                    list(teams.keys()),
                    format_func=lambda x: f"{x} - {teams[x]}"
                )
                
                phase = st.selectbox(
                    "Analysis Phase:",
                    ["Overall", "PP", "Post PP"],
                    help="PP = Powerplay, Post PP = Middle/Death overs"
                )
                
                if st.button("🔄 Generate Game Plan", type="primary"):
                    st.session_state.generate_plan = True
            
            with col2:
                if selected_team and hasattr(st.session_state, 'generate_plan'):
                    st.subheader(f"Game Plan: {teams[selected_team]}")
                    
                    # Strategic Insights
                    insights = cricket_prep.get_strategic_insights(selected_team, phase)
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown("#### 🌟 Strengths")
                        for strength in insights['strengths']:
                            st.markdown(f"""
                            <div class="insight-card strength-card">
                                <strong>{strength['icon']} {strength['title']}</strong><br>
                                <small>{strength['description']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown("#### 🚀 Opportunities")
                        for opp in insights['opportunities']:
                            st.markdown(f"""
                            <div class="insight-card opportunity-card">
                                <strong>{opp['icon']} {opp['title']}</strong><br>
                                <small>{opp['description']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown("#### ⚠️ Weaknesses")
                        for weakness in insights['weaknesses']:
                            st.markdown(f"""
                            <div class="insight-card weakness-card">
                                <strong>{weakness['icon']} {weakness['title']}</strong><br>
                                <small>{weakness['description']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Batting Analysis
                    st.markdown("---")
                    st.subheader("🏏 Batting Analysis")
                    
                    batting_insights = cricket_prep.get_batting_insights(selected_team, phase)
                    
                    if batting_insights:
                        batting_df = pd.DataFrame(batting_insights)
                        
                        # Create batting performance chart
                        fig = px.scatter(
                            batting_df,
                            x='strike_rate',
                            y='average',
                            size='runs',
                            color='boundary_percentage',
                            hover_name='player',
                            title=f"Batting Performance - {phase}",
                            labels={
                                'strike_rate': 'Strike Rate',
                                'average': 'Average',
                                'boundary_percentage': 'Boundary %'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Top performers table
                        st.markdown("#### Top Performers")
                        display_df = batting_df[['player', 'strike_rate', 'average', 'runs', 'boundary_percentage']].head(5)
                        display_df.columns = ['Player', 'Strike Rate', 'Average', 'Runs', 'Boundary %']
                        st.dataframe(display_df, use_container_width=True)
        else:
            st.error("Cricket Game Preparation not available")

# TAB: Matchup Analysis
if "⚔️ Matchup Analysis" in tabs:
    tab_idx = tabs.index("⚔️ Matchup Analysis")
    with tab_objects[tab_idx]:
        if cricket_prep:
            st.header("⚔️ Detailed Matchup Analysis")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                teams = cricket_prep.teams
                selected_team = st.selectbox(
                    "Team:",
                    list(teams.keys()),
                    format_func=lambda x: f"{x} - {teams[x]}",
                    key="matchup_team"
                )
                
                phase = st.selectbox(
                    "Phase:",
                    ["Overall", "PP", "Post PP"],
                    key="matchup_phase"
                )
            
            with col2:
                if selected_team:
                    matchups = cricket_prep.get_key_matchups(selected_team, phase)
                    
                    if matchups:
                        st.subheader(f"Key Matchups - {teams[selected_team]} ({phase})")
                        
                        # Separate favorable and challenging matchups
                        favorable = [m for m in matchups if m['advantage'] == 'batsman']
                        challenging = [m for m in matchups if m['advantage'] == 'bowler']
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.markdown("#### ✅ Favorable Matchups")
                            for matchup in favorable[:5]:
                                st.success(
                                    f"**{matchup['batsman']}** vs {matchup['bowler']}\n"
                                    f"SR: {matchup['strike_rate']:.1f} | "
                                    f"Runs: {matchup['runs']} | "
                                    f"Balls: {matchup['balls_faced']}"
                                )
                        
                        with col_b:
                            st.markdown("#### ❌ Challenging Matchups")
                            for matchup in challenging[:5]:
                                st.error(
                                    f"**{matchup['batsman']}** vs {matchup['bowler']}\n"
                                    f"Wickets: {matchup['wickets']} | "
                                    f"SR: {matchup['strike_rate']:.1f} | "
                                    f"Runs: {matchup['runs']}"
                                )
                        
                        # Matchup visualization
                        st.markdown("---")
                        st.subheader("Matchup Performance Distribution")
                        
                        matchup_df = pd.DataFrame(matchups)
                        
                        fig = px.scatter(
                            matchup_df,
                            x='balls_faced',
                            y='strike_rate',
                            color='advantage',
                            size='runs',
                            hover_data=['batsman', 'bowler', 'wickets'],
                            title="Matchup Performance Overview",
                            color_discrete_map={'batsman': 'green', 'bowler': 'red'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No matchup data available for selected team and phase")
        else:
            st.error("Cricket Matchup Analysis not available")

# TAB: Player Insights (IPL)
if "👤 Player Insights" in tabs:
    tab_idx = tabs.index("👤 Player Insights")
    with tab_objects[tab_idx]:
        if analytics:
            st.header("👤 Player Deep Dive")
            
            df = pd.read_csv('ipl_data.csv')
            col1, col2 = st.columns(2)
            
            with col1:
                all_players = sorted(set(
                    list(df['Player'].dropna().unique()) + 
                    list(df['Batsman'].dropna().unique())
                ))
                
                selected_player = st.selectbox("🏏 Select Player:", all_players)
                
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
        else:
            st.error("Player Insights not available")

# TAB: Data Explorer
if "📊 Data Explorer" in tabs:
    tab_idx = tabs.index("📊 Data Explorer")
    with tab_objects[tab_idx]:
        if analytics:
            st.header("📊 Interactive Data Explorer")
            
            df = pd.read_csv('ipl_data.csv')
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown("#### Filters")
                
                teams_filter = st.multiselect("Teams:", sorted(df['Team'].unique()))
                players_filter = st.multiselect("Players:", sorted(df['Player'].dropna().unique())[:20])
                
                if 'Date⬆' in df.columns:
                    df['date_parsed'] = pd.to_datetime(df['Date⬆'])
                    date_range = st.date_input(
                        "Date Range:",
                        value=(df['date_parsed'].min(), df['date_parsed'].max()),
                        min_value=df['date_parsed'].min(),
                        max_value=df['date_parsed'].max()
                    )
            
            with col2:
                filtered_df = df.copy()
                
                if teams_filter:
                    filtered_df = filtered_df[filtered_df['Team'].isin(teams_filter)]
                
                if players_filter:
                    filtered_df = filtered_df[filtered_df['Player'].isin(players_filter)]
                
                st.markdown(f"#### Data Preview ({len(filtered_df):,} records)")
                
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
                    
                    csv = filtered_df[display_cols].to_csv(index=False)
                    st.download_button(
                        "📥 Download Filtered Data",
                        csv,
                        "cricket_filtered_data.csv",
                        "text/csv",
                        use_container_width=True
                    )
        else:
            st.error("Data Explorer not available")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🏏 Cricket Analytics Pro | AI-Powered Intelligence & Game Preparation"
    "</div>",
    unsafe_allow_html=True
)