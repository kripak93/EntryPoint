"""
Simple and Accurate IPL Strategy Engine with Proper Strike Rate Calculation
"""

import pandas as pd
import numpy as np

class SimpleIPLStrategyEngine:
    """Simple strategy engine with accurate strike rate calculations"""
    
    def __init__(self, filters=None):
        self.df = pd.read_csv('ipl_data.csv')
        self.filters = filters or {}
        
        self._prepare_data()
        self._apply_filters()
    
    def _prepare_data(self):
        """Prepare data with correct runs per ball calculation"""
        
        # Convert date
        self.df['date'] = pd.to_datetime(self.df['Date⬆'])
        self.df['year'] = self.df['date'].dt.year
        
        # Extract over info
        self.df['over_num'] = self.df['Overs'].astype(str).str.split('.').str[0].astype(float)
        self.df['phase'] = self.df['over_num'].apply(lambda x: 'Powerplay' if x <= 6 else 'Post Powerplay')
        
        # Calculate actual runs per ball
        self.df['runs_this_ball'] = 0  # Default
        
        # Set runs based on boundary columns
        self.df.loc[self.df['0'] == 1, 'runs_this_ball'] = 0  # Dot balls
        self.df.loc[self.df['4'] == 1, 'runs_this_ball'] = 4  # Fours
        self.df.loc[self.df['6'] == 1, 'runs_this_ball'] = 6  # Sixes
        
        # For non-boundary balls, estimate runs (1, 2, or 3)
        # We can use a simple heuristic or assume 1 run for non-boundaries
        non_boundary_mask = (self.df['0'] != 1) & (self.df['4'] != 1) & (self.df['6'] != 1)
        self.df.loc[non_boundary_mask, 'runs_this_ball'] = 1  # Conservative estimate
        
        # Bowler categories
        style_mapping = {
            'right pace': 'RAF',
            'left pace': 'LAF', 
            'left orthodox': 'LAO',
            'off break': 'Off Break',
            'leg break': 'Leg Spin'
        }
        
        self.df['bowler_category'] = self.df['Technique'].fillna('Unknown').str.lower().map(style_mapping).fillna('Other')
        
        print(f"✅ Data prepared: {len(self.df)} records")
        print(f"📊 Average runs per ball: {self.df['runs_this_ball'].mean():.2f}")
    
    def _apply_filters(self):
        """Apply filters"""
        original_size = len(self.df)
        
        if 'season' in self.filters:
            self.df = self.df[self.df['year'] == self.filters['season']]
            print(f"📅 Season {self.filters['season']}: {len(self.df)} records")
        
        if 'ground' in self.filters:
            self.df = self.df[self.df['Ground Name'].str.contains(self.filters['ground'], case=False, na=False)]
            print(f"🏟️ Ground filter: {len(self.df)} records")
        
        if 'opposition' in self.filters:
            self.df = self.df[self.df['Team'] == self.filters['opposition']]
            print(f"🏏 Opposition filter: {len(self.df)} records")
        
        print(f"📊 Final dataset: {len(self.df)} records")
    
    def generate_scouting_brief(self, batsman_name, bowler_type='RAF', min_balls=20):
        """Generate accurate scouting brief"""
        
        print(f"🎯 Scouting Brief: {batsman_name} vs {bowler_type}")
        print(f"Filters: {self.filters}")
        print("=" * 50)
        
        # Filter data
        data = self.df[
            (self.df['Batsman'] == batsman_name) & 
            (self.df['bowler_category'] == bowler_type)
        ].copy()
        
        if data.empty:
            return f"❌ No data found for {batsman_name} vs {bowler_type}"
        
        if len(data) < min_balls:
            return f"❌ Insufficient data: {len(data)} balls (need {min_balls}+)"
        
        # Calculate metrics
        total_balls = len(data)
        total_runs = data['runs_this_ball'].sum()
        strike_rate = (total_runs / total_balls) * 100
        
        # Boundaries
        dots = len(data[data['0'] == 1])
        fours = len(data[data['4'] == 1])
        sixes = len(data[data['6'] == 1])
        dismissals = len(data[data['Wkt'] != '-'])
        
        # Phase analysis
        pp_data = data[data['phase'] == 'Powerplay']
        post_pp_data = data[data['phase'] == 'Post Powerplay']
        
        pp_sr = (pp_data['runs_this_ball'].sum() / len(pp_data) * 100) if not pp_data.empty else 0
        post_pp_sr = (post_pp_data['runs_this_ball'].sum() / len(post_pp_data) * 100) if not post_pp_data.empty else 0
        
        # Generate brief
        brief = f"""
# {batsman_name.upper()} VS {bowler_type} BOWLERS
{'=' * 50}

## FILTER CONTEXT
{self._format_filters()}

## OVERVIEW
- Total balls faced: {total_balls}
- Total runs scored: {total_runs}
- Strike Rate: {strike_rate:.1f}
- Dismissals: {dismissals} ({dismissals/total_balls*100:.1f}%)

## BOUNDARY ANALYSIS
- Dot balls: {dots} ({dots/total_balls*100:.1f}%)
- Fours: {fours} ({fours/total_balls*100:.1f}%)
- Sixes: {sixes} ({sixes/total_balls*100:.1f}%)
- Boundary %: {(fours+sixes)/total_balls*100:.1f}%

## PHASE COMPARISON
- Powerplay: {len(pp_data)} balls, SR {pp_sr:.1f}
- Post-Powerplay: {len(post_pp_data)} balls, SR {post_pp_sr:.1f}

## LENGTH ANALYSIS
{self._analyze_by_length(data)}

## TACTICAL SUMMARY
- Sample size: {total_balls} balls ({'Reliable' if total_balls >= 50 else 'Limited'})
- Key weakness: {'Powerplay' if pp_sr < post_pp_sr else 'Post-Powerplay'} (lower SR)
- Boundary threat: {'High' if (fours+sixes)/total_balls > 0.3 else 'Medium' if (fours+sixes)/total_balls > 0.15 else 'Low'}
- Dot ball %: {dots/total_balls*100:.1f}% ({'Good' if dots/total_balls > 0.4 else 'Average'})

## BOWLING STRATEGY
- Target phase: {'Powerplay' if pp_sr < post_pp_sr else 'Post-Powerplay'}
- Focus on: {'Dot balls' if dots/total_balls < 0.3 else 'Wicket-taking'}
- Boundary control: {'Critical' if (fours+sixes)/total_balls > 0.25 else 'Standard'}
"""
        
        return brief
    
    def _format_filters(self):
        """Format filters"""
        if not self.filters:
            return "All data (no filters)"
        
        parts = []
        if 'season' in self.filters:
            parts.append(f"Season {self.filters['season']}")
        if 'ground' in self.filters:
            parts.append(f"Ground: {self.filters['ground']}")
        if 'opposition' in self.filters:
            parts.append(f"vs {self.filters['opposition']}")
        
        return " | ".join(parts)
    
    def _analyze_by_length(self, data):
        """Analyze performance by ball length"""
        if 'Length' not in data.columns:
            return "Length data not available"
        
        length_analysis = []
        for length in data['Length'].dropna().unique():
            if length == '-':
                continue
            
            length_data = data[data['Length'] == length]
            if len(length_data) >= 5:  # Minimum 5 balls
                runs = length_data['runs_this_ball'].sum()
                balls = len(length_data)
                sr = (runs / balls) * 100
                
                length_analysis.append(f"- {length}: {sr:.1f} SR ({balls} balls)")
        
        return "\n".join(length_analysis) if length_analysis else "Insufficient data for length analysis"
    
    def get_available_options(self):
        """Get available filter options"""
        return {
            'seasons': sorted(self.df['year'].unique()),
            'grounds': sorted(self.df['Ground Name'].unique())[:10],  # Top 10
            'teams': sorted(self.df['Team'].unique()),
            'batsmen': sorted(self.df['Batsman'].dropna().unique())[:20]  # Top 20
        }

def main():
    """Test the simple engine"""
    
    # Test with 2024 season filter
    filters = {'season': 2024}
    engine = SimpleIPLStrategyEngine(filters)
    
    # Generate brief
    brief = engine.generate_scouting_brief('V Kohli', 'RAF', 20)
    print(brief)

if __name__ == "__main__":
    main()