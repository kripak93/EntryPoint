"""
Analyze how efficiently the AI handles large datasets
"""

import pandas as pd

def analyze_token_efficiency():
    """Analyze token efficiency of data processing"""
    
    print("🧠 AI Large Dataset Reconciliation Analysis")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv('ipl_data.csv')
    
    # Test with A Mhatre (131 records)
    mhatre = df[df['Batsman'] == 'A Mhatre']
    
    print(f"📊 A Mhatre Dataset:")
    print(f"  Raw records: {len(mhatre)}")
    print(f"  Columns: {len(mhatre.columns)}")
    
    # Estimate raw data size
    raw_data_str = mhatre[['Batsman', 'Team.1', 'R.1', 'B', 'RR', 'Overs']].to_string()
    raw_tokens = len(raw_data_str.split())
    
    print(f"  Raw data tokens: ~{raw_tokens:,}")
    
    # Calculate optimized summary
    total_runs = mhatre['R.1'].max()
    total_balls = len(mhatre)
    strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0
    matches = mhatre['Match⬆'].nunique()
    fours = len(mhatre[mhatre['4'] == 1])
    sixes = len(mhatre[mhatre['6'] == 1])
    dots = len(mhatre[mhatre['0'] == 1])
    
    summary = f"""
COMPREHENSIVE BATTING ANALYSIS:
- Total Records: {total_balls} balls faced
- Matches Played: {matches}
- Total Runs: {total_runs}
- Strike Rate: {strike_rate:.1f}
- Boundaries: {fours} fours, {sixes} sixes
- Dot Balls: {dots} ({dots/total_balls*100:.1f}%)
- Teams: {', '.join(mhatre['Team.1'].unique())}

RECENT PERFORMANCE (Last 10 balls):
{mhatre[['Batsman', 'Team.1', 'R.1', 'B', 'RR', 'Overs']].tail(10).to_string()}
"""
    
    summary_tokens = len(summary.split())
    
    print(f"  Optimized summary tokens: ~{summary_tokens}")
    print(f"  Token reduction: {raw_tokens / summary_tokens:.1f}x smaller")
    print(f"  Efficiency: {(1 - summary_tokens/raw_tokens)*100:.1f}% reduction")
    
    # Test with larger dataset (V Kohli)
    print(f"\n📊 V Kohli Dataset (Larger):")
    kohli = df[df['Batsman'] == 'V Kohli']
    print(f"  Raw records: {len(kohli)}")
    
    kohli_raw_tokens = len(kohli[['Batsman', 'Team.1', 'R.1', 'B', 'RR']].to_string().split())
    print(f"  Raw data tokens: ~{kohli_raw_tokens:,}")
    print(f"  With same summary approach: ~{summary_tokens} tokens")
    print(f"  Token reduction: {kohli_raw_tokens / summary_tokens:.1f}x smaller")
    
    print(f"\n🎯 AI Reconciliation Strategies:")
    print(f"1. ✅ Statistical Aggregation: Convert {len(mhatre)} rows → key metrics")
    print(f"2. ✅ Sample + Summary: Show recent 10 balls + full stats")
    print(f"3. ✅ Token Optimization: {raw_tokens} → {summary_tokens} tokens ({(1-summary_tokens/raw_tokens)*100:.0f}% reduction)")
    print(f"4. ✅ Contextual Filtering: Only relevant columns")
    print(f"5. ✅ Pre-computed Insights: Strike rates, percentages calculated")
    
    print(f"\n💰 Cost Efficiency:")
    print(f"  Raw approach: ~{raw_tokens * 0.075 / 1000:.4f} credits per query")
    print(f"  Optimized approach: ~{summary_tokens * 0.075 / 1000:.4f} credits per query")
    print(f"  Cost savings: {(1 - summary_tokens/raw_tokens)*100:.0f}%")
    
    print(f"\n🧠 How AI Handles This:")
    print(f"  • Receives pre-computed statistics (not raw data)")
    print(f"  • Gets context from recent performance sample")
    print(f"  • Works with structured summaries")
    print(f"  • Focuses on insights rather than data processing")

if __name__ == "__main__":
    analyze_token_efficiency()