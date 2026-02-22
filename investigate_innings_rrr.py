"""
Deep dive into innings and RRR data to understand the structure
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("INVESTIGATING INNINGS AND RRR DATA")
print("=" * 80)

# Load raw ball-by-ball data
df = pd.read_csv('ipl_data_mens_only.csv')
print(f"\n1. TOTAL DATA: {len(df)} balls")

# Check Bat column (innings indicator)
print("\n2. BAT COLUMN (Innings Indicator):")
print(df['Bat'].value_counts())
print(f"   - '1st' = {(df['Bat'] == '1st').sum()} balls")
print(f"   - '2nd' = {(df['Bat'] == '2nd').sum()} balls")

# Check RRreq availability
df['RRreq_num'] = pd.to_numeric(df['RRreq'], errors='coerce')
print("\n3. RRreq (Required Run Rate) AVAILABILITY:")
print(f"   - Total balls with RRreq: {df['RRreq_num'].notna().sum()}")
print(f"   - Total balls without RRreq: {df['RRreq_num'].isna().sum()}")

print("\n4. RRreq BY INNINGS:")
rrr_by_innings = df.groupby('Bat').agg({
    'RRreq_num': ['count', lambda x: x.notna().sum(), 'mean', 'min', 'max']
})
rrr_by_innings.columns = ['Total Balls', 'Balls with RRreq', 'Avg RRreq', 'Min RRreq', 'Max RRreq']
print(rrr_by_innings)

# Sample matches to understand the pattern
print("\n5. SAMPLE MATCH ANALYSIS:")
sample_matches = df['Match⬆'].unique()[:3]

for match in sample_matches:
    match_df = df[df['Match⬆'] == match].copy()
    print(f"\n   Match: {match}")
    print(f"   Total balls: {len(match_df)}")
    
    # Check innings
    innings_dist = match_df['Bat'].value_counts()
    print(f"   Innings distribution: {innings_dist.to_dict()}")
    
    # Check RRreq by innings
    for innings in ['1st', '2nd']:
        innings_df = match_df[match_df['Bat'] == innings]
        if len(innings_df) > 0:
            rrr_count = innings_df['RRreq_num'].notna().sum()
            print(f"   - {innings} innings: {len(innings_df)} balls, {rrr_count} with RRreq")
            
            if rrr_count > 0:
                print(f"     RRreq range: {innings_df['RRreq_num'].min():.2f} to {innings_df['RRreq_num'].max():.2f}")
                # Show first few balls with RRreq
                sample = innings_df[innings_df['RRreq_num'].notna()].head(3)
                print(f"     Sample balls:")
                for idx, row in sample.iterrows():
                    print(f"       Over {row['Overs']}: {row['Batsman']}, RRreq={row['RRreq']}, Target={row['Target']}, RReq={row['RReq']}")

# Check what Target column means
print("\n6. TARGET COLUMN ANALYSIS:")
print(f"   Balls with Target data: {df['Target'].notna().sum()}")
target_by_innings = df.groupby('Bat')['Target'].agg(['count', lambda x: x.notna().sum()])
target_by_innings.columns = ['Total Balls', 'Balls with Target']
print(target_by_innings)

# Sample some 1st innings balls with RRreq
print("\n7. SAMPLE 1ST INNINGS BALLS WITH RRreq:")
first_with_rrr = df[(df['Bat'] == '1st') & (df['RRreq_num'].notna())].head(10)
cols = ['Match⬆', 'Batsman', 'Bat', 'Overs', 'RRreq', 'RReq', 'BRem', 'Target', 'Score', 'Opposition']
print(first_with_rrr[cols].to_string())

# Sample some 2nd innings balls
print("\n8. SAMPLE 2ND INNINGS BALLS (checking for RRreq):")
second_sample = df[df['Bat'] == '2nd'].head(20)
print(second_sample[cols].to_string())

# Check if there's a pattern with Target
print("\n9. UNDERSTANDING THE PATTERN:")
print("   Checking if RRreq in 1st innings means they're CHASING...")

# Get a match and check both innings
sample_match = df['Match⬆'].unique()[0]
match_df = df[df['Match⬆'] == sample_match].copy()

first_inn = match_df[match_df['Bat'] == '1st']
second_inn = match_df[match_df['Bat'] == '2nd']

print(f"\n   Match: {sample_match}")
print(f"   1st innings team: {first_inn['Opposition'].iloc[0] if len(first_inn) > 0 else 'N/A'}")
print(f"   1st innings has RRreq: {first_inn['RRreq_num'].notna().any()}")
if first_inn['RRreq_num'].notna().any():
    print(f"   1st innings Target: {first_inn['Target'].iloc[0]}")
    print(f"   1st innings first RRreq: {first_inn[first_inn['RRreq_num'].notna()]['RRreq'].iloc[0]}")

print(f"\n   2nd innings team: {second_inn['Opposition'].iloc[0] if len(second_inn) > 0 else 'N/A'}")
print(f"   2nd innings has RRreq: {second_inn['RRreq_num'].notna().any()}")

# Check Toss and Bat columns relationship
print("\n10. TOSS AND BAT DECISION:")
print("    Checking if 'Bat' column relates to toss decision...")
toss_bat = df.groupby(['Bat', 'Toss']).size().reset_index(name='count')
print(toss_bat.head(20))

print("\n11. HYPOTHESIS:")
print("    Based on the data:")
print("    - RRreq appears ONLY in '1st' innings")
print("    - This suggests '1st' might mean 'first to bat in THIS match'")
print("    - OR it could mean the team batting first is CHASING a DLS target")
print("    - Need to check if Target column indicates a chase scenario")

# Check if Target exists in both innings
print("\n12. TARGET PRESENCE BY INNINGS:")
for innings in ['1st', '2nd']:
    innings_df = df[df['Bat'] == innings]
    has_target = innings_df['Target'].notna().sum()
    unique_targets = innings_df['Target'].nunique()
    print(f"    {innings} innings: {has_target} balls with Target, {unique_targets} unique targets")
    if has_target > 0:
        print(f"    Target range: {innings_df['Target'].min()} to {innings_df['Target'].max()}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("The 'Bat' column shows '1st' and '2nd' but RRreq only exists in '1st'.")
print("This likely means:")
print("  1. The dataset may be filtered to only show chase scenarios")
print("  2. OR '1st' represents the team chasing (batting second chronologically)")
print("  3. OR there's DLS-adjusted targets for the first batting team")
print("\nWe should focus on using Personal Impact (player SR vs RRR) rather than")
print("Team RRR Impact, since individual performance is what matters for player analysis.")
