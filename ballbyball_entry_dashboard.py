"""
Cricket Entry Analysis Dashboard - Ball-by-Ball Data
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

load_dotenv()

st.set_page_config(
    page_title="Cricket Entry Analysis Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    .filter-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_ai():
    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass
    if not api_key:
        load_dotenv(override=True)
        api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        _ = model.generate_content("test")
        return model
    except Exception as e:
        st.error(f"AI initialization error: {e}")
        return None

@st.cache_data(ttl=60)
def load_entry_data():
    try:
        df = pd.read_csv('processed_entry_points_ballbyball.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Run process_ballbyball_data.py first to generate data")
        return pd.DataFrame()

@st.cache_data
def load_bowling_matchups():
    try:
        return pd.read_csv('bowling_type_matchups.csv')
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_ball_position_data():
    try:
        return pd.read_csv('ball_position_analysis.csv')
    except FileNotFoundError:
        return pd.DataFrame()

entry_df = load_entry_data()
bowling_df = load_bowling_matchups()
ball_position_df = load_ball_position_data()

if entry_df.empty:
    st.stop()

st.markdown('<div class="main-header"><h1>🏏 Cricket Entry Analysis Dashboard</h1><p>Ball-by-Ball Data Analysis</p></div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Entry Points", f"{len(entry_df):,}")
with col2:
    st.metric("Unique Players", entry_df['Player'].nunique())
with col3:
    st.metric("Matches", entry_df['Match'].nunique())
with col4:
    st.metric("Competitions", entry_df['Competition'].nunique() if 'Competition' in entry_df.columns else 'N/A')
with col5:
    st.metric("Years", f"{entry_df['Year'].min()}-{entry_df['Year'].max()}")

tab1, tab2, tab3 = st.tabs(["📊 General Analysis", "🎯 Ball Position Analysis", "🤖 AI Insights"])

# ─── TAB 1: GENERAL ANALYSIS (ball-by-ball) ──────────────────────────────────
with tab1:
    st.header("📊 Entry Point Analysis")

    # ── FILTERS ──────────────────────────────────────────────────────────────
    with st.expander("🎯 Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)

        # Pre-filter data by competition to cascade into Players/Teams
        _ga_comp_df = ball_position_df.copy() if not ball_position_df.empty else pd.DataFrame()

        with fc1:
            ga_competitions = st.multiselect(
                "🏆 Competition",
                sorted(ball_position_df['Competition'].dropna().unique()) if not ball_position_df.empty and 'Competition' in ball_position_df.columns else [],
                default=sorted(ball_position_df['Competition'].dropna().unique()) if not ball_position_df.empty and 'Competition' in ball_position_df.columns else [],
                key="ga_competitions"
            )
            # Cascade: filter by selected competitions
            if ga_competitions and not _ga_comp_df.empty and 'Competition' in _ga_comp_df.columns:
                _ga_comp_df = _ga_comp_df[_ga_comp_df['Competition'].isin(ga_competitions)]

            ga_players = st.multiselect(
                "👤 Batters",
                sorted(_ga_comp_df['Batsman'].dropna().unique()) if not _ga_comp_df.empty else [],
                default=[],
                key="ga_players"
            )
            ga_over_slabs = st.multiselect(
                "🎯 Over Slabs",
                ["1-3", "4-6", "7-10", "11-14", "15-17", "18-20"],
                default=["1-3", "4-6", "7-10", "11-14", "15-17", "18-20"],
                key="ga_over_slabs"
            )

        with fc2:
            ga_teams = st.multiselect(
                "🏟️ Team",
                sorted(_ga_comp_df['Team'].dropna().unique()) if not _ga_comp_df.empty and 'Team' in _ga_comp_df.columns else [],
                default=[],
                key="ga_teams"
            )
            ga_venues = st.multiselect(
                "🏟️ Venue",
                sorted(_ga_comp_df['Ground_Name'].dropna().unique()) if not _ga_comp_df.empty and 'Ground_Name' in _ga_comp_df.columns else [],
                default=[],
                key="ga_venues"
            )

        with fc3:
            ga_bowl_type = st.multiselect(
                "🎾 Bowling Type",
                ["Pace", "Spin"],
                default=["Pace", "Spin"],
                key="ga_bowl_type"
            )
            # Bowling spec mapping
            bowl_spec_map = {
                "RAF (Right Arm Fast)": "right pace",
                "LAF (Left Arm Fast)": "left pace",
                "RAOS (Off Spin)": "off break",
                "RALS (Leg Spin)": "leg break",
                "LAO (Left Arm Orthodox)": "left orthodox",
                "LACM (Left Arm Chinaman)": "left unorthodox"
            }
            ga_bowl_spec = st.multiselect(
                "🎾 Bowling Spec",
                list(bowl_spec_map.keys()),
                default=[],
                key="ga_bowl_spec"
            )

        with fc4:
            ga_years = st.multiselect(
                "📅 Year",
                sorted(ball_position_df['Year'].dropna().unique()) if not ball_position_df.empty else [],
                default=sorted(ball_position_df['Year'].dropna().unique()) if not ball_position_df.empty else [],
                key="ga_years"
            )
            if not ball_position_df.empty and 'Date' in ball_position_df.columns:
                dates = pd.to_datetime(ball_position_df['Date'], errors='coerce').dropna()
                if not dates.empty:
                    ga_date_range = st.date_input(
                        "📅 Date Range",
                        value=(dates.min().date(), dates.max().date()),
                        min_value=dates.min().date(),
                        max_value=dates.max().date(),
                        key="ga_date_range"
                    )
                else:
                    ga_date_range = None
            else:
                ga_date_range = None

    # ── APPLY FILTERS ────────────────────────────────────────────────────────
    if ball_position_df.empty:
        st.warning("Ball position data not loaded. Run process_ball_position_data.py first.")
        st.stop()

    ga_df = ball_position_df.copy()

    # Competition
    if ga_competitions and 'Competition' in ga_df.columns:
        ga_df = ga_df[ga_df['Competition'].isin(ga_competitions)]
    # Year
    if ga_years:
        ga_df = ga_df[ga_df['Year'].isin(ga_years)]
    # Team
    if ga_teams and 'Team' in ga_df.columns:
        ga_df = ga_df[ga_df['Team'].isin(ga_teams)]
    # Over slabs
    if ga_over_slabs and 'Over_Slab' in ga_df.columns:
        ga_df = ga_df[ga_df['Over_Slab'].isin(ga_over_slabs)]
    # Venue
    if ga_venues and 'Ground_Name' in ga_df.columns:
        ga_df = ga_df[ga_df['Ground_Name'].isin(ga_venues)]
    # Bowling type
    if ga_bowl_type and 'Bowling_Type' in ga_df.columns:
        ga_df = ga_df[ga_df['Bowling_Type'].isin(ga_bowl_type)]
    # Bowling spec (uses Technique column from raw data)
    if ga_bowl_spec and 'Technique' in ga_df.columns:
        selected_techniques = [bowl_spec_map[s] for s in ga_bowl_spec]
        ga_df = ga_df[ga_df['Technique'].isin(selected_techniques)]
    # Date range
    if ga_date_range and 'Date' in ga_df.columns and len(ga_date_range) == 2:
        ga_df = ga_df[
            (pd.to_datetime(ga_df['Date']).dt.date >= ga_date_range[0]) &
            (pd.to_datetime(ga_df['Date']).dt.date <= ga_date_range[1])
        ]
    # Players (applied last so metrics show filtered context)
    if ga_players:
        ga_df = ga_df[ga_df['Batsman'].isin(ga_players)]

    st.caption(f"Showing {len(ga_df):,} balls | {ga_df['Batsman'].nunique()} players | {ga_df['Match'].nunique()} matches")

    if ga_df.empty:
        st.warning("No data matches the selected filters.")
    else:
        # ── AGGREGATE PER BATTER ─────────────────────────────────────────────
        def build_batter_stats(df):
            """Aggregate ball-by-ball data into per-batter metrics."""
            g = df.groupby('Batsman').agg(
                Balls=('Runs_This_Ball', 'count'),
                Runs=('Runs_This_Ball', 'sum'),
                Dots=('Is_Dot', 'sum'),
                Boundaries=('Is_Boundary', 'sum'),
                Fours=('Is_Four', 'sum'),
                Sixes=('Is_Six', 'sum'),
                Innings=('Match', 'nunique'),
            ).reset_index()

            g['Strike_Rate'] = (g['Runs'] / g['Balls'] * 100).round(1)
            g['Dot_Pct'] = (g['Dots'] / g['Balls'] * 100).round(1)
            g['Boundary_Pct'] = (g['Boundaries'] / g['Balls'] * 100).round(1)
            g['Balls_Per_Boundary'] = (g['Balls'] / g['Boundaries'].replace(0, np.nan)).round(1)
            g['Strike_Rotation_Pct'] = (
                ((g['Balls'] - g['Dots'] - g['Boundaries']) / g['Balls']) * 100
            ).round(1)
            g['Avg_BF'] = (g['Balls'] / g['Innings']).round(1)
            return g

        batter_stats = build_batter_stats(ga_df)

        # ── SUMMARY METRICS ──────────────────────────────────────────────────
        total_balls = ga_df['Runs_This_Ball'].count()
        total_runs = ga_df['Runs_This_Ball'].sum()
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Avg SR", f"{(total_runs / total_balls * 100):.1f}" if total_balls else "N/A")
        m2.metric("Dot %", f"{(ga_df['Is_Dot'].sum() / total_balls * 100):.1f}%" if total_balls else "N/A")
        m3.metric("Boundary %", f"{(ga_df['Is_Boundary'].sum() / total_balls * 100):.1f}%" if total_balls else "N/A")
        m4.metric("Balls/Boundary", f"{(total_balls / ga_df['Is_Boundary'].sum()):.1f}" if ga_df['Is_Boundary'].sum() else "N/A")
        m5.metric("Strike Rotation %", f"{((total_balls - ga_df['Is_Dot'].sum() - ga_df['Is_Boundary'].sum()) / total_balls * 100):.1f}%" if total_balls else "N/A")

        # ── BATTER COMPARISON TABLE ──────────────────────────────────────────
        st.subheader("📋 Batter Comparison")

        display_stats = batter_stats[batter_stats['Balls'] >= 10].sort_values('Strike_Rate', ascending=False)
        display_cols = ['Batsman', 'Innings', 'Balls', 'Runs', 'Strike_Rate', 'Dot_Pct',
                        'Boundary_Pct', 'Balls_Per_Boundary', 'Strike_Rotation_Pct', 'Avg_BF',
                        'Fours', 'Sixes']
        display_rename = {
            'Batsman': 'Player', 'Strike_Rate': 'SR', 'Dot_Pct': 'Dot%',
            'Boundary_Pct': 'Bnd%', 'Balls_Per_Boundary': 'Balls/Bnd',
            'Strike_Rotation_Pct': 'Rotation%', 'Avg_BF': 'Avg BF'
        }
        st.dataframe(
            display_stats[display_cols].rename(columns=display_rename).reset_index(drop=True),
            use_container_width=True
        )

        # ── SR BY EACH BALL IN OVER ──────────────────────────────────────────
        st.subheader("📊 Strike Rate by Ball in Over")

        if ga_players:
            sr_ball = ga_df.groupby(['Batsman', 'Ball_Num']).agg(
                Runs=('Runs_This_Ball', 'sum'), Balls=('Runs_This_Ball', 'count')
            ).reset_index()
            sr_ball['SR'] = (sr_ball['Runs'] / sr_ball['Balls'] * 100).round(1)
            fig = px.bar(sr_ball, x='Ball_Num', y='SR', color='Batsman', barmode='group',
                         title="Strike Rate by Ball Number in Over",
                         labels={'Ball_Num': 'Ball in Over', 'SR': 'Strike Rate'})
        else:
            sr_ball = ga_df.groupby('Ball_Num').agg(
                Runs=('Runs_This_Ball', 'sum'), Balls=('Runs_This_Ball', 'count')
            ).reset_index()
            sr_ball['SR'] = (sr_ball['Runs'] / sr_ball['Balls'] * 100).round(1)
            fig = px.bar(sr_ball, x='Ball_Num', y='SR',
                         title="Strike Rate by Ball Number in Over",
                         labels={'Ball_Num': 'Ball in Over', 'SR': 'Strike Rate'},
                         color='SR', color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)

        # ── SR BY EACH OVER ──────────────────────────────────────────────────
        st.subheader("📊 Strike Rate by Over")

        if ga_players:
            sr_over = ga_df.groupby(['Batsman', 'Over_Num']).agg(
                Runs=('Runs_This_Ball', 'sum'), Balls=('Runs_This_Ball', 'count')
            ).reset_index()
            sr_over['SR'] = (sr_over['Runs'] / sr_over['Balls'] * 100).round(1)
            fig = px.line(sr_over, x='Over_Num', y='SR', color='Batsman',
                          title="Strike Rate by Over",
                          labels={'Over_Num': 'Over', 'SR': 'Strike Rate'},
                          markers=True)
        else:
            sr_over = ga_df.groupby('Over_Num').agg(
                Runs=('Runs_This_Ball', 'sum'), Balls=('Runs_This_Ball', 'count')
            ).reset_index()
            sr_over['SR'] = (sr_over['Runs'] / sr_over['Balls'] * 100).round(1)
            fig = px.line(sr_over, x='Over_Num', y='SR',
                          title="Strike Rate by Over",
                          labels={'Over_Num': 'Over', 'SR': 'Strike Rate'},
                          markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # ── PERFORMANCE BY OVER SLAB ─────────────────────────────────────────
        st.subheader("📈 Performance by Over Slab")

        if ga_players:
            slab_stats = ga_df.groupby(['Batsman', 'Over_Slab']).agg(
                Balls=('Runs_This_Ball', 'count'),
                Runs=('Runs_This_Ball', 'sum'),
                Dots=('Is_Dot', 'sum'),
                Boundaries=('Is_Boundary', 'sum')
            ).reset_index()
            slab_stats['SR'] = (slab_stats['Runs'] / slab_stats['Balls'] * 100).round(1)
            slab_stats['Dot%'] = (slab_stats['Dots'] / slab_stats['Balls'] * 100).round(1)
            slab_stats['Bnd%'] = (slab_stats['Boundaries'] / slab_stats['Balls'] * 100).round(1)
            slab_stats['Balls/Bnd'] = (slab_stats['Balls'] / slab_stats['Boundaries'].replace(0, np.nan)).round(1)
            st.dataframe(slab_stats.rename(columns={'Batsman': 'Player'}).sort_values(['Player', 'Over_Slab']),
                         use_container_width=True)
        else:
            slab_stats = ga_df.groupby('Over_Slab').agg(
                Balls=('Runs_This_Ball', 'count'),
                Runs=('Runs_This_Ball', 'sum'),
                Dots=('Is_Dot', 'sum'),
                Boundaries=('Is_Boundary', 'sum')
            ).reset_index()
            slab_stats['SR'] = (slab_stats['Runs'] / slab_stats['Balls'] * 100).round(1)
            slab_stats['Dot%'] = (slab_stats['Dots'] / slab_stats['Balls'] * 100).round(1)
            slab_stats['Bnd%'] = (slab_stats['Boundaries'] / slab_stats['Balls'] * 100).round(1)
            slab_stats['Balls/Bnd'] = (slab_stats['Balls'] / slab_stats['Boundaries'].replace(0, np.nan)).round(1)
            st.dataframe(slab_stats, use_container_width=True)


# ─── TAB 2: BALL POSITION ANALYSIS (unchanged) ──────────────────────────────
with tab2:
    st.header("🎯 Ball Position Analysis")
    st.info("💡 Analyze player performance by ball position in over (1-6) and Required Run Rate")

    if ball_position_df.empty:
        st.warning("Ball position data not loaded. Run process_ball_position_data.py first.")
    else:
        # Sidebar-style filters kept inline here
        available_years_bp = sorted(ball_position_df['Year'].dropna().unique()) if 'Year' in ball_position_df.columns else []
        available_teams_bp = sorted(ball_position_df['Team'].dropna().unique()) if 'Team' in ball_position_df.columns else []

        with st.expander("🎯 Filters", expanded=False):
            # Pre-filter by competition for cascading
            _bp_comp_df = ball_position_df.copy()

            bpf1, bpf2, bpf3 = st.columns(3)
            with bpf1:
                bp_competitions = st.multiselect("🏆 Competition",
                    sorted(ball_position_df['Competition'].dropna().unique()) if 'Competition' in ball_position_df.columns else [],
                    default=sorted(ball_position_df['Competition'].dropna().unique()) if 'Competition' in ball_position_df.columns else [],
                    key="bp_competitions")
                if bp_competitions and 'Competition' in _bp_comp_df.columns:
                    _bp_comp_df = _bp_comp_df[_bp_comp_df['Competition'].isin(bp_competitions)]
                bp_years = st.multiselect("📅 Years", sorted(_bp_comp_df['Year'].dropna().unique()) if 'Year' in _bp_comp_df.columns else [], default=sorted(_bp_comp_df['Year'].dropna().unique()) if 'Year' in _bp_comp_df.columns else [], key="bp_years")
                bp_teams = st.multiselect("🏟️ Teams", sorted(_bp_comp_df['Team'].dropna().unique()) if 'Team' in _bp_comp_df.columns else [], default=[], key="bp_teams")
            with bpf2:
                bp_players = st.multiselect("👤 Players", sorted(_bp_comp_df['Batsman'].dropna().unique()) if 'Batsman' in _bp_comp_df.columns else [], default=[], key="bp_players")
                if 'Ground_Name' in _bp_comp_df.columns:
                    bp_venues = st.multiselect("🏟️ Venues", sorted(_bp_comp_df['Ground_Name'].dropna().unique()), default=[], key="bp_venues")
                else:
                    bp_venues = []
            with bpf3:
                bp_bowling = st.selectbox("🎾 Bowling Type", ["All", "Pace", "Spin"], key="bp_bowling")
                if 'Over_Slab' in ball_position_df.columns:
                    over_slabs = sorted(ball_position_df['Over_Slab'].dropna().unique())
                    bp_over_slabs = st.multiselect("🎯 Over Slabs", over_slabs, default=over_slabs, key="bp_over_slabs")
                else:
                    bp_over_slabs = []

        # Build filter conditions
        bp_conditions = []
        if bp_competitions and 'Competition' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Competition'].isin(bp_competitions))
        if bp_years and 'Year' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Year'].isin(bp_years))
        if bp_teams and 'Team' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Team'].isin(bp_teams))
        if bp_players and 'Batsman' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Batsman'].isin(bp_players))
        if bp_venues and 'Ground_Name' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Ground_Name'].isin(bp_venues))
        if bp_over_slabs and 'Over_Slab' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Over_Slab'].isin(bp_over_slabs))
        if bp_bowling != "All" and 'Bowling_Type' in ball_position_df.columns:
            bp_conditions.append(ball_position_df['Bowling_Type'] == bp_bowling)

        bp_filtered = ball_position_df.copy()
        for cond in bp_conditions:
            bp_filtered = bp_filtered[cond]

        chase_bp = bp_filtered[bp_filtered['RRR_Range'] != 'No RRR'].copy() if 'RRR_Range' in bp_filtered.columns else bp_filtered.copy()

        if not chase_bp.empty:
            st.markdown("**📊 Filtered Data Summary:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Balls", f"{len(chase_bp):,}")
            with col2:
                st.metric("Unique Players", chase_bp['Batsman'].nunique() if 'Batsman' in chase_bp.columns else 'N/A')
            with col3:
                st.metric("Matches", chase_bp['Match'].nunique() if 'Match' in chase_bp.columns else 'N/A')
            with col4:
                if 'Ground_Name' in chase_bp.columns:
                    st.metric("Venues", chase_bp['Ground_Name'].nunique())
                else:
                    st.metric("Years", chase_bp['Year'].nunique() if 'Year' in chase_bp.columns else 'N/A')

            st.markdown("**🎯 Performance Metrics:**")
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
                if 'Bowling_Type' in chase_bp.columns:
                    pace_pct = (len(chase_bp[chase_bp['Bowling_Type'] == 'Pace']) / len(chase_bp) * 100)
                    st.metric("Pace %", f"{pace_pct:.1f}%")
                else:
                    st.metric("Avg Runs/Ball", f"{(total_runs / total_balls):.2f}")

            st.subheader("👤 Player Performance by Ball Position, RRR & Entry Phase")

            col1, col2, col3 = st.columns(3)
            with col1:
                selected_ball_pos = st.multiselect(
                    "Ball Position:",
                    ['Early (1-2)', 'Middle (3-4)', 'Late (5-6)'],
                    default=['Late (5-6)'],
                    key="bp_ball_pos"
                )
            with col2:
                selected_rrr = st.multiselect(
                    "RRR Range:",
                    ['0-6 RPO', '6-9 RPO', '9-12 RPO', '12-15 RPO', '15+ RPO'],
                    default=['12-15 RPO', '15+ RPO'],
                    key="bp_rrr"
                )
            with col3:
                available_entry_phases = sorted(chase_bp['Entry_Phase'].unique()) if 'Entry_Phase' in chase_bp.columns else []
                selected_entry_phase = st.multiselect(
                    "Entry Phase:",
                    available_entry_phases,
                    default=available_entry_phases,
                    key="bp_entry_phase"
                )

            chase_bp_filtered = chase_bp[chase_bp['Entry_Phase'].isin(selected_entry_phase)].copy() if selected_entry_phase else chase_bp.copy()

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
            player_bp = player_bp[player_bp['Balls'] >= 5]

            filtered_bp = player_bp[
                (player_bp['Ball_Position'].isin(selected_ball_pos)) &
                (player_bp['RRR_Range'].isin(selected_rrr))
            ]

            if not filtered_bp.empty:
                sort_by = st.radio("Sort by:", ["Strike Rate", "Boundary %", "Total Balls"], horizontal=True, key="bp_sort")
                sort_map = {"Strike Rate": "Strike_Rate", "Boundary %": "Boundary_Pct", "Total Balls": "Balls"}
                filtered_bp = filtered_bp.sort_values(sort_map[sort_by], ascending=False)
                st.dataframe(filtered_bp.head(20), use_container_width=True)

                # AI insights
                st.markdown("---")
                st.subheader("🤖 AI Expert Analysis")
                ai_model = initialize_ai()

                if ai_model is not None:
                    if st.button("🔍 Generate Expert Insights", key="ball_position_ai"):
                        with st.spinner("Analyzing patterns and trends..."):
                            try:
                                top_performers = filtered_bp.head(15)
                                total_balls = filtered_bp['Balls'].sum()
                                total_runs = filtered_bp['Runs'].sum()
                                avg_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
                                total_boundaries = filtered_bp['Boundaries'].sum()
                                total_dots = filtered_bp['Dots'].sum()
                                avg_boundary_pct = (total_boundaries / total_balls * 100) if total_balls > 0 else 0
                                avg_dot_pct = (total_dots / total_balls * 100) if total_balls > 0 else 0

                                ball_pos_analysis = filtered_bp.groupby('Ball_Position').agg(
                                    Runs=('Runs', 'sum'), Balls=('Balls', 'sum'), Boundaries=('Boundaries', 'sum')
                                ).reset_index()
                                ball_pos_analysis['Strike_Rate'] = (ball_pos_analysis['Runs'] / ball_pos_analysis['Balls'] * 100).round(1)
                                ball_pos_analysis['Boundary_Pct'] = (ball_pos_analysis['Boundaries'] / ball_pos_analysis['Balls'] * 100).round(1)

                                early_ball_specialists = filtered_bp[filtered_bp['Ball_Position'] == 'Early (1-2)'].nlargest(5, 'Strike_Rate')
                                late_ball_specialists = filtered_bp[filtered_bp['Ball_Position'] == 'Late (5-6)'].nlargest(5, 'Strike_Rate')

                                context = f"""You are an expert cricket analyst. Analyze this IPL ball position data.

