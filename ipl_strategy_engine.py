"""
IPL Strategy Engine - Game Prep & Scouting Mode
Generates tactical briefs for batsmen vs different bowler types
"""

import pandas as pd
import numpy as np
from enhanced_gemini_ipl_backend import EnhancedGeminiIPLAnalytics
import os
from dotenv import load_dotenv

class IPLStrategyEngine:
    """Strategic analysis engine for IPL game preparation"""
    
    def __init__(self):
        load_dotenv()
        self.df = pd.read_csv('ipl_data.csv')
        self.analytics = None
        
        # Map your columns to standard format
        self.column_mapping = {
            'Match⬆': 'match_id',
            'Date⬆': 'date', 
            'Ground Name': 'venue',
            'Team.1': 'team_batting',
            'Team': 'team_bowling',
            'Overs': 'over',
            'Batsman': 'batsman',
            'Player': 'bowler',
            'Technique': 'bowler_style',
            'R.1': 'runs_batsman',
            'Ext': 'runs_extras',
            'R': 'runs_total',
            'Wkt': 'dismissal_kind',
            'Length': 'ball_type',
            'Shot Type': 'shot_type',
            'Zone': 'field_zone'
        }
        
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare and standardize the dataset"""
        # Rename columns to standard format
        for old_col, new_col in self.column_mapping.items():
            if old_col in self.df.columns:
                self.df[new_col] = self.df[old_col]
        
        # Extract over and ball numbers
        if 'Overs' in self.df.columns:
            self.df['over_num'] = self.df['Overs'].astype(str).str.split('.').str[0].astype(float)
            self.df['ball_num'] = self.df['Overs'].astype(str).str.split('.').str[1].astype(float)
        
        # Define phases
        self.df['phase'] = self.df['over_num'].apply(
            lambda x: 'Powerplay' if x <= 6 else 'Post Powerplay'
        )
        
        # Standardize bowler styles
        self.df['bowler_style_clean'] = self.df['bowler_style'].fillna('Unknown').str.lower()
        
        # Map to standard categories
        style_mapping = {
            'right pace': 'RAF',
            'left pace': 'LAF', 
            'left orthodox': 'LAO',
            'off break': 'Off Break',
            'leg break': 'Leg Spin',
            'right orthodox': 'Off Break'
        }
        
        self.df['bowler_category'] = self.df['bowler_style_clean'].map(style_mapping).fillna('Other')
        
        print(f"✅ Data prepared: {len(self.df)} records")
        print(f"📊 Bowler categories: {self.df['bowler_category'].value_counts().to_dict()}")
    
    def generate_scouting_brief(self, batsman_name, bowler_type='RAF'):
        """Generate comprehensive scouting brief for batsman vs bowler type"""
        
        print(f"🎯 Generating Scouting Brief: {batsman_name} vs {bowler_type}")
        print("=" * 60)
        
        # Filter data for the batsman
        batsman_data = self.df[self.df['batsman'] == batsman_name].copy()
        
        if batsman_data.empty:
            return f"❌ No data found for {batsman_name}"
        
        # Filter by bowler type
        bowler_data = batsman_data[batsman_data['bowler_category'] == bowler_type].copy()
        
        if bowler_data.empty:
            return f"❌ No data found for {batsman_name} vs {bowler_type} bowlers"
        
        # Generate brief
        brief = self._create_tactical_brief(batsman_name, bowler_type, bowler_data)
        
        return brief
    
    def _create_tactical_brief(self, batsman_name, bowler_type, data):
        """Create detailed tactical brief in Gulf Giants style"""
        
        brief = f"""
# {batsman_name.upper()} VS {bowler_type} BOWLERS
{'=' * 50}

## OVERVIEW
- Total balls faced vs {bowler_type}: {len(data)}
- Total runs scored: {data['runs_batsman'].sum()}
- Overall Strike Rate: {self._calculate_strike_rate(data):.1f}
- Dismissals: {len(data[data['dismissal_kind'] != '-'])}

