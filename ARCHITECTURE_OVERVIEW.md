# Cricket Analytics Dashboard - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                    (Streamlit Web Dashboard)                         │
│                   ballbyball_entry_dashboard.py                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ├─────────────────────────────────────┐
                             │                                     │
                             ▼                                     ▼
┌────────────────────────────────────────┐    ┌──────────────────────────────┐
│         DATA LAYER (Local CSV)         │    │    AI INSIGHTS LAYER         │
│                                        │    │   (Optional Feature)         │
│  • ipl_data_mens_only.csv             │    │                              │
│    - 34,340 ball-by-ball records      │    │  react_cricket_agent.py      │
│    - IPL 2024-2025                    │    │         │                    │
│                                        │    │         ▼                    │
│  • processed_entry_points_ballbyball  │    │  ┌──────────────────────┐   │
│    .csv (Generated)                   │    │  │  Google Gemini API   │   │
│    - 1,671 entry points               │    │  │  (gemini-2.0-flash)  │   │
│    - 205 players, 144 matches         │    │  │                      │   │
│                                        │    │  │  🔑 API KEY REQUIRED │   │
│  • bowling_type_matchups.csv          │    │  └──────────────────────┘   │
│    (Generated)                        │    │                              │
└────────────────────────────────────────┘    └──────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING LAYER                             │
│                  process_ballbyball_data.py                          │
│                                                                      │
│  Transforms raw ball-by-ball data into entry point analysis:        │
│  • Identifies player entry points (minimum over per match)          │
│  • Calculates performance metrics (SR, Dot%, Boundary%)             │
│  • Computes match impact metrics (% of Runs Remaining, RRR)         │
│  • Generates bowling type matchups (Pace vs Spin)                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer (No API Required)
**Files:**
- `ipl_data_mens_only.csv` - Raw ball-by-ball data
- `processed_entry_points_ballbyball.csv` - Processed entry analysis
- `bowling_type_matchups.csv` - Bowling type statistics

**Data Flow:**
```
Raw CSV → process_ballbyball_data.py → Processed CSV → Dashboard
```

**No external APIs or credentials needed for data processing**

### 2. Dashboard Layer (No API Required for Core Features)
**File:** `ballbyball_entry_dashboard.py`

**Features (No API Key):**
- Entry Overview - Player entry point distributions
- Player Analysis - Individual performance metrics
- Team Analysis - Team-level statistics
- Match Impact Analysis - Chase contribution metrics
  - % of Runs Remaining
  - Contribution per Over
  - Over-by-over progression charts

**Technology:** Streamlit (Python web framework)

### 3. AI Insights Layer (API Key Required - OPTIONAL)
**File:** `react_cricket_agent.py`

**Purpose:** Natural language Q&A about player performance

**API Used:** Google Gemini API (gemini-2.5-flash)

**API Key Storage:**
```
.env file (local development):
GEMINI_API_KEY=your_api_key_here

.streamlit/secrets.toml (deployment):
GEMINI_API_KEY = "your_api_key_here"
```

**Example Queries:**
- "Who are the best powerplay players?"
- "Which players perform well in middle overs?"
- "What is the optimal batting order for chasing 180+ runs?"

**Important:** AI Insights is an OPTIONAL feature. The dashboard works fully without it.

## Data Flow Diagram

```
┌──────────────────┐
│  CricViz Data    │
│  (Ball-by-Ball)  │
└────────┬─────────┘
         │
         │ Manual Import
         ▼
┌──────────────────────────┐
│ ipl_data_mens_only.csv   │
│ (34,340 balls)           │
└────────┬─────────────────┘
         │
         │ Run: python process_ballbyball_data.py
         ▼
┌──────────────────────────────────────────┐
│ processed_entry_points_ballbyball.csv    │
│ • 1,671 entry points                     │
│ • Performance metrics                    │
│ • Match impact calculations              │
└────────┬─────────────────────────────────┘
         │
         │ Load into memory
         ▼
┌──────────────────────────────────────────┐
│ Streamlit Dashboard                      │
│ • Filters (Year, Team, Phase, Min Balls)│
│ • Visualizations (Charts, Tables)       │
│ • Interactive Analysis                  │
└────────┬─────────────────────────────────┘
         │
         │ User asks question (Optional)
         ▼
┌──────────────────────────────────────────┐
│ AI Insights (react_cricket_agent.py)    │
│ • Validates question                     │
│ • Queries filtered data                  │
│ • Calls Gemini API 🔑                   │
│ • Returns natural language answer       │
└──────────────────────────────────────────┘
```

