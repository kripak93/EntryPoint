#!/usr/bin/env python3
"""
Cricket Matchup Analyzer
Specialized tool for analyzing player vs player matchups
"""

import json
from typing import Dict, List, Tuple
import pandas as pd

class MatchupAnalyzer:
    def __init__(self, data_file: str):
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.teams = self.data.get('metadata', {}).get('teams', {})
        self.matchups = self.data.get('matchups', {})
        self.insights = self.data.get('insights', [])
    
    def find_explosive_batsmen(self, min_sr: float = 150, min_boundary_pct: float = 20) -> List[Dict]:
        """Find explosive batsmen across all teams"""
        explosive_batsmen = []
        
        for matchup_key, data in self.matchups.items():
            if 'batsmen' in data:
                for batsman in data['batsmen']:
                    sr = batsman.get('sr', 0)
                    bnd_pct = batsman.get('bnd', 0)
                    
                    if sr >= min_sr and bnd_pct >= min_boundary_pct:
                        explosive_batsmen.append({
                            'player': batsman['player'],
                            'strike_rate': sr,
                            'boundary_pct': bnd_pct,
                            'runs': batsman.get('runs', 0),
                            'phase': self._extract_phase(matchup_key),
                            'team': self._extract_team(matchup_key)
                        })
        
        return sorted(explosive_batsmen, key=lambda x: x['strike_rate'], reverse=True)
    
    def find_vulnerable_batsmen(self, min_wickets: int = 3, max_avg: float = 25) -> List[Dict]:
        """Find vulnerable batsmen who get out frequently"""
        vulnerable = []
        
        for matchup_key, data in self.matchups.items():
            if 'batsmen' in data:
                for batsman in data['batsmen']:
                    wks = batsman.get('wks', 0)
                    avg = batsman.get('avg', 0) or 0
                    
                    if wks >= min_wickets and avg <= max_avg and avg > 0:
                        vulnerable.append({
                            'player': batsman['player'],
                            'wickets': wks,
                            'average': avg,
                            'runs': batsman.get('runs', 0),
                            'phase': self._extract_phase(matchup_key),
                            'team': self._extract_team(matchup_key)
                        })
        
        return sorted(vulnerable, key=lambda x: (x['wickets'], -x['average']), reverse=True)
    
    def find_favorable_matchups(self, min_sr: float = 180) -> List[Dict]:
        """Find highly favorable batting matchups"""
        favorable = []
        
        for matchup_key, data in self.matchups.items():
            if 'matchups' in data:
                for matchup in data['matchups']:
                    if (matchup['advantage'] == 'batsman' and 
                        matchup['sr'] >= min_sr and 
                        matchup['wks'] == 0):
                        
                        favorable.append({
                            'batsman': matchup['batsman'],
                            'bowler': matchup['bowler'],
                            'strike_rate': matchup['sr'],
                            'runs': matchup['runs'],
                            'balls_faced': matchup['bf'],
                            'phase': self._extract_phase(matchup_key),
                            'team': self._extract_team(matchup_key)
                        })
        
        return sorted(favorable, key=lambda x: x['strike_rate'], reverse=True)
    
    def _extract_phase(self, matchup_key: str) -> str:
        """Extract phase from matchup key"""
        if 'PP' in matchup_key and 'Post' not in matchup_key:
            return 'Powerplay'
        elif 'Post_PP' in matchup_key:
            return 'Post Powerplay'
        else:
            return 'Overall'
    
    def _extract_team(self, matchup_key: str) -> str:
        """Extract team from matchup key"""
        for team_code in self.teams.keys():
            if matchup_key.startswith(team_code):
                return team_code
        return 'Unknown'