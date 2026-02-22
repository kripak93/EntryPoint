"""
Cricket Entry Analysis Dashboard
Analyzing when players enter and their strike rate performance
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
    <p>Analyzing Player Entry Timing & Strike Rate Performance</p>
</div>
""", unsafe_allow_html=True)

# Initialize AI
@st.cache_resource
def initialize_ai():
    """Initialize Gemini AI"""
    api_key = os.getenv('GEMINI_API_KEY')
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
def load_entry_data():
    """Load CricViz entry analysis data"""
    try:
        df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
        
        # Clean and process data
        df['Strike_Rate'] = pd.to_numeric(df['RR'], errors='coerce')
        df['Runs'] = pd.to_numeric(df['Runs'], errors='coerce')
        df['BF'] = pd.to_numeric(df['BF'], errors='coerce')
        df['Over'] = pd.to_numeric(df['Over'], errors='coerce')
        
        # Extract year from span
        df['Year'] = df['Span⬇'].str.split('-').str[0]
        
        # Create entry phase categories
        df['Entry_Phase'] = df['Over'].apply(lambda x: 
            'Powerplay (1-6)' if x <= 6 else
            'Middle Overs (7-15)' if x <= 15 else
            'Death Overs (16-20)'
        )
        
        # Calculate actual strike rate where missing
        df.loc[df['Strike_Rate'].isna() & (df['BF'] > 0), 'Strike_Rate'] = (df['Runs'] / df['BF']) * 100
        
        return df
    except FileNotFoundError:
        st.error("CricViz data file not found!")
        return None

# Load data
df = load_entry_data()

if df is None:
    st.stop()

# Sidebar
st.sidebar.header("🎯 Entry Analysis Controls")

# Filters
available_years = sorted(df['Year'].unique())
selected_years = st.sidebar.multiselect(
    "📅 Select Years:",
    available_years,
    default=available_years
)

available_teams = sorted(df['Team'].unique())
selected_teams = st.sidebar.multiselect(
    "🏟️ Select Teams:",
    available_teams,
    default=available_teams[:5] if len(available_teams) > 5 else available_teams
)

min_balls = st.sidebar.slider(
    "⚾ Minimum Balls Faced:",
    1, 50, 5,
    help="Filter players with minimum balls faced for reliable analysis"
)

analysis_type = st.sidebar.selectbox(
    "📊 Analysis Type:",
    ["Entry Timing Analysis", "Strike Rate by Entry", "Player Performance", "Team Comparison", "AI Insights"]
)

# Filter data
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Team'].isin(selected_teams)) &
    (df['BF'] >= min_balls)
].copy()