SCOPE: Ball Positions: {', '.join(selected_ball_pos)} | RRR: {', '.join(selected_rrr)} | Entry Phases: {', '.join(selected_entry_phase)}
Dataset: {total_balls:,} balls

METRICS: SR={avg_sr:.1f}, Boundary%={avg_boundary_pct:.1f}%, Dot%={avg_dot_pct:.1f}%

BALL POSITION BREAKDOWN:
{ball_pos_analysis.to_string()}

TOP PERFORMERS:
{top_performers[['Player', 'Entry_Phase', 'Ball_Position', 'RRR_Range', 'Balls', 'Strike_Rate', 'Boundary_Pct']].to_string(index=False)}

EARLY BALL SPECIALISTS: {early_ball_specialists[['Player', 'Strike_Rate', 'Boundary_Pct']].to_string(index=False) if not early_ball_specialists.empty else 'No data'}
LATE BALL SPECIALISTS: {late_ball_specialists[['Player', 'Strike_Rate', 'Boundary_Pct']].to_string(index=False) if not late_ball_specialists.empty else 'No data'}

Provide tactical insights: player archetypes, deployment recommendations, pressure situation analysis."""

                                response = ai_model.generate_content(context)
                                st.markdown(response.text)
                            except Exception as e:
                                st.error(f"Error generating insights: {e}")
                else:
                    st.info("💡 Configure GEMINI_API_KEY in .env to enable AI insights")

                st.markdown("---")
                st.subheader("📊 Performance Heatmaps")
                col1, col2 = st.columns(2)

                with col1:
                    pivot_sr_data = player_bp.groupby(['Ball_Position', 'RRR_Range']).agg(
                        Runs=('Runs', 'sum'), Balls=('Balls', 'sum')
                    ).reset_index()
                    pivot_sr_data['Strike_Rate'] = (pivot_sr_data['Runs'] / pivot_sr_data['Balls'] * 100).round(1)
                    pivot_sr_wide = pivot_sr_data.pivot(index='Ball_Position', columns='RRR_Range', values='Strike_Rate')
                    fig = px.imshow(pivot_sr_wide, title="Strike Rate by Ball Position & RRR",
                                    color_continuous_scale='RdYlGn', aspect="auto")
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    pivot_bnd_data = player_bp.groupby(['Ball_Position', 'RRR_Range']).agg(
                        Boundaries=('Boundaries', 'sum'), Balls=('Balls', 'sum')
                    ).reset_index()
                    pivot_bnd_data['Boundary_Pct'] = (pivot_bnd_data['Boundaries'] / pivot_bnd_data['Balls'] * 100).round(1)
                    pivot_bnd_wide = pivot_bnd_data.pivot(index='Ball_Position', columns='RRR_Range', values='Boundary_Pct')
                    fig = px.imshow(pivot_bnd_wide, title="Boundary % by Ball Position & RRR",
                                    color_continuous_scale='Blues', aspect="auto")
                    st.plotly_chart(fig, use_container_width=True)

                # Individual player deep-dive
                st.subheader("🔍 Individual Player Analysis")
                bp_player_list = sorted(player_bp['Player'].unique())
                bp_selected_player = st.selectbox("Select Player:", bp_player_list, key="bp_player_select")

                if bp_selected_player:
                    player_data = player_bp[player_bp['Player'] == bp_selected_player]

                    if not player_data.empty:
                        st.markdown(f"### {bp_selected_player} - Ball Position Performance")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Balls", int(player_data['Balls'].sum()))
                        with col2:
                            avg_sr = (player_data['Runs'].sum() / player_data['Balls'].sum() * 100)
                            st.metric("Overall SR", f"{avg_sr:.1f}")
                        with col3:
                            avg_bnd = (player_data['Boundaries'].sum() / player_data['Balls'].sum() * 100)
                            st.metric("Boundary %", f"{avg_bnd:.1f}%")
                        with col4:
                            st.metric("Entry Phases", len(player_data['Entry_Phase'].unique()))

                        entry_summary = player_data.groupby('Entry_Phase').agg(
                            Balls=('Balls', 'sum'), Runs=('Runs', 'sum'), Boundaries=('Boundaries', 'sum')
                        ).reset_index()
                        entry_summary['Strike_Rate'] = (entry_summary['Runs'] / entry_summary['Balls'] * 100).round(1)
                        entry_summary['Boundary_Pct'] = (entry_summary['Boundaries'] / entry_summary['Balls'] * 100).round(1)
                        st.dataframe(entry_summary, use_container_width=True)

                        # AI player profile
                        st.markdown("---")
                        st.markdown("#### 🤖 Expert Player Profile")
                        if ai_model is not None:
                            if st.button(f"🔍 Generate Expert Analysis for {bp_selected_player}", key=f"player_ai_{bp_selected_player}"):
                                with st.spinner(f"Building tactical profile for {bp_selected_player}..."):
                                    try:
                                        total_balls = player_data['Balls'].sum()
                                        total_runs = player_data['Runs'].sum()
                                        overall_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
                                        overall_bnd = (player_data['Boundaries'].sum() / total_balls * 100) if total_balls > 0 else 0

                                        ball_pos_profile = player_data.groupby('Ball_Position').agg(
                                            Balls=('Balls', 'sum'), Runs=('Runs', 'sum'), Boundaries=('Boundaries', 'sum')
                                        ).reset_index()
                                        ball_pos_profile['Strike_Rate'] = (ball_pos_profile['Runs'] / ball_pos_profile['Balls'] * 100).round(1)
                                        ball_pos_profile['Boundary_Pct'] = (ball_pos_profile['Boundaries'] / ball_pos_profile['Balls'] * 100).round(1)

                                        rrr_profile = player_data.groupby('RRR_Range').agg(
                                            Balls=('Balls', 'sum'), Runs=('Runs', 'sum'), Boundaries=('Boundaries', 'sum')
                                        ).reset_index()
                                        rrr_profile['Strike_Rate'] = (rrr_profile['Runs'] / rrr_profile['Balls'] * 100).round(1)
                                        rrr_profile['Boundary_Pct'] = (rrr_profile['Boundaries'] / rrr_profile['Balls'] * 100).round(1)

                                        high_pressure = player_data[player_data['RRR_Range'].isin(['12-15 RPO', '15+ RPO'])]

                                        context = f"""Expert cricket analyst profile for {bp_selected_player}.

