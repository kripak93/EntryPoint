#!/usr/bin/env python3
"""
Quick Cricket Game Preparation Tool
Command-line interface for rapid game preparation analysis
"""

import json
import argparse
from typing import Dict, List, Any
from tabulate import tabulate
import sys

class QuickGamePrep:
    def __init__(self, data_file: str):
        """Initialize with cricket analytics data"""
        try:
            with open(data_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Data file '{data_file}' not found!")
            sys.exit(1)
        
        self.teams = self.data.get('metadata', {}).get('teams', {})
        self.matchups = self.data.get('matchups', {})
        self.insights = self.data.get('insights', [])
    
    def show_teams(self):
        """Display available teams"""
        print("\n🏏 Available Teams:")
        print("=" * 50)
        for code, name in self.teams.items():
            print(f"{code:4} - {name}")
        print()
    
    def get_team_brief(self, team_code: str, phase: str = "Overall"):
        """Get quick team brief"""
        if team_code not in self.teams:
            print(f"❌ Team '{team_code}' not found!")
            return
        
        print(f"\n🏏 {self.teams[team_code]} - {phase} Analysis")
        print("=" * 60)
        
        # Get team-specific insights
        team_insights = [insight for insight in self.insights 
                        if team_code in insight.get('matchup', '') and 
                        phase.replace(' ', '_') in insight.get('matchup', '')]
        
        if team_insights:
            print("\n📊 Key Insights:")
            for insight in team_insights:
                icon = insight.get('icon', '•')
                priority = insight.get('priority', 'medium').upper()
                print(f"{icon} [{priority}] {insight['title']}")
                print(f"   {insight['description']}")
        
        # Get batting analysis
        self._show_batting_analysis(team_code, phase)
        
        # Get matchup analysis
        self._show_key_matchups(team_code, phase)
    
    def _show_batting_analysis(self, team_code: str, phase: str):
        """Show batting analysis for team"""
        print(f"\n🏏 Top Batsmen ({phase}):")
        
        # Find relevant matchup data
        batting_data = []
        for matchup_key, data in self.matchups.items():
            if team_code in matchup_key and phase.replace(' ', '_') in matchup_key:
                if 'batsmen' in data:
                    for batsman in data['batsmen'][:5]:  # Top 5
                        batting_data.append([
                            batsman['player'],
                            f"{batsman.get('sr', 0):.1f}",
                            f"{batsman.get('avg', 'N/A')}",
                            f"{batsman.get('runs', 0)}",
                            f"{batsman.get('wks', 0)}",
                            f"{batsman.get('bnd', 0):.1f}%"
                        ])
                    break
        
        if batting_data:
            headers = ['Player', 'Strike Rate', 'Average', 'Runs', 'Wickets', 'Boundary%']
            print(tabulate(batting_data, headers=headers, tablefmt='grid'))
    
    def _show_key_matchups(self, team_code: str, phase: str):
        """Show key matchups for team"""
        print(f"\n⚔️ Key Matchups ({phase}):")
        
        matchup_data = []
        for matchup_key, data in self.matchups.items():
            if team_code in matchup_key and phase.replace(' ', '_') in matchup_key:
                if 'matchups' in data:
                    # Show top 5 favorable and unfavorable matchups
                    favorable = [m for m in data['matchups'] if m['advantage'] == 'batsman'][:3]
                    unfavorable = [m for m in data['matchups'] if m['advantage'] == 'bowler'][:3]
                    
                    print("\n✅ Favorable Matchups:")
                    for matchup in favorable:
                        print(f"   {matchup['batsman']} vs {matchup['bowler']} - SR: {matchup['sr']:.1f}")
                    
                    print("\n❌ Challenging Matchups:")
                    for matchup in unfavorable:
                        print(f"   {matchup['batsman']} vs {matchup['bowler']} - {matchup['wks']} dismissals")
                    break
    
    def compare_teams(self, team1: str, team2: str, phase: str = "Overall"):
        """Compare two teams"""
        if team1 not in self.teams or team2 not in self.teams:
            print("❌ One or both teams not found!")
            return
        
        print(f"\n🆚 {self.teams[team1]} vs {self.teams[team2]} - {phase}")
        print("=" * 70)
        
        # Get head-to-head data if available
        h2h_key = f"{team1}_vs_{team2}_{phase.replace(' ', '_')}"
        alt_h2h_key = f"{team2}_vs_{team1}_{phase.replace(' ', '_')}"
        
        if h2h_key in self.matchups:
            self._show_head_to_head(h2h_key, team1, team2)
        elif alt_h2h_key in self.matchups:
            self._show_head_to_head(alt_h2h_key, team2, team1)
        else:
            print("📊 No direct head-to-head data available")
            print("\nShowing individual team analysis:")
            self.get_team_brief(team1, phase)
            self.get_team_brief(team2, phase)
    
    def _show_head_to_head(self, matchup_key: str, team1: str, team2: str):
        """Show head-to-head analysis"""
        data = self.matchups[matchup_key]
        
        if 'batsmen' in data:
            print(f"\n🏏 {self.teams[team1]} Batting Performance:")
            batting_data = []
            for batsman in data['batsmen'][:5]:
                batting_data.append([
                    batsman['player'],
                    f"{batsman.get('sr', 0):.1f}",
                    f"{batsman.get('avg', 'N/A')}",
                    f"{batsman.get('runs', 0)}",
                    f"{batsman.get('wks', 0)}"
                ])
            
            headers = ['Player', 'Strike Rate', 'Average', 'Runs', 'Wickets']
            print(tabulate(batting_data, headers=headers, tablefmt='simple'))
        
        if 'matchups' in data:
            print(f"\n⚔️ Key Individual Matchups:")
            for matchup in data['matchups'][:5]:
                advantage_icon = "✅" if matchup['advantage'] == 'batsman' else "❌"
                print(f"{advantage_icon} {matchup['batsman']} vs {matchup['bowler']} - "
                      f"SR: {matchup['sr']:.1f}, Wickets: {matchup['wks']}")
    
    def get_phase_comparison(self, team_code: str):
        """Compare team performance across phases"""
        if team_code not in self.teams:
            print(f"❌ Team '{team_code}' not found!")
            return
        
        print(f"\n📈 {self.teams[team_code]} - Phase Comparison")
        print("=" * 60)
        
        phases = ["PP", "Post_PP", "Overall"]
        phase_data = []
        
        for phase in phases:
            # Get insights for this phase
            phase_insights = [insight for insight in self.insights 
                            if team_code in insight.get('matchup', '') and 
                            phase in insight.get('matchup', '')]
            
            strengths = len([i for i in phase_insights if i['type'] == 'strength'])
            opportunities = len([i for i in phase_insights if i['type'] == 'opportunity'])
            weaknesses = len([i for i in phase_insights if i['type'] == 'weakness'])
            
            phase_data.append([
                phase.replace('_', ' '),
                strengths,
                opportunities,
                weaknesses
            ])
        
        headers = ['Phase', 'Strengths', 'Opportunities', 'Weaknesses']
        print(tabulate(phase_data, headers=headers, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Quick Cricket Game Preparation Tool')
    parser.add_argument('--data', default='cricket_analytics_data (1).json', 
                       help='Path to cricket analytics data file')
    parser.add_argument('--teams', action='store_true', help='Show available teams')
    parser.add_argument('--team', help='Get team brief (e.g., ADKR)')
    parser.add_argument('--phase', default='Overall', 
                       choices=['Overall', 'PP', 'Post PP'], help='Analysis phase')
    parser.add_argument('--compare', nargs=2, metavar=('TEAM1', 'TEAM2'), 
                       help='Compare two teams')
    parser.add_argument('--phase-comparison', help='Compare team across phases')
    
    args = parser.parse_args()
    
    # Initialize game prep
    game_prep = QuickGamePrep(args.data)
    
    if args.teams:
        game_prep.show_teams()
    elif args.team:
        game_prep.get_team_brief(args.team.upper(), args.phase)
    elif args.compare:
        game_prep.compare_teams(args.compare[0].upper(), args.compare[1].upper(), args.phase)
    elif args.phase_comparison:
        game_prep.get_phase_comparison(args.phase_comparison.upper())
    else:
        print("🏏 Quick Cricket Game Preparation Tool")
        print("\nUsage examples:")
        print("  python quick_game_prep.py --teams")
        print("  python quick_game_prep.py --team ADKR --phase PP")
        print("  python quick_game_prep.py --compare ADKR GG --phase Overall")
        print("  python quick_game_prep.py --phase-comparison ADKR")
        print("\nUse --help for more options")

if __name__ == "__main__":
    main()