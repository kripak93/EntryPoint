# Deploy to Render

## Steps:

### 1. Create render.yaml
```yaml
services:
  - type: web
    name: ipl-analytics
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run enhanced_gemini_streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

### 2. Deploy
1. Go to https://render.com/
2. Connect GitHub repo
3. Add environment variable
4. Deploy

## Pros:
✅ Free tier available
✅ Easy deployment
✅ Good documentation
✅ Automatic SSL

## Cons:
❌ Free tier has limitations
❌ Can be slow on free tier