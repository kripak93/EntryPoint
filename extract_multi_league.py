"""
Extract selected T20 leagues from cricviz_all_pages_combined.csv
Leagues: IPL, SMAT, MLC, ILT20, CPL, T20 Blast, The Hundred, BBL, SA20
"""
import pandas as pd

# Team -> Competition mapping
COMPETITION_TEAMS = {
    "IPL": [
        "Chennai Super Kings", "Mumbai Indians", "Royal Chal Bengaluru",
        "Kolkata Knight Riders", "Delhi Capitals", "Gujarat Titans",
        "Lucknow Super Giants", "Punjab Kings", "Rajasthan Royals",
        "Sunrisers Hyderabad"
    ],
    "SA20": [
        "Durban's Super Giants", "Joburg Super Kings", "MI Cape Town",
        "Paarl Royals", "Pretoria Capitals", "Sunrisers Eastern Cape"
    ],
    "BBL": [
        "Adelaide Strikers", "Brisbane Heat", "Hobart Hurricanes",
        "Melbourne Renegades", "Melbourne Stars", "Perth Scorchers",
        "Sydney Sixers", "Sydney Thunder", "Hobart Hurricanes XI"
    ],
    "The Hundred": [
        "Birmingham Phoenix Men", "London Spirit Men",
        "Manchester Originals Men", "Northern Brave Men",
        "Oval Invincibles Men", "Southern Brave Men",
        "Superchargers", "Trent Rockets Men", "Welsh Fire Men"
    ],
    "T20 Blast": [
        "Bears", "Birmingham Bears", "Derbyshire Falcons", "Durham",
        "Essex", "Glamorgan", "Gloucestershire", "Hampshire Hawks",
        "Kent Spitfires", "Lancashire Lightning", "Leicestershire Foxes",
        "Middlesex", "Northants Steelbacks", "Nottinghamshire Outlaws",
        "Somerset", "Surrey", "Sussex Sharks", "Worcestershire Rapids",
        "Yorkshire", "Yorkshire Vikings"
    ],
    "CPL": [
        "Barbados Royals", "Guyana Amazon Warriors",
        "Trinbago Knight Riders", "St Kitts Patriots",
        "Saint Lucia Kings", "Antigua & Barbuda Falcons",
        "A&B Falcons"
    ],
    "ILT20": [
        "Abu Dhabi Knight Riders", "Desert Vipers", "Dubai Capitals",
        "Gulf Giants", "MI Emirates", "Sharjah Warriors", "Sharjah Warriorz"
    ],
    "MLC": [
        "LA Knight Riders", "MI New York", "San Francisco Unicorns",
        "Seattle Orcas", "Texas Super Kings", "Washington Freedom"
    ],
    "SMAT": [
        "Andhra", "Baroda", "Bengal", "Bihar", "Delhi", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Hyderabad", "Jharkhand",
        "Jammu and Kashmir", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Mumbai", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Saurashtra",
        "Services", "Sikkim", "Tamil Nadu", "Tripura", "Uttar Pradesh",
        "Uttarakhand", "Vidarbha", "Chandigarh", "Arunachal Pradesh",
        "Assam", "Chhattisgarh"
    ],
}

# Build reverse lookup: team -> competition
team_to_comp = {}
for comp, teams in COMPETITION_TEAMS.items():
    for team in teams:
        team_to_comp[team] = comp

print("Loading cricviz_all_pages_combined.csv...")
df = pd.read_csv('cricviz_all_pages_combined.csv', low_memory=False)
print(f"Total rows: {len(df):,}")

# Filter to LAT20 only
df = df[df['Match⬆'].str.startswith('LAT20', na=False)]
print(f"LAT20 rows: {len(df):,}")

# Map competition from Opposition (batting team)
df['Competition'] = df['Opposition'].map(team_to_comp)

# Keep only rows that matched a competition
matched = df[df['Competition'].notna()].copy()
print(f"\nMatched rows: {len(matched):,}")
print(f"\nBy competition:")
print(matched['Competition'].value_counts())

print(f"\nUnmatched teams (not in any league):")
unmatched_teams = df[df['Competition'].isna()]['Opposition'].value_counts()
print(unmatched_teams.head(20))

# Save
output = 'multi_league_data.csv'
matched.to_csv(output, index=False)
print(f"\n✅ Saved {len(matched):,} rows to {output}")
print(f"Competitions: {sorted(matched['Competition'].unique())}")
print(f"Teams: {matched['Opposition'].nunique()}")
print(f"Players: {matched['Batsman'].nunique()}")
