"""
Cricket Entry Analysis Dashboard - Ball-by-Ball Data
Clean implementation with bowling type support
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai
from react_cricket_agent import CricketDataAnalyzer, ReActCricketAgent

# Load environment variables
load_dotenv()

# Debug: Check if API key is loaded
_api_key_loaded = bool(os.getenv('GEMINI_API_KEY'))

# Page config
st.set_page_config(
    page_title="Cricket Entry Analysis Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #2E8B57, #228B22);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_ai():
    """Initialize Gemini AI"""
    # Force reload environment variables
    load_dotenv(override=True)
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Use stable gemini-2.5-flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Test the model to ensure it works
        _ = model.generate_content("test")
        return model
    except Exception as e:
        st.error(f"AI initialization error: {e}")
        return None

@st.cache_data(ttl=60)  # Cache for 60 seconds to allow updates
def load_entry_data():
    """Load processed entry point data"""
    try:
        df = pd.read_csv('processed_entry_points_ballbyball.csv')
        # Standardize phase names
        df['Entry_Phase'] = df['Entry_Phase'].replace({
            'Powerplay': 'Powerplay',
            'Middle': 'Middle', 
            'Death': 'Death'
        })
        return df
    except FileNotFoundError:
        st.error("❌ Run process_ballbyball_data.py first to generate data")
        return pd.DataFrame()

@st.cache_data
def load_bowling_matchups():
    """Load bowling type matchup data"""
    try:
        return pd.read_csv('bowling_type_matchups.csv')
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=60)  # Cache for 60 seconds to allow updates
def load_ball_position_data():
    """Load ball position analysis data"""
    try:
        return pd.read_csv('ball_position_analysis.csv')
    except FileNotFoundError:
        st.error("❌ Run process_ball_position_data.py first to generate data")
        return pd.DataFrame()

# Load data
entry_df = load_entry_data()
bowling_df = load_bowling_matchups()
ball_position_df = load_ball_position_data()

if entry_df.empty:
    st.stop()

# Header
st.markdown('<div class="main-header"><h1>🏏 Cricket Entry Analysis Dashboard</h1><p>Ball-by-Ball Data with Bowling Type Support</p></div>', unsafe_allow_html=True)

# Data summary
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Entry Points", f"{len(entry_df):,}")
with col2:
    st.metric("Unique Players", entry_df['Player'].nunique())
with col3:
    st.metric("Matches", entry_df['Match'].nunique())
with col4:
    st.metric("Years", f"{entry_df['Year'].min()}-{entry_df['Year'].max()}")

# Sidebar filters
st.sidebar.header("🎯 Filters")

# Year filter
available_years = sorted(entry_df['Year'].dropna().unique())
selected_years = st.sidebar.multiselect(
    "📅 Years:",
    available_years,
    default=available_years
)

# Team filter
available_teams = sorted(entry_df['Team'].unique())
selected_teams = st.sidebar.multiselect(
    "🏟️ Teams:",
    available_teams,
    default=available_teams  # Show all teams by default
)

# Phase filter
selected_phases = st.sidebar.multiselect(
    "⏱️ Entry Phase:",
    ["Powerplay", "Middle", "Death"],
    default=["Powerplay", "Middle", "Death"]
)

# Bowling type filter (NEW!)
if not bowling_df.empty:
    bowling_filter = st.sidebar.selectbox(
        "🎾 Bowling Type:",
        ["All", "Pace", "Spin"]
    )
else:
    bowling_filter = "All"
    st.sidebar.info("Bowling type data not available")

# Min balls filter
min_balls = st.sidebar.slider(
    "⚾ Min Balls Faced:",
    1, 50, 5  # Default to 5 instead of 10
)

# Apply filters
filtered_df = entry_df[
    (entry_df['Year'].isin(selected_years)) &
    (entry_df['Team'].isin(selected_teams)) &
    (entry_df['Entry_Phase'].isin(selected_phases)) &
    (entry_df['BF'] >= min_balls)
].copy()

st.sidebar.metric("Filtered Entries", len(filtered_df))

# Analysis type selector
analysis_type = st.sidebar.selectbox(
    "📊 Analysis Type:",
    ["Entry Overview", "Player Analysis", "Team Analysis", "Ball Position Analysis", "AI Insights"]
)

# Main content
if analysis_type == "Entry Overview":
    st.header("📊 Entry Point Overview")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Entry distribution
            entry_dist = filtered_df['Entry_Over'].value_counts().sort_index().reset_index()
            entry_dist.columns = ['Entry Over', 'Count']
            
            fig1 = px.bar(
                entry_dist,
                x='Entry Over',
                y='Count',
                title="Entry Points by Over",
                color='Count',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Phase distribution
            phase_dist = filtered_df['Entry_Phase'].value_counts().reset_index()
            phase_dist.columns = ['Phase', 'Count']
            
            fig2 = px.pie(
                phase_dist,
                values='Count',
                names='Phase',
                title="Entry Distribution by Phase"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Performance metrics
        st.subheader("📈 Performance Metrics by Phase")
        
        phase_stats = filtered_df.groupby('Entry_Phase').agg({
            'Player': 'count',
            'Final_Strike_Rate': 'mean',
            'Runs': 'mean',
            'Dot_Pct': 'mean',
            'Bnd_Pct': 'mean',
            'Innings_Duration': 'mean'
        }).round(2).reset_index()
        
        phase_stats.columns = ['Phase', 'Entries', 'Avg SR', 'Avg Runs', 'Avg Dot%', 'Avg Bnd%', 'Avg Duration']
        st.dataframe(phase_stats, use_container_width=True)
        
        # Top performers
        st.subheader("🌟 Top Performers")
        
        top_performers = filtered_df.groupby('Player').agg({
            'Final_Strike_Rate': 'mean',
            'Runs': 'mean',
            'Entry_Over': 'count',
            'Dot_Pct': 'mean',
            'Bnd_Pct': 'mean'
        }).reset_index()
        
        top_performers = top_performers[top_performers['Entry_Over'] >= 3]
        top_performers = top_performers.nlargest(15, 'Final_Strike_Rate')
        top_performers.columns = ['Player', 'Avg SR', 'Avg Runs', 'Matches', 'Dot%', 'Bnd%']
        
        st.dataframe(top_performers.round(1), use_container_width=True)

elif analysis_type == "Player Analysis":
    st.header("👤 Individual Player Analysis")
    
    if not filtered_df.empty:
        available_players = sorted(filtered_df['Player'].unique())
        selected_player = st.selectbox("Select Player:", available_players)
        
        if selected_player:
            player_data = filtered_df[filtered_df['Player'] == selected_player]
            
            # Player summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Matches", len(player_data))
            with col2:
                st.metric("Avg SR", f"{player_data['Final_Strike_Rate'].mean():.1f}")
            with col3:
                st.metric("Avg Runs", f"{player_data['Runs'].mean():.1f}")
            with col4:
                st.metric("Avg Entry", f"Over {player_data['Entry_Over'].mean():.1f}")
            
            # Bowling type performance (if available)
            if not bowling_df.empty and bowling_filter != "All":
                st.subheader(f"🎾 Performance vs {bowling_filter}")
                player_bowling = bowling_df[
                    (bowling_df['Batsman'] == selected_player) &
                    (bowling_df['Bowling_Category'] == bowling_filter)
                ]
                
                if not player_bowling.empty:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Balls Faced", int(player_bowling['Balls'].sum()))
                    with col2:
                        st.metric("Runs Scored", int(player_bowling['Runs'].sum()))
                    with col3:
                        st.metric("Strike Rate", f"{player_bowling['Strike_Rate'].mean():.1f}")
                else:
                    st.info(f"No {bowling_filter} data for {selected_player}")
            
            # Performance by phase
            st.subheader("📊 Performance by Phase")
            
            phase_perf = player_data.groupby('Entry_Phase').agg({
                'Entry_Over': 'count',
                'Final_Strike_Rate': 'mean',
                'Runs': 'mean',
                'Dot_Pct': 'mean',
                'Bnd_Pct': 'mean'
            }).round(1).reset_index()
            
            phase_perf.columns = ['Phase', 'Matches', 'Avg SR', 'Avg Runs', 'Dot%', 'Bnd%']
            st.dataframe(phase_perf, use_container_width=True)
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(
                    player_data,
                    x='Entry_Over',
                    y='Final_Strike_Rate',
                    size='Runs',
                    color='Entry_Phase',
                    title=f"{selected_player} - Entry vs Strike Rate",
                    hover_data=['Runs', 'BF']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    player_data,
                    x='Entry_Phase',
                    y='Runs',
                    title=f"{selected_player} - Runs by Phase",
                    color='Entry_Phase'
                )
                st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Team Analysis":
    st.header("🏟️ Team Analysis")
    
    if not filtered_df.empty:
        team_stats = []
        
        for team in selected_teams:
            team_data = filtered_df[filtered_df['Team'] == team]
            if not team_data.empty:
                stats = {
                    'Team': team,
                    'Entries': len(team_data),
                    'Avg SR': team_data['Final_Strike_Rate'].mean(),
                    'Avg Runs': team_data['Runs'].mean(),
                    'Powerplay %': (len(team_data[team_data['Entry_Over'] <= 6]) / len(team_data) * 100),
                    'Death %': (len(team_data[team_data['Entry_Over'] >= 16]) / len(team_data) * 100)
                }
                team_stats.append(stats)
        
        team_df = pd.DataFrame(team_stats).round(1)
        st.dataframe(team_df, use_container_width=True)
        
        # Team comparison
        fig = px.bar(
            team_df,
            x='Team',
            y='Avg SR',
            title="Average Strike Rate by Team",
            color='Avg SR',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Ball Position Analysis":
    st.header("🎯 Ball Position Analysis")
    
    st.info("💡 Analyze player performance by ball position in over (1-6) and Required Run Rate")
    
    if not ball_position_df.empty:
        # Filter ball position data
        bp_filtered = ball_position_df[
            (ball_position_df['Year'].isin(selected_years)) &
            (ball_position_df['Team'].isin(selected_teams))
        ].copy()
        
        # Filter to chase scenarios only
        chase_bp = bp_filtered[bp_filtered['RRR_Range'] != 'No RRR'].copy()
        
        if not chase_bp.empty:
            st.markdown(f"**Analyzing {len(chase_bp):,} balls in chase scenarios**")
            
            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_runs = chase_bp['Runs_This_Ball'].sum()
                total_balls = len(chase_bp)
                avg_sr = (total_runs / total_balls) * 100
                st.metric("Avg Strike Rate", f"{avg_sr:.1f}")
            with col2:
                boundary_pct = (chase_bp['Is_Boundary'].sum() / len(chase_bp) * 100)
                st.metric("Boundary %", f"{boundary_pct:.1f}%")
            with col3:
                dot_pct = (chase_bp['Is_Dot'].sum() / len(chase_bp) * 100)
                st.metric("Dot Ball %", f"{dot_pct:.1f}%")
            with col4:
                st.metric("Total Balls", f"{len(chase_bp):,}")
            
            # Player aggregation
            st.subheader("👤 Player Performance by Ball Position, RRR & Entry Phase")
            
            # Add entry phase filter
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_ball_pos = st.multiselect(
                    "Ball Position:",
                    ['Early (1-2)', 'Middle (3-4)', 'Late (5-6)'],
                    default=['Late (5-6)']
                )
            with col2:
                selected_rrr = st.multiselect(
                    "RRR Range:",
                    ['0-6 RPO', '6-9 RPO', '9-12 RPO', '12-15 RPO', '15+ RPO'],
                    default=['12-15 RPO', '15+ RPO']
                )
            with col3:
                available_entry_phases = sorted(chase_bp['Entry_Phase'].unique())
                selected_entry_phase = st.multiselect(
                    "Entry Phase:",
                    available_entry_phases,
                    default=available_entry_phases
                )
            
            # Filter by entry phase
            chase_bp_filtered = chase_bp[chase_bp['Entry_Phase'].isin(selected_entry_phase)].copy()
            
            # Aggregate with entry phase
            player_bp = chase_bp_filtered.groupby(['Batsman', 'Entry_Phase', 'Ball_Position', 'RRR_Range']).agg({
                'Runs_This_Ball': ['count', 'sum'],
                'Is_Dot': 'sum',
                'Is_Boundary': 'sum',
                'Is_Four': 'sum',
                'Is_Six': 'sum'
            }).reset_index()
            
            player_bp.columns = ['Player', 'Entry_Phase', 'Ball_Position', 'RRR_Range', 'Balls', 'Runs', 
                                'Dots', 'Boundaries', 'Fours', 'Sixes']
            
            player_bp['Strike_Rate'] = (player_bp['Runs'] / player_bp['Balls'] * 100).round(1)
            player_bp['Dot_Pct'] = (player_bp['Dots'] / player_bp['Balls'] * 100).round(1)
            player_bp['Boundary_Pct'] = (player_bp['Boundaries'] / player_bp['Balls'] * 100).round(1)
            
            # Filter minimum sample
            player_bp = player_bp[player_bp['Balls'] >= 5]
            
            filtered_bp = player_bp[
                (player_bp['Ball_Position'].isin(selected_ball_pos)) &
                (player_bp['RRR_Range'].isin(selected_rrr))
            ]
            
            if not filtered_bp.empty:
                # Sort options
                sort_by = st.radio(
                    "Sort by:",
                    ["Strike Rate", "Boundary %", "Total Balls"],
                    horizontal=True
                )
                
                sort_map = {
                    "Strike Rate": "Strike_Rate",
                    "Boundary %": "Boundary_Pct",
                    "Total Balls": "Balls"
                }
                
                filtered_bp = filtered_bp.sort_values(sort_map[sort_by], ascending=False)
                
                st.dataframe(filtered_bp.head(20), use_container_width=True)
                
                # AI Insights for filtered data
                st.markdown("---")
                st.subheader("🤖 AI Expert Analysis")
                
                ai_model = initialize_ai()
                
                if ai_model is not None:
                    if st.button("🔍 Generate Expert Insights", key="ball_position_ai"):
                        with st.spinner("Analyzing patterns and trends..."):
                            try:
                                # Prepare comprehensive context for AI
                                top_performers = filtered_bp.head(15)
                                
                                # Calculate overall stats
                                total_balls = filtered_bp['Balls'].sum()
                                total_runs = filtered_bp['Runs'].sum()
                                avg_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
                                avg_boundary_pct = filtered_bp['Boundary_Pct'].mean()
                                avg_dot_pct = filtered_bp['Dot_Pct'].mean()
                                
                                # Analyze by ball position
                                ball_pos_analysis = filtered_bp.groupby('Ball_Position').agg({
                                    'Strike_Rate': 'mean',
                                    'Boundary_Pct': 'mean',
                                    'Balls': 'sum'
                                }).round(1)
                                
                                # Analyze by entry phase
                                entry_phase_analysis = filtered_bp.groupby('Entry_Phase').agg({
                                    'Strike_Rate': 'mean',
                                    'Boundary_Pct': 'mean',
                                    'Balls': 'sum'
                                }).round(1)
                                
                                # Find specialists
                                early_ball_specialists = filtered_bp[filtered_bp['Ball_Position'] == 'Early (1-2)'].nlargest(5, 'Strike_Rate')
                                late_ball_specialists = filtered_bp[filtered_bp['Ball_Position'] == 'Late (5-6)'].nlargest(5, 'Strike_Rate')
                                
                                # Build expert context
                                context = f"""You are an expert cricket analyst specializing in ball-by-ball performance patterns. Analyze this IPL data with deep tactical insight.

