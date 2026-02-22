"""
Professional Game Prep Interface using Gradio
Fast, reliable alternative to Streamlit
"""

import gradio as gr
import pandas as pd
from corrected_strategy_engine import CorrectedIPLStrategyEngine

# Load data once
df = pd.read_csv('ipl_data.csv')
available_batsmen = sorted(df['Batsman'].dropna().unique())
bowler_types = ["RAF", "LAF", "Off Break", "Leg Spin", "LAO"]

def generate_brief(batsman, bowler_type, min_balls, season_filter):
    """Generate scouting brief"""
    try:
        # Set up filters
        filters = {}
        if season_filter != "All Seasons":
            filters['season'] = int(season_filter)
        
        # Create engine and generate brief
        engine = CorrectedIPLStrategyEngine(filters=filters)
        engine._ensure_data_loaded()
        
        # Capture the output
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        engine.generate_scouting_brief(batsman, bowler_type, min_balls)
        
        output = buffer.getvalue()
        sys.stdout = old_stdout
        
        if not output or "No data available" in output:
            return f"❌ No data available for {batsman} vs {bowler_type} with minimum {min_balls} balls"
        
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="IPL Game Prep", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎯 Professional IPL Scouting & Game Prep")
    gr.Markdown("*Generate comprehensive scouting briefs for batsmen vs specific bowler types*")
    
    with gr.Row():
        with gr.Column(scale=1):
            season = gr.Dropdown(
                choices=["All Seasons", "2024", "2025"],
                value="All Seasons",
                label="📅 Season"
            )
            batsman = gr.Dropdown(
                choices=available_batsmen,
                value=available_batsmen[0] if available_batsmen else None,
                label="🏏 Select Batsman",
                filterable=True
            )
            bowler = gr.Dropdown(
                choices=bowler_types,
                value="RAF",
                label="🎳 vs Bowler Type"
            )
            min_balls = gr.Slider(
                minimum=10,
                maximum=100,
                value=20,
                step=5,
                label="📊 Minimum Balls"
            )
            
            generate_btn = gr.Button("🎯 Generate Scouting Brief", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            output = gr.Textbox(
                label="📋 Scouting Brief",
                lines=25,
                max_lines=50,
                show_copy_button=True
            )
    
    generate_btn.click(
        fn=generate_brief,
        inputs=[batsman, bowler, min_balls, season],
        outputs=output
    )
    
    gr.Markdown("---")
    gr.Markdown("💡 **Tip:** Adjust the minimum balls slider to see more or fewer matchups")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting IPL Game Prep Interface...")
    print("="*60)
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )
