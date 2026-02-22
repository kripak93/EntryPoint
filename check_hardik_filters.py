import pandas as pd

df = pd.read_csv('processed_entry_points_ballbyball.csv')
hh = df[df['Player'] == 'HH Pandya']
chase = hh[hh['Entry_RR_Required'].notna()]

print('HH Pandya chase entries:')
print(f'  Total: {len(chase)}')
print(f'  With BF >= 5: {(chase["BF"] >= 5).sum()}')
print(f'  With BF >= 10: {(chase["BF"] >= 10).sum()}')

print('\nWith new defaults (all teams, BF >= 5):')
filtered = chase[chase['BF'] >= 5]
print(f'  Entries shown: {len(filtered)}')

print('\nBreakdown by balls faced:')
print(chase['BF'].value_counts().sort_index())