ANALYSIS SCOPE:
- Ball Positions: {', '.join(selected_ball_pos)}
- RRR Ranges: {', '.join(selected_rrr)}
- Entry Phases: {', '.join(selected_entry_phase)}
- Dataset: {total_balls:,} balls from {len(filtered_bp)} player-situation combinations

AGGREGATE PERFORMANCE METRICS:
- Overall Strike Rate: {avg_sr:.1f}
- Overall Boundary %: {avg_boundary_pct:.1f}%
- Overall Dot Ball %: {avg_dot_pct:.1f}%

PERFORMANCE BY BALL POSITION:
{ball_pos_analysis.to_string()}

PERFORMANCE BY ENTRY PHASE:
{entry_phase_analysis.to_string()}

TOP PERFORMERS (Overall):
{top_performers[['Player', 'Entry_Phase', 'Ball_Position', 'RRR_Range', 'Balls', 'Strike_Rate', 'Boundary_Pct', 'Dot_Pct']].to_string(index=False)}

EARLY BALL SPECIALISTS (Balls 1-2):
{early_ball_specialists[['Player', 'Entry_Phase', 'RRR_Range', 'Strike_Rate', 'Boundary_Pct']].to_string(index=False) if not early_ball_specialists.empty else 'No data'}

LATE BALL SPECIALISTS (Balls 5-6):
{late_ball_specialists[['Player', 'Entry_Phase', 'RRR_Range', 'Strike_Rate', 'Boundary_Pct']].to_string(index=False) if not late_ball_specialists.empty else 'No data'}