"""
        
        # Powerplay Analysis
        powerplay_data = data[data['phase'] == 'Powerplay']
        brief += self._analyze_phase(powerplay_data, "POWERPLAY (Overs 1-6)")
        
        # Post Powerplay Analysis  
        post_pp_data = data[data['phase'] == 'Post Powerplay']
        brief += self._analyze_phase(post_pp_data, "POST POWERPLAY (Overs 7-20)")
        
        # Tactical Summary
        brief += self._generate_tactical_summary(batsman_name, bowler_type, data, powerplay_data, post_pp_data)
        
        return brief
    
    def _analyze_phase(self, phase_data, phase_name):
        """Analyze specific phase (Powerplay or Post Powerplay)"""
        
        if phase_data.empty:
            return f"\n## {phase_name}\n❌ No data available\n"
        
        analysis = f"\n## {phase_name}\n"
        analysis += f"Balls faced: {len(phase_data)} | Runs: {phase_data['runs_batsman'].sum()} | SR: {self._calculate_strike_rate(phase_data):.1f}\n\n"
        
        # Strike Rate by Length
        analysis += "### Strike Rate by Length:\n"
        length_sr = self._calculate_sr_by_category(phase_data, 'ball_type')
        for length, sr in length_sr.items():
            analysis += f"- {length}: {sr:.1f}\n"
        
        # Strike Rate by Zone
        analysis += "\n### Strike Rate by Zone:\n"
        zone_sr = self._calculate_sr_by_category(phase_data, 'field_zone')
        for zone, sr in list(zone_sr.items())[:6]:  # Top 6 zones
            analysis += f"- {zone}: {sr:.1f}\n"
        
        # Boundary Analysis
        boundaries = self._analyze_boundaries(phase_data)
        analysis += f"\n### Boundary Analysis:\n"
        analysis += f"- Fours: {boundaries['fours']} ({boundaries['four_rate']:.1f}%)\n"
        analysis += f"- Sixes: {boundaries['sixes']} ({boundaries['six_rate']:.1f}%)\n"
        
        # Dismissal Analysis
        dismissals = phase_data[phase_data['dismissal_kind'] != '-']
        if not dismissals.empty:
            analysis += f"\n### Dismissal Pattern:\n"
            dismissal_types = dismissals['dismissal_kind'].value_counts()
            for dismissal, count in dismissal_types.items():
                analysis += f"- {dismissal}: {count}\n"
        
        return analysis
    
    def _calculate_strike_rate(self, data):
        """Calculate strike rate"""
        if len(data) == 0:
            return 0.0
        return (data['runs_batsman'].sum() / len(data)) * 100
    
    def _calculate_sr_by_category(self, data, category_col):
        """Calculate strike rate by category (length/zone)"""
        sr_dict = {}
        
        for category in data[category_col].dropna().unique():
            cat_data = data[data[category_col] == category]
            if len(cat_data) >= 3:  # Minimum 3 balls for meaningful SR
                sr = self._calculate_strike_rate(cat_data)
                sr_dict[category] = sr
        
        # Sort by strike rate (descending)
        return dict(sorted(sr_dict.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_boundaries(self, data):
        """Analyze boundary hitting patterns"""
        total_balls = len(data)
        fours = len(data[data['4'] == 1]) if '4' in data.columns else 0
        sixes = len(data[data['6'] == 1]) if '6' in data.columns else 0
        
        return {
            'fours': fours,
            'sixes': sixes,
            'four_rate': (fours / total_balls * 100) if total_balls > 0 else 0,
            'six_rate': (sixes / total_balls * 100) if total_balls > 0 else 0
        }
    
    def _generate_tactical_summary(self, batsman_name, bowler_type, all_data, pp_data, post_pp_data):
        """Generate tactical summary and recommendations"""
        
        summary = f"\n## TACTICAL SUMMARY\n"
        summary += f"{'=' * 30}\n\n"
        
        # Initial Plan (First 6 balls)
        summary += "### INITIAL PLAN (First 6 balls):\n"
        
        # Find most effective length
        length_sr = self._calculate_sr_by_category(all_data, 'ball_type')
        if length_sr:
            best_length = min(length_sr.items(), key=lambda x: x[1])
            summary += f"- Bowl {best_length[0]} length (lowest SR: {best_length[1]:.1f})\n"
        
        # Find most effective zone
        zone_sr = self._calculate_sr_by_category(all_data, 'field_zone')
        if zone_sr:
            best_zone = min(zone_sr.items(), key=lambda x: x[1])
            summary += f"- Target {best_zone[0]} area (lowest SR: {best_zone[1]:.1f})\n"
        
        # Shut Down Lines/Lengths
        summary += "\n### SHUT DOWN LINES/LENGTHS:\n"
        if length_sr:
            for length, sr in list(length_sr.items())[:3]:
                if sr < 100:  # Below run-a-ball
                    summary += f"- {length}: {sr:.1f} SR ✅\n"
        
        # Hot Zones to Protect
        summary += "\n### HOT ZONES TO PROTECT:\n"
        boundaries = self._analyze_boundaries(all_data)
        if zone_sr:
            hot_zones = [zone for zone, sr in list(zone_sr.items())[:3] if sr > 150]
            for zone in hot_zones:
                summary += f"- {zone}: High scoring zone ⚠️\n"
        
        # Key Dismissal Opportunities
        summary += "\n### KEY DISMISSAL OPPORTUNITIES:\n"
        dismissals = all_data[all_data['dismissal_kind'] != '-']
        if not dismissals.empty:
            dismissal_lengths = dismissals['ball_type'].value_counts()
            for length, count in dismissal_lengths.head(2).items():
                summary += f"- {length} length: {count} dismissals\n"
        
        # Phase-specific recommendations
        summary += "\n### PHASE-SPECIFIC STRATEGY:\n"
        pp_sr = self._calculate_strike_rate(pp_data) if not pp_data.empty else 0
        post_pp_sr = self._calculate_strike_rate(post_pp_data) if not post_pp_data.empty else 0
        
        if pp_sr > post_pp_sr:
            summary += f"- More aggressive in Powerplay (SR: {pp_sr:.1f} vs {post_pp_sr:.1f})\n"
            summary += f"- Tighten up in middle overs\n"
        else:
            summary += f"- Builds innings through middle overs (SR: {post_pp_sr:.1f} vs {pp_sr:.1f})\n"
            summary += f"- Early pressure crucial\n"
        
        return summary
    
    def generate_team_brief(self, opposition_team, our_bowlers):
        """Generate comprehensive team brief against opposition"""
        
        print(f"🏟️ Generating Team Brief vs {opposition_team}")
        print("=" * 50)
        
        # Get opposition batting lineup
        opp_batsmen = self.df[self.df['team_batting'] == opposition_team]['batsman'].unique()
        
        team_brief = f"""
