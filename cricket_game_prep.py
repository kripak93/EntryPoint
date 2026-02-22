#!/usr/bin/env python3
"""
Cricket Game Preparation System
Leverages comprehensive cricket analytics data for strategic game preparation
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import streamlit as st

@dataclass
class PlayerInsight:
    player: str
    strength_rating: float
    weakness_rating: float
    key_stats: Dict[str, Any]
    recommendations: List[str]

@dataclass
class MatchupAnalysis:
    batsman: str
    bowler: str
    runs: int
    balls_faced: int
    strike_rate: float
    wickets: int
    advantage: str
    recommendation: str

class CricketGamePrep:
    def __init__(self, data_file: str):
        """Initialize with cricket analytics data"""
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.teams = self.data.get('metadata', {}).get('teams', {})
        self.matchups = self.data.get('matchups', {})
        self.insights = self.data.get('insights', [])
        
    def get_team_analysis(self, team_code: str, phase: str = "Overall") -> Dict[str, Any]:
        """Get comprehensive team analysis for a specific phase"""
        team_data = {}
        
        # Find relevant matchups for the team
        for matchup_key, matchup_data in self.matchups.items():
            if team_code in matchup_key and phase in matchup_key:
                team_data[matchup_key] = matchup_data
        
        return team_data
    
    def analyze_batting_strengths(self, team_code: str, phase: str = "Overall") -> List[PlayerInsight]:
        """Analyze batting strengths for a team in specific phase"""
        insights = []
        team_data = self.get_team_analysis(team_code, phase)
        
        for matchup_key, data in team_data.items():
            if 'batsmen' in data:
                for batsman in data['batsmen']:
                    player = batsman['player']
                    sr = batsman.get('sr', 0)
                    avg = batsman.get('avg', 0)
                    dot_pct = batsman.get('dot', 0)
                    bnd_pct = batsman.get('bnd', 0)
                    
                    # Calculate strength rating
                    strength_rating = self._calculate_batting_strength(sr, avg, dot_pct, bnd_pct)
                    weakness_rating = self._calculate_batting_weakness(batsman.get('wks', 0), avg)
                    
                    recommendations = self._generate_batting_recommendations(sr, avg, dot_pct, bnd_pct)
                    
                    insights.append(PlayerInsight(
                        player=player,
                        strength_rating=strength_rating,
                        weakness_rating=weakness_rating,
                        key_stats={
                            'strike_rate': sr,
                            'average': avg,
                            'dot_percentage': dot_pct,
                            'boundary_percentage': bnd_pct,
                            'runs': batsman.get('runs', 0),
                            'balls_faced': batsman.get('bf', 0)
                        },
                        recommendations=recommendations
                    ))
        
        return sorted(insights, key=lambda x: x.strength_rating, reverse=True)
    
    def analyze_bowling_matchups(self, team_code: str, phase: str = "Overall") -> List[MatchupAnalysis]:
        """Analyze specific bowling matchups"""
        matchups = []
        team_data = self.get_team_analysis(team_code, phase)
        
        for matchup_key, data in team_data.items():
            if 'matchups' in data:
                for matchup in data['matchups']:
                    analysis = MatchupAnalysis(
                        batsman=matchup['batsman'],
                        bowler=matchup['bowler'],
                        runs=matchup['runs'],
                        balls_faced=matchup['bf'],
                        strike_rate=matchup['sr'],
                        wickets=matchup['wks'],
                        advantage=matchup['advantage'],
                        recommendation=self._generate_matchup_recommendation(matchup)
                    )
                    matchups.append(analysis)
        
        return matchups
    
    def get_phase_specific_strategy(self, team_code: str, phase: str) -> Dict[str, Any]:
        """Get phase-specific strategic recommendations"""
        strategy = {
            'phase': phase,
            'key_players': [],
            'tactical_focus': [],
            'risk_areas': [],
            'opportunities': []
        }
        
        # Get insights for this phase
        phase_insights = [insight for insight in self.insights 
                         if phase.replace(' ', '_') in insight.get('matchup', '')]
        
        for insight in phase_insights:
            if insight['type'] == 'strength':
                strategy['key_players'].append(insight['description'])
            elif insight['type'] == 'opportunity':
                strategy['opportunities'].append(insight['description'])
            elif insight['type'] == 'weakness':
                strategy['risk_areas'].append(insight['description'])
        
        return strategy
    
    def generate_game_plan(self, team_code: str, opposition: str = None) -> Dict[str, Any]:
        """Generate comprehensive game plan"""
        game_plan = {
            'team': self.teams.get(team_code, team_code),
            'powerplay_strategy': self.get_phase_specific_strategy(team_code, 'PP'),
            'middle_overs_strategy': self.get_phase_specific_strategy(team_code, 'Post PP'),
            'overall_strategy': self.get_phase_specific_strategy(team_code, 'Overall'),
            'key_matchups': self.analyze_bowling_matchups(team_code),
            'batting_order_insights': self.analyze_batting_strengths(team_code),
            'tactical_recommendations': self._generate_tactical_recommendations(team_code)
        }
        
        return game_plan
    
    def _calculate_batting_strength(self, sr: float, avg: float, dot_pct: float, bnd_pct: float) -> float:
        """Calculate batting strength rating (0-100)"""
        sr_score = min(sr / 200 * 40, 40)  # Max 40 points for SR
        avg_score = min(avg / 50 * 25, 25) if avg else 0  # Max 25 points for average
        dot_score = max(0, (50 - dot_pct) / 50 * 20)  # Max 20 points for low dot%
        bnd_score = min(bnd_pct / 30 * 15, 15)  # Max 15 points for boundary%
        
        return sr_score + avg_score + dot_score + bnd_score
    
    def _calculate_batting_weakness(self, wickets: int, avg: float) -> float:
        """Calculate batting weakness rating (0-100)"""
        wicket_penalty = min(wickets * 10, 50)  # Max 50 penalty for wickets
        avg_penalty = max(0, (20 - avg) / 20 * 30) if avg else 30  # Max 30 penalty for low avg
        
        return wicket_penalty + avg_penalty
    
    def _generate_batting_recommendations(self, sr: float, avg: float, dot_pct: float, bnd_pct: float) -> List[str]:
        """Generate batting recommendations based on stats"""
        recommendations = []
        
        if sr > 150:
            recommendations.append("Aggressive batsman - use in power-hitting situations")
        elif sr < 100:
            recommendations.append("Anchor role - focus on building partnerships")
        
        if dot_pct > 40:
            recommendations.append("Struggles with dot balls - target with tight bowling")
        
        if bnd_pct > 20:
            recommendations.append("Strong boundary hitter - avoid loose deliveries")
        
        return recommendations
    
    def _generate_matchup_recommendation(self, matchup: Dict) -> str:
        """Generate specific matchup recommendation"""
        if matchup['advantage'] == 'batsman':
            return f"Avoid bowling {matchup['bowler']} to {matchup['batsman']} - batsman dominates (SR: {matchup['sr']:.1f})"
        else:
            return f"Target {matchup['batsman']} with {matchup['bowler']} - bowler has advantage ({matchup['wks']} dismissals)"
    
    def _generate_tactical_recommendations(self, team_code: str) -> List[str]:
        """Generate tactical recommendations based on data analysis"""
        recommendations = []
        
        # Analyze team-specific insights
        team_insights = [insight for insight in self.insights 
                        if team_code in insight.get('matchup', '')]
        
        for insight in team_insights:
            if insight['priority'] == 'high':
                recommendations.append(f"HIGH PRIORITY: {insight['description']}")
            else:
                recommendations.append(insight['description'])
        
        return recommendations

def create_streamlit_app():
    """Create Streamlit app for game preparation"""
    st.set_page_config(page_title="Cricket Game Prep", page_icon="🏏", layout="wide")
    
    st.title("🏏 Cricket Game Preparation System")
    st.markdown("*Comprehensive analytics-driven game preparation*")
    
    # Initialize game prep system
    try:
        game_prep = CricketGamePrep('cricket_analytics_data (1).json')
    except FileNotFoundError:
        st.error("Cricket analytics data file not found!")
        return
    
    # Sidebar for team selection
    st.sidebar.header("Team Selection")
    teams = game_prep.teams
    selected_team = st.sidebar.selectbox("Select Team", list(teams.keys()), 
                                       format_func=lambda x: f"{x} - {teams[x]}")
    
    phase = st.sidebar.selectbox("Select Phase", ["Overall", "PP", "Post PP"])
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"Game Plan: {teams[selected_team]}")
        
        # Generate and display game plan
        game_plan = game_prep.generate_game_plan(selected_team)
        
        # Batting Analysis
        st.subheader("🏏 Batting Strengths")
        batting_insights = game_prep.analyze_batting_strengths(selected_team, phase)
        
        for insight in batting_insights[:5]:  # Top 5 batsmen
            with st.expander(f"{insight.player} (Strength: {insight.strength_rating:.1f})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Strike Rate", f"{insight.key_stats['strike_rate']:.1f}")
                    st.metric("Dot %", f"{insight.key_stats['dot_percentage']:.1f}%")
                with col_b:
                    st.metric("Average", f"{insight.key_stats.get('average', 'N/A')}")
                    st.metric("Boundary %", f"{insight.key_stats['boundary_percentage']:.1f}%")
                
                st.write("**Recommendations:**")
                for rec in insight.recommendations:
                    st.write(f"• {rec}")
        
        # Matchup Analysis
        st.subheader("⚔️ Key Matchups")
        matchups = game_prep.analyze_bowling_matchups(selected_team, phase)
        
        if matchups:
            matchup_df = pd.DataFrame([
                {
                    'Batsman': m.batsman,
                    'Bowler': m.bowler,
                    'SR': f"{m.strike_rate:.1f}",
                    'Runs': m.runs,
                    'Wickets': m.wickets,
                    'Advantage': m.advantage
                }
                for m in matchups[:10]  # Top 10 matchups
            ])
            st.dataframe(matchup_df, use_container_width=True)
    
    with col2:
        st.header("📊 Strategic Insights")
        
        # Phase-specific strategy
        strategy = game_prep.get_phase_specific_strategy(selected_team, phase)
        
        if strategy['key_players']:
            st.subheader("🌟 Key Players")
            for player in strategy['key_players']:
                st.success(player)
        
        if strategy['opportunities']:
            st.subheader("🚀 Opportunities")
            for opp in strategy['opportunities']:
                st.info(opp)
        
        if strategy['risk_areas']:
            st.subheader("⚠️ Risk Areas")
            for risk in strategy['risk_areas']:
                st.warning(risk)
        
        # Tactical recommendations
        st.subheader("🎯 Tactical Focus")
        tactical_recs = game_prep._generate_tactical_recommendations(selected_team)
        for rec in tactical_recs:
            if "HIGH PRIORITY" in rec:
                st.error(rec)
            else:
                st.write(f"• {rec}")

if __name__ == "__main__":
    create_streamlit_app()