EXPERT ANALYSIS REQUIRED:

1. BALL POSITION TRENDS:
   - Which players consistently exploit early balls (1-2) in the over? What makes them effective?
   - Who are the late-over specialists (balls 5-6)? How do they differ from early ball players?
   - Are there players who perform across all ball positions? What's their secret?

2. ENTRY PHASE IMPACT:
   - How does entry timing (Powerplay/Middle/Death) influence ball position performance?
   - Do Powerplay entrants show different ball position preferences than Death over entrants?
   - Which entry phase produces the most versatile players?

3. PRESSURE SITUATIONS:
   - At high RRR (12+ RPO), which ball positions are most productive?
   - Do certain players thrive on specific balls when pressure is high?
   - What's the risk-reward profile for different ball positions under pressure?

4. TACTICAL PATTERNS:
   - Identify 3-4 distinct player archetypes based on ball position preferences
   - Which combinations of entry phase + ball position are most/least effective?
   - Are there counter-intuitive findings that challenge conventional wisdom?

5. TEAM SELECTION STRATEGY:
   - Recommend specific players for specific match situations
   - Suggest batting order positions based on ball position strengths
   - Identify gaps in the current player pool

Provide actionable insights that a team management can use immediately. Focus on WHY patterns exist, not just WHAT they are.
"""
                                
                                response = ai_model.generate_content(context)
                                st.markdown(response.text)
                                
                            except Exception as e:
                                st.error(f"Error generating insights: {e}")
                else:
                    st.info("💡 Configure GEMINI_API_KEY in .env to enable AI insights")
                
                st.markdown("---")
                
                # Visualizations
                st.subheader("📊 Performance Heatmaps")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Strike Rate by Ball Position and RRR
                    pivot_sr = player_bp.groupby(['Ball_Position', 'RRR_Range'])['Strike_Rate'].mean().reset_index()
                    pivot_sr_wide = pivot_sr.pivot(index='Ball_Position', columns='RRR_Range', values='Strike_Rate')
                    
                    fig = px.imshow(
                        pivot_sr_wide,
                        title="Average Strike Rate by Ball Position & RRR",
                        labels=dict(x="RRR Range", y="Ball Position", color="Strike Rate"),
                        color_continuous_scale='RdYlGn',
                        aspect="auto"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Boundary % by Ball Position and RRR
                    pivot_bnd = player_bp.groupby(['Ball_Position', 'RRR_Range'])['Boundary_Pct'].mean().reset_index()
                    pivot_bnd_wide = pivot_bnd.pivot(index='Ball_Position', columns='RRR_Range', values='Boundary_Pct')
                    
                    fig = px.imshow(
                        pivot_bnd_wide,
                        title="Average Boundary % by Ball Position & RRR",
                        labels=dict(x="RRR Range", y="Ball Position", color="Boundary %"),
                        color_continuous_scale='Blues',
                        aspect="auto"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Individual player analysis
                st.subheader("🔍 Individual Player Analysis")
                
                available_players = sorted(player_bp['Player'].unique())
                selected_player = st.selectbox("Select Player:", available_players)
                
                if selected_player:
                    player_data = player_bp[player_bp['Player'] == selected_player]
                    
                    if not player_data.empty:
                        # Player summary
                        st.markdown(f"### {selected_player} - Ball Position Performance")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Balls", int(player_data['Balls'].sum()))
                        with col2:
                            avg_sr = (player_data['Runs'].sum() / player_data['Balls'].sum() * 100)
                            st.metric("Overall SR", f"{avg_sr:.1f}")
                        with col3:
                            avg_bnd = (player_data['Boundaries'].sum() / player_data['Balls'].sum() * 100)
                            st.metric("Overall Boundary %", f"{avg_bnd:.1f}%")
                        with col4:
                            entry_phases = player_data['Entry_Phase'].unique()
                            st.metric("Entry Phases", len(entry_phases))
                        
                        # Entry phase breakdown
                        st.markdown("#### Performance by Entry Phase")
                        entry_summary = player_data.groupby('Entry_Phase').agg({
                            'Balls': 'sum',
                            'Runs': 'sum',
                            'Boundaries': 'sum'
                        }).reset_index()
                        entry_summary['Strike_Rate'] = (entry_summary['Runs'] / entry_summary['Balls'] * 100).round(1)
                        entry_summary['Boundary_Pct'] = (entry_summary['Boundaries'] / entry_summary['Balls'] * 100).round(1)
                        st.dataframe(entry_summary, use_container_width=True)
                        
                        # AI Insights for individual player
                        st.markdown("---")
                        st.markdown("#### 🤖 Expert Player Profile")
                        
                        if ai_model is not None:
                            if st.button(f"🔍 Generate Expert Analysis for {selected_player}", key=f"player_ai_{selected_player}"):
                                with st.spinner(f"Building tactical profile for {selected_player}..."):
                                    try:
                                        # Prepare comprehensive player context
                                        total_balls = player_data['Balls'].sum()
                                        total_runs = player_data['Runs'].sum()
                                        overall_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
                                        overall_boundary_pct = (player_data['Boundaries'].sum() / total_balls * 100) if total_balls > 0 else 0
                                        
                                        # Analyze by ball position
                                        ball_pos_profile = player_data.groupby('Ball_Position').agg({
                                            'Balls': 'sum',
                                            'Strike_Rate': 'mean',
                                            'Boundary_Pct': 'mean'
                                        }).round(1)
                                        
                                        # Analyze by RRR range
                                        rrr_profile = player_data.groupby('RRR_Range').agg({
                                            'Balls': 'sum',
                                            'Strike_Rate': 'mean',
                                            'Boundary_Pct': 'mean'
                                        }).round(1)
                                        
                                        # Best and worst situations
                                        best_situations = player_data.nlargest(3, 'Strike_Rate')
                                        worst_situations = player_data.nsmallest(3, 'Strike_Rate')
                                        
                                        # High pressure performance (RRR 12+)
                                        high_pressure = player_data[player_data['RRR_Range'].isin(['12-15 RPO', '15+ RPO'])]
                                        
                                        context = f"""You are an expert cricket analyst creating a detailed tactical profile for {selected_player}. Analyze their ball position performance with deep insight.

