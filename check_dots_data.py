import pandas as pd

df = pd.read_csv('ipl_data_mens_only.csv')

# Get one match for A Badoni
sample = df[(df['Batsman'] == 'A Badoni') & (df['Match⬆'] == 'LAT20 # 13409')].sort_values('Overs')

print("Match: LAT20 # 13409 - A Badoni")
print(sample[['Batsman', 'Overs', 'R.1', 'B', '0', '4', '6', 'R']].to_string())

print("\n\nChecking what the columns mean:")
print("R.1 = Cumulative runs by batsman")
print("B = Cumulative balls faced by batsman")
print("0 = ???")
print("4 = ???")
print("6 = ???")
print("R = Runs scored on THIS ball")
