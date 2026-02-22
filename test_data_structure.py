"""
Quick test to check the data structure
"""

import json
import pandas as pd

# Load the cricket data
with open('cricket_analytics_data (1).json', 'r') as f:
    cricket_data = json.load(f)

print("Available matchup keys:")
for key in cricket_data['matchups'].keys():
    print(f"  - {key}")

# Check the structure of player data
for matchup_key, matchup_data in cricket_data['matchups'].items():
    if 'players' in matchup_data and matchup_data['players']:
        print(f"\nSample player data from {matchup_key}:")
        sample_player = matchup_data['players'][0]
        print("Available fields:")
        for field, value in sample_player.items():
            print(f"  - {field}: {value}")
        break

# Check ADKR team data specifically
adkr_data = {k: v for k, v in cricket_data['matchups'].items() if k.startswith('ADKR')}
print(f"\nADKR matchups found: {len(adkr_data)}")

for key in adkr_data.keys():
    print(f"  - {key}")
    if 'players' in adkr_data[key]:
        print(f"    Players: {len(adkr_data[key]['players'])}")
        if adkr_data[key]['players']:
            sample = adkr_data[key]['players'][0]
            print(f"    Sample fields: {list(sample.keys())}")