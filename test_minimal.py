"""Minimal test - step by step"""
print("Step 1: Starting...")

print("Step 2: Importing streamlit...")
import streamlit as st
print("✓ Streamlit imported")

print("Step 3: Importing pandas...")
import pandas as pd
print("✓ Pandas imported")

print("Step 4: Checking CSV file size...")
import os
csv_size = os.path.getsize('ipl_data.csv')
print(f"✓ CSV file size: {csv_size:,} bytes ({csv_size / 1024 / 1024:.2f} MB)")

print("Step 5: Reading first 100 rows of CSV...")
df = pd.read_csv('ipl_data.csv', nrows=100)
print(f"✓ Sample loaded: {len(df)} rows, {len(df.columns)} columns")

print("\nStep 6: Trying full CSV load...")
df_full = pd.read_csv('ipl_data.csv')
print(f"✓ Full CSV loaded: {len(df_full)} rows")

print("\n✓✓✓ All tests passed!")