OVERALL: {total_balls} balls, SR={overall_sr:.1f}, Boundary%={overall_bnd:.1f}%
Entry Phases: {', '.join(player_data['Entry_Phase'].unique())}

ENTRY PHASE PERFORMANCE:
{entry_summary.to_string(index=False)}

BALL POSITION PROFILE:
{ball_pos_profile.to_string()}

RRR PROFILE:
{rrr_profile.to_string()}

HIGH PRESSURE (RRR 12+): {high_pressure['Balls'].sum()} balls, SR={(high_pressure['Runs'].sum() / high_pressure['Balls'].sum() * 100) if not high_pressure.empty and high_pressure['Balls'].sum() > 0 else 'N/A'}

Provide: tactical archetype, optimal deployment situations, ball position strengths/weaknesses, strategic recommendations."""

                                        response = ai_model.generate_content(context)
                                        st.markdown(response.text)
                                    except Exception as e:
                                        st.error(f"Error generating insights: {e}")
                        else:
                            st.info("💡 Configure GEMINI_API_KEY in .env to enable AI insights")

                        st.markdown("---")
                        st.markdown("#### Detailed Breakdown")
                        st.dataframe(player_data.sort_values(['Entry_Phase', 'RRR_Range', 'Ball_Position']),
                                     use_container_width=True)

                        # Heatmaps
                        st.markdown("#### Performance Heatmaps")
                        row_order = ['Early (1-2)', 'Middle (3-4)', 'Late (5-6)']
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            pivot_data = player_data.groupby(['Ball_Position', 'RRR_Range']).agg(
                                Runs=('Runs', 'sum'), Balls=('Balls', 'sum')
                            ).reset_index()
                            pivot_data['Strike_Rate'] = (pivot_data['Runs'] / pivot_data['Balls'] * 100).round(1)
                            pivot_sr = pivot_data.pivot(index='Ball_Position', columns='RRR_Range', values='Strike_Rate')
                            pivot_sr = pivot_sr.reindex([r for r in row_order if r in pivot_sr.index])
                            fig = px.imshow(pivot_sr, title="Strike Rate", color_continuous_scale='RdYlGn',
                                            aspect="auto", text_auto='.1f')
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            pivot_data_bnd = player_data.groupby(['Ball_Position', 'RRR_Range']).agg(
                                Boundaries=('Boundaries', 'sum'), Balls=('Balls', 'sum')
                            ).reset_index()
                            pivot_data_bnd['Boundary_Pct'] = (pivot_data_bnd['Boundaries'] / pivot_data_bnd['Balls'] * 100).round(1)
                            pivot_bnd = pivot_data_bnd.pivot(index='Ball_Position', columns='RRR_Range', values='Boundary_Pct')
                            pivot_bnd = pivot_bnd.reindex([r for r in row_order if r in pivot_bnd.index])
                            fig = px.imshow(pivot_bnd, title="Boundary %", color_continuous_scale='Blues',
                                            aspect="auto", text_auto='.1f')
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)

                        with col3:
                            pivot_data_dot = player_data.groupby(['Ball_Position', 'RRR_Range']).agg(
                                Dots=('Dots', 'sum'), Balls=('Balls', 'sum')
                            ).reset_index()
                            pivot_data_dot['Dot_Pct'] = (pivot_data_dot['Dots'] / pivot_data_dot['Balls'] * 100).round(1)
                            pivot_dot = pivot_data_dot.pivot(index='Ball_Position', columns='RRR_Range', values='Dot_Pct')
                            pivot_dot = pivot_dot.reindex([r for r in row_order if r in pivot_dot.index])
                            fig = px.imshow(pivot_dot, title="Dot Ball %", color_continuous_scale='Reds_r',
                                            aspect="auto", text_auto='.1f')
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"No data for {bp_selected_player} with current filters")
            else:
                st.warning("No data available with selected filters")
        else:
            st.warning("No chase scenario data available")


# ─── TAB 3: AI INSIGHTS ─────────────────────────────────────────────────────
with tab3:
    st.header("🤖 AI-Powered Insights")

    ai_model = initialize_ai()

    if ai_model is None:
        st.error("❌ AI not configured. Set GEMINI_API_KEY in .env file")
    else:
        # Use a simple filtered dataset for the AI agent (all data, no sidebar dependency)
        ai_df = entry_df.copy()

        if 'react_agent' not in st.session_state:
            try:
                analyzer = CricketDataAnalyzer(ai_df)
                st.session_state.react_agent = ReActCricketAgent(analyzer, ai_model)
            except Exception as e:
                st.error(f"Error initializing AI: {e}")
                st.session_state.react_agent = None

        if st.session_state.get('react_agent'):
            st.info(f"📊 Analyzing {len(ai_df):,} entry points")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🎯 Best Powerplay Players", key="ai_pp"):
                    st.session_state.ai_question = "Who are the best powerplay players?"
            with col2:
                if st.button("💥 Best Death Over Finishers", key="ai_death"):
                    st.session_state.ai_question = "Who are the best death over finishers?"
            with col3:
                if st.button("📋 Optimal Batting Order", key="ai_order"):
                    st.session_state.ai_question = "What is the optimal batting order for chasing 180+ runs?"

            user_question = st.text_input(
                "Ask the AI Coach:",
                placeholder="e.g., Which players perform best in middle overs?",
                key="ai_question_input"
            )

            if st.button("🚀 Get Answer", key="ai_submit") or user_question:
                question = user_question or st.session_state.get('ai_question', '')
                if question:
                    with st.spinner("🤔 AI Coach analyzing..."):
                        try:
                            st.session_state.react_agent.analyzer = CricketDataAnalyzer(ai_df)
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
