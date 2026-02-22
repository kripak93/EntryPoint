#!/usr/bin/env python3
"""
Debug version to identify the issue
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

st.title("🔍 Debug Cricket App")

# Test 1: Check data loading
st.header("1. Data Loading Test")
try:
    df = pd.read_csv('ipl_data.csv')
    st.success(f"✅ IPL data loaded: {len(df):,} rows")
except Exception as e:
    st.error(f"❌ IPL data failed: {e}")

# Test 2: Check cricket analytics
st.header("2. Cricket Analytics Test")
try:
    import json
    with open('cricket_analytics_data (1).json', 'r') as f:
        cricket_data = json.load(f)
    st.success(f"✅ Cricket data loaded: {len(cricket_data.get('teams', {}))} teams")
except Exception as e:
    st.error(f"❌ Cricket data failed: {e}")

# Test 3: Check API key
st.header("3. API Key Test")
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    st.success(f"✅ API key found: {api_key[:10]}...")
else:
    st.error("❌ No API key found")

# Test 4: Check backend import
st.header("4. Backend Import Test")
try:
    from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
    st.success("✅ Backend imported successfully")
    
    # Try to initialize
    try:
        analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv', api_key=api_key)
        st.success("✅ Backend initialized successfully")
        st.info(f"Model: {analytics.model_name}")
    except Exception as e:
        st.error(f"❌ Backend initialization failed: {e}")
        st.code(str(e))
        
except Exception as e:
    st.error(f"❌ Backend import failed: {e}")
    st.code(str(e))

# Test 5: Simple Streamlit functionality
st.header("5. Basic Streamlit Test")
if st.button("Test Button"):
    st.balloons()
    st.success("✅ Streamlit working!")