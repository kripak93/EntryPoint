# Deploy to Railway

## Steps:

### 1. Create Procfile
```
web: streamlit run enhanced_gemini_streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

### 2. Update for Railway
Add to requirements.txt:
```
streamlit>=1.28.0
pandas>=2.0.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
```

### 3. Deploy
1. Go to https://railway.app/
2. Connect GitHub repo
3. Add environment variable: `GEMINI_API_KEY`
4. Deploy automatically

### 4. Custom Domain (Optional)
Get URL like: https://your-app.railway.app/

## Pros:
✅ $5/month starter plan
✅ Easy deployment
✅ Custom domains
✅ Good performance
✅ Supports any Python app

## Cons:
❌ Not free (but very cheap)
❌ Requires credit card