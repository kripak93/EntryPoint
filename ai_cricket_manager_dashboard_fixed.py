"""
AI-Powered Cricket Manager Dashboard - Fixed Version
Strategic insights and recommendations for team management
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Cricket Manager Dashboard",
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
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .recommendation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏏 AI Cricket Manager Dashboard</h1>
    <p>Strategic Intelligence & Performance Analysis for Team Management</p>
</div>
""", unsafe_allow_html=True)

# Initialize Gemini AI
@st.cache_resource
def initialize_ai():
    """Initialize Gemini AI"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    
    if not api_key:
        st.error("🔑 Gemini API key not found. Please configure GEMINI_API_KEY in environment variables or Streamlit secrets.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        return model
    except Exception as e:
        st.error(f"❌ Failed to initialize AI: {e}")
        return None

@st.cache_data
def load_cricket_data():
    """Load cricket analytics data"""
    try:
        with open('cricket_analytics_data (1).json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("❌ Cricket analytics data file not found! Please ensure 'cricket_analytics_data (1).json' is in the same directory.")
        return None

def generate_ai_insight(prompt, data_context, detailed_stats=None):
    """Generate AI insights using Gemini with actual cricket data"""
    ai_model = initialize_ai()
    if not ai_model:
        return "AI analysis unavailable - API key not configured"
    
    try:
        cricket_context = f"""
        CRICKET PERFORMANCE DATA ANALYSIS:
        
        BASIC CONTEXT:
        {data_context}
        
        DETAILED STATISTICS:
        {detailed_stats if detailed_stats else "No detailed stats provided"}
        
        CRICKET METRICS EXPLANATION:
        - SR (Strike Rate): Runs per 100 balls faced (higher is more aggressive)
        - RR (Run Rate): Runs per over (economy rate for bowlers)
        - BF: Balls Faced by batsman
        - Wks: Wickets taken (for bowlers) or times dismissed (for batsmen)
        - Ave: Batting/Bowling average
        - PP: Powerplay (overs 1-6)
        - Post PP: Middle and death overs (7-20)
        """
        
        full_prompt = f"""
        You are a professional cricket analyst with deep knowledge of T20 cricket strategy.
        
        {cricket_context}

        ANALYSIS REQUEST:
        {prompt}

        Please provide actionable insights based on the actual statistics provided above.
        """
        
        response = ai_model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"AI analysis error: {str(e)}"

def extract_detailed_team_stats(team_data):
    """Extract comprehensive statistics for AI analysis"""
    detailed_stats = {
        'players': [],
        'bowling_data': [],
        'matchups': [],
        'phase_performance': {}
    }
    
    for matchup_key, matchup_data in team_data.items():
        phase = matchup_key.split('_')[-1]
        
        # Extract player batting stats
        if 'players' in matchup_data:
            for player in matchup_data['players']:
                player_stat = {
                    'name': player.get('player', 'Unknown'),
                    'phase': phase,
                    'runs': player.get('runs', 0),
                    'balls_faced': player.get('bf', 0),
                    'strike_rate': player.get('sr', 0),
                    'average': player.get('avg', 0),
                    'wickets_lost': player.get('wks', 0),
                    'innings': player.get('innings', 0),
                    'technique': player.get('technique', 'Unknown')
                }
                detailed_stats['players'].append(player_stat)
        
        # Extract bowling data
        if 'data' in matchup_data:
            for bowler in matchup_data['data']:
                if bowler and bowler.get('Player'):
                    bowler_stat = {
                        'name': bowler.get('Player'),
                        'phase': phase,
                        'bowl_type': bowler.get('BowlType', 'Unknown'),
                        'runs_conceded': bowler.get('Runs', 0),
                        'balls_bowled': bowler.get('BF', 0),
                        'wickets': bowler.get('Wks', 0),
                        'run_rate': bowler.get('RR', 0),
                        'strike_rate': bowler.get('SR', 0)
                    }
                    detailed_stats['bowling_data'].append(bowler_stat)
        
        # Extract matchup data
        if 'matchups' in matchup_data:
            for matchup in matchup_data['matchups']:
                matchup_stat = {
                    'batsman': matchup.get('batsman', 'Unknown'),
                    'bowler': matchup.get('bowler', 'Unknown'),
                    'runs': matchup.get('runs', 0),
                    'balls': matchup.get('bf', 0),
                    'strike_rate': matchup.get('sr', 0),
                    'wickets': matchup.get('wks', 0),
                    'advantage': matchup.get('advantage', 'neutral'),
                    'phase': phase
                }
                detailed_stats['matchups'].append(matchup_stat)
    
    return detailed_stats

def get_team_data(team_code, year_filter=None):
    """Get all data for a specific team, optionally filtered by year"""
    cricket_data = load_cricket_data()
    if not cricket_data:
        return {}
    
    team_matchups = {k: v for k, v in cricket_data['matchups'].items() 
                    if k.startswith(team_code)}
    
    if year_filter is None:
        return team_matchups
    
    # Filter by year if specified
    filtered_matchups = {}
    for matchup_key, matchup_data in team_matchups.items():
        filtered_data = matchup_data.copy()
        
        # Filter bowling data by year
        if 'data' in filtered_data:
            filtered_bowling = []
            for bowler in filtered_data['data']:
                if bowler and bowler.get('Span'):
                    span = bowler['Span']
                    if span and any(year in span for year in year_filter):
                        filtered_bowling.append(bowler)
            filtered_data['data'] = filtered_bowling
        
        filtered_matchups[matchup_key] = filtered_data
    
    return filtered_matchups

def main():
    """Main application function"""
    # Load data
    cricket_data = load_cricket_data()
    if cricket_data is None:
        st.stop()

    # Sidebar
    st.sidebar.header("🎯 Manager's Control Panel")

    # Get available teams, phases, and years
    matchup_keys = list(cricket_data.get('matchups', {}).keys())
    teams = set()
    phases = set()
    available_years = set()

    # Extract available years from bowling data
    for matchup_key, matchup_data in cricket_data['matchups'].items():
        parts = matchup_key.split('_')
        if len(parts) >= 3:
            team = parts[0]
            phase = parts[-1]
            teams.add(team)
            phases.add(phase)
        
        # Extract years from bowling data
        if 'data' in matchup_data:
            for bowler in matchup_data['data']:
                if bowler and bowler.get('Span'):
                    span = bowler['Span']
                    if span and '-' in span:
                        start_year, end_year = span.split('-')
                        available_years.add(start_year)
                        available_years.add(end_year)

    teams = sorted(list(teams))
    phases = sorted(list(phases))
    available_years = sorted(list(available_years))

    # Team mapping for better display
    team_names = {
        'ADKR': 'Abu Dhabi Knight Riders',
        'DC': 'Desert Capitals', 
        'GG': 'Gulf Giants',
        'MIE': 'MI Emirates',
        'SW': 'Sharjah Warriors',
        'DV': 'Dubai Vipers'
    }

    # Sidebar selections
    if not teams:
        st.error("No team data found in the cricket analytics file.")
        st.stop()

    selected_team = st.sidebar.selectbox(
        "🏟️ Select Your Team:", 
        teams,
        format_func=lambda x: team_names.get(x, x)
    )

    # Year filter
    year_filter = None
    if available_years:
        st.sidebar.subheader("📅 Time Period Filter")
        year_filter_type = st.sidebar.radio(
            "Filter by:",
            ["All Years", "Specific Year"]
        )
        
        if year_filter_type == "Specific Year":
            selected_year = st.sidebar.selectbox("Select Year:", available_years)
            year_filter = [selected_year]

    analysis_mode = st.sidebar.selectbox(
        "📊 Analysis Mode:", 
        ["Team Strategy Overview", "Player Performance Analysis", "AI Insights"]
    )

    # Main content based on analysis mode
    if analysis_mode == "Team Strategy Overview":
        st.header(f"🎯 Strategic Overview: {team_names.get(selected_team, selected_team)}")
        
        if year_filter:
            st.info(f"📅 Filtered for: {', '.join(year_filter)}")
        
        team_data = get_team_data(selected_team, year_filter)
        
        if team_data:
            # Overall team metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_players = 0
            total_runs = 0
            total_wickets = 0
            
            for matchup_key, matchup_data in team_data.items():
                if 'players' in matchup_data:
                    players_data = matchup_data['players']
                    total_players += len(players_data)
                    total_runs += sum(p.get('runs', 0) for p in players_data)
                    total_wickets += sum(p.get('wks', 0) for p in players_data)
            
            with col1:
                st.metric("Squad Size", total_players)
            with col2:
                st.metric("Total Runs", f"{total_runs:,}")
            with col3:
                st.metric("Total Wickets", total_wickets)
            with col4:
                st.metric("Matchups", len(team_data))
            
            # Phase-wise performance
            st.subheader("📊 Performance by Match Phase")
            
            phase_performance = []
            for matchup_key, matchup_data in team_data.items():
                phase = matchup_key.split('_')[-1]
                if 'players' in matchup_data:
                    players = matchup_data['players']
                    if players:
                        avg_sr = sum(p.get('sr', 0) for p in players) / len(players)
                        total_runs_phase = sum(p.get('runs', 0) for p in players)
                        
                        phase_performance.append({
                            'Phase': phase,
                            'Average Strike Rate': avg_sr,
                            'Total Runs': total_runs_phase,
                            'Players': len(players)
                        })
            
            if phase_performance:
                df_phase = pd.DataFrame(phase_performance)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.bar(df_phase, x='Phase', y='Average Strike Rate', 
                                 title="Strike Rate by Phase",
                                 color='Average Strike Rate',
                                 color_continuous_scale='viridis')
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    fig2 = px.pie(df_phase, values='Total Runs', names='Phase',
                                 title="Run Distribution by Phase")
                    st.plotly_chart(fig2, use_container_width=True)
            
            # AI Strategic Analysis
            if st.button("🤖 Generate AI Strategic Analysis", type="primary"):
                with st.spinner("🧠 AI is analyzing team strategy..."):
                    detailed_stats = extract_detailed_team_stats(team_data)
                    
                    data_context = f"""
                    Team: {team_names.get(selected_team, selected_team)}
                    Year Filter: {year_filter if year_filter else 'All Years'}
                    Total Players: {total_players}
                    Total Runs: {total_runs}
                    Total Wickets: {total_wickets}
                    Phase Performance: {phase_performance}
                    """
                    
                    prompt = f"Provide a comprehensive strategic analysis for {team_names.get(selected_team, selected_team)} including strengths, weaknesses, and tactical recommendations."
                    
                    ai_analysis = generate_ai_insight(prompt, data_context, detailed_stats)
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <h3>🧠 AI Strategic Analysis</h3>
                        <p>{ai_analysis}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No data available for the selected team and filters.")

    elif analysis_mode == "Player Performance Analysis":
        st.header("👤 Player Performance Intelligence")
        
        if year_filter:
            st.info(f"📅 Filtered for: {', '.join(year_filter)}")
        
        team_data = get_team_data(selected_team, year_filter)
        
        # Get all players for the team
        all_players = []
        for matchup_key, matchup_data in team_data.items():
            if 'players' in matchup_data:
                for player in matchup_data['players']:
                    player_info = player.copy()
                    player_info['phase'] = matchup_key.split('_')[-1]
                    all_players.append(player_info)
        
        if all_players:
            df_players = pd.DataFrame(all_players)
            
            # Top performers
            st.subheader("🏆 Top Performers")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🏏 Highest Run Scorers**")
                top_scorers = df_players.nlargest(5, 'runs')[['player', 'runs', 'sr']]
                for _, player in top_scorers.iterrows():
                    st.success(f"**{player['player']}**: {player['runs']} runs (SR: {player['sr']:.1f})")
            
            with col2:
                st.markdown("**⚡ Best Strike Rates**")
                min_balls = 50
                qualified = df_players[df_players['bf'] >= min_balls]
                if not qualified.empty:
                    best_sr = qualified.nlargest(5, 'sr')[['player', 'sr', 'runs']]
                    for _, player in best_sr.iterrows():
                        st.info(f"**{player['player']}**: SR {player['sr']:.1f} ({player['runs']} runs)")
            
            with col3:
                st.markdown("**🎯 Most Consistent**")
                if 'innings' in df_players.columns:
                    consistent = df_players[df_players['innings'] >= 3]
                    if not consistent.empty and 'avg' in consistent.columns:
                        consistent_with_avg = consistent.dropna(subset=['avg'])
                        if not consistent_with_avg.empty:
                            consistent_top = consistent_with_avg.nlargest(5, 'avg')[['player', 'avg', 'innings']]
                            for _, player in consistent_top.iterrows():
                                if pd.notna(player['avg']) and player['avg'] > 0:
                                    st.warning(f"**{player['player']}**: Avg {player['avg']:.1f} ({player['innings']} innings)")
            
            # Player selection for detailed analysis
            st.subheader("🔍 Detailed Player Analysis")
            
            unique_players = sorted(df_players['player'].unique())
            selected_player = st.selectbox("Select Player for Analysis:", unique_players)
            
            if selected_player:
                player_data = df_players[df_players['player'] == selected_player]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    total_runs = player_data['runs'].sum()
                    total_balls = player_data['bf'].sum()
                    avg_sr = player_data['sr'].mean()
                    total_wickets = player_data['wks'].sum()
                    
                    st.metric("Total Runs", f"{total_runs:,}")
                    st.metric("Total Balls Faced", f"{total_balls:,}")
                    st.metric("Average Strike Rate", f"{avg_sr:.1f}")
                    st.metric("Times Dismissed", total_wickets)
                
                with col2:
                    if st.button(f"🤖 AI Analysis for {selected_player}", type="primary"):
                        with st.spinner(f"🧠 Analyzing {selected_player}..."):
                            team_detailed_stats = extract_detailed_team_stats(team_data)
                            player_detailed_stats = [p for p in team_detailed_stats['players'] if p['name'] == selected_player]
                            
                            player_context = f"""
                            Player: {selected_player}
                            Team: {team_names.get(selected_team, selected_team)}
                            Total Runs: {total_runs}
                            Total Balls: {total_balls}
                            Average Strike Rate: {avg_sr:.1f}
                            Times Dismissed: {total_wickets}
                            """
                            
                            prompt = f"Provide detailed performance analysis and recommendations for {selected_player}."
                            
                            ai_analysis = generate_ai_insight(prompt, player_context, {'player_stats': player_detailed_stats})
                            
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <h4>🎯 AI Player Analysis: {selected_player}</h4>
                                <p>{ai_analysis}</p>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No player data available for the selected team and filters.")

    else:  # AI Insights
        st.header("🧠 AI-Powered Team Insights")
        
        if year_filter:
            st.info(f"📅 Filtered for: {', '.join(year_filter)}")
        
        # Custom analysis input
        st.subheader("🎯 Custom Analysis Request")
        
        analysis_type = st.selectbox(
            "Select Analysis Type:",
            ["Team Strengths & Weaknesses", "Player Role Optimization", "Tactical Recommendations", "Custom Query"]
        )
        
        if analysis_type == "Custom Query":
            custom_query = st.text_area("Enter your specific question:", 
                                       placeholder="e.g., How should we approach the powerplay against spin-heavy teams?")
        else:
            custom_query = None
        
        team_data = get_team_data(selected_team, year_filter)
        
        if st.button("🚀 Generate AI Analysis", type="primary"):
            with st.spinner("🧠 AI is analyzing..."):
                detailed_stats = extract_detailed_team_stats(team_data)
                
                data_summary = {
                    'team': team_names.get(selected_team, selected_team),
                    'total_matchups': len(team_data),
                    'player_count': len(detailed_stats['players']),
                    'bowler_count': len(detailed_stats['bowling_data']),
                    'matchup_count': len(detailed_stats['matchups'])
                }
                
                if analysis_type == "Custom Query" and custom_query:
                    prompt = custom_query
                else:
                    prompt = f"Provide {analysis_type.lower()} for {team_names.get(selected_team, selected_team)} based on the available performance data."
                
                ai_analysis = generate_ai_insight(prompt, str(data_summary), detailed_stats)
                
                st.markdown(f"""
                <div class="insight-card">
                    <h3>🧠 AI Analysis: {analysis_type}</h3>
                    <p>{ai_analysis}</p>
                </div>
                """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🏏 AI Cricket Manager Dashboard | Powered by Advanced Analytics & AI"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()