PLAYER: {selected_player}

OVERALL STATISTICS:
- Total Balls Analyzed: {total_balls}
- Overall Strike Rate: {overall_sr:.1f}
- Overall Boundary %: {overall_boundary_pct:.1f}%
- Entry Phases: {', '.join(player_data['Entry_Phase'].unique())}

ENTRY PHASE PERFORMANCE:
{entry_summary.to_string(index=False)}

BALL POSITION PROFILE:
{ball_pos_profile.to_string()}

RRR RANGE PROFILE:
{rrr_profile.to_string()}

TOP 3 BEST SITUATIONS:
{best_situations[['Entry_Phase', 'Ball_Position', 'RRR_Range', 'Balls', 'Strike_Rate', 'Boundary_Pct', 'Dot_Pct']].to_string(index=False)}

TOP 3 WORST SITUATIONS:
{worst_situations[['Entry_Phase', 'Ball_Position', 'RRR_Range', 'Balls', 'Strike_Rate', 'Boundary_Pct', 'Dot_Pct']].to_string(index=False)}

HIGH PRESSURE PERFORMANCE (RRR 12+ RPO):
- Balls Faced: {high_pressure['Balls'].sum() if not high_pressure.empty else 0}
- Strike Rate: {(high_pressure['Runs'].sum() / high_pressure['Balls'].sum() * 100) if not high_pressure.empty and high_pressure['Balls'].sum() > 0 else 'N/A'}
- Boundary %: {(high_pressure['Boundaries'].sum() / high_pressure['Balls'].sum() * 100) if not high_pressure.empty and high_pressure['Balls'].sum() > 0 else 'N/A'}

