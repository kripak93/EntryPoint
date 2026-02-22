import pandas as pd

df = pd.read_csv('processed_entry_points_ballbyball.csv')
hh = df[df['Player'] == 'HH Pandya'].copy()

print('=== Hardik Pandya Personal Impact ===')
cols = ['Player', 'Entry_Over', 'Entry_RR_Required', 'Runs', 'BF', 
        'Final_Strike_Rate', 'Player_Run_Rate', 'Personal_Impact', 'Impact_Runs']
print(hh[cols].sort_values('Personal_Impact', ascending=False).to_string())

print('\n=== Summary ===')
print(f'Avg Personal Impact: {hh["Personal_Impact"].mean():.2f}')
print(f'Positive impacts: {(hh["Personal_Impact"] > 0).sum()}')
print(f'Negative impacts: {(hh["Personal_Impact"] < 0).sum()}')
print(f'Avg Strike Rate: {hh["Final_Strike_Rate"].mean():.1f}')
