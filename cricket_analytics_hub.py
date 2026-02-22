"""
Cricket Analytics Hub - Main Dashboard Launcher
Choose between different cricket analysis dashboards
"""

import streamlit as st
import subprocess
import sys
import os

# Page config
st.set_page_config(
    page_title="Cricket Analytics Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .dashboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
    }
    .entry-card {
        background: linear-gradient(135deg, #32CD32 0%, #228B22 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
    }
    .entry-card:hover {
        transform: translateY(-5px);
    }
    .feature-list {
        list-style-type: none;
        padding-left: 0;
    }
    .feature-list li {
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    .feature-list li:before {
        content: "✅ ";
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricket Analytics Hub</h1>
    <p>Professional Cricket Intelligence & Performance Analysis Platform</p>
    <p><em>Choose your analysis dashboard below</em></p>
</div>
""", unsafe_allow_html=True)

# Dashboard selection
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="dashboard-card">
        <h2>🎯 AI Cricket Manager Dashboard</h2>
        <p><strong>For Team Managers & Coaches</strong></p>
        <p>Comprehensive team management and strategic analysis using advanced cricket analytics data.</p>
        
        <ul class="feature-list">
            <li>Team Strategy Overview with AI insights</li>
            <li>Player Performance Intelligence</li>
            <li>Opposition Analysis & Matchup Intelligence</li>
            <li>Match Preparation & Tactical Planning</li>
            <li>Year-over-Year Performance Comparison</li>
            <li>AI-Powered Strategic Recommendations</li>
        </ul>
        
        <p><strong>Data Source:</strong> Comprehensive cricket analytics (2024-2025)</p>
        <p><strong>Teams:</strong> ADKR, DC, GG, MIE, SW, DV</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Launch Team Manager Dashboard", type="primary", use_container_width=True):
        st.success("🎯 Launching AI Cricket Manager Dashboard...")
        st.markdown("**Dashboard Features:**")
        st.markdown("- 🏟️ Team strategy analysis")
        st.markdown("- 👤 Player performance insights")
        st.markdown("- ⚔️ Opposition intelligence")
        st.markdown("- 🏏 Match preparation tools")
        st.markdown("- 🤖 AI-powered recommendations")
        
        # Instructions to run
        st.markdown("---")
        st.markdown("### 🔧 To Launch:")
        st.code("streamlit run ai_cricket_manager_dashboard.py --server.port 8501")
        
        st.markdown("### 📊 Or run directly:")
        if st.button("▶️ Run Team Manager Dashboard"):
            try:
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", "ai_cricket_manager_dashboard.py", "--server.port", "8501"])
                st.success("Dashboard launched! Check http://localhost:8501")
            except Exception as e:
                st.error(f"Failed to launch: {e}")

with col2:
    st.markdown("""
    <div class="entry-card">
        <h2>⏰ Entry Analysis Dashboard</h2>
        <p><strong>For Performance Analysts & Scouts</strong></p>
        <p>Specialized analysis of player entry timing and strike rate performance patterns.</p>
        
        <ul class="feature-list">
            <li>Entry Timing Analysis (When players enter)</li>
            <li>Strike Rate by Entry Over</li>
            <li>Individual Player Entry Patterns</li>
            <li>Team Entry Strategy Comparison</li>
            <li>Phase-wise Performance Analysis</li>
            <li>AI-Powered Entry Optimization</li>
        </ul>
        
        <p><strong>Data Source:</strong> CricViz Entry Data (2022-2026)</p>
        <p><strong>Analysis:</strong> Entry timing vs performance correlation</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Launch Entry Analysis Dashboard", type="secondary", use_container_width=True):
        st.success("⏰ Launching Entry Analysis Dashboard...")
        st.markdown("**Dashboard Features:**")
        st.markdown("- ⏰ Entry timing patterns")
        st.markdown("- ⚡ Strike rate by entry over")
        st.markdown("- 👤 Individual player analysis")
        st.markdown("- 🏟️ Team strategy comparison")
        st.markdown("- 🧠 AI entry optimization")
        
        # Instructions to run
        st.markdown("---")
        st.markdown("### 🔧 To Launch:")
        st.code("streamlit run entry_analysis_dashboard.py --server.port 8502")
        
        st.markdown("### 📊 Or run directly:")
        if st.button("▶️ Run Entry Analysis Dashboard"):
            try:
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", "entry_analysis_dashboard.py", "--server.port", "8502"])
                st.success("Dashboard launched! Check http://localhost:8502")
            except Exception as e:
                st.error(f"Failed to launch: {e}")

# Comparison section
st.markdown("---")
st.markdown("## 🔍 Dashboard Comparison")

comparison_data = {
    "Feature": [
        "Target Users",
        "Primary Focus",
        "Data Source",
        "Time Period",
        "Key Analysis",
        "AI Features",
        "Best For"
    ],
    "Team Manager Dashboard": [
        "Team Managers, Coaches",
        "Team Strategy & Management",
        "Cricket Analytics JSON",
        "2024-2025",
        "Team performance, player roles, opposition analysis",
        "Strategic recommendations, tactical insights",
        "Match preparation, team selection, strategic planning"
    ],
    "Entry Analysis Dashboard": [
        "Performance Analysts, Scouts",
        "Entry Timing & Strike Rates",
        "CricViz CSV Data",
        "2022-2026",
        "Entry patterns, timing optimization, performance correlation",
        "Entry optimization, role recommendations",
        "Player development, role optimization, timing strategies"
    ]
}

import pandas as pd
comparison_df = pd.DataFrame(comparison_data)
st.dataframe(comparison_df, use_container_width=True)

# Quick start guide
st.markdown("---")
st.markdown("## 🚀 Quick Start Guide")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 For Team Management:")
    st.markdown("1. **Choose Team Manager Dashboard**")
    st.markdown("2. **Select your team** (ADKR, DC, GG, etc.)")
    st.markdown("3. **Apply year filters** (2024-2025)")
    st.markdown("4. **Explore analysis modes:**")
    st.markdown("   - Team Strategy Overview")
    st.markdown("   - Player Performance Analysis")
    st.markdown("   - Opposition Analysis")
    st.markdown("   - Match Preparation")
    st.markdown("5. **Generate AI insights** for strategic decisions")

with col2:
    st.markdown("### ⏰ For Entry Analysis:")
    st.markdown("1. **Choose Entry Analysis Dashboard**")
    st.markdown("2. **Select years** (2022-2026)")
    st.markdown("3. **Filter teams and minimum balls**")
    st.markdown("4. **Explore analysis types:**")
    st.markdown("   - Entry Timing Analysis")
    st.markdown("   - Strike Rate by Entry")
    st.markdown("   - Player Performance")
    st.markdown("   - Team Comparison")
    st.markdown("5. **Get AI recommendations** for entry optimization")

# Requirements
st.markdown("---")
st.markdown("## ⚙️ Requirements")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 System Requirements:")
    st.markdown("- Python 3.11+")
    st.markdown("- Streamlit 1.28+")
    st.markdown("- Pandas, Plotly")
    st.markdown("- Google Generative AI")
    st.markdown("- 2GB RAM minimum")

with col2:
    st.markdown("### 🔑 API Requirements:")
    st.markdown("- **Gemini API Key** (for AI features)")
    st.markdown("- Get from: [Google AI Studio](https://makersuite.google.com/app/apikey)")
    st.markdown("- Free tier: 60 requests/minute")
    st.markdown("- Set in `.env` file: `GEMINI_API_KEY=your_key`")

# Data files check
st.markdown("---")
st.markdown("## 📁 Data Files Status")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Team Manager Dashboard:")
    if os.path.exists('cricket_analytics_data (1).json'):
        st.success("✅ cricket_analytics_data (1).json - Found")
    else:
        st.error("❌ cricket_analytics_data (1).json - Missing")
    
    if os.path.exists('ai_cricket_manager_dashboard.py'):
        st.success("✅ ai_cricket_manager_dashboard.py - Found")
    else:
        st.error("❌ ai_cricket_manager_dashboard.py - Missing")

with col2:
    st.markdown("### Entry Analysis Dashboard:")
    if os.path.exists('cricviz_2022_2026_20260122_093415(in).csv'):
        st.success("✅ cricviz_2022_2026_20260122_093415(in).csv - Found")
    else:
        st.error("❌ cricviz_2022_2026_20260122_093415(in).csv - Missing")
    
    if os.path.exists('entry_analysis_dashboard.py'):
        st.success("✅ entry_analysis_dashboard.py - Found")
    else:
        st.error("❌ entry_analysis_dashboard.py - Missing")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 2rem;'>"
    "🏏 Cricket Analytics Hub | Professional Cricket Intelligence Platform<br>"
    "Built with ❤️ for cricket team management and performance analysis"
    "</div>",
    unsafe_allow_html=True
)