DETAILED BREAKDOWN (All Situations):
{player_data.nlargest(10, 'Balls')[['Entry_Phase', 'Ball_Position', 'RRR_Range', 'Balls', 'Strike_Rate', 'Boundary_Pct', 'Dot_Pct']].to_string(index=False)}

EXPERT ANALYSIS REQUIRED:

1. BALL POSITION MASTERY:
   - Which balls in the over does {selected_player} dominate? (Early 1-2, Middle 3-4, Late 5-6)
   - Is there a clear pattern or is the player versatile across all positions?
   - What technical or tactical reasons explain their ball position preferences?

2. ENTRY TIMING IMPACT:
   - How does entry phase (Powerplay/Middle/Death) affect their performance?
   - Does {selected_player} adapt their approach based on when they enter?
   - Which entry phase brings out their best performance and why?

3. PRESSURE HANDLING:
   - How does {selected_player} perform under high RRR pressure (12+ RPO)?
   - Do they maintain consistency or show volatility in pressure situations?
   - Which ball positions do they prefer when chasing high run rates?

4. TACTICAL ARCHETYPE:
   - Classify {selected_player} into a tactical archetype (e.g., "Early Ball Aggressor", "Late Over Finisher", "Pressure Specialist", "Versatile Accumulator")
   - What makes them unique compared to other players?
   - Are there any counter-intuitive findings about their game?

