"""
ReAct Cricket Strategy Agent
Implements Reasoning + Acting pattern for intelligent cricket analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import re
import json
from difflib import get_close_matches

class CricketDataAnalyzer:
    """Data analysis tools for the ReAct agent"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.entry_points = self._calculate_entry_points()
    
    def _calculate_entry_points(self):
        """Calculate true entry points"""
        df = self.df.copy()
        
        # Check if data is already processed (has Entry_Over column)
        if 'Entry_Over' in df.columns and 'Final_Strike_Rate' in df.columns:
            # Data is already processed, just return it
            return df
        
        # Process raw data
        df['Strike_Rate'] = pd.to_numeric(df.get('RR', df.get('Strike_Rate', 0)), errors='coerce')
        df['Runs'] = pd.to_numeric(df['Runs'], errors='coerce')
        df['BF'] = pd.to_numeric(df['BF'], errors='coerce')
        df['Over'] = pd.to_numeric(df.get('Over', df.get('Entry_Over', 0)), errors='coerce')
        df['Dot_Pct'] = pd.to_numeric(df.get('Dot%', 0), errors='coerce')
        df['Bnd_Pct'] = pd.to_numeric(df.get('Bnd%', 0), errors='coerce')
        
        # Handle Year column
        if 'Year' not in df.columns:
            if 'Span⬇' in df.columns:
                df['Year'] = df['Span⬇'].str.split('-').str[0]
            else:
                df['Year'] = '2024'  # Default year
        
        # If Over column exists, calculate entry points with progression
        if 'Over' in df.columns and df['Over'].notna().any():
            # Group by player-match to get entry point and progression
            entry_points = df.groupby(['Player', 'Team', 'Match', 'Year']).agg({
                'Over': ['min', 'max', 'count'],  # Entry, exit, overs played
                'Runs': 'sum',
                'BF': 'sum',
                'Strike_Rate': 'mean',
                'Dot_Pct': 'mean',
                'Bnd_Pct': 'mean'
            }).reset_index()
            
            # Flatten column names
            entry_points.columns = ['Player', 'Team', 'Match', 'Year', 'Entry_Over', 'Exit_Over', 'Overs_Played', 'Runs', 'BF', 'Strike_Rate', 'Dot_Pct', 'Bnd_Pct']
            
            # Calculate innings duration
            entry_points['Innings_Duration'] = entry_points['Exit_Over'] - entry_points['Entry_Over'] + 1
        else:
            # Data might already have Entry_Over
            entry_points = df.copy()
            if 'Entry_Over' not in entry_points.columns:
                entry_points['Entry_Over'] = 1  # Default
        
        # Create entry phase categories
        entry_points['Entry_Phase'] = entry_points['Entry_Over'].apply(lambda x: 
            'Powerplay' if x <= 6 else 'Middle' if x <= 15 else 'Death'
        )
        
        # Calculate final strike rate
        if 'Final_Strike_Rate' not in entry_points.columns:
            entry_points.loc[entry_points['BF'] > 0, 'Final_Strike_Rate'] = (
                entry_points['Runs'] / entry_points['BF']
            ) * 100
            entry_points['Final_Strike_Rate'] = entry_points['Final_Strike_Rate'].fillna(
                entry_points['Strike_Rate']
            )
        
        return entry_points
    
    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """Get comprehensive stats for a specific player with intelligent fuzzy matching"""
        
        # First try exact match (case-insensitive substring)
        player_data = self.entry_points[
            self.entry_points['Player'].str.contains(player_name, case=False, na=False)
        ]
        
        # If no exact match, try intelligent fuzzy matching
        if player_data.empty:
            all_players = self.entry_points['Player'].unique().tolist()
            matched_player = None
            
            # Strategy 1: Try matching full name with fuzzy logic
            matches = get_close_matches(player_name.lower(), 
                                       [p.lower() for p in all_players], 
                                       n=3, cutoff=0.6)
            
            if matches:
                # Prioritize matches that contain all words from input
                input_words = set(player_name.lower().split())
                for match in matches:
                    match_words = set(match.split())
                    # Check if all input words are in the match
                    if input_words.issubset(match_words) or len(input_words & match_words) >= len(input_words):
                        matched_player = next(p for p in all_players if p.lower() == match)
                        break
                
                # If no perfect match, take the best fuzzy match
                if not matched_player:
                    matched_player = next(p for p in all_players if p.lower() == matches[0])
            
            # Strategy 2: Try matching on last name only
            if not matched_player:
                last_name = player_name.split()[-1] if ' ' in player_name else player_name
                # Find players where last name matches
                candidates = [p for p in all_players if last_name.lower() in p.lower().split()]
                if candidates:
                    # If multiple candidates, prefer the one with more matches
                    if len(candidates) == 1:
                        matched_player = candidates[0]
                    else:
                        # Prefer players with more data (likely more famous)
                        candidate_counts = [(p, len(self.entry_points[self.entry_points['Player'] == p])) 
                                          for p in candidates]
                        matched_player = max(candidate_counts, key=lambda x: x[1])[0]
            
            # Strategy 3: Try matching on first name for unique first names
            if not matched_player and ' ' in player_name:
                first_name = player_name.split()[0]
                candidates = [p for p in all_players if first_name.lower() in p.lower()]
                if len(candidates) == 1:  # Only if unique
                    matched_player = candidates[0]
            
            if matched_player:
                player_data = self.entry_points[self.entry_points['Player'] == matched_player]
        
        if player_data.empty:
            return None
        
        # Get the most common full name
        full_name = player_data['Player'].mode().iloc[0]
        
        # Calculate recency metrics
        years = player_data['Year'].astype(str).unique()
        years_sorted = sorted(years, reverse=True)
        most_recent_year = years_sorted[0] if years_sorted else 'Unknown'
        years_span = f"{years_sorted[-1]}-{years_sorted[0]}" if len(years_sorted) > 1 else most_recent_year
        
        # Determine current year (from data)
        all_years = self.entry_points['Year'].astype(str).unique()
        current_year = max(all_years) if all_years.size > 0 else '2026'
        
        # Calculate recency score
        try:
            years_since_last = int(current_year) - int(most_recent_year)
            if years_since_last == 0:
                recency_status = "ACTIVE - Current season"
                recency_score = 1.0
            elif years_since_last == 1:
                recency_status = "RECENT - Last season"
                recency_score = 0.8
            elif years_since_last <= 2:
                recency_status = "SEMI-RECENT - 2 years ago"
                recency_score = 0.6
            else:
                recency_status = f"HISTORICAL - {years_since_last} years ago"
                recency_score = 0.3
        except:
            recency_status = "UNKNOWN"
            recency_score = 0.5
        
        # Get recent performance (last 2 years)
        recent_years = years_sorted[:2]
        recent_data = player_data[player_data['Year'].isin(recent_years)]
        historical_data = player_data[~player_data['Year'].isin(recent_years)]
        
        stats = {
            'name': full_name,
            'total_matches': len(player_data),
            'avg_entry_over': round(player_data['Entry_Over'].mean(), 1),
            'avg_strike_rate': round(player_data['Final_Strike_Rate'].mean(), 1),
            'avg_dot_pct': round(player_data.get('Dot_Pct', pd.Series([0])).mean(), 1),
            'avg_bnd_pct': round(player_data.get('Bnd_Pct', pd.Series([0])).mean(), 1),
            'avg_innings_duration': round(player_data.get('Innings_Duration', pd.Series([0])).mean(), 1),
            'total_runs': int(player_data['Runs'].sum()),
            'avg_runs_per_match': round(player_data['Runs'].mean(), 1),
            'best_strike_rate': round(player_data['Final_Strike_Rate'].max(), 1),
            'teams': player_data['Team'].unique().tolist(),
            'years': years_sorted,
            'years_span': years_span,
            'most_recent_year': most_recent_year,
            'recency_status': recency_status,
            'recency_score': recency_score,
            'phase_breakdown': {
                'powerplay': len(player_data[player_data['Entry_Phase'] == 'Powerplay']),
                'middle': len(player_data[player_data['Entry_Phase'] == 'Middle']),
                'death': len(player_data[player_data['Entry_Phase'] == 'Death'])
            },
            'phase_performance': player_data.groupby('Entry_Phase').agg({
                'Final_Strike_Rate': 'mean',
                'Runs': 'mean',
                'Dot_Pct': 'mean',
                'Bnd_Pct': 'mean'
            }).round(1).to_dict()
        }
        
        # Add recent vs historical comparison if applicable
        if not recent_data.empty and not historical_data.empty:
            stats['recent_performance'] = {
                'years': recent_years,
                'matches': len(recent_data),
                'avg_sr': round(recent_data['Final_Strike_Rate'].mean(), 1),
                'avg_runs': round(recent_data['Runs'].mean(), 1)
            }
            stats['historical_performance'] = {
                'years': [y for y in years_sorted if y not in recent_years],
                'matches': len(historical_data),
                'avg_sr': round(historical_data['Final_Strike_Rate'].mean(), 1),
                'avg_runs': round(historical_data['Runs'].mean(), 1)
            }
        elif not recent_data.empty:
            stats['recent_performance'] = {
                'years': recent_years,
                'matches': len(recent_data),
                'avg_sr': round(recent_data['Final_Strike_Rate'].mean(), 1),
                'avg_runs': round(recent_data['Runs'].mean(), 1)
            }
        
        return stats
    
    def get_best_players_for_phase(self, phase: str, min_matches: int = 3, top_n: int = None, min_sr: float = None, max_sr: float = None) -> List[Dict]:
        """Get best players for a specific phase with flexible filtering"""
        phase_map = {
            'powerplay': 'Powerplay',
            'middle': 'Middle', 
            'death': 'Death'
        }
        
        target_phase = phase_map.get(phase.lower(), phase)
        filtered_data = self.entry_points[self.entry_points['Entry_Phase'] == target_phase]
        
        player_performance = filtered_data.groupby('Player').agg({
            'Final_Strike_Rate': 'mean',
            'Runs': 'mean',
            'Dot_Pct': 'mean',
            'Bnd_Pct': 'mean',
            'Entry_Over': 'count'
        }).reset_index()
        
        # Apply filters
        player_performance = player_performance[player_performance['Entry_Over'] >= min_matches]
        
        if min_sr is not None:
            player_performance = player_performance[player_performance['Final_Strike_Rate'] >= min_sr]
        
        if max_sr is not None:
            player_performance = player_performance[player_performance['Final_Strike_Rate'] <= max_sr]
        
        # Sort by strike rate
        player_performance = player_performance.sort_values('Final_Strike_Rate', ascending=False)
        
        # Limit results if specified
        if top_n is not None:
            player_performance = player_performance.head(top_n)
        
        results = []
        for _, row in player_performance.iterrows():
            results.append({
                'player': row['Player'],
                'avg_strike_rate': round(row['Final_Strike_Rate'], 1),
                'avg_runs': round(row['Runs'], 1),
                'avg_dot_pct': round(row.get('Dot_Pct', 0), 1),
                'avg_bnd_pct': round(row.get('Bnd_Pct', 0), 1),
                'matches': int(row['Entry_Over'])
            })
        
        return results
    
    def get_phase_summary(self, phase: str) -> Dict:
        """Get summary statistics for a phase"""
        phase_map = {
            'powerplay': 'Powerplay',
            'middle': 'Middle', 
            'death': 'Death'
        }
        
        target_phase = phase_map.get(phase.lower(), phase)
        filtered_data = self.entry_points[self.entry_points['Entry_Phase'] == target_phase]
        
        return {
            'phase': target_phase,
            'total_entries': len(filtered_data),
            'unique_players': filtered_data['Player'].nunique(),
            'avg_strike_rate': round(filtered_data['Final_Strike_Rate'].mean(), 1),
            'avg_runs': round(filtered_data['Runs'].mean(), 1),
            'avg_dot_pct': round(filtered_data.get('Dot_Pct', pd.Series([0])).mean(), 1),
            'avg_bnd_pct': round(filtered_data.get('Bnd_Pct', pd.Series([0])).mean(), 1)
        }
    
    def compare_players(self, player_names: List[str]) -> Dict:
        """Compare multiple players"""
        comparison = {}
        
        for name in player_names:
            stats = self.get_player_stats(name)
            if stats:
                comparison[stats['name']] = stats
        
        return comparison
    
    def get_diverse_players_for_phase(self, phase: str, min_matches: int = 3) -> Dict:
        """Get diverse set of players with different playing styles for a phase"""
        phase_map = {
            'powerplay': 'Powerplay',
            'middle': 'Middle', 
            'death': 'Death'
        }
        
        target_phase = phase_map.get(phase.lower(), phase)
        filtered_data = self.entry_points[self.entry_points['Entry_Phase'] == target_phase]
        
        player_performance = filtered_data.groupby('Player').agg({
            'Final_Strike_Rate': 'mean',
            'Runs': 'mean',
            'Entry_Over': 'count',
            'Dot_Pct': 'mean',
            'Bnd_Pct': 'mean'
        }).reset_index()
        
        player_performance = player_performance[player_performance['Entry_Over'] >= min_matches]
        
        # Get different categories of players (top 15 each for more options)
        categories = {}
        
        # Aggressive strikers (high SR)
        aggressive = player_performance.nlargest(15, 'Final_Strike_Rate')
        categories['aggressive_strikers'] = self._format_player_list(aggressive, "High strike rate")
        
        # Consistent run-scorers (high avg runs)
        consistent = player_performance.nlargest(15, 'Runs')
        categories['consistent_scorers'] = self._format_player_list(consistent, "High average runs")
        
        # Boundary hitters (high boundary %)
        boundary = player_performance.nlargest(15, 'Bnd_Pct')
        categories['boundary_hitters'] = self._format_player_list(boundary, "High boundary %")
        
        # Rotators (low dot %, good strike rotation)
        rotators = player_performance.nsmallest(15, 'Dot_Pct')
        categories['strike_rotators'] = self._format_player_list(rotators, "Low dot %, good rotation")
        
        # Experienced (most matches)
        experienced = player_performance.nlargest(15, 'Entry_Over')
        categories['experienced'] = self._format_player_list(experienced, "Most matches played")
        
        # Balanced (SR 120-150, good all-round)
        balanced = player_performance[
            (player_performance['Final_Strike_Rate'] >= 120) & 
            (player_performance['Final_Strike_Rate'] <= 150)
        ].nlargest(15, 'Runs')
        categories['balanced'] = self._format_player_list(balanced, "Balanced SR 120-150")
        
        return categories
    
    def _format_player_list(self, df, description):
        """Helper to format player list"""
        players = []
        for _, row in df.iterrows():
            players.append({
                'player': row['Player'],
                'avg_strike_rate': round(row['Final_Strike_Rate'], 1),
                'avg_runs': round(row['Runs'], 1),
                'matches': int(row['Entry_Over']),
                'dot_pct': round(row.get('Dot_Pct', 0), 1),
                'bnd_pct': round(row.get('Bnd_Pct', 0), 1),
                'description': description
            })
        return players
    
    def get_team_strategy(self, team_name: str) -> Dict:
        """Get team's entry strategy"""
        team_data = self.entry_points[
            self.entry_points['Team'].str.contains(team_name, case=False, na=False)
        ]
        
        if team_data.empty:
            return {}
        
        strategy = {
            'team': team_data['Team'].iloc[0],
            'total_entries': len(team_data),
            'avg_entry_over': round(team_data['Entry_Over'].mean(), 1),
            'phase_distribution': team_data['Entry_Phase'].value_counts().to_dict(),
            'top_performers': team_data.nlargest(5, 'Final_Strike_Rate')[
                ['Player', 'Final_Strike_Rate', 'Entry_Over']
            ].to_dict('records')
        }
        
        return strategy

