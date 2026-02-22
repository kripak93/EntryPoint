# 🏏 AI Cricket Manager Dashboard - Deployment Guide

## 📋 Deployment Files Overview

### Core Application Files
- `ai_cricket_manager_dashboard.py` - Main dashboard application
- `cricket_analytics_data (1).json` - Cricket analytics dataset
- `requirements_deployment.txt` - Python dependencies
- `.env.template` - Environment variables template

### Platform-Specific Files
- `Procfile` - Heroku deployment
- `runtime.txt` - Python version specification
- `app.py` - Alternative entry point
- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml` - Streamlit Cloud secrets

## 🚀 Deployment Options

### 1. Streamlit Cloud (Recommended)

**Steps:**
1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select repository and branch
5. Set main file: `ai_cricket_manager_dashboard.py`
6. Add secrets in Streamlit Cloud dashboard:
   ```
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

**Advantages:**
- Free hosting
- Automatic deployments
- Built for Streamlit apps
- Easy secret management

### 2. Heroku

**Steps:**
1. Install Heroku CLI
2. Create Heroku app:
   ```bash
   heroku create your-cricket-dashboard
   ```
3. Set environment variables:
   ```bash
   heroku config:set GEMINI_API_KEY=your_actual_api_key_here
   ```
4. Deploy:
   ```bash
   git add .
   git commit -m "Deploy cricket dashboard"
   git push heroku main
   ```

### 3. Railway

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add environment variable:
   - `GEMINI_API_KEY`: your_actual_api_key_here
4. Deploy automatically

### 4. Render

**Steps:**
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Set build command: `pip install -r requirements_deployment.txt`
5. Set start command: `streamlit run ai_cricket_manager_dashboard.py --server.port $PORT --server.address 0.0.0.0`
6. Add environment variable:
   - `GEMINI_API_KEY`: your_actual_api_key_here

## 🔧 Environment Setup

### Required Environment Variables
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Getting Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy the key for deployment

## 📁 File Structure for Deployment

```
cricket-dashboard/
├── ai_cricket_manager_dashboard.py    # Main app
├── cricket_analytics_data (1).json   # Data file
├── requirements_deployment.txt        # Dependencies
├── Procfile                          # Heroku config
├── runtime.txt                       # Python version
├── app.py                           # Alternative entry
├── .streamlit/
│   ├── config.toml                  # Streamlit config
│   └── secrets.toml                 # Local secrets (don't commit)
├── .env.template                    # Environment template
└── README.md                        # Documentation
```

## ⚠️ Important Notes

### Security
- Never commit `.env` or `secrets.toml` files
- Use platform-specific secret management
- Keep API keys secure

### Data File
- Ensure `cricket_analytics_data (1).json` is included in deployment
- File size should be under platform limits (usually 100MB)

### Performance
- App loads ~2MB of cricket data on startup
- First load may take 10-15 seconds
- Subsequent interactions are fast

## 🧪 Testing Before Deployment

### Local Testing
```bash
# Install dependencies
pip install -r requirements_deployment.txt

# Set environment variable
export GEMINI_API_KEY=your_key_here

# Run locally
streamlit run ai_cricket_manager_dashboard.py
```

### Deployment Checklist
- [ ] All files present
- [ ] API key configured
- [ ] Requirements file updated
- [ ] Data file included
- [ ] Platform-specific config set
- [ ] Local testing successful

## 🔍 Troubleshooting

### Common Issues

**1. Module Import Errors**
- Check `requirements_deployment.txt` has all dependencies
- Verify Python version compatibility

**2. API Key Issues**
- Ensure environment variable is set correctly
- Check API key is valid and has quota

**3. Data Loading Errors**
- Verify `cricket_analytics_data (1).json` is in root directory
- Check file permissions and size

**4. Port Issues**
- Use platform-provided PORT environment variable
- Default to 8501 for local development

### Platform-Specific Troubleshooting

**Streamlit Cloud:**
- Check logs in dashboard
- Verify secrets are set correctly
- Ensure repository is public or properly connected

**Heroku:**
- Check logs: `heroku logs --tail`
- Verify Procfile syntax
- Check dyno status

**Railway/Render:**
- Check build logs
- Verify start command
- Check environment variables

## 📞 Support

If you encounter issues:
1. Check platform-specific logs
2. Verify all environment variables
3. Test locally first
4. Check API key quota and validity

## 🎯 Features Available After Deployment

- **Team Strategy Analysis** - AI-powered team insights
- **Player Performance** - Detailed player analytics
- **Opposition Analysis** - Head-to-head matchup intelligence
- **Match Preparation** - Tactical game planning
- **Year Filtering** - Historical performance comparison
- **Interactive Visualizations** - Charts and graphs
- **AI Recommendations** - Strategic advice for team management

---

**Ready for deployment!** 🚀 Choose your preferred platform and follow the steps above.