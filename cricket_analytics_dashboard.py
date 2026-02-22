"""
Cricket Analytics Dashboard
Clean, queryable interface for cricket analytics data
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Cricket Analytics Dashboard",
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
        background: linear-gradient(90deg, #1f4e79, #2e8b57);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricket Analytics Dashboard</h1>
    <p>Professional Cricket Intelligence & Performance Analysis</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_cricket_data():
    """Load cricket analytics data"""
    try:
        with open('cricket_analytics_data (1).json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Cricket analytics data file not found!")
        return None

# Load data
cricket_data = load_cricket_data()

if cricket_data is None:
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters & Navigation")

# Get available matchups and teams
matchup_keys = list(cricket_data.get('matchups', {}).keys())
teams = set()
phases = set()

for key in matchup_keys:
    parts = key.split('_')
    if len(parts) >= 3:
        team = parts[0]
        phase = parts[-1]
        teams.add(team)
        phases.add(phase)

teams = sorted(list(teams))
phases = sorted(list(phases))

# Sidebar filters
selected_team = st.sidebar.selectbox("🏟️ Select Team:", ["All Teams"] + teams)
selected_phase = st.sidebar.selectbox("📊 Select Phase:", ["All Phases"] + phases)
analysis_type = st.sidebar.selectbox(
    "📈 Analysis Type:", 
    ["Team Overview", "Player Performance", "Matchup Analysis", "Bowling Analysis", "Data Explorer"]
)

# Main content based on analysis type
if analysis_type == "Team Overview":
    st.header("🏟️ Team Performance Overview")
    
    if selected_team != "All Teams":
        # Filter matchups for selected team
        team_matchups = {k: v for k, v in cricket_data['matchups'].items() 
                        if k.startswith(selected_team)}
        
        if team_matchups:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📊 {selected_team} Statistics")
                
                # Aggregate team stats
                total_players = 0
                total_runs = 0
                total_wickets = 0
                
                for matchup_key, matchup_data in team_matchups.items():
                    if 'players' in matchup_data:
                        players_data = matchup_data['players']
                        total_players += len(players_data)
                        total_runs += sum(p.get('runs', 0) for p in players_data)
                        total_wickets += sum(p.get('wks', 0) for p in players_data)
                
                st.metric("Total Players", total_players)
                st.metric("Total Runs", f"{total_runs:,}")
                st.metric("Total Wickets", total_wickets)
            
            with col2:
                st.subheader("📈 Performance by Phase")
                
                phase_data = []
                for matchup_key, matchup_data in team_matchups.items():
                    phase = matchup_key.split('_')[-1]
                    if 'players' in matchup_data:
                        players = matchup_data['players']
                        avg_sr = sum(p.get('sr', 0) for p in players) / len(players) if players else 0
                        phase_data.append({
                            'Phase': phase,
                            'Average Strike Rate': avg_sr,
                            'Players': len(players)
                        })
                
                if phase_data:
                    df_phase = pd.DataFrame(phase_data)
                    fig = px.bar(df_phase, x='Phase', y='Average Strike Rate', 
                               title=f"{selected_team} Strike Rate by Phase")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No data available for {selected_team}")
    else:
        st.info("Please select a specific team to view overview")

elif analysis_type == "Player Performance":
    st.header("👤 Player Performance Analysis")
    
    # Get all players from all matchups
    all_players = []
    
    for matchup_key, matchup_data in cricket_data['matchups'].items():
        if 'players' in matchup_data:
            for player in matchup_data['players']:
                player_info = player.copy()
                player_info['matchup'] = matchup_key
                player_info['team'] = matchup_key.split('_')[0]
                player_info['phase'] = matchup_key.split('_')[-1]
                all_players.append(player_info)
    
    if all_players:
        df_players = pd.DataFrame(all_players)
        
        # Player selection
        unique_players = sorted(df_players['player'].unique())
        selected_player = st.selectbox("🏏 Select Player:", unique_players)
        
        if selected_player:
            player_data = df_players[df_players['player'] == selected_player]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_runs = player_data['runs'].sum()
                st.metric("Total Runs", f"{total_runs:,}")
            
            with col2:
                total_balls = player_data['bf'].sum()
                st.metric("Total Balls Faced", f"{total_balls:,}")
            
            with col3:
                avg_sr = player_data['sr'].mean()
                st.metric("Average Strike Rate", f"{avg_sr:.1f}")
            
            # Performance by phase
            st.subheader("📊 Performance by Phase")
            
            phase_summary = player_data.groupby('phase').agg({
                'runs': 'sum',
                'bf': 'sum',
                'sr': 'mean',
                'wks': 'sum'
            }).round(2)
            
            st.dataframe(phase_summary, use_container_width=True)
            
            # Strike rate visualization
            fig = px.bar(player_data, x='phase', y='sr', 
                        title=f"{selected_player} - Strike Rate by Phase")
            st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Matchup Analysis":
    st.header("⚔️ Matchup Analysis")
    
    # Get matchups data
    matchup_data_list = []
    
    for matchup_key, matchup_data in cricket_data['matchups'].items():
        if 'matchups' in matchup_data:
            for matchup in matchup_data['matchups']:
                matchup_info = matchup.copy()
                matchup_info['team'] = matchup_key.split('_')[0]
                matchup_info['phase'] = matchup_key.split('_')[-1]
                matchup_data_list.append(matchup_info)
    
    if matchup_data_list:
        df_matchups = pd.DataFrame(matchup_data_list)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Favorable Matchups (Batsman Advantage)")
            favorable = df_matchups[df_matchups['advantage'] == 'batsman'].nlargest(10, 'sr')
            
            for _, row in favorable.iterrows():
                st.success(
                    f"**{row['batsman']}** vs {row['bowler']}\n"
                    f"Strike Rate: {row['sr']:.1f} | Runs: {row['runs']}"
                )
        
        with col2:
            st.subheader("⚠️ Challenging Matchups (Bowler Advantage)")
            challenging = df_matchups[df_matchups['advantage'] == 'bowler'].nsmallest(10, 'sr')
            
            for _, row in challenging.iterrows():
                st.error(
                    f"**{row['batsman']}** vs {row['bowler']}\n"
                    f"Strike Rate: {row['sr']:.1f} | Wickets: {row['wks']}"
                )

elif analysis_type == "Bowling Analysis":
    st.header("🎳 Bowling Performance Analysis")
    
    # Get bowling data from matchups
    bowling_data = []
    
    for matchup_key, matchup_data in cricket_data['matchups'].items():
        if 'data' in matchup_data:
            for bowler in matchup_data['data']:
                if bowler.get('Player'):  # Skip null entries
                    bowler_info = bowler.copy()
                    bowler_info['team'] = matchup_key.split('_')[0]
                    bowler_info['phase'] = matchup_key.split('_')[-1]
                    bowling_data.append(bowler_info)
    
    if bowling_data:
        df_bowling = pd.DataFrame(bowling_data)
        
        # Remove null entries
        df_bowling = df_bowling.dropna(subset=['Player'])
        
        st.subheader("🏆 Top Bowlers by Economy Rate")
        
        # Filter for minimum overs
        min_overs = st.slider("Minimum Balls Faced:", 20, 200, 50)
        qualified_bowlers = df_bowling[df_bowling['BF'] >= min_overs]
        
        if not qualified_bowlers.empty:
            top_bowlers = qualified_bowlers.nsmallest(10, 'RR')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(
                    top_bowlers[['Player', 'BowlType', 'RR', 'SR', 'Wks', 'BF']].round(2),
                    use_container_width=True
                )
            
            with col2:
                fig = px.scatter(
                    qualified_bowlers, 
                    x='RR', 
                    y='SR', 
                    size='Wks',
                    hover_data=['Player', 'BowlType'],
                    title="Economy Rate vs Strike Rate"
                )
                st.plotly_chart(fig, use_container_width=True)

else:  # Data Explorer
    st.header("🔍 Data Explorer")
    
    # Raw data exploration
    data_type = st.selectbox(
        "Select Data Type:", 
        ["Matchups Overview", "Player Statistics", "Bowling Statistics", "Raw JSON Structure"]
    )
    
    if data_type == "Matchups Overview":
        st.subheader("Available Matchups")
        
        matchup_info = []
        for key, value in cricket_data['matchups'].items():
            info = {
                'Matchup Key': key,
                'Type': value.get('type', 'Unknown'),
                'Players Count': len(value.get('players', [])),
                'Matchups Count': len(value.get('matchups', [])),
                'Data Records': len(value.get('data', []))
            }
            matchup_info.append(info)
        
        df_info = pd.DataFrame(matchup_info)
        st.dataframe(df_info, use_container_width=True)
    
    elif data_type == "Raw JSON Structure":
        st.subheader("JSON Data Structure")
        st.json(cricket_data)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🏏 Cricket Analytics Dashboard | Professional Cricket Intelligence"
    "</div>",
    unsafe_allow_html=True
)