5. STRATEGIC RECOMMENDATIONS:
   - Optimal batting position for {selected_player} based on this data
   - Best match situations to deploy them (entry phase + RRR context)
   - Specific balls in the over where they should be on strike
   - Situations to avoid or where they need support
   - Training focus areas to improve weaknesses

6. COMPARATIVE INSIGHTS:
   - How does {selected_player} compare to typical IPL batsmen in these situations?
   - What's their unique value proposition for team selection?

Provide tactical insights that coaches and team management can act on immediately. Focus on actionable recommendations backed by data patterns.
"""
                                        
                                        response = ai_model.generate_content(context)
                                        st.markdown(response.text)
                                        
                                    except Exception as e:
                                        st.error(f"Error generating insights: {e}")
                        else:
                            st.info("💡 Configure GEMINI_API_KEY in .env to enable AI insights")
                        
                        st.markdown("---")
                        
                        # Detailed breakdown
                        st.markdown("#### Detailed Breakdown")
                        st.dataframe(player_data.sort_values(['Entry_Phase', 'RRR_Range', 'Ball_Position']), 
                                   use_container_width=True)
                        
                        # Heatmaps for individual player
                        st.markdown("#### Performance Heatmaps")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Strike Rate Heatmap - aggregate across entry phases
                            pivot_data = player_data.groupby(['Ball_Position', 'RRR_Range']).agg({
                                'Runs': 'sum',
                                'Balls': 'sum'
                            }).reset_index()
                            pivot_data['Strike_Rate'] = (pivot_data['Runs'] / pivot_data['Balls'] * 100).round(1)
                            
                            pivot_sr = pivot_data.pivot(
                                index='Ball_Position', 
                                columns='RRR_Range', 
                                values='Strike_Rate'
                            )
                            # Reorder rows for better visualization
                            row_order = ['Early (1-2)', 'Middle (3-4)', 'Late (5-6)']
                            pivot_sr = pivot_sr.reindex([r for r in row_order if r in pivot_sr.index])
                            
                            fig = px.imshow(
                                pivot_sr,
                                title=f"{selected_player} - Strike Rate",
                                labels=dict(x="RRR Range", y="Ball Position", color="SR"),
                                color_continuous_scale='RdYlGn',
                                aspect="auto",
                                text_auto='.1f'
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Boundary % Heatmap - aggregate across entry phases
                            pivot_data_bnd = player_data.groupby(['Ball_Position', 'RRR_Range']).agg({
                                'Boundaries': 'sum',
                                'Balls': 'sum'
                            }).reset_index()
                            pivot_data_bnd['Boundary_Pct'] = (pivot_data_bnd['Boundaries'] / pivot_data_bnd['Balls'] * 100).round(1)
                            
                            pivot_bnd = pivot_data_bnd.pivot(
                                index='Ball_Position', 
                                columns='RRR_Range', 
                                values='Boundary_Pct'
                            )
                            pivot_bnd = pivot_bnd.reindex([r for r in row_order if r in pivot_bnd.index])
                            
                            fig = px.imshow(
                                pivot_bnd,
                                title=f"{selected_player} - Boundary %",
                                labels=dict(x="RRR Range", y="Ball Position", color="Bnd %"),
                                color_continuous_scale='Blues',
                                aspect="auto",
                                text_auto='.1f'
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col3:
                            # Dot % Heatmap - aggregate across entry phases
                            pivot_data_dot = player_data.groupby(['Ball_Position', 'RRR_Range']).agg({
                                'Dots': 'sum',
                                'Balls': 'sum'
                            }).reset_index()
                            pivot_data_dot['Dot_Pct'] = (pivot_data_dot['Dots'] / pivot_data_dot['Balls'] * 100).round(1)
                            
                            pivot_dot = pivot_data_dot.pivot(
                                index='Ball_Position', 
                                columns='RRR_Range', 
                                values='Dot_Pct'
                            )
                            pivot_dot = pivot_dot.reindex([r for r in row_order if r in pivot_dot.index])
                            
                            fig = px.imshow(
                                pivot_dot,
                                title=f"{selected_player} - Dot Ball %",
                                labels=dict(x="RRR Range", y="Ball Position", color="Dot %"),
                                color_continuous_scale='Reds_r',
                                aspect="auto",
                                text_auto='.1f'
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Sample size heatmap
                        st.markdown("#### Sample Size (Balls Faced)")
                        pivot_balls_data = player_data.groupby(['Ball_Position', 'RRR_Range'])['Balls'].sum().reset_index()
                        pivot_balls = pivot_balls_data.pivot(
                            index='Ball_Position', 
                            columns='RRR_Range', 
                            values='Balls'
                        )
                        pivot_balls = pivot_balls.reindex([r for r in row_order if r in pivot_balls.index])
                        
                        fig = px.imshow(
                            pivot_balls,
                            title=f"{selected_player} - Balls Faced by Situation",
                            labels=dict(x="RRR Range", y="Ball Position", color="Balls"),
                            color_continuous_scale='Greys',
                            aspect="auto",
                            text_auto='d'
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Entry Phase Heatmaps
                        st.markdown("#### Performance by Entry Phase")
                        st.info("Shows how the player performs based on when they entered the innings")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Strike Rate by Entry Phase and Ball Position
                            if 'Entry_Phase' in player_data.columns:
                                entry_sr_data = player_data.groupby(['Entry_Phase', 'Ball_Position']).agg({
                                    'Runs': 'sum',
                                    'Balls': 'sum'
                                }).reset_index()
                                entry_sr_data['Strike_Rate'] = (entry_sr_data['Runs'] / entry_sr_data['Balls'] * 100).round(1)
                                
                                pivot_entry_sr_wide = entry_sr_data.pivot(
                                    index='Entry_Phase', 
                                    columns='Ball_Position', 
                                    values='Strike_Rate'
                                )
                                # Reorder columns
                                col_order = ['Early (1-2)', 'Middle (3-4)', 'Late (5-6)']
                                pivot_entry_sr_wide = pivot_entry_sr_wide[[c for c in col_order if c in pivot_entry_sr_wide.columns]]
                                
                                fig = px.imshow(
                                    pivot_entry_sr_wide,
                                    title=f"SR by Entry Phase & Ball Position",
                                    labels=dict(x="Ball Position", y="Entry Phase", color="SR"),
                                    color_continuous_scale='RdYlGn',
                                    aspect="auto",
                                    text_auto='.1f'
                                )
                                fig.update_layout(height=300)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Boundary % by Entry Phase and RRR
                            if 'Entry_Phase' in player_data.columns:
                                entry_bnd_data = player_data.groupby(['Entry_Phase', 'RRR_Range']).agg({
                                    'Boundaries': 'sum',
                                    'Balls': 'sum'
                                }).reset_index()
                                entry_bnd_data['Boundary_Pct'] = (entry_bnd_data['Boundaries'] / entry_bnd_data['Balls'] * 100).round(1)
                                
                                pivot_entry_bnd_wide = entry_bnd_data.pivot(
                                    index='Entry_Phase', 
                                    columns='RRR_Range', 
                                    values='Boundary_Pct'
                                )
                                
                                fig = px.imshow(
                                    pivot_entry_bnd_wide,
                                    title=f"Boundary % by Entry Phase & RRR",
                                    labels=dict(x="RRR Range", y="Entry Phase", color="Bnd %"),
                                    color_continuous_scale='Blues',
                                    aspect="auto",
                                    text_auto='.1f'
                                )
                                fig.update_layout(height=300)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col3:
                            # Balls faced by Entry Phase
                            if 'Entry_Phase' in player_data.columns:
                                entry_balls_data = player_data.groupby(['Entry_Phase', 'RRR_Range'])['Balls'].sum().reset_index()
                                
                                pivot_entry_balls_wide = entry_balls_data.pivot(
                                    index='Entry_Phase', 
                                    columns='RRR_Range', 
                                    values='Balls'
                                )
                                
                                fig = px.imshow(
                                    pivot_entry_balls_wide,
                                    title=f"Sample Size by Entry Phase & RRR",
                                    labels=dict(x="RRR Range", y="Entry Phase", color="Balls"),
                                    color_continuous_scale='Greys',
                                    aspect="auto",
                                    text_auto='d'
                                )
                                fig.update_layout(height=300)
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"No data for {selected_player} with current filters")
            else:
                st.warning("No data available with selected filters")
        else:
            st.warning("No chase scenario data available")
    else:
        st.warning("Ball position data not loaded. Run process_ball_position_data.py first.")

elif analysis_type == "AI Insights":
    st.header("🤖 AI-Powered Insights")
    
    # Initialize AI
    ai_model = initialize_ai()
    
    if ai_model is None:
        st.error("❌ AI not configured. Set GEMINI_API_KEY in .env file")
    else:
        # Initialize ReAct agent
        if 'react_agent' not in st.session_state:
            try:
                analyzer = CricketDataAnalyzer(filtered_df)
                st.session_state.react_agent = ReActCricketAgent(analyzer, ai_model)
                st.success("✅ AI Coach initialized")
            except Exception as e:
                st.error(f"Error initializing AI: {e}")
                st.session_state.react_agent = None
        
        if st.session_state.react_agent:
            st.info(f"📊 Analyzing {len(filtered_df)} entry points with current filters")
            
            # Quick action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🎯 Best Powerplay Players"):
                    question = "Who are the best powerplay players?"
                    st.session_state.current_question = question
            with col2:
                if st.button("💥 Best Death Over Finishers"):
                    question = "Who are the best death over finishers?"
                    st.session_state.current_question = question
            with col3:
                if st.button("📋 Optimal Batting Order"):
                    question = "What is the optimal batting order for chasing 180+ runs?"
                    st.session_state.current_question = question
            
            # Question input
            user_question = st.text_input(
                "Ask the AI Coach:",
                placeholder="e.g., Which players perform best in middle overs?",
                key="user_question_input"
            )
            
            if st.button("🚀 Get Answer") or user_question:
                question = user_question if user_question else st.session_state.get('current_question', '')
                
                if question:
                    with st.spinner("🤔 AI Coach analyzing..."):
                        try:
                            # Update agent with current filtered data
                            st.session_state.react_agent.analyzer = CricketDataAnalyzer(filtered_df)
                            
                            answer = st.session_state.react_agent.answer_question(question)
                            
                            st.markdown("### 🎓 AI Coach Response:")
                            st.markdown(answer)
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            if "quota" in str(e).lower() or "429" in str(e):
                                st.warning("⚠️ API quota exceeded. Please wait or upgrade your API plan.")
        else:
            st.error("Failed to initialize AI agent")

# Footer
st.markdown("---")
st.markdown(f"**Data:** {len(entry_df):,} entry points | **Players:** {entry_df['Player'].nunique()} | **Matches:** {entry_df['Match'].nunique()}")
