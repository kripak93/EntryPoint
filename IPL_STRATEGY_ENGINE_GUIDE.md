# IPL Strategy Engine - User Guide

## Overview
The IPL Strategy Engine is a **command-line tool** (not a dashboard) that generates tactical scouting briefs for batsmen vs different bowler types. It's designed for game preparation and opposition analysis.

## What It Does
- Generates detailed scouting briefs for individual batsmen vs specific bowler types
- Analyzes performance by phase (Powerplay vs Post-Powerplay)
- Breaks down strike rates by ball length and field zones
- Identifies dismissal patterns and hot zones
- Creates tactical recommendations for bowlers

## Data Source
- Uses: `ipl_data.csv` (ball-by-ball IPL data with detailed shot/length/zone information)
- Different from: `cricviz_2022_2026_20260122_093415(in).csv` (entry point analysis data)

## How to Run

### Start the Interactive CLI:
```bash
python ipl_strategy_engine.py
```

### Menu Options:

**1. Individual Batsman Scouting Brief**
- Enter batsman name (e.g., "V Kohli", "F du Plessis")
- Enter bowler type:
  - `RAF` = Right Arm Fast
  - `LAF` = Left Arm Fast
  - `LAO` = Left Arm Orthodox (spin)
  - `Off Break` = Off-spin
  - `Leg Spin` = Leg-spin
- Generates detailed brief and saves as markdown file

**2. Team Brief vs Opposition**
- Enter opposition team name
- Enter your bowler types (comma-separated)
- Generates analysis of opposition's top 6 batsmen

**3. Available Players**
- Lists all batsmen in the dataset (first 20)

**0. Exit**

## Example Usage

```
🏏 IPL Strategy Engine - Game Prep Mode
==================================================

Choose analysis type:
1. Individual Batsman Scouting Brief
2. Team Brief vs Opposition
3. Available Players
0. Exit

Enter choice: 1
Enter batsman name: V Kohli
Enter bowler type (RAF/LAF/LAO/Off Break/Leg Spin): RAF

[Generates detailed brief...]

💾 Brief saved as: scouting_brief_V_Kohli_RAF.md
```

## Output Format

The scouting brief includes:

### Overview
- Total balls faced vs bowler type
- Total runs, strike rate, dismissals

### Powerplay Analysis (Overs 1-6)
- Strike rate by ball length (full, length, short, etc.)
- Strike rate by field zone
- Boundary analysis (4s and 6s percentage)
- Dismissal patterns

### Post-Powerplay Analysis (Overs 7-20)
- Same metrics as powerplay

### Tactical Summary
- **Initial Plan**: Best lengths/zones to bowl first 6 balls
- **Shut Down Lines**: Lengths where batsman struggles (SR < 100)
- **Hot Zones to Protect**: Areas where batsman scores freely
- **Key Dismissal Opportunities**: Lengths that get wickets
- **Phase-Specific Strategy**: Powerplay vs middle overs approach

## Key Differences from Entry Analysis Dashboard

| Feature | IPL Strategy Engine | Entry Analysis Dashboard |
|---------|-------------------|-------------------------|
| **Interface** | Command-line (CLI) | Web dashboard (Streamlit) |
| **Data** | Ball-by-ball details | Entry point aggregates |
| **Focus** | Bowler vs batsman matchups | When players enter innings |
| **Output** | Markdown scouting reports | Interactive visualizations |
| **Use Case** | Pre-match preparation | Performance analysis |
| **AI** | No AI (pure stats) | ReAct AI coach |

## Data Columns Available

The `ipl_data.csv` contains:
- **Bowler info**: Player, Team, Technique (bowling style)
- **Batsman info**: Batsman, RL (right/left handed)
- **Ball details**: Line, Length, Variation, Ball Speed, Spin
- **Shot details**: Foot Move, Shot Type, Connection, Quality
- **Result**: Runs, Wicket, Zone (where ball went)
- **Context**: Overs, Phase, Match, Date, Ground

## Limitations

1. **No bowling type in CricViz data**: The entry analysis dashboard uses `cricviz_2022_2026_20260122_093415(in).csv` which doesn't have bowling type info
2. **Different datasets**: These two tools use completely different data sources
3. **No integration**: They operate independently

## When to Use Each Tool

**Use IPL Strategy Engine when:**
- Preparing for a specific match
- Need detailed bowler vs batsman analysis
- Want tactical recommendations for bowlers
- Need to understand length/zone vulnerabilities

**Use Entry Analysis Dashboard when:**
- Analyzing when players should bat in the order
- Understanding phase-based performance (powerplay/middle/death)
- Comparing players across teams/years
- Need AI-powered strategic insights
- Want interactive visualizations

## Dependencies

The strategy engine requires:
- `pandas`, `numpy`
- `enhanced_gemini_ipl_backend.py` (imported but not actively used in main flow)
- `ipl_data.csv` (ball-by-ball data)

## Running It Now

To start using the IPL Strategy Engine:

```bash
python ipl_strategy_engine.py
```

Then follow the interactive prompts!
