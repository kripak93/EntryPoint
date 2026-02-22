"""
Corrected Cricket Entry Analysis Dashboard
Properly calculating player entry points as minimum over per player per match
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai
from react_cricket_agent import create_react_agent

# Load environment variables
load_dotenv()

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
    .entry-card {
        background: linear-gradient(135deg, #32CD32 0%, #228B22 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .insight-card {
        background: linear-gradient(135deg, #4169E1 0%, #1E90FF 100%);
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
        border-left: 4px solid #2E8B57;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricket Entry Analysis Dashboard</h1>
    <p>Analyzing True Player Entry Points & Performance</p>
</div>
""", unsafe_allow_html=True)

# Initialize AI
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
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        return model
    except Exception as e:
        st.error(f"❌ Failed to initialize AI: {e}")
        return None

ai_model = initialize_ai()

@st.cache_data
def get_player_detailed_analysis(player_name, df):
    """Get detailed analysis for a specific player"""
    player_data = df[df['Player'].str.contains(player_name, case=False, na=False)]
    
    if player_data.empty:
        return None
    
    analysis = {
        'player_name': player_data['Player'].iloc[0],
        'total_matches': len(player_data),
        'avg_entry_over': player_data['Entry_Over'].mean(),
        'avg_strike_rate': player_data['Final_Strike_Rate'].mean(),
        'total_runs': player_data['Runs'].sum(),
        'avg_runs_per_match': player_data['Runs'].mean(),
        'best_strike_rate': player_data['Final_Strike_Rate'].max(),
        'preferred_phase': player_data['Entry_Phase'].mode().iloc[0] if not player_data['Entry_Phase'].mode().empty else 'Unknown',
        'teams_played': player_data['Team'].unique().tolist(),
        'years_active': player_data['Year'].unique().tolist(),
        'powerplay_matches': len(player_data[player_data['Entry_Over'] <= 6]),
        'death_over_matches': len(player_data[player_data['Entry_Over'] >= 16]),
        'middle_over_matches': len(player_data[(player_data['Entry_Over'] > 6) & (player_data['Entry_Over'] < 16)]),
        'phase_performance': player_data.groupby('Entry_Phase').agg({
            'Final_Strike_Rate': 'mean',
            'Runs': 'mean',
            'Entry_Over': 'count'
        }).to_dict()
    }
    
    return analysis

@st.cache_data
def get_matchup_analysis(bowling_type, df):
    """Analyze player performance against specific bowling types"""
    # This is a simplified version - in real implementation, you'd have bowling data
    # For now, we'll use entry timing as a proxy for different match situations
    
    if bowling_type.lower() == 'spin':
        # Assume spin is more common in middle overs
        relevant_data = df[(df['Entry_Over'] >= 7) & (df['Entry_Over'] <= 15)]
        context = "middle overs (typical spin bowling phase)"
    elif bowling_type.lower() == 'pace':
        # Assume pace is more common in powerplay and death
        relevant_data = df[(df['Entry_Over'] <= 6) | (df['Entry_Over'] >= 16)]
        context = "powerplay and death overs (typical pace bowling phases)"
    else:
        relevant_data = df
        context = "all phases"
    
    top_performers = relevant_data.groupby('Player').agg({
        'Final_Strike_Rate': 'mean',
        'Runs': 'mean',
        'Entry_Over': 'count'
    }).reset_index()
    
    top_performers = top_performers[top_performers['Entry_Over'] >= 3]  # Minimum 3 matches
    top_performers = top_performers.nlargest(10, 'Final_Strike_Rate')
    
    return top_performers, context