# TEAM BRIEF: vs {opposition_team.upper()}
{'=' * 50}

## OPPOSITION BATTING LINEUP ANALYSIS
"""
        
        # Analyze top 6 batsmen
        for i, batsman in enumerate(opp_batsmen[:6], 1):
            team_brief += f"\n### {i}. {batsman}\n"
            
            # Quick summary vs our bowler types
            for bowler_type in ['RAF', 'LAF', 'Off Break', 'Leg Spin']:
                batsman_data = self.df[
                    (self.df['batsman'] == batsman) & 
                    (self.df['bowler_category'] == bowler_type)
                ]
                
                if not batsman_data.empty:
                    sr = self._calculate_strike_rate(batsman_data)
                    dismissals = len(batsman_data[batsman_data['dismissal_kind'] != '-'])
                    team_brief += f"- vs {bowler_type}: SR {sr:.1f}, {dismissals} dismissals\n"
        
        return team_brief

def main():
    """Interactive strategy engine"""
    
    engine = IPLStrategyEngine()
    
    print("🏏 IPL Strategy Engine - Game Prep Mode")
    print("=" * 50)
    
    while True:
        print("\nChoose analysis type:")
        print("1. Individual Batsman Scouting Brief")
        print("2. Team Brief vs Opposition")
        print("3. Available Players")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            batsman = input("Enter batsman name: ").strip()
            bowler_type = input("Enter bowler type (RAF/LAF/LAO/Off Break/Leg Spin): ").strip() or 'RAF'
            
            brief = engine.generate_scouting_brief(batsman, bowler_type)
            print(brief)
            
            # Save to file
            filename = f"scouting_brief_{batsman.replace(' ', '_')}_{bowler_type}.md"
            with open(filename, 'w') as f:
                f.write(brief)
            print(f"\n💾 Brief saved as: {filename}")
            
        elif choice == '2':
            team = input("Enter opposition team: ").strip()
            bowlers = input("Enter our bowler types (comma separated): ").strip().split(',')
            
            brief = engine.generate_team_brief(team, bowlers)
            print(brief)
            
        elif choice == '3':
            print("\n👤 Available batsmen:")
            batsmen = engine.df['batsman'].dropna().unique()
            for i, batsman in enumerate(sorted(batsmen)[:20], 1):
                print(f"{i}. {batsman}")

if __name__ == "__main__":
    main()