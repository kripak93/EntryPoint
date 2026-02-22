"""
Consolidated IPL Analytics Toolkit
All analysis functions in one place
"""

import pandas as pd
import os
from dotenv import load_dotenv
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics

class IPLAnalyticsToolkit:
    """Consolidated toolkit for all IPL analysis functions"""
    
    def __init__(self):
        load_dotenv()
        self.df = pd.read_csv('ipl_data.csv')
        self.analytics = None
        
    def setup_ai(self, season_filter=None):
        """Setup AI analytics with optional season filter"""
        try:
            self.analytics = EnhancedGeminiIPLAnalytics('ipl_data.csv', season_filter=season_filter)
            print(f"✅ AI setup complete: {self.analytics.model_name}")
            if hasattr(self.analytics, 'season'):
                print(f"📅 Season: {self.analytics.season}")
            return True
        except Exception as e:
            print(f"❌ AI setup failed: {e}")
            return False
    
    def validate_data(self):
        """Validate the IPL data file"""
        print("🏏 IPL Data Validation")
        print("=" * 30)
        
        if not os.path.exists('ipl_data.csv'):
            print("❌ ipl_data.csv not found")
            return False
        
        try:
            df = pd.read_csv('ipl_data.csv')
            print(f"✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Show teams and players
            if 'Team' in df.columns:
                teams = sorted(df['Team'].unique())
                print(f"🏟️  Teams: {', '.join(teams)}")
            
            if 'Player' in df.columns:
                player_count = df['Player'].nunique()
                print(f"👤 Unique players: {player_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading data: {e}")
            return False
    
    def analyze_seasons(self):
        """Analyze data by seasons (2024 vs 2025)"""
        print("📅 Season Analysis")
        print("=" * 30)
        
        # Extract year from date
        self.df['Year'] = pd.to_datetime(self.df['Date⬆']).dt.year
        
        print(f"📊 Total records: {len(self.df)}")
        print(f"📅 Date range: {self.df['Date⬆'].min()} to {self.df['Date⬆'].max()}")
        
        # Show data by year
        year_counts = self.df['Year'].value_counts().sort_index()
        for year, count in year_counts.items():
            print(f"  {year}: {count:,} records")
        
        # Top bowlers by year
        print(f"\n🏏 Top bowlers by year (min 2 overs):")
        for year in sorted(self.df['Year'].unique()):
            year_data = self.df[self.df['Year'] == year]
            valid_bowlers = year_data[year_data['O'] >= 2.0]
            top_bowlers = valid_bowlers.nlargest(5, 'W')[['Player', 'Team', 'W', 'O', 'Econ']]
            
            print(f"\n  📊 {year} Season:")
            if not top_bowlers.empty:
                print(top_bowlers.to_string(index=False))
    
    def test_api(self):
        """Test the Gemini API connection"""
        print("🔑 Testing Gemini API")
        print("=" * 30)
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("❌ API key not found or not set")
            return False
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        if self.setup_ai():
            # Test query
            result = self.analytics.smart_analyze("Who has the best economy rate?")
            print(f"🧪 Test query successful")
            print(f"Response preview: {result['gemini_response'][:100]}...")
            return True
        
        return False
    
    def analyze_ball_position(self, player_name="JJ Bumrah"):
        """Analyze player performance by ball position within an over"""
        print(f"🎯 Ball Position Analysis: {player_name}")
        print("=" * 50)
        
        player_data = self.df[self.df['Player'] == player_name].copy()
        
        if player_data.empty:
            print(f"❌ No data found for {player_name}")
            return
        
        # Extract ball position
        player_data['Ball_Position'] = player_data['Overs'].astype(str).str.split('.').str[1].astype(int)
        
        # Compare 1st vs 6th ball
        first_ball = player_data[player_data['Ball_Position'] == 1]
        last_ball = player_data[player_data['Ball_Position'] == 6]
        
        if not first_ball.empty and not last_ball.empty:
            print(f"1st Ball: {len(first_ball)} balls, {first_ball['R'].sum()} runs")
            print(f"6th Ball: {len(last_ball)} balls, {last_ball['R'].sum()} runs")
            
            first_avg = round(first_ball['R'].sum() / len(first_ball), 2)
            last_avg = round(last_ball['R'].sum() / len(last_ball), 2)
            
            print(f"Average: 1st ball = {first_avg}, 6th ball = {last_avg}")
            print(f"Better on: {'1st ball' if first_avg < last_avg else '6th ball'}")
        else:
            print("❌ Insufficient data for comparison")
    
    def compare_seasons_ai(self):
        """AI-powered season comparison"""
        print("🤖 AI Season Comparison")
        print("=" * 30)
        
        if not self.setup_ai():
            return
        
        # Analyze current season
        result = self.analytics.smart_analyze("Who are the top 3 bowlers by economy rate?")
        print("Top bowlers analysis:")
        print(result['gemini_response'][:300] + "..." if len(result['gemini_response']) > 300 else result['gemini_response'])
    
    def quick_stats(self):
        """Show quick statistics"""
        print("📈 Quick Stats")
        print("=" * 20)
        
        # Top economy bowlers (min 2 overs)
        valid_bowlers = self.df[self.df['O'] >= 2.0]
        valid_bowlers = valid_bowlers[valid_bowlers['Econ'] != '-']
        valid_bowlers['Econ'] = pd.to_numeric(valid_bowlers['Econ'], errors='coerce')
        top_economy = valid_bowlers.nsmallest(5, 'Econ')[['Player', 'Team', 'O', 'W', 'Econ']]
        
        print("🎯 Top 5 Economy Rates:")
        print(top_economy.to_string(index=False))
        
        # Top wicket takers
        top_wickets = self.df.nlargest(5, 'W')[['Player', 'Team', 'W', 'O', 'Econ']]
        print("\n🏆 Top 5 Wicket Takers:")
        print(top_wickets.to_string(index=False))

def main():
    """Main function with menu"""
    toolkit = IPLAnalyticsToolkit()
    
    print("🏏 IPL Analytics Toolkit")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Validate Data")
        print("2. Test API Connection")
        print("3. Quick Stats")
        print("4. Season Analysis")
        print("5. Ball Position Analysis")
        print("6. AI Season Comparison")
        print("7. Setup AI for Custom Queries")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-7): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            toolkit.validate_data()
        elif choice == '2':
            toolkit.test_api()
        elif choice == '3':
            toolkit.quick_stats()
        elif choice == '4':
            toolkit.analyze_seasons()
        elif choice == '5':
            player = input("Enter player name (default: JJ Bumrah): ").strip() or "JJ Bumrah"
            toolkit.analyze_ball_position(player)
        elif choice == '6':
            toolkit.compare_seasons_ai()
        elif choice == '7':
            season = input("Enter season (2024/2025) or press Enter for all: ").strip()
            season_filter = int(season) if season.isdigit() else None
            if toolkit.setup_ai(season_filter):
                print("✅ AI ready! You can now use the Streamlit app or ask custom queries.")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()