@st.cache_data
def load_and_process_entry_data():
    """Load processed ball-by-ball data with entry points already calculated"""
    try:
        # Load processed entry points from ball-by-ball data
        df = pd.read_csv('processed_entry_points_ballbyball.csv')
        
        # Data is already processed with entry points calculated
        # Columns: Player, Team, Match, Year, Entry_Over, Runs, BF, Dots, Fours, Sixes,
        #          Strike_Rate, Dot_Pct, Bnd_Pct, Overs_Played, Exit_Over, 
        #          Innings_Duration, Entry_Phase, Final_Strike_Rate
        
        print(f"✅ Loaded {len(df)} entry points from ball-by-ball data")
        print(f"   Unique players: {df['Player'].nunique()}")
        print(f"   Years: {sorted(df['Year'].dropna().unique())}")
        
        return df
        
    except FileNotFoundError:
        st.error("❌ Processed data file not found. Please run process_ballbyball_data.py first.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_bowling_matchups():
    """Load bowling type matchup data (Pace vs Spin)"""
    try:
        df = pd.read_csv('bowling_type_matchups.csv')
        print(f"✅ Loaded bowling matchups for {df['Batsman'].nunique()} players")
        return df
    except FileNotFoundError:
        st.warning("⚠️ Bowling matchup data not found. Bowling type filtering unavailable.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading bowling matchups: {str(e)}")
        return pd.DataFrame()
        df['Bnd_Pct'] = pd.to_numeric(df['Bnd%'], errors='coerce')
        
        # Extract year from span
        df['Year'] = df['Span⬇'].str.split('-').str[0]
        
        # Calculate actual strike rate where missing
        df.loc[df['Strike_Rate'].isna() & (df['BF'] > 0), 'Strike_Rate'] = (df['Runs'] / df['BF']) * 100
        
        st.info("📊 Raw data loaded. Now calculating true entry points with performance metrics...")
        
        # CRITICAL: Calculate true entry points with progression metrics
        entry_points = df.groupby(['Player', 'Team', 'Match', 'Year']).agg({
            'Over': ['min', 'max', 'count'],  # Entry, exit, overs played
            'Runs': 'sum',  # Total runs in the match
            'BF': 'sum',    # Total balls faced in the match
            'Strike_Rate': 'mean',  # Average strike rate for the match
            'Dot_Pct': 'mean',  # Average dot ball percentage
            'Bnd_Pct': 'mean'   # Average boundary percentage
        }).reset_index()
        
        # Flatten column names
        entry_points.columns = ['Player', 'Team', 'Match', 'Year', 'Entry_Over', 'Exit_Over', 'Overs_Played', 'Runs', 'BF', 'Strike_Rate', 'Dot_Pct', 'Bnd_Pct']
        
        # Calculate innings duration
        entry_points['Innings_Duration'] = entry_points['Exit_Over'] - entry_points['Entry_Over'] + 1
        
        # Create entry phase categories based on TRUE entry over
        entry_points['Entry_Phase'] = entry_points['Entry_Over'].apply(lambda x: 
            'Powerplay (1-6)' if x <= 6 else
            'Middle Overs (7-15)' if x <= 15 else
            'Death Overs (16-20)'
        )
        
        # Recalculate strike rate based on match totals
        entry_points.loc[entry_points['BF'] > 0, 'Match_Strike_Rate'] = (
            entry_points['Runs'] / entry_points['BF']
        ) * 100
        
        # Use match strike rate where available, otherwise use average
        entry_points['Final_Strike_Rate'] = entry_points['Match_Strike_Rate'].fillna(
            entry_points['Strike_Rate']
        )
        
        st.success(f"✅ Calculated {len(entry_points)} true entry points from {len(df)} raw records")
        
        return df, entry_points
        
    except FileNotFoundError:
        st.error("❌ CricViz data file not found!")
        return None, None
    except Exception as e:
        st.error(f"❌ Error processing data: {e}")
        return None, None

# Load data
raw_df, entry_df = load_and_process_entry_data()

if raw_df is None or entry_df is None:
    st.stop()

# Show data processing summary
with st.expander("📊 Data Processing Summary", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Raw Records", f"{len(raw_df):,}")
    with col2:
        st.metric("True Entry Points", f"{len(entry_df):,}")
    with col3:
        st.metric("Unique Players", entry_df['Player'].nunique())
    
    st.markdown("**How Entry Points Are Calculated:**")
    st.markdown("- Each player's **entry point** = minimum over they appeared in each match")
    st.markdown("- **Match performance** = aggregated stats for that player in that match")
    st.markdown("- **Strike rate** = calculated from total runs/balls for the match")

# Sidebar
st.sidebar.header("🎯 Entry Analysis Controls")

# Filters
available_years = sorted(entry_df['Year'].unique())
selected_years = st.sidebar.multiselect(
    "📅 Select Years:",
    available_years,
    default=available_years
)

available_teams = sorted(entry_df['Team'].unique())
selected_teams = st.sidebar.multiselect(
    "🏟️ Select Teams:",
    available_teams,
    default=available_teams[:5] if len(available_teams) > 5 else available_teams
)

min_balls = st.sidebar.slider(
    "⚾ Minimum Balls Faced (per match):",
    1, 50, 10,
    help="Filter matches where player faced minimum balls for reliable analysis"
)

analysis_type = st.sidebar.selectbox(
    "📊 Analysis Type:",
    ["True Entry Analysis", "Entry vs Performance", "Player Entry Patterns", "Team Entry Strategies", "AI Insights"]
)

# Filter data
filtered_df = entry_df[
    (entry_df['Year'].isin(selected_years)) &
    (entry_df['Team'].isin(selected_teams)) &
    (entry_df['BF'] >= min_balls)
].copy()

# Main content
if analysis_type == "True Entry Analysis":
    st.header("⏰ True Player Entry Points Analysis")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Entry distribution by over (TRUE entry points)
            entry_dist = filtered_df['Entry_Over'].value_counts().sort_index().reset_index()
            entry_dist.columns = ['Entry_Over', 'Count']
            
            fig1 = px.bar(
                entry_dist, 
                x='Entry_Over', 
                y='Count',
                title="True Entry Points Distribution",
                labels={'Count': 'Number of Entries', 'Entry_Over': 'Entry Over'},
                color='Count',
                color_continuous_scale='Greens'
            )
            fig1.add_annotation(
                text="Each bar = number of times players entered in that over",
                xref="paper", yref="paper",
                x=0.5, y=-0.15, showarrow=False
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Entry by phase
            phase_dist = filtered_df['Entry_Phase'].value_counts().reset_index()
            phase_dist.columns = ['Phase', 'Count']
            
            fig2 = px.pie(
                phase_dist,
                values='Count',
                names='Phase',
                title="Entry Distribution by Phase",
                color_discrete_sequence=['#2E8B57', '#32CD32', '#228B22']
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Summary statistics
        st.subheader("📊 True Entry Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_entry_over = filtered_df['Entry_Over'].mean()
            st.metric("Average Entry Over", f"{avg_entry_over:.1f}")
        
        with col2:
            most_common_over = filtered_df['Entry_Over'].mode().iloc[0] if not filtered_df['Entry_Over'].mode().empty else 0
            st.metric("Most Common Entry", f"Over {most_common_over}")
        
        with col3:
            early_entries = len(filtered_df[filtered_df['Entry_Over'] <= 6])
            st.metric("Powerplay Entries", f"{early_entries}")
        
        with col4:
            late_entries = len(filtered_df[filtered_df['Entry_Over'] >= 16])
            st.metric("Death Over Entries", f"{late_entries}")
        
        # Detailed entry analysis
        st.subheader("🔍 Entry Over Breakdown with Performance Metrics")
        
        entry_breakdown = filtered_df.groupby('Entry_Over').agg({
            'Player': 'count',
            'Final_Strike_Rate': 'mean',
            'Runs': 'mean',
            'BF': 'mean',
            'Dot_Pct': 'mean',
            'Bnd_Pct': 'mean',
            'Innings_Duration': 'mean'
        }).round(2).reset_index()
        entry_breakdown.columns = ['Entry Over', 'Entries', 'Avg Strike Rate', 'Avg Runs', 'Avg Balls', 'Avg Dot%', 'Avg Bnd%', 'Avg Duration']
        
        st.dataframe(entry_breakdown, use_container_width=True)

elif analysis_type == "Entry vs Performance":
    st.header("⚡ Entry Timing vs Performance Analysis")
    
    if not filtered_df.empty:
        # Remove invalid strike rates
        valid_sr_df = filtered_df[
            filtered_df['Final_Strike_Rate'].notna() & 
            (filtered_df['Final_Strike_Rate'] > 0) &
            (filtered_df['Final_Strike_Rate'] < 500)  # Remove outliers
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Strike rate by entry over
            sr_by_over = valid_sr_df.groupby('Entry_Over').agg({
                'Final_Strike_Rate': ['mean', 'count', 'std']
            }).round(2)
            sr_by_over.columns = ['Avg_SR', 'Count', 'Std_SR']
            sr_by_over = sr_by_over.reset_index()
            sr_by_over = sr_by_over[sr_by_over['Count'] >= 3]  # Minimum 3 entries per over
            
            fig1 = px.line(
                sr_by_over,
                x='Entry_Over',
                y='Avg_SR',
                title="Strike Rate by Entry Over",
                labels={'Avg_SR': 'Average Strike Rate', 'Entry_Over': 'Entry Over'},
                markers=True
            )
            fig1.add_hline(
                y=valid_sr_df['Final_Strike_Rate'].mean(), 
                line_dash="dash", 
                annotation_text=f"Overall Average: {valid_sr_df['Final_Strike_Rate'].mean():.1f}"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Strike rate by phase with error bars
            phase_sr = valid_sr_df.groupby('Entry_Phase').agg({
                'Final_Strike_Rate': ['mean', 'std', 'count']
            }).round(2)
            phase_sr.columns = ['Mean_SR', 'Std_SR', 'Count']
            phase_sr = phase_sr.reset_index()
            
            fig2 = px.bar(
                phase_sr,
                x='Entry_Phase',
                y='Mean_SR',
                error_y='Std_SR',
                title="Strike Rate by Entry Phase",
                labels={'Mean_SR': 'Average Strike Rate', 'Entry_Phase': 'Entry Phase'},
                color='Mean_SR',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Scatter plot: Entry over vs Strike rate
        st.subheader("🎯 Entry Over vs Strike Rate Correlation")
        
        fig3 = px.scatter(
            valid_sr_df,
            x='Entry_Over',
            y='Final_Strike_Rate',
            size='Runs',
            color='Entry_Phase',
            hover_data=['Player', 'Team', 'Runs', 'BF'],
            title="Entry Over vs Strike Rate (Size = Runs scored)",
            labels={'Final_Strike_Rate': 'Strike Rate', 'Entry_Over': 'Entry Over'}
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Performance summary by phase
        st.subheader("📊 Performance Summary by Entry Phase")
        
        performance_summary = valid_sr_df.groupby('Entry_Phase').agg({
            'Final_Strike_Rate': ['mean', 'median', 'std'],
            'Runs': ['mean', 'sum'],
            'BF': 'mean',
            'Player': 'count'
        }).round(2)
        
        # Flatten column names
        performance_summary.columns = [
            'Avg_SR', 'Median_SR', 'Std_SR', 'Avg_Runs', 'Total_Runs', 'Avg_BF', 'Entries'
        ]
        
        st.dataframe(performance_summary, use_container_width=True)

elif analysis_type == "Player Entry Patterns":
    st.header("👤 Individual Player Entry Patterns")
    
    if not filtered_df.empty:
        # Player selection
        available_players = sorted(filtered_df['Player'].unique())
        selected_player = st.selectbox("🏏 Select Player:", available_players)
        
        if selected_player:
            player_data = filtered_df[filtered_df['Player'] == selected_player]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Player summary
                st.subheader(f"📊 {selected_player} Entry Summary")
                
                total_matches = len(player_data)
                avg_entry_over = player_data['Entry_Over'].mean()
                avg_strike_rate = player_data['Final_Strike_Rate'].mean()
                total_runs = player_data['Runs'].sum()
                avg_dot_pct = player_data['Dot_Pct'].mean()
                avg_bnd_pct = player_data['Bnd_Pct'].mean()
                avg_duration = player_data['Innings_Duration'].mean()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Total Matches", total_matches)
                    st.metric("Average Entry Over", f"{avg_entry_over:.1f}")
                    st.metric("Average Strike Rate", f"{avg_strike_rate:.1f}")
                    st.metric("Total Runs", total_runs)
                
                with col_b:
                    st.metric("Avg Dot Ball %", f"{avg_dot_pct:.1f}%")
                    st.metric("Avg Boundary %", f"{avg_bnd_pct:.1f}%")
                    st.metric("Avg Innings Duration", f"{avg_duration:.1f} overs")
                
                # Entry pattern
                entry_pattern = player_data['Entry_Phase'].value_counts()
                st.markdown("**Entry Pattern:**")
                for phase, count in entry_pattern.items():
                    percentage = (count / total_matches) * 100
                    st.write(f"- {phase}: {count} times ({percentage:.1f}%)")
            
            with col2:
                # Performance visualization
                if len(player_data) > 1:
                    fig = px.scatter(
                        player_data,
                        x='Entry_Over',
                        y='Final_Strike_Rate',
                        size='Runs',
                        color='Entry_Phase',
                        title=f"{selected_player} - Entry Over vs Strike Rate",
                        hover_data=['Runs', 'BF', 'Team', 'Year']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Need more data points for visualization")
            
            # Entry over distribution for this player
            st.subheader("📈 Entry Over Distribution")
            
            entry_dist = player_data['Entry_Over'].value_counts().sort_index()
            fig_dist = px.bar(
                x=entry_dist.index,
                y=entry_dist.values,
                title=f"{selected_player} - Entry Over Frequency",
                labels={'x': 'Entry Over', 'y': 'Number of Matches'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Detailed performance table
            st.subheader("📋 Match-by-Match Entry Records")
            display_cols = ['Entry_Over', 'Entry_Phase', 'Runs', 'BF', 'Final_Strike_Rate', 'Dot_Pct', 'Bnd_Pct', 'Innings_Duration', 'Team', 'Year']
            display_data = player_data[display_cols].sort_values('Entry_Over')
            st.dataframe(display_data, use_container_width=True)
            
            # Enhanced Performance Metrics
            st.subheader("📈 Performance Efficiency Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Dot% by entry phase for this player
                if len(player_data['Entry_Phase'].unique()) > 1:
                    phase_dot = player_data.groupby('Entry_Phase')['Dot_Pct'].mean().reset_index()
                    fig_dot = px.bar(
                        phase_dot,
                        x='Entry_Phase',
                        y='Dot_Pct',
                        title=f"{selected_player} - Dot Ball % by Entry Phase",
                        labels={'Dot_Pct': 'Dot Ball %', 'Entry_Phase': 'Entry Phase'},
                        color='Dot_Pct',
                        color_continuous_scale='Reds_r'
                    )
                    st.plotly_chart(fig_dot, use_container_width=True)
                else:
                    st.info("Player has entries in only one phase")
            
            with col2:
                # Boundary% by entry phase for this player
                if len(player_data['Entry_Phase'].unique()) > 1:
                    phase_bnd = player_data.groupby('Entry_Phase')['Bnd_Pct'].mean().reset_index()
                    fig_bnd = px.bar(
                        phase_bnd,
                        x='Entry_Phase',
                        y='Bnd_Pct',
                        title=f"{selected_player} - Boundary % by Entry Phase",
                        labels={'Bnd_Pct': 'Boundary %', 'Entry_Phase': 'Entry Phase'},
                        color='Bnd_Pct',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig_bnd, use_container_width=True)
                else:
                    st.info("Player has entries in only one phase")
            
            # Innings duration analysis for this player
            st.subheader("⏱️ Innings Duration Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Duration distribution for this player
                duration_dist = player_data['Innings_Duration'].value_counts().sort_index().reset_index()
                duration_dist.columns = ['Duration (overs)', 'Count']
                
                fig_dur = px.bar(
                    duration_dist,
                    x='Duration (overs)',
                    y='Count',
                    title=f"{selected_player} - Innings Duration Distribution",
                    labels={'Count': 'Number of Innings'},
                    color='Count',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_dur, use_container_width=True)
            
            with col2:
                # Duration vs Strike Rate for this player
                if len(player_data) > 1:
                    fig_dur_sr = px.scatter(
                        player_data,
                        x='Innings_Duration',
                        y='Final_Strike_Rate',
                        size='Runs',
                        color='Entry_Phase',
                        title=f"{selected_player} - Duration vs Strike Rate",
                        labels={'Innings_Duration': 'Duration (overs)', 'Final_Strike_Rate': 'Strike Rate'},
                        hover_data=['Runs', 'BF', 'Team', 'Year']
                    )
                    st.plotly_chart(fig_dur_sr, use_container_width=True)
                else:
                    st.info("Need more data points for scatter plot")

elif analysis_type == "Team Entry Strategies":
    st.header("🏟️ Team Entry Strategy Analysis")
    
    if not filtered_df.empty:
        # Team-wise entry analysis
        team_analysis = []
        
        for team in selected_teams:
            team_data = filtered_df[filtered_df['Team'] == team]
            if not team_data.empty:
                analysis = {
                    'Team': team,
                    'Total_Entries': len(team_data),
                    'Avg_Entry_Over': team_data['Entry_Over'].mean(),
                    'Avg_Strike_Rate': team_data['Final_Strike_Rate'].mean(),
                    'Powerplay_Entries': len(team_data[team_data['Entry_Over'] <= 6]),
                    'Death_Entries': len(team_data[team_data['Entry_Over'] >= 16]),
                    'Total_Runs': team_data['Runs'].sum(),
                    'Powerplay_Percentage': (len(team_data[team_data['Entry_Over'] <= 6]) / len(team_data)) * 100
                }
                team_analysis.append(analysis)
        
        team_df = pd.DataFrame(team_analysis)
        
        if not team_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Average entry over by team
                fig1 = px.bar(
                    team_df,
                    x='Team',
                    y='Avg_Entry_Over',
                    title="Average Entry Over by Team",
                    color='Avg_Entry_Over',
                    color_continuous_scale='RdYlGn_r'
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Powerplay entry percentage
                fig2 = px.bar(
                    team_df,
                    x='Team',
                    y='Powerplay_Percentage',
                    title="Powerplay Entry Percentage by Team",
                    color='Powerplay_Percentage',
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Team strategy heatmap
            st.subheader("🔥 Team Entry Strategy Heatmap")
            
            # Create heatmap data
            heatmap_data = []
            for team in selected_teams:
                team_data = filtered_df[filtered_df['Team'] == team]
                for over in range(1, 21):
                    over_entries = len(team_data[team_data['Entry_Over'] == over])
                    heatmap_data.append({
                        'Team': team,
                        'Over': over,
                        'Entries': over_entries
                    })
            
            heatmap_df = pd.DataFrame(heatmap_data)
            heatmap_pivot = heatmap_df.pivot(index='Team', columns='Over', values='Entries').fillna(0)
            
            fig3 = px.imshow(
                heatmap_pivot,
                title="Entry Frequency Heatmap (Team vs Over)",
                color_continuous_scale='Greens',
                aspect='auto'
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Summary table
            st.subheader("📊 Team Strategy Summary")
            st.dataframe(team_df.round(2), use_container_width=True)

else:  # AI Insights
    st.header("🧠 ReAct Cricket Strategy Assistant")
    st.caption("Powered by Reasoning + Acting AI methodology")
    
    if ai_model and not filtered_df.empty:
        # Initialize ReAct agent with raw data (it will process internally)
        if "react_agent" not in st.session_state:
            st.session_state.react_agent = create_react_agent(raw_df, ai_model)
        
        # Create a filtered version of the agent for this query
        # This ensures filters are applied without modifying the original agent
        filtered_agent = st.session_state.react_agent
        
        # Apply current filters to the agent's data (non-destructive)
        original_entry_points = filtered_agent.analyzer.entry_points.copy()
        filtered_entry_points = original_entry_points[
            (original_entry_points['Year'].isin(selected_years)) &
            (original_entry_points['Team'].isin(selected_teams)) &
            (original_entry_points['BF'] >= min_balls)
        ]
        
        # Show filter context to user
        st.info(f"🔍 AI analyzing {len(filtered_entry_points)} entry points (filtered by: Years={len(selected_years)}, Teams={len(selected_teams)}, Min Balls={min_balls})")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # ReAct explanation
        with st.expander("🤖 How ReAct AI Works", expanded=False):
            st.markdown("""
            **ReAct (Reasoning + Acting) Methodology:**
            
            1. **🧠 Reason**: AI analyzes your question to understand what data it needs
            2. **🔍 Act**: AI queries the cricket database for specific player/team statistics  
            3. **👀 Observe**: AI examines the data results and identifies patterns
            4. **💡 Reason Again**: AI combines observations with cricket knowledge to give strategic advice
            
            This ensures every recommendation is backed by actual performance data!
            """)
        
        # Quick strategy buttons
        st.subheader("🚀 Quick Strategy Questions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🏏 Hardik vs Spin", help="Analyze Hardik Pandya against spin bowling"):
                question = "When should I play Hardik Pandya against spin bowling? What does his data show?"
                st.session_state.chat_history.append({"role": "user", "content": question})
        
        with col2:
            if st.button("⚡ Death Specialists", help="Find best death over batsmen"):
                question = "Who are the best death over specialists based on entry timing and strike rates?"
                st.session_state.chat_history.append({"role": "user", "content": question})
        
        with col3:
            if st.button("🎯 Powerplay Strategy", help="Optimal powerplay batting approach"):
                question = "What's the optimal powerplay strategy based on player entry patterns?"
                st.session_state.chat_history.append({"role": "user", "content": question})
        
        with col4:
            if st.button("🔄 Middle Overs", help="Best middle overs approach"):
                question = "How should I approach middle overs batting? Which players perform best?"
                st.session_state.chat_history.append({"role": "user", "content": question})
        
        # Chat interface
        st.subheader("💬 Ask Your Cricket Strategy Questions")
        
        # Display chat history with ReAct process visualization
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #2196f3;">
                    <strong>🏏 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show ReAct process if available
                if "react_process" in message:
                    with st.expander(f"🔍 ReAct Process for Question {i//2 + 1}", expanded=False):
                        process = message["react_process"]
                        st.markdown("**🧠 Reasoning:** " + str(process.get("entities", {})))
                        st.markdown("**🔍 Actions Taken:** " + ", ".join(process.get("actions", [])))
                        st.markdown("**👀 Data Observations:** " + process.get("observations", ""))
                
                st.markdown(f"""
                <div style="background: #f1f8e9; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #4caf50;">
                    <strong>🧠 ReAct AI Coach:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_question = st.text_input(
            "Ask me anything about cricket strategy:",
            placeholder="e.g., 'When should I play Hardik Pandya against spin?' or 'Compare Kohli vs Rohit for powerplay'",
            key="cricket_question"
        )
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            send_button = st.button("Send 🚀", type="primary")
        with col2:
            if st.button("Clear Chat 🗑️"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Process user question with ReAct
        if send_button and user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            with st.spinner("🧠 ReAct AI analyzing... (Reasoning → Acting → Observing)"):
                try:
                    # Temporarily apply filters to agent's data
                    original_data = filtered_agent.analyzer.entry_points
                    filtered_agent.analyzer.entry_points = filtered_entry_points
                    
                    # Get answer using ReAct methodology with filtered data
                    answer = filtered_agent.answer_question(user_question)
                    
                    # Restore original data
                    filtered_agent.analyzer.entry_points = original_data
                    
                    # Get the ReAct process details from the last conversation
                    last_conversation = filtered_agent.conversation_history[-1]
                    react_process = {
                        "entities": last_conversation["entities"],
                        "actions": last_conversation["actions"],
                        "observations": str(last_conversation["results"])
                    }
                    
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": answer,
                        "react_process": react_process
                    })
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"ReAct AI Coach error: {e}")
                    # Restore original data on error
                    if 'original_data' in locals():
                        filtered_agent.analyzer.entry_points = original_data
                    # Fallback to simple response
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"I encountered an issue with the ReAct analysis: {e}. Let me try a simpler approach to answer your question."
                    })
        
        # Suggested questions
        if not st.session_state.chat_history:
            st.subheader("💡 Try These ReAct-Powered Questions")
            
            suggestions = [
                "When should I play Hardik Pandya against spin bowling?",
                "Compare Virat Kohli vs Rohit Sharma for powerplay batting",
                "Who are my best death over finishers and when should I use them?",
                "What's the optimal batting order for chasing 180+ runs?",
                "Which players should I deploy in middle overs against spin?",
                "How does MS Dhoni perform in different entry scenarios?",
                "Best strategy for defending low totals in death overs?",
                "Which players adapt best to pressure situations?",
                "Optimal approach against pace vs spin bowling attacks?",
                "How to maximize powerplay advantage with current squad?"
            ]
            
            cols = st.columns(2)
            for i, suggestion in enumerate(suggestions[:8]):  # Show 8 suggestions
                with cols[i % 2]:
                    if st.button(f"💭 {suggestion}", key=f"suggest_{i}"):
                        st.session_state.chat_history.append({"role": "user", "content": suggestion})
                        st.rerun()
        
        # ReAct insights panel
        with st.expander("📊 ReAct Agent Data Access", expanded=False):
            st.markdown("**The ReAct agent can analyze:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Players in Database", filtered_df['Player'].nunique())
                st.metric("Total Match Entries", len(filtered_df))
            
            with col2:
                st.metric("Teams Analyzed", filtered_df['Team'].nunique())
                st.metric("Years of Data", len(filtered_df['Year'].unique()))
            
            with col3:
                st.metric("Entry Phases", 3)
                st.metric("Performance Metrics", "Strike Rate, Runs, Entry Timing")
            
            st.markdown("**ReAct Capabilities:**")
            st.markdown("- 🔍 **Player Analysis**: Detailed stats for any player")
            st.markdown("- 📊 **Phase Performance**: Best players for powerplay/middle/death")
            st.markdown("- ⚔️ **Matchup Analysis**: Performance against spin/pace")
            st.markdown("- 🏟️ **Team Strategies**: Entry patterns and deployment tactics")
            st.markdown("- 📈 **Comparative Analysis**: Head-to-head player comparisons")
    
    else:
        if not ai_model:
            st.warning("🔑 ReAct Cricket Coach requires Gemini API key configuration")
            st.info("Add your GEMINI_API_KEY to unlock ReAct-powered cricket strategy insights!")
            st.markdown("""
            **What you'll get with ReAct AI:**
            - 🧠 **Intelligent Reasoning**: AI understands what data it needs
            - 🔍 **Data-Driven Actions**: Queries specific player/team statistics  
            - 👀 **Pattern Recognition**: Identifies trends in performance data
            - 💡 **Strategic Insights**: Combines data with cricket expertise
            """)
        else:
            st.info("📊 Select data filters to enable ReAct Cricket Coach")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🏏 Corrected Cricket Entry Analysis Dashboard | True Entry Points = Min Over per Player per Match"
    "</div>",
    unsafe_allow_html=True
)