class ReActCricketAgent:
    """ReAct-powered cricket strategy agent"""
    
    def __init__(self, analyzer: CricketDataAnalyzer, ai_model):
        self.analyzer = analyzer
        self.ai_model = ai_model
        self.conversation_history = []
    
    def _validate_question(self, question: str) -> Dict:
        """Validate if the question can be answered with available data"""
        question_lower = question.lower()
        
        # Define what data we have
        available_data = [
            "player names", "teams", "matches", "overs", "years", 
            "runs", "balls faced", "strike rate", "dot percentage", 
            "boundary percentage", "entry phase (powerplay/middle/death)",
            "innings duration", "entry over", "exit over"
        ]
        
        # Define what data we DON'T have
        unavailable_concepts = {
            'bowling_type': ['spin', 'pace', 'fast', 'seam', 'off-spin', 'leg-spin', 'left-arm', 'right-arm'],
            'bowler_identity': ['bowler', 'against', 'facing'],
            'ball_by_ball': ['ball-by-ball', 'delivery', 'specific ball'],
            'fielding': ['fielding', 'catches', 'run-outs', 'field placement'],
            'bowling_stats': ['wickets taken', 'economy rate', 'bowling average', 'bowling strike rate'],
            'match_outcome': ['win', 'loss', 'result', 'victory'],
            'venue': ['ground', 'stadium', 'venue', 'pitch'],
            'weather': ['weather', 'rain', 'dew'],
            'toss': ['toss', 'bat first', 'chase']
        }
        
        # Check for unavailable concepts
        for concept_type, keywords in unavailable_concepts.items():
            for keyword in keywords:
                if keyword in question_lower:
                    # Special handling for "against" - it might be asking about teams or comparing players
                    if keyword == 'against':
                        # Check if it's about team matchups or player comparisons
                        if any(word in question_lower for word in ['team', 'mi', 'csk', 'rcb', 'kkr', 'dc', 'pbks', 'rr', 'srh', 'gt', 'lsg']):
                            continue  # This is okay, asking about team matchups
                        # Check if comparing players
                        if 'compare' in question_lower or any(name in question_lower for name in ['kohli', 'rohit', 'dhoni', 'pandya', 'sharma']):
                            continue  # This is okay, comparing players
                    
                    # Build helpful error message
                    if concept_type == 'bowling_type':
                        return {
                            'is_valid': False,
                            'message': f"""
⚠️ **Question Out of Bounds**

Your question mentions **bowling type** ("{keyword}"), but our dataset doesn't contain this information.

**What we CAN analyze:**
- Player performance by **entry phase** (Powerplay overs 1-6, Middle overs 7-15, Death overs 16-20)
- Strike rates, runs, balls faced, dot%, boundary%
- Performance by team, year, and match
- Entry timing and innings duration

**What we CANNOT analyze:**
- Performance against specific bowling types (spin/pace)
- Performance against specific bowlers
- Ball-by-ball details

**Try asking instead:**
- "Which players perform best in middle overs?" (instead of "against spin")
- "Who are the best death-overs finishers?"
- "How does [player] perform in the powerplay?"

**Available data fields:** {', '.join(available_data)}
"""
                        }
                    elif concept_type == 'bowler_identity':
                        return {
                            'is_valid': False,
                            'message': f"""
⚠️ **Question Out of Bounds**

Your question asks about **specific bowlers or bowling matchups**, but our dataset only contains batting statistics.

**What we CAN analyze:**
- Batting performance by entry phase (Powerplay/Middle/Death)
- Player strike rates, runs, efficiency metrics
- Team and year-based analysis

**What we CANNOT analyze:**
- Performance against specific bowlers
- Bowler vs batsman matchups

**Try asking instead:**
- "Which batsmen perform best in [phase]?"
- "How does [player] perform when entering in the death overs?"

**Available data fields:** {', '.join(available_data)}
"""
                        }
                    else:
                        return {
                            'is_valid': False,
                            'message': f"""
⚠️ **Question Out of Bounds**

Your question asks about **{concept_type.replace('_', ' ')}**, which is not available in our dataset.

**What we CAN analyze:**
- Player batting performance by entry phase (Powerplay/Middle/Death)
- Strike rates, runs, balls faced, dot%, boundary%
- Performance by team, year, and match
- Entry timing and innings duration

**Available data fields:** {', '.join(available_data)}

**Try rephrasing your question** to focus on batting performance metrics and entry phases.
"""
                        }
        
        return {'is_valid': True, 'message': None}
    
    def _extract_entities(self, question: str) -> Dict:
        """Extract players, teams, bowling types from question"""
        entities = {
            'players': [],
            'teams': [],
            'bowling_types': [],
            'phases': [],
            'intent': 'general'
        }
        
        question_lower = question.lower()
        
        # Extract player names (common cricket names)
        player_patterns = [
            r'\b(hardik\s*pandya?|pandya)\b',
            r'\b(virat\s*kohli|kohli)\b', 
            r'\b(ms\s*dhoni|dhoni)\b',
            r'\b(rohit\s*sharma|rohit)\b',
            r'\b(kl\s*rahul|rahul)\b',
            r'\b(david\s*warner|warner)\b',
            r'\b(ab\s*de\s*villiers|abd)\b'
        ]
        
        for pattern in player_patterns:
            matches = re.findall(pattern, question_lower)
            if matches:
                entities['players'].extend(matches)
        
        # Extract bowling types
        if 'spin' in question_lower:
            entities['bowling_types'].append('spin')
        if 'pace' in question_lower or 'fast' in question_lower:
            entities['bowling_types'].append('pace')
        
        # Extract phases
        if 'powerplay' in question_lower or 'power play' in question_lower:
            entities['phases'].append('powerplay')
        if 'death' in question_lower or 'death over' in question_lower or 'final over' in question_lower or 'last over' in question_lower:
            entities['phases'].append('death')
        if 'middle' in question_lower or 'middle over' in question_lower:
            entities['phases'].append('middle')
        
        # Determine intent
        if any(word in question_lower for word in ['when', 'should', 'deploy', 'play']):
            entities['intent'] = 'deployment'
        elif any(word in question_lower for word in ['best', 'top', 'who']):
            entities['intent'] = 'recommendation'
        elif any(word in question_lower for word in ['compare', 'vs', 'versus']):
            entities['intent'] = 'comparison'
        
        return entities
    
    def _reason_and_plan(self, question: str, entities: Dict) -> List[str]:
        """Reason about what data analysis is needed"""
        actions = []
        
        # Check if this is a "who is best" or "top performers" question
        question_lower = question.lower()
        is_general_recommendation = any(phrase in question_lower for phrase in [
            'who are', 'who is best', 'best players', 'top players', 'best batsmen',
            'best bowlers', 'top performers', 'which players'
        ])
        
        # Check if this is a batting order question (needs all phases)
        is_batting_order_question = any(phrase in question_lower for phrase in [
            'batting order', 'batting lineup', 'batting line up', 'order for',
            'who should open', 'who should bat', 'lineup for', 'line up for',
            'optimal order', 'best order', 'batting positions', 'who bats where',
            'chasing', 'chase', 'defending', 'defend'  # Match situation questions
        ])
        
        # If specific players mentioned, get their stats
        if entities['players'] and not is_general_recommendation:
            for player in entities['players']:
                actions.append(f"get_player_stats:{player}")
        
        # IMPORTANT: We don't have bowling type data (spin/pace) in the dataset
        # If bowling types mentioned, ignore them and use phases instead
        if entities['bowling_types']:
            # Add a note that bowling type filtering is not available
            actions.append("note:bowling_type_unavailable")
        
        # If this is a batting order question, get ALL phases with diverse players
        if is_batting_order_question:
            actions.append("get_diverse_players_for_phase:powerplay")
            actions.append("get_diverse_players_for_phase:middle")
            actions.append("get_diverse_players_for_phase:death")
        # If phases mentioned, get best players for those phases
        elif entities['phases']:
            for phase in entities['phases']:
                actions.append(f"get_best_players_for_phase:{phase}")
        # If it's a general recommendation question without specific players
        elif is_general_recommendation or (entities['intent'] == 'recommendation' and not entities['players']):
            # Only use phases, not bowling types
            if entities['phases']:
                for phase in entities['phases']:
                    actions.append(f"get_best_players_for_phase:{phase}")
            else:
                # Default to common phases if no specific context
                actions.append("get_best_players_for_phase:death")
        
        # If no actions planned yet, default to powerplay analysis
        if not actions:
            actions.append("get_best_players_for_phase:powerplay")
        
        return actions
    
    def _execute_action(self, action: str) -> Any:
        """Execute a data analysis action"""
        try:
            if ':' not in action:
                return None
                
            action_type, param = action.split(':', 1)
            
            if action_type == 'note':
                # Return a note for the AI to consider
                if param == 'bowling_type_unavailable':
                    return "IMPORTANT: Bowling type data (spin/pace) is not available in the dataset. Analysis is based on entry phase (Powerplay/Middle/Death) only."
                return None
            elif action_type == 'get_player_stats':
                result = self.analyzer.get_player_stats(param)
                # If not found, try partial match
                if result is None:
                    # Try searching for last name or partial match
                    for name_part in param.split():
                        result = self.analyzer.get_player_stats(name_part)
                        if result:
                            break
                return result
            elif action_type == 'get_best_players_for_phase':
                return self.analyzer.get_best_players_for_phase(param)
            elif action_type == 'get_diverse_players_for_phase':
                return self.analyzer.get_diverse_players_for_phase(param)
            elif action_type == 'compare_players':
                players = param.split(',')
                return self.analyzer.compare_players(players)
            elif action_type == 'get_team_strategy':
                return self.analyzer.get_team_strategy(param)
            
        except Exception as e:
            return f"Error executing {action}: {str(e)}"
        
        return None
    
    def answer_question(self, question: str) -> str:
        """Main ReAct loop to answer cricket strategy questions"""
        
        # Step 0: VALIDATE - Check if question is answerable with available data
        validation_result = self._validate_question(question)
        if not validation_result['is_valid']:
            return validation_result['message']
        
        # Step 1: REASON - Extract entities and plan actions
        entities = self._extract_entities(question)
        planned_actions = self._reason_and_plan(question, entities)
        
        # Step 2: ACT - Execute data analysis actions
        action_results = {}
        for action in planned_actions:
            result = self._execute_action(action)
            action_results[action] = result
        
        # Step 3: OBSERVE - Analyze results and reason about findings
        observations = self._analyze_results(action_results, entities)
        
        # Step 4: REASON & RESPOND - Generate final answer using AI
        final_answer = self._generate_response(question, entities, observations)
        
        # Store in conversation history
        self.conversation_history.append({
            'question': question,
            'entities': entities,
            'actions': planned_actions,
            'results': action_results,
            'answer': final_answer
        })
        
        return final_answer
    
    def _analyze_results(self, results: Dict, entities: Dict) -> str:
        """Analyze the data results and create observations"""
        observations = []
        
        # Check if bowling type was mentioned but can't be filtered
        if entities.get('bowling_types'):
            observations.append(f"""
⚠️ DATA LIMITATION NOTICE:
The question mentions bowling type ({', '.join(entities['bowling_types'])}), but the dataset does not contain bowling type information.
Analysis is based on ENTRY PHASE (Powerplay/Middle/Death) only, not specific bowling matchups.
""")
        
        for action, result in results.items():
            if result is None:
                continue
            
            # Handle note actions
            if action.startswith('note:'):
                observations.append(str(result))
                continue
                
            action_type = action.split(':')[0]
            
            if action_type == 'get_player_stats' and result:
                player = result['name']
                
                # CRITICAL: Always provide the player's actual data with recency context
                obs = f"""
PLAYER DATA FOR {player.upper()}:
- Total Matches: {result['total_matches']}
- Years Active: {result['years_span']} (Most Recent: {result['most_recent_year']})
- Recency Status: {result['recency_status']} (Score: {result['recency_score']})
- Average Entry Over: {result['avg_entry_over']}
- Average Innings Duration: {result.get('avg_innings_duration', 'N/A')} overs
- Average Strike Rate: {result['avg_strike_rate']}
- Average Dot Ball %: {result.get('avg_dot_pct', 'N/A')}%
- Average Boundary %: {result.get('avg_bnd_pct', 'N/A')}%
- Total Runs: {result['total_runs']}
- Avg Runs per Match: {result['avg_runs_per_match']}
- Best Strike Rate: {result['best_strike_rate']}
- Phase Breakdown: Powerplay={result['phase_breakdown']['powerplay']}, Middle={result['phase_breakdown']['middle']}, Death={result['phase_breakdown']['death']}
- Phase Performance: {result['phase_performance']}
"""
                
                # Add recent vs historical comparison if available
                if 'recent_performance' in result:
                    obs += f"""
- RECENT PERFORMANCE ({', '.join(result['recent_performance']['years'])}):
  * Matches: {result['recent_performance']['matches']}
  * Avg Strike Rate: {result['recent_performance']['avg_sr']}
  * Avg Runs: {result['recent_performance']['avg_runs']}
"""
                
                if 'historical_performance' in result:
                    obs += f"""
- HISTORICAL PERFORMANCE ({', '.join(result['historical_performance']['years'])}):
  * Matches: {result['historical_performance']['matches']}
  * Avg Strike Rate: {result['historical_performance']['avg_sr']}
  * Avg Runs: {result['historical_performance']['avg_runs']}
"""
                
                observations.append(obs)
            
            elif action_type == 'get_best_players_for_phase' and result:
                phase = action.split(':')[1]
                
                # Show ALL performers (not just top 5)
                player_list = [f"{p['player']} (SR: {p['avg_strike_rate']}, {p['matches']} matches, Avg Runs: {p['avg_runs']})" for p in result]
                obs = f"""
TOP PERFORMERS FOR {phase.upper()} PHASE:
{chr(10).join([f"  {i+1}. {p}" for i, p in enumerate(player_list)])}

Total players analyzed: {len(result)}
"""
                observations.append(obs)
            
            elif action_type == 'get_diverse_players_for_phase' and result:
                phase = action.split(':')[1]
                
                # Show diverse categories of players
                obs = f"\nDIVERSE PLAYER POOL FOR {phase.upper()} PHASE:\n"
                obs += "=" * 60 + "\n"
                
                for category, players in result.items():
                    category_name = category.replace('_', ' ').title()
                    obs += f"\n{category_name}:\n"
                    for i, p in enumerate(players, 1):
                        obs += f"  {i}. {p['player']} - SR: {p['avg_strike_rate']}, Runs: {p['avg_runs']}, "
                        obs += f"Matches: {p['matches']}, Dot%: {p['dot_pct']}, Bnd%: {p['bnd_pct']}\n"
                
                obs += f"\nTotal categories: {len(result)}\n"
                obs += "Note: Players may appear in multiple categories based on their strengths\n"
                observations.append(obs)
        
        return "\n".join(observations) if observations else "No specific data retrieved"
    
    def _generate_response(self, question: str, entities: Dict, observations: str) -> str:
        """Generate final response using AI with ReAct observations"""
        
        # Extract player names from observations for validation
        player_data_sections = [line for line in observations.split('\n') if 'PLAYER DATA FOR' in line]
        players_with_data = [section.split('PLAYER DATA FOR')[1].split(':')[0].strip() for section in player_data_sections]
        
        # Also check for top performers data
        has_top_performers = 'TOP PERFORMERS FOR' in observations
        
        # Determine data availability message
        if players_with_data:
            data_availability = ', '.join(players_with_data)
        elif has_top_performers:
            data_availability = "Top performers data available (see observations)"
        else:
            data_availability = "None - general analysis only"
        
        prompt = f"""
You are an expert cricket strategy coach using ReAct methodology (Reasoning + Acting).

QUESTION: {question}

EXTRACTED ENTITIES: {json.dumps(entities, indent=2)}

DATA ANALYSIS OBSERVATIONS:
{observations}

PLAYERS WITH ACTUAL DATA AVAILABLE: {data_availability}

⚠️ DATASET LIMITATIONS:
- The dataset contains: Player, Team, Match, Over, Runs, BF, Strike Rate, Dot%, Bnd%, Entry Phase
- The dataset DOES NOT contain: Bowling type (spin/pace), bowler names, ball-by-ball details
- If the question asks about "spin" or "pace", you MUST clarify that we can only analyze by phase (Powerplay/Middle/Death)
- Analysis is based on WHEN players enter (phase), not WHO they face (bowling type)

🚨 CRITICAL VALIDATION RULES - YOU MUST FOLLOW THESE:

1. **MANDATORY DATA USAGE**: 
   - If "PLAYER DATA FOR [NAME]" appears, you MUST use that player's specific statistics
   - If "TOP PERFORMERS FOR [PHASE]" appears, you MUST reference those players and their stats
   - Quote ACTUAL numbers from the observations (strike rates, matches, etc.)
   - Base ALL recommendations on the data provided in observations
   - **FOR BATTING ORDER QUESTIONS**: Use players from ALL THREE phases (Powerplay, Middle, Death)

2. **BATTING ORDER SPECIFIC RULES**:
   - If the question asks for a "batting order" or "lineup", you MUST recommend players for ALL positions (1-11)
   - You will receive DIVERSE PLAYER POOLS with different categories:
     * Aggressive Strikers: High strike rate players for quick scoring
     * Consistent Scorers: High average runs, reliable performers
     * Boundary Hitters: High boundary %, power hitters
     * Strike Rotators: Low dot %, good at rotating strike
     * Experienced: Most matches, proven track record
     * Balanced: SR 120-150, all-round contributors
   - Mix and match from these categories based on the match situation
   - For chasing 180+: Prioritize aggressive strikers and boundary hitters
   - For building innings: Use balanced players and strike rotators
   - For death overs: Use experienced finishers with high SR
   - DO NOT only pick from one category - create a balanced lineup

3. **FORBIDDEN REASONING PATTERNS**:
   ❌ "No data available" when observations contain TOP PERFORMERS
   ❌ "Player X is not in the top 3, so they're not suitable"
   ❌ Claiming to analyze "against spin" when we only have phase data
   ❌ Making recommendations without citing actual statistics from observations
   ❌ Ignoring the TOP PERFORMERS data when answering "who is best" questions
   ❌ Stopping at position 3 when asked for a full batting order

4. **REQUIRED REASONING PATTERNS**:
   ✅ "Based on the data, the top death over performers are [names from observations]..."
   ✅ "Player X has SR [NUMBER] across [NUMBER] matches (from observations)..."
   ✅ "The TOP PERFORMERS data shows [specific players and their stats]..."
   ✅ "Comparing the provided statistics: [reference actual numbers]..."
   ✅ "For the middle order (positions 4-7), the data shows [list players with stats]..."

5. **DATA-DRIVEN ANALYSIS FRAMEWORK**:
   - Start with the player's ACTUAL statistics
   - Analyze what those numbers mean for different match situations
   - Compare to phase averages or benchmarks (not just top performers)
   - Identify scenarios where their stats indicate effectiveness
   - Provide nuanced tactical recommendations based on their data

6. **RECENCY CONSIDERATION**:
   - ALWAYS note the player's recency status (ACTIVE, RECENT, HISTORICAL)
   - If player is HISTORICAL (retired/inactive), clearly state this upfront
   - For HISTORICAL players, acknowledge data is from past years
   - For ACTIVE players, emphasize current relevance
   - Compare recent vs historical performance when available

7. **SAMPLE SIZE CONSIDERATION**:
   - Always mention the number of matches in the player's data
   - Higher sample sizes (20+ matches) = more reliable patterns
   - Lower sample sizes (3-10 matches) = acknowledge limited data but still analyze what's there

8. **VALIDATION CHECK** (You must pass this):
   - If player data exists in observations, your response MUST quote at least 3 specific numbers from their data
   - Your response MUST explain what those numbers mean tactically
   - Your response MUST NOT rely solely on "top performers" comparisons
   - For batting order questions, you MUST recommend at least 11 players across all phases

EXAMPLE OF CORRECT RESPONSE (ACTIVE PLAYER):
"Based on the data, [Player Name] is currently active (2025 season) with 45 matches and an 
average strike rate of 125.3. Their recent performance (2024-2025) shows 25 matches with SR 
130.2, indicating improving form. This makes them a strong current option for scenarios 
requiring 7-8 runs per over during middle overs."

EXAMPLE OF CORRECT RESPONSE (RETIRED PLAYER):
"Important Note: [Player Name] last played in 2022 (HISTORICAL status), so this analysis is 
based on past performance. During their career, they had 45 matches with SR 125.3. While they 
were effective for middle-over consolidation, you'll need to consider current squad members 
for active deployment decisions."

Now provide your comprehensive, data-driven answer following ALL the rules above.
"""
        
        try:
            response = self.ai_model.generate_content(prompt)
            
            # Post-validation: Check if response uses player data when available
            if players_with_data:
                response_text = response.text
                response_lower = response_text.lower()
                
                # Check if response is just echoing the observations (fallback format)
                if response_text.startswith("Based on the data analysis:") and observations in response_text:
                    # This is the fallback - AI didn't generate properly, try again with simpler prompt
                    simplified_prompt = f"""
You are a cricket coach. Answer this question using the player data below:

QUESTION: {question}

PLAYER DATA:
{observations}

Provide a clear answer that:
1. States the player's actual statistics (matches, strike rate, entry over)
2. Explains what those numbers mean for cricket strategy
3. Recommends when/how to use the player based on their data

Keep it conversational and practical.
"""
                    response = self.ai_model.generate_content(simplified_prompt)
                    response_text = response.text
                
                # Final check: ensure player name is mentioned
                if not any(player.lower() in response_lower for player in players_with_data):
                    # Prepend player context
                    response_text = f"Analyzing {', '.join(players_with_data)}:\n\n" + response_text
                
                return response_text
            
            return response.text
            
        except Exception as e:
            # Fallback to data-only response
            return f"""Based on the data analysis:

{observations}

Strategic Recommendation: The data shows specific performance metrics that should guide deployment decisions. Consider the player's actual strike rate, entry patterns, and match situations where their statistics indicate effectiveness.

(Note: Full AI analysis unavailable due to: {str(e)})"""

# Example usage functions
def create_react_agent(df, ai_model):
    """Create a ReAct cricket agent"""
    analyzer = CricketDataAnalyzer(df)
    agent = ReActCricketAgent(analyzer, ai_model)
    return agent

def test_react_agent():
    """Test the ReAct agent"""
    import pandas as pd
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    
    # Create mock AI model for testing
    class MockAI:
        def generate_content(self, prompt):
            class MockResponse:
                def __init__(self):
                    self.text = "Based on the data analysis, here are my recommendations..."
            return MockResponse()
    
    # Create agent
    agent = create_react_agent(df, MockAI())
    
    # Test questions
    test_questions = [
        "When should I play Hardik Pandya against spin?",
        "Who are the best death over batsmen?",
        "Best powerplay strategy for my team?"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        answer = agent.answer_question(question)
        print(f"A: {answer}")

if __name__ == "__main__":
    test_react_agent()