"""
Analyze the IPL data by year (2024 vs 2025)
"""

import pandas as pd

def analyze_by_years():
    """Analyze IPL data separated by years"""
    
    print("📅 Analyzing IPL data by years...")
    
    # Load data
    df = pd.read_csv('ipl_data.csv')
    
    # Extract year from date
    df['Year'] = pd.to_datetime(df['Date⬆']).dt.year
    
    print(f"📊 Total records: {len(df)}")
    print(f"📅 Date range: {df['Date⬆'].min()} to {df['Date⬆'].max()}")
    
    # Show data by year
    print(f"\n📈 Data distribution by year:")
    year_counts = df['Year'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"  {year}: {count:,} records")
    
    # Show date ranges by year
    print(f"\n📅 Date ranges by year:")
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        print(f"  {year}: {year_data['Date⬆'].min()} to {year_data['Date⬆'].max()}")
    
    # Compare top players by year
    print(f"\n🏏 Top bowlers by year (by wickets, min 2 overs):")
    
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        valid_bowlers = year_data[year_data['O'] >= 2.0]
        top_bowlers = valid_bowlers.nlargest(5, 'W')[['Player', 'Team', 'W', 'O', 'Econ']]
        
        print(f"\n  📊 {year} Season:")
        if not top_bowlers.empty:
            print(top_bowlers.to_string(index=False))
        else:
            print("    No data with minimum criteria")
    
    # Compare teams by year
    print(f"\n🏟️  Teams by year:")
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        teams = sorted(year_data['Team'].unique())
        print(f"  {year}: {teams}")
    
    # Save separate files for each year
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        filename = f'ipl_data_{year}.csv'
        year_data.to_csv(filename, index=False)
        print(f"\n💾 Saved {year} data: {filename} ({len(year_data):,} records)")

if __name__ == "__main__":
    analyze_by_years()