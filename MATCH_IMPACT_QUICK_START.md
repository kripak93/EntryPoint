# Match Impact Analysis - Quick Start Guide

## What We Built

A Personal Impact metric that measures individual player performance against match requirements in chase scenarios, isolating their contribution from team context.

## How to Use

### 1. Run the Dashboard
```bash
streamlit run ballbyball_entry_dashboard.py
```

### 2. Navigate to "Match Impact Analysis"
Select from the sidebar dropdown: Analysis Type → "Match Impact Analysis"

### 3. Understanding the Metrics

#### Personal Impact (Primary Metric)
- **Formula**: Player's Run Rate - Required Run Rate at Entry
- **Units**: Runs per over (RPO)
- **Interpretation**:
  - **Positive**: Player scored faster than required (good)
  - **Negative**: Player scored slower than required (needs improvement)
  - **Example**: +3.5 RPO means player scored 3.5 runs per over faster than needed

#### Impact Runs (Secondary Metric)
- **Formula**: Actual Runs - Required Runs (based on balls faced)
- **Units**: Runs
- **Interpretation**:
  - **Positive**: Scored more runs than required
  - **Negative**: Scored fewer runs than required
  - **Example**: +12 runs means player contributed 12 extra runs above requirement

#### Player Run Rate
- **Formula**: Strike Rate / 100 × 6
- **Units**: Runs per over
- **Purpose**: Converts strike rate to same scale as RRR for comparison

## Key Insights from Analysis

### Top Performers (Min 3 chase entries)
1. **SD Hope**: +2.90 RPO (142 SR, enters at 5.62 RRR)
2. **VR Iyer**: +2.00 RPO (152 SR, enters at 7.13 RRR)
3. **SS Iyer**: +2.00 RPO (154 SR, enters at 7.23 RRR)
4. **KL Rahul**: +1.23 RPO (166 SR, enters at 8.76 RRR)

### Known Specialists Performance
- **Hardik Pandya**: -2.62 RPO (enters at tough 12.26 RRR)
- **MS Dhoni**: -3.88 RPO (enters at very tough 13.12 RRR)
- **Rohit Sharma**: +0.73 RPO (limited data, 2 entries)

### Overall Statistics
- **777 chase entries** analyzed
- **25.5% success rate** (positive impact)
- **Average Personal Impact**: -6.18 RPO
- **High pressure scenarios** (RRR > 12): 312 entries

## Use Cases

### 1. Player Selection for Chases
**Question**: Who should bat at #5 when chasing 180+?

**Steps**:
1. Filter by Entry Phase: "Middle" or "Death"
2. Look at Player Impact Rankings table
3. Sort by "Avg Personal Impact" (descending)
4. Check "Entries" column for sample size (min 3-5)
5. Consider "Avg Entry RRR" to match scenario

### 2. Pressure Performance Analysis
**Question**: Who handles high-pressure chases (RRR > 12)?

**Steps**:
1. Select individual player from dropdown
2. Look at scatter plot: Entry RRR vs Personal Impact
3. Check if they have positive impacts at high RRR values
4. Review match-by-match breakdown table

### 3. Strike Rate vs Impact Correlation
**Question**: Does higher strike rate always mean better impact?

**Steps**:
1. Select player from dropdown
2. View "Strike Rate vs Personal Impact" scatter plot
3. Look for correlation pattern
4. Note: High SR with negative impact = entered at very high RRR

## Filters Available

### Sidebar Filters
- **Years**: 2024-2025
- **Teams**: All IPL teams
- **Entry Phase**: Powerplay, Middle, Death
- **Min Balls Faced**: Adjust to filter out small samples

### Impact on Analysis
All filters apply to the Match Impact Analysis section, allowing you to:
- Compare teams' chase performance
- Analyze specific phases (e.g., death over specialists)
- Focus on recent seasons

## Visualizations

### 1. Personal Impact Distribution
- Histogram showing spread of player performances
- Red line at 0 = required rate
- Right side = faster than required
- Left side = slower than required

### 2. Impact by Entry Phase
- Bar chart comparing Powerplay, Middle, Death
- Shows which phase has better chase performance
- Helps identify phase-specific specialists

### 3. Individual Player Scatter Plots
- **Entry RRR vs Personal Impact**: Shows performance under different pressure levels
- **Strike Rate vs Personal Impact**: Shows efficiency correlation

### 4. Match-by-Match Breakdown
- Detailed table with all metrics per entry
- Sortable by any column
- Useful for identifying patterns

## Data Limitations

### What We Have
- 777 chase entries with RRR data
- IPL 2024-2025 seasons
- Ball-by-ball granularity
- Entry and exit over tracking

### What We Don't Have
- Match outcomes (win/loss)
- Wickets context at entry
- Opposition bowling quality
- Venue/pitch conditions
- 2nd innings setting scenarios (no RRR data)

## Advanced Analysis Tips

### 1. Context Matters
- Player entering at RRR 15+ faces extreme pressure
- Negative impact at high RRR may still be valuable
- Consider entry situation when evaluating

### 2. Sample Size
- Min 3 entries for basic trends
- Min 5-10 entries for reliable patterns
- Check "Entries" column in rankings

### 3. Phase-Specific Roles
- Powerplay: Aggressive start (RRR usually lower)
- Middle: Building platform (RRR moderate)
- Death: Finishing (RRR often high)

### 4. Team Strategy
- Some players are sent to "see off" tough overs (negative impact expected)
- Finishers often enter at high RRR (harder to have positive impact)
- Anchors may have lower SR but positive impact if RRR is low

## Troubleshooting

### "No data available"
- Check if filters are too restrictive
- Ensure processed_entry_points_ballbyball.csv exists
- Run: `python process_ballbyball_data.py`

### Cache Issues
- Dashboard has 60-second cache TTL
- Refresh page if data seems stale
- Restart dashboard if needed

### Missing Players
- Only players with chase entries (RRR data) appear
- Check if player is in dataset: `python test_personal_impact.py`

## Next Steps

### Optional Enhancements
1. **Pressure Index**: Weight by RRR difficulty
2. **Wickets Context**: Factor in wickets lost
3. **Match Outcome**: Link to chase success
4. **Opposition Analysis**: Performance vs specific teams
5. **Venue Analysis**: Home/away performance

### Export Data
```python
import pandas as pd
df = pd.read_csv('processed_entry_points_ballbyball.csv')
chase_df = df[df['Personal_Impact'].notna()]
chase_df.to_csv('chase_analysis_export.csv', index=False)
```

## Questions?

Run the test scripts to explore the data:
- `python test_personal_impact.py` - Top performers analysis
- `python verify_dashboard_data.py` - Data validation
- `python investigate_innings_rrr.py` - Deep dive into data structure

## Summary

The Personal Impact metric successfully isolates individual player performance from team context in chase scenarios. Use it to identify reliable chase contributors, pressure performers, and phase-specific specialists for strategic team selection.
