# 🏏 IPL Entry Point Analysis Dashboard

AI-powered cricket analytics dashboard analyzing player performance by entry point, ball position, and match situation using Google's Gemini API.

## Features

- **Entry Point Analysis**: Track player performance based on when they entered the innings
- **Ball Position Analytics**: Analyze performance by ball number in over (1-6) at different RRR ranges
- **Entry Phase Tracking**: Powerplay (0-6), Middle (7-15), Death (16-20) overs analysis
- **AI-Powered Insights**: Get intelligent recommendations based on filtered data
- **Interactive Heatmaps**: Visualize performance across multiple dimensions
- **Individual Player Analysis**: Deep dive into any player's strengths and weaknesses

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key (Optional - for AI Insights)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Configure Environment
```bash
# Copy the template
copy .env.template .env

# Edit .env and add your API key:
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Prepare Your Data
Place your ball-by-ball IPL dataset as `ipl_data_mens_only.csv` in the project root.

Required columns:
- Batsman, Opposition, Match⬆, Date⬆
- Overs, R.1 (cumulative runs), B (balls faced)
- RRreq, RReq, BRem (chase situation data)
- Bat (innings identifier)

### 5. Generate Processed Data
```bash
# Generate entry point data
python process_ballbyball_data.py

# Generate ball position data
python process_ball_position_data.py
```

This creates:
- `processed_entry_points_ballbyball.csv` - Entry point analysis data
- `ball_position_analysis.csv` - Ball-by-ball position data
- `bowling_type_matchups.csv` - Pace vs Spin statistics

### 6. Run the Dashboard
```bash
streamlit run ballbyball_entry_dashboard.py
```

## Dashboard Sections

### 📊 Player Entry Analysis
- Entry point statistics (when players entered)
- Performance metrics: Strike Rate, Boundary %, Dot %
- RRR impact analysis (% of runs remaining contributed)
- Over-by-over progression charts
- Bowling type matchups (Pace vs Spin)

### 🎯 Ball Position Analysis
- Performance by ball number in over (1-6)
- RRR range filtering (0-6, 6-9, 9-12, 12-15, 15+ RPO)
- Entry phase filtering (Powerplay/Middle/Death)
- Comprehensive heatmaps
- Individual player deep dives

### 🤖 AI Insights
- Natural language Q&A about player performance
- Automated insights on filtered data
- Strategic recommendations for team selection
- Player strengths and weaknesses analysis

## Usage Examples

### Analyze Late Over Performance
1. Go to "Ball Position Analysis"
2. Select "Late (5-6)" ball position
3. Select "12-15 RPO" and "15+ RPO" RRR ranges
4. Click "Generate AI Insights" for recommendations

### Individual Player Analysis
1. Select a player from the dropdown
2. View performance heatmaps by situation
3. Check entry phase impact
4. Click "Generate Insights" for tactical analysis

### Entry Point Tracking
1. Go to "Player Entry Analysis"
2. Filter by team, year, bowling type
3. View entry over vs performance metrics
4. Analyze over-by-over progression for specific matches

## File Structure
```
├── 🏏 MAIN FILES
│   ├── ballbyball_entry_dashboard.py      # Main dashboard
│   ├── react_cricket_agent.py             # AI agent for Q&A
│   ├── process_ballbyball_data.py         # Entry point processor
│   ├── process_ball_position_data.py      # Ball position processor
│   ├── ipl_data_mens_only.csv             # Source data
│   ├── .env                               # API key configuration
│   └── requirements.txt                   # Dependencies
├── 📊 GENERATED DATA
│   ├── processed_entry_points_ballbyball.csv
│   ├── ball_position_analysis.csv
│   └── bowling_type_matchups.csv
├── 📁 .streamlit/                         # Streamlit configuration
└── 📄 ARCHITECTURE_OVERVIEW.md            # System architecture
```

## Key Metrics Explained

### Entry Point Metrics
- **Entry Over**: The over when the player first faced a ball
- **Entry RRR**: Required run rate when player entered
- **% of Runs Remaining**: (Player Runs / Runs Required at Entry) × 100
- **Contribution per Over**: Player Runs / Overs Played

### Ball Position Metrics
- **Ball Position**: Early (1-2), Middle (3-4), Late (5-6) in over
- **RRR Range**: Required run rate categorized in ranges
- **Entry Phase**: When player entered - Powerplay/Middle/Death
- **Strike Rate**: (Runs / Balls) × 100
- **Boundary %**: (Boundaries / Balls) × 100
- **Dot %**: (Dot Balls / Balls) × 100

## Troubleshooting

### Data Not Loading
- Ensure you've run both processing scripts first
- Check that CSV files exist in the project root
- Verify source data has required columns

### AI Insights Not Working
- Check GEMINI_API_KEY is set in .env
- Verify API key is valid and active
- Dashboard works without AI - only insights require API

### Performance Issues
- Filter data by year/team to reduce dataset size
- Increase minimum balls filter (default: 5)
- Close other browser tabs running Streamlit

## Architecture

See [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) for detailed system architecture, data flow, and API usage information.

## Support

For issues or questions:
1. Verify data files are generated
2. Check API key configuration (if using AI)
3. Ensure all dependencies are installed
4. Python 3.8+ required