## Key Metrics Calculated

### Entry Point Analysis
- **Entry Over**: First over player batted in match
- **Exit Over**: Last over player batted in match
- **Duration**: Number of overs played
- **Strike Rate**: (Runs / Balls) × 100
- **Dot Ball %**: (Dots / Balls) × 100
- **Boundary %**: (4s + 6s / Balls) × 100

### Match Impact Metrics (Chase Scenarios)
- **% of Runs Remaining**: (Player Runs / Runs Required at Entry) × 100
- **Contribution per Over**: Player Runs / Overs Played
- **% of Target**: (Player Runs / Chase Target) × 100
- **RRR Comparison**: Player SR vs Required Run Rate

### Over-by-Over Progression
- Cumulative runs and balls at each over
- Strike rate progression
- Required run rate progression
- Visual comparison chart

## API Key Usage - Security Considerations

### Where API Key is Used
**ONLY in AI Insights feature** (`react_cricket_agent.py`)

### API Call Flow
```
User Question → Validate Question → Query Local Data → 
Format Context → Call Gemini API 🔑 → Parse Response → Display Answer
```

### Security Measures
1. **Environment Variables**: API key stored in `.env` (not in code)
2. **Gitignore**: `.env` file excluded from version control
3. **Local Processing**: All data analysis done locally, only Q&A uses API
4. **Optional Feature**: Dashboard works without API key
5. **Rate Limiting**: Gemini API has built-in rate limits

### API Key Configuration
```python
# .env file (local)
GEMINI_API_KEY=your_actual_api_key_here

# .streamlit/secrets.toml (deployment)
GEMINI_API_KEY = "your_actual_api_key_here"
```

### Cost Considerations
- **Gemini 2.0 Flash**: Free tier available
- **Usage**: Only when user asks questions in AI Insights section
- **Typical Usage**: 5-10 API calls per session
- **Cost**: Minimal (within free tier for development)

## Deployment Options

### Option 1: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional)
echo "GEMINI_API_KEY=your_key" > .env

# Run dashboard
streamlit run ballbyball_entry_dashboard.py
```

### Option 2: Streamlit Cloud (Recommended)
- Free hosting for Streamlit apps
- Set API key in Streamlit Cloud secrets
- Automatic HTTPS and scaling
- No server management needed

### Option 3: Internal Server
- Deploy on company infrastructure
- Store API key in secure vault
- Control access and usage
- Monitor API calls

## Data Privacy & Compliance

### Data Handling
- **All cricket data is local** (CSV files)
- **No data sent to external services** except AI queries
- **AI queries**: Only send aggregated statistics, not raw data
- **No PII**: Only player names and performance stats

### API Data Transmission
When AI Insights is used:
- **Sent to Gemini API**: Filtered statistics, player names, performance metrics
- **NOT sent**: Raw ball-by-ball data, personal information
- **Response**: Natural language text analysis

## System Requirements

### Development Environment
- Python 3.8+
- 2GB RAM minimum
- 100MB disk space for data
- Internet connection (for AI Insights only)

### Dependencies
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
google-generativeai>=0.3.0  # Only for AI Insights
python-dotenv>=1.0.0
```

## Monitoring & Maintenance

### Data Updates
- **Frequency**: As new match data becomes available
- **Process**: Replace `ipl_data_mens_only.csv` → Re-run processing script
- **Downtime**: None (can update while dashboard is running)

### API Monitoring
- **Gemini API Status**: Check Google Cloud status page
- **Rate Limits**: Monitor usage in Google Cloud Console
- **Fallback**: Dashboard works without AI if API is down

## Questions for Team Lead

1. **API Key Management**: Should we use company's Google Cloud account or individual keys?
2. **Deployment Target**: Streamlit Cloud, internal server, or local only?
3. **Data Updates**: Who will provide updated CricViz data and how often?
4. **Access Control**: Should AI Insights be enabled for all users or restricted?
5. **Cost Approval**: Confirm budget for Gemini API usage (likely within free tier)

## Summary

**Core Dashboard**: Fully functional without any API keys
**AI Insights**: Optional feature requiring Google Gemini API key
**Data**: All stored locally in CSV files
**Security**: API key in environment variables, not in code
**Cost**: Minimal (free tier sufficient for development)
