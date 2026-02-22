"""Test without streamlit - just the data loading"""
print("Step 1: Starting...")

print("Step 2: Importing pandas...")
import pandas as pd
print("✓ Pandas imported")

print("Step 3: Checking CSV file size...")
import os
csv_size = os.path.getsize('ipl_data.csv')
print(f"✓ CSV file size: {csv_size:,} bytes ({csv_size / 1024 / 1024:.2f} MB)")

print("Step 4: Reading first 100 rows of CSV...")
df = pd.read_csv('ipl_data.csv', nrows=100)
print(f"✓ Sample loaded: {len(df)} rows, {len(df.columns)} columns")

print("\nStep 5: Trying full CSV load...")
df_full = pd.read_csv('ipl_data.csv')
print(f"✓ Full CSV loaded: {len(df_full)} rows")

print("\nStep 6: Testing strategy engine import...")
from corrected_strategy_engine import CorrectedIPLStrategyEngine
print("✓ Strategy engine imported")

print("\nStep 7: Creating engine instance...")
engine = CorrectedIPLStrategyEngine()
print("✓ Engine created (data not loaded yet)")

print("\n✓✓✓ All tests passed (except Streamlit)!")
