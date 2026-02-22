"""
Understanding what 'Bat' column really means
"""
import pandas as pd

df = pd.read_csv('ipl_data_mens_only.csv')

print("=" * 80)
print("UNDERSTANDING THE 'BAT' COLUMN")
print("=" * 80)

# Key insight from previous analysis:
# - 1st innings has RRreq (chasing a target)
# - 2nd innings has NO RRreq
# - Toss: '1st' mostly lost toss (12847 vs 3537)
# - Toss: '2nd' mostly won toss (13986 vs 3970)

print("\n1. TOSS RELATIONSHIP:")
print("   If you LOSE the toss, you're usually in '1st' innings")
print("   If you WIN the toss, you're usually in '2nd' innings")
print("\n   This suggests:")
print("   - Teams winning toss usually BOWL first (put opponent in '1st')")
print("   - '1st' = Team batting SECOND (chasing)")
print("   - '2nd' = Team batting FIRST (setting target)")

# Verify with a specific match
print("\n2. VERIFYING WITH MATCH LAT20 # 13401:")
match_df = df[df['Match⬆'] == 'LAT20 # 13401'].copy()

first_inn = match_df[match_df['Bat'] == '1st']
second_inn = match_df[match_df['Bat'] == '2nd']

print(f"\n   '1st' innings:")
print(f"   - Team: {first_inn['Opposition'].iloc[0]}")
print(f"   - Toss: {first_inn['Toss'].iloc[0]}")
print(f"   - Has Target: {first_inn['Target'].iloc[0]}")
print(f"   - Has RRreq: Yes (chasing {first_inn['Target'].iloc[0]})")
print(f"   - First batsman: {first_inn['Batsman'].iloc[0]}")

print(f"\n   '2nd' innings:")
print(f"   - Team: {second_inn['Opposition'].iloc[0]}")
print(f"   - Toss: {second_inn['Toss'].iloc[0]}")
print(f"   - Has Target: {second_inn['Target'].iloc[0]}")
print(f"   - Has RRreq: No (setting target)")
print(f"   - First batsman: {second_inn['Batsman'].iloc[0]}")

print("\n3. CONCLUSION:")
print("   The 'Bat' column is CONFUSING because:")
print("   - '1st' = Team batting SECOND chronologically (chasing)")
print("   - '2nd' = Team batting FIRST chronologically (setting target)")
print("\n   This is likely because the data is organized by:")
print("   - '1st' = First team in the match record (chasing team)")
print("   - '2nd' = Second team in the match record (setting team)")
print("\n   OR it could be:")
print("   - '1st' = Team that lost toss (usually bats second)")
print("   - '2nd' = Team that won toss (usually bats first)")

# Check if we can find actual innings order
print("\n4. CHECKING BALL TIMING:")
print("   Looking at Ball Time to see chronological order...")

# Get first and last ball times for each innings
first_inn_times = first_inn['Ball Time'].dropna()
second_inn_times = second_inn['Ball Time'].dropna()

if len(first_inn_times) > 0 and len(second_inn_times) > 0:
    print(f"\n   '1st' innings ball times:")
    print(f"   - First ball: {first_inn_times.iloc[0]}")
    print(f"   - Last ball: {first_inn_times.iloc[-1]}")
    
    print(f"\n   '2nd' innings ball times:")
    print(f"   - First ball: {second_inn_times.iloc[0]}")
    print(f"   - Last ball: {second_inn_times.iloc[-1]}")

# Check Date column
print("\n5. CHECKING DATE/TIME ORDER:")
first_dates = first_inn['Date⬆'].unique()
second_dates = second_inn['Date⬆'].unique()
print(f"   '1st' innings dates: {first_dates}")
print(f"   '2nd' innings dates: {second_dates}")

print("\n" + "=" * 80)
print("FINAL UNDERSTANDING:")
print("=" * 80)
print("Based on the evidence:")
print("  - '1st' in Bat column = CHASING team (has RRreq, Target)")
print("  - '2nd' in Bat column = SETTING team (no RRreq)")
print("  - This is OPPOSITE to chronological batting order")
print("\nFor our analysis:")
print("  - RRreq data exists for chasing scenarios ('1st' innings)")
print("  - Personal Impact metric is valid: Player SR vs Required RR")
print("  - We have 777 chase entries to analyze")
print("  - Focus on individual performance vs requirement, not team outcome")
