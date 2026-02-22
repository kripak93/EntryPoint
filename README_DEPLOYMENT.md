# 🏏 AI Cricket Manager Dashboard

> **Professional Cricket Intelligence & Performance Analysis for Team Management**

## 🌟 Features

### 🎯 Strategic Team Management
- **AI-Powered Analysis** - Get intelligent insights using Google Gemini AI
- **Team Strategy Overview** - Comprehensive performance analysis by phase
- **Player Performance Intelligence** - Detailed individual player analytics
- **Opposition Analysis** - Head-to-head matchup intelligence
- **Match Preparation Hub** - Tactical game planning tools

### 📊 Advanced Analytics
- **Year-over-Year Filtering** - Compare performance across seasons (2024-2025)
- **Phase-Based Analysis** - Powerplay vs Post-Powerplay insights
- **Interactive Visualizations** - Dynamic charts and graphs
- **Real-time Data Processing** - Instant analysis of cricket statistics

### 🤖 AI-Driven Insights
- **Strategic Recommendations** - AI-generated tactical advice
- **Player Role Optimization** - Position and usage suggestions
- **Weakness Identification** - Areas for improvement analysis
- **Match-Specific Tips** - Situation-based strategic guidance

## 🚀 Quick Start

### Option 1: Streamlit Cloud (Recommended)
1. **Deploy instantly**: [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
2. **Repository**: Connect your GitHub repo
3. **Main file**: `ai_cricket_manager_dashboard.py`
4. **Add secret**: `GEMINI_API_KEY = "your_api_key"`

### Option 2: Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/cricket-dashboard.git
cd cricket-dashboard

# Install dependencies
pip install -r requirements_deployment.txt

# Set environment variable
export GEMINI_API_KEY=your_api_key_here

# Run application
streamlit run ai_cricket_manager_dashboard.py
```

## 📋 Requirements

### System Requirements
- Python 3.11+
- 2GB RAM minimum
- Internet connection for AI features

### API Requirements
- **Gemini API Key** (Free tier available)
  - Get from: [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Free quota: 60 requests per minute

### Dependencies
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
```

## 🏗️ Architecture

### Data Pipeline
```
Cricket Analytics JSON → Data Processing → AI Analysis → Interactive Dashboard
```

### Key Components
- **Frontend**: Streamlit web interface
- **Backend**: Pandas data processing
- **AI Engine**: Google Gemini integration
- **Visualization**: Plotly charts
- **Data**: Comprehensive cricket statistics (2024-2025)

## 📊 Data Overview

### Teams Included
- **ADKR**: Abu Dhabi Knight Riders
- **DC**: Desert Capitals
- **GG**: Gulf Giants
- **MIE**: MI Emirates
- **SW**: Sharjah Warriors
- **DV**: Dubai Vipers

### Statistics Available
- **Player Performance**: Runs, strike rates, averages, wickets
- **Bowling Analysis**: Economy rates, dot ball percentages, speeds
- **Matchup Data**: Head-to-head performance records
- **Phase Analysis**: Powerplay vs middle/death overs
- **Technique Breakdown**: Performance by batting/bowling style

## 🎮 Usage Guide

### For Team Managers
1. **Select Your Team** from the sidebar
2. **Choose Analysis Mode**:
   - Team Strategy Overview
   - Player Performance Analysis
   - Opposition Analysis
   - Match Preparation
   - AI Insights
3. **Apply Filters** (year, phase) as needed
4. **Generate AI Analysis** for strategic recommendations

### For Analysts
1. **Explore Data** using interactive filters
2. **Compare Performance** across different time periods
3. **Analyze Matchups** for tactical advantages
4. **Export Insights** for reports and presentations

### For Coaches
1. **Review Player Performance** for selection decisions
2. **Prepare Match Strategy** using opposition analysis
3. **Optimize Team Composition** based on phase performance
4. **Get AI Recommendations** for tactical improvements

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for advanced features)
STREAMLIT_THEME=light
DEBUG_MODE=false
```

### Streamlit Configuration
```toml
# .streamlit/config.toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#1f4e79"
backgroundColor = "#ffffff"
```

## 🚀 Deployment Options

### 1. Streamlit Cloud (Free)
- **Best for**: Quick deployment, sharing
- **Setup time**: 5 minutes
- **Cost**: Free
- **Guide**: See `deploy_streamlit_cloud.md`

### 2. Heroku
- **Best for**: Production apps
- **Setup time**: 10 minutes
- **Cost**: Free tier available
- **Command**: `git push heroku main`

### 3. Railway
- **Best for**: Modern deployment
- **Setup time**: 5 minutes
- **Cost**: Usage-based pricing
- **Features**: Auto-scaling, monitoring

### 4. Local/Self-hosted
- **Best for**: Development, private use
- **Setup time**: 2 minutes
- **Cost**: Infrastructure only
- **Control**: Full customization

## 📈 Performance

### Metrics
- **Load Time**: ~3-5 seconds (first load)
- **Response Time**: <1 second (interactions)
- **Data Size**: ~2MB cricket dataset
- **Memory Usage**: ~200MB runtime

### Optimization
- **Caching**: Automatic data caching
- **Lazy Loading**: On-demand AI analysis
- **Efficient Filtering**: Fast data operations
- **Responsive Design**: Works on all devices

## 🔒 Security

### Data Protection
- **No Personal Data**: Only cricket statistics
- **API Key Security**: Environment variable storage
- **HTTPS**: Secure connections
- **No Data Storage**: Stateless application

### Best Practices
- Keep API keys secure
- Use environment variables
- Regular key rotation
- Monitor usage quotas

## 🤝 Contributing

### Development Setup
```bash
# Fork repository
git clone https://github.com/yourusername/cricket-dashboard.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_deployment.txt

# Run in development mode
streamlit run ai_cricket_manager_dashboard.py
```

### Code Structure
```
├── ai_cricket_manager_dashboard.py  # Main application
├── cricket_analytics_data (1).json # Cricket dataset
├── requirements_deployment.txt     # Dependencies
├── .streamlit/                     # Configuration
└── deployment/                     # Deployment files
```

## 📞 Support

### Documentation
- **Deployment Guide**: `DEPLOYMENT_GUIDE_FINAL.md`
- **Streamlit Cloud**: `deploy_streamlit_cloud.md`
- **API Reference**: Google Gemini AI docs

### Troubleshooting
1. **Check logs** in deployment platform
2. **Verify API key** configuration
3. **Test locally** first
4. **Check data file** presence

### Common Issues
- **Module not found**: Update `requirements_deployment.txt`
- **API errors**: Check key and quota
- **Data loading**: Verify file path
- **Performance**: Check memory limits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent analysis
- **Streamlit** for the web framework
- **Plotly** for interactive visualizations
- **Cricket Analytics Team** for comprehensive data

---

## 🎯 Ready to Deploy?

Choose your deployment method:

1. **🌟 Streamlit Cloud** (Recommended for beginners)
2. **🚀 Heroku** (Production-ready)
3. **⚡ Railway** (Modern platform)
4. **🏠 Self-hosted** (Full control)

**Get your Gemini API key** → **Choose platform** → **Deploy in minutes!**

---

*Built with ❤️ for cricket team management and strategic analysis*