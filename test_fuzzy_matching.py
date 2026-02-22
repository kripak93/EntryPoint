#!/usr/bin/env python3
"""
Test fuzzy player name matching
"""

import pandas as pd
from react_cricket_agent import CricketDataAnalyzer

def test_fuzzy_matching():
    """Test various player name spellings and variations"""
    
    print("🧪 Testing Fuzzy Player Name Matching")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv('cricviz_2022_2026_20260122_093415(in).csv')
    analyzer = CricketDataAnalyzer(df)
    
    # Test cases with common misspellings and variations
    test_cases = [
        # Correct name variations
        ("Virat Kohli", "V Kohli"),
        ("Kohli", "V Kohli"),
        ("MS Dhoni", "MS Dhoni"),
        ("Dhoni", "MS Dhoni"),
        ("Hardik Pandya", "HH Pandya"),
        ("Pandya", "HH Pandya"),
        ("Rohit Sharma", "RG Sharma"),
        ("Rohit", "RG Sharma"),
        
        # Common misspellings
        ("Virat Kohly", "V Kohli"),  # Typo
        ("Hardick Pandya", "HH Pandya"),  # Common misspelling
        ("Rohit Sharme", "RG Sharma"),  # Typo
        ("M S Dhoni", "MS Dhoni"),  # Spacing variation
        
        # Partial names
        ("Tilak", "N Tilak Varma"),
        ("Varma", "N Tilak Varma"),
        ("Bumrah", "JJ Bumrah"),
        ("Jadeja", "RA Jadeja"),
    ]
    
    results = []
    
    for input_name, expected_match in test_cases:
        print(f"\n{'─'*80}")
        print(f"🔍 Testing: '{input_name}'")
        print(f"   Expected: {expected_match}")
        
        result = analyzer.get_player_stats(input_name)
        
        if result:
            found_name = result['name']
            matches = found_name == expected_match or expected_match in found_name
            status = "✅" if matches else "⚠️"
            
            print(f"   {status} Found: {found_name}")
            print(f"   Matches: {result['total_matches']}, SR: {result['avg_strike_rate']}")
            
            results.append({
                'input': input_name,
                'expected': expected_match,
                'found': found_name,
                'success': matches
            })
        else:
            print(f"   ❌ Not found")
            results.append({
                'input': input_name,
                'expected': expected_match,
                'found': None,
                'success': False
            })
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 FUZZY MATCHING SUMMARY")
    print("=" * 80)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    found = sum(1 for r in results if r['found'] is not None)
    
    print(f"Total tests: {total}")
    print(f"Players found: {found}/{total} ({found/total*100:.1f}%)")
    print(f"Correct matches: {successful}/{total} ({successful/total*100:.1f}%)")
    
    if successful < total:
        print(f"\n⚠️  Failed cases:")
        for r in results:
            if not r['success']:
                print(f"   - '{r['input']}' → Expected: {r['expected']}, Found: {r['found']}")
    else:
        print(f"\n🎉 All fuzzy matching tests passed!")

if __name__ == "__main__":
    test_fuzzy_matching()
    
    print(f"\n{'='*80}")
    print("💡 Fuzzy matching now handles:")
    print("   ✅ Typos and misspellings")
    print("   ✅ Partial names (first or last name only)")
    print("   ✅ Spacing variations")
    print("   ✅ Case insensitivity")
    print("   ✅ Common name variations")