# Main content
if analysis_type == "Entry Timing Analysis":
    st.header("⏰ When Do Players Typically Enter?")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Entry distribution by over
            entry_dist = filtered_df.groupby('Over').agg({
                'Player': 'count',
                'Strike_Rate': 'mean'
            }).reset_index()
            entry_dist.columns = ['Over', 'Player_Count', 'Avg_Strike_Rate']
            
            fig1 = px.bar(
                entry_dist, 
                x='Over', 
                y='Player_Count',
                title="Player Entries by Over",
                labels={'Player_Count': 'Number of Entries', 'Over': 'Over Number'},
                color='Player_Count',
                color_continuous_scale='Greens'
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
        st.subheader("📊 Entry Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_entry_over = filtered_df['Over'].mean()
            st.metric("Average Entry Over", f"{avg_entry_over:.1f}")
        
        with col2:
            most_common_over = filtered_df['Over'].mode().iloc[0] if not filtered_df['Over'].mode().empty else 0
            st.metric("Most Common Entry", f"Over {most_common_over}")
        
        with col3:
            early_entries = len(filtered_df[filtered_df['Over'] <= 6])
            st.metric("Powerplay Entries", f"{early_entries}")
        
        with col4:
            late_entries = len(filtered_df[filtered_df['Over'] >= 16])
            st.metric("Death Over Entries", f"{late_entries}")

elif analysis_type == "Strike Rate by Entry":
    st.header("⚡ Strike Rate Performance by Entry Timing")
    
    if not filtered_df.empty:
        # Remove invalid strike rates
        valid_sr_df = filtered_df[filtered_df['Strike_Rate'].notna() & (filtered_df['Strike_Rate'] > 0)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Strike rate by over
            sr_by_over = valid_sr_df.groupby('Over')['Strike_Rate'].agg(['mean', 'count']).reset_index()
            sr_by_over = sr_by_over[sr_by_over['count'] >= 3]  # Minimum 3 entries per over
            
            fig1 = px.line(
                sr_by_over,
                x='Over',
                y='mean',
                title="Average Strike Rate by Entry Over",
                labels={'mean': 'Average Strike Rate', 'Over': 'Entry Over'},
                markers=True
            )
            fig1.add_hline(y=valid_sr_df['Strike_Rate'].mean(), 
                          line_dash="dash", 
                          annotation_text="Overall Average")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Strike rate by phase
            phase_sr = valid_sr_df.groupby('Entry_Phase')['Strike_Rate'].agg(['mean', 'std', 'count']).reset_index()
            
            fig2 = px.bar(
                phase_sr,
                x='Entry_Phase',
                y='mean',
                error_y='std',
                title="Strike Rate by Entry Phase",
                labels={'mean': 'Average Strike Rate', 'Entry_Phase': 'Entry Phase'},
                color='mean',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed analysis
        st.subheader("🔍 Detailed Strike Rate Analysis")
        
        # Box plot of strike rates by phase
        fig3 = px.box(
            valid_sr_df,
            x='Entry_Phase',
            y='Strike_Rate',
            title="Strike Rate Distribution by Entry Phase",
            points="outliers"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top performers by entry timing
        st.subheader("🏆 Top Performers by Entry Phase")
        
        for phase in valid_sr_df['Entry_Phase'].unique():
            phase_data = valid_sr_df[valid_sr_df['Entry_Phase'] == phase]
            if not phase_data.empty:
                top_performers = phase_data.nlargest(5, 'Strike_Rate')[['Player', 'Team', 'Strike_Rate', 'Runs', 'BF']]
                
                st.markdown(f"**{phase}**")
                st.dataframe(top_performers, use_container_width=True)

elif analysis_type == "Player Performance":
    st.header("👤 Individual Player Entry Analysis")
    
    if not filtered_df.empty:
        # Player selection
        available_players = sorted(filtered_df['Player'].unique())
        selected_player = st.selectbox("🏏 Select Player:", available_players)
        
        if selected_player:
            player_data = filtered_df[filtered_df['Player'] == selected_player]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Player summary
                st.subheader(f"📊 {selected_player} Summary")
                
                total_entries = len(player_data)
                avg_entry_over = player_data['Over'].mean()
                avg_strike_rate = player_data['Strike_Rate'].mean()
                total_runs = player_data['Runs'].sum()
                
                st.metric("Total Entries", total_entries)
                st.metric("Average Entry Over", f"{avg_entry_over:.1f}")
                st.metric("Average Strike Rate", f"{avg_strike_rate:.1f}")
                st.metric("Total Runs", total_runs)
                
                # Entry pattern
                entry_pattern = player_data['Entry_Phase'].value_counts()
                st.markdown("**Entry Pattern:**")
                for phase, count in entry_pattern.items():
                    st.write(f"- {phase}: {count} times")
            
            with col2:
                # Performance visualization
                if len(player_data) > 1:
                    fig = px.scatter(
                        player_data,
                        x='Over',
                        y='Strike_Rate',
                        size='Runs',
                        color='Entry_Phase',
                        title=f"{selected_player} - Strike Rate by Entry Over",
                        hover_data=['Runs', 'BF']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Need more data points for visualization")
            
            # Detailed performance table
            st.subheader("📋 Detailed Performance Records")
            display_cols = ['Over', 'Entry_Phase', 'Runs', 'BF', 'Strike_Rate', 'Team', 'Year']
            st.dataframe(player_data[display_cols].sort_values('Over'), use_container_width=True)

elif analysis_type == "Team Comparison":
    st.header("🏟️ Team Entry Strategy Comparison")
    
    if not filtered_df.empty:
        # Team-wise entry analysis
        team_analysis = []
        
        for team in selected_teams:
            team_data = filtered_df[filtered_df['Team'] == team]
            if not team_data.empty:
                analysis = {
                    'Team': team,
                    'Total_Entries': len(team_data),
                    'Avg_Entry_Over': team_data['Over'].mean(),
                    'Avg_Strike_Rate': team_data['Strike_Rate'].mean(),
                    'Powerplay_Entries': len(team_data[team_data['Over'] <= 6]),
                    'Death_Entries': len(team_data[team_data['Over'] >= 16]),
                    'Total_Runs': team_data['Runs'].sum()
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
                # Strike rate comparison
                fig2 = px.bar(
                    team_df,
                    x='Team',
                    y='Avg_Strike_Rate',
                    title="Average Strike Rate by Team",
                    color='Avg_Strike_Rate',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Team strategy heatmap
            st.subheader("🔥 Team Entry Strategy Heatmap")
            
            # Create heatmap data
            heatmap_data = []
            for team in selected_teams:
                team_data = filtered_df[filtered_df['Team'] == team]
                for over in range(1, 21):
                    over_entries = len(team_data[team_data['Over'] == over])
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
            st.subheader("📊 Team Comparison Summary")
            st.dataframe(team_df.round(2), use_container_width=True)

else:  # AI Insights
    st.header("🧠 AI-Powered Entry Analysis Insights")
    
    if ai_model and not filtered_df.empty:
        # Generate comprehensive analysis
        analysis_summary = {
            'total_entries': len(filtered_df),
            'avg_entry_over': filtered_df['Over'].mean(),
            'avg_strike_rate': filtered_df['Strike_Rate'].mean(),
            'powerplay_percentage': (len(filtered_df[filtered_df['Over'] <= 6]) / len(filtered_df)) * 100,
            'death_percentage': (len(filtered_df[filtered_df['Over'] >= 16]) / len(filtered_df)) * 100,
            'teams_analyzed': len(selected_teams),
            'years_analyzed': len(selected_years)
        }
        
        # Phase-wise performance
        phase_performance = filtered_df.groupby('Entry_Phase').agg({
            'Strike_Rate': 'mean',
            'Player': 'count'
        }).to_dict()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Generate Entry Strategy Insights", type="primary"):
                with st.spinner("🧠 AI analyzing entry patterns..."):
                    prompt = f"""
                    Analyze cricket player entry timing and performance data:
                    
                    ENTRY ANALYSIS DATA:
                    - Total entries analyzed: {analysis_summary['total_entries']}
                    - Average entry over: {analysis_summary['avg_entry_over']:.1f}
                    - Average strike rate: {analysis_summary['avg_strike_rate']:.1f}
                    - Powerplay entries: {analysis_summary['powerplay_percentage']:.1f}%
                    - Death over entries: {analysis_summary['death_percentage']:.1f}%
                    - Teams analyzed: {analysis_summary['teams_analyzed']}
                    - Years covered: {analysis_summary['years_analyzed']}
                    
                    PHASE PERFORMANCE:
                    {phase_performance}
                    
                    Provide strategic insights about:
                    1. Optimal entry timing for different player roles
                    2. Strike rate patterns by entry phase
                    3. Team strategy recommendations
                    4. Risk vs reward analysis of entry timing
                    5. Tactical advantages of early vs late entries
                    """
                    
                    try:
                        response = ai_model.generate_content(prompt)
                        st.markdown(f"""
                        <div class="insight-card">
                            <h3>🎯 Entry Strategy Insights</h3>
                            <p>{response.text}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"AI analysis failed: {e}")
        
        with col2:
            if st.button("📊 Analyze Player Role Optimization", type="secondary"):
                with st.spinner("🧠 AI analyzing player roles..."):
                    # Get top performers by phase
                    top_performers = {}
                    for phase in filtered_df['Entry_Phase'].unique():
                        phase_data = filtered_df[filtered_df['Entry_Phase'] == phase]
                        if not phase_data.empty:
                            top_performers[phase] = phase_data.nlargest(3, 'Strike_Rate')[['Player', 'Strike_Rate']].to_dict('records')
                    
                    prompt = f"""
                    Analyze player role optimization based on entry timing:
                    
                    TOP PERFORMERS BY PHASE:
                    {top_performers}
                    
                    OVERALL STATISTICS:
                    {analysis_summary}
                    
                    Provide recommendations for:
                    1. Which players should enter in powerplay vs death overs
                    2. Role-specific entry timing strategies
                    3. Player development suggestions based on entry performance
                    4. Team composition optimization
                    5. Match situation-specific entry decisions
                    """
                    
                    try:
                        response = ai_model.generate_content(prompt)
                        st.markdown(f"""
                        <div class="entry-card">
                            <h3>👤 Player Role Optimization</h3>
                            <p>{response.text}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"AI analysis failed: {e}")
        
        # Quick insights
        st.subheader("⚡ Quick Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💡 Entry Timing Tips"):
                st.info(f"""
                **Key Findings:**
                - Average entry: Over {analysis_summary['avg_entry_over']:.1f}
                - {analysis_summary['powerplay_percentage']:.1f}% enter in powerplay
                - {analysis_summary['death_percentage']:.1f}% enter in death overs
                """)
        
        with col2:
            if st.button("📈 Performance Trends"):
                best_phase = filtered_df.groupby('Entry_Phase')['Strike_Rate'].mean().idxmax()
                st.success(f"""
                **Best Performance:**
                - Highest SR: {best_phase}
                - Overall avg SR: {analysis_summary['avg_strike_rate']:.1f}
                """)
        
        with col3:
            if st.button("🎯 Strategy Recommendations"):
                st.warning(f"""
                **Strategic Focus:**
                - Optimize {best_phase} entries
                - Develop death over specialists
                - Balance entry timing
                """)
    else:
        if not ai_model:
            st.warning("🔑 AI features require Gemini API key configuration")
        else:
            st.info("📊 Select data filters to enable AI analysis")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🏏 Cricket Entry Analysis Dashboard | Powered by CricViz Data & AI Analytics"
    "</div>",
    unsafe_allow_html=True
)