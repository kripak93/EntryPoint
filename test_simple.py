print("Starting import test...")
import pandas as pd
print("Pandas imported OK")

print("Trying to read CSV...")
df = pd.read_csv('ipl_data.csv')
print(f"CSV loaded: {len(df)} rows")
print("Done!")
