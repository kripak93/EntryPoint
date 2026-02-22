"""
Simple Flask Web Interface for IPL Game Prep
Lightweight and reliable
"""

from flask import Flask, render_template_string, request, jsonify
import pandas as pd
from corrected_strategy_engine import CorrectedIPLStrategyEngine
import io
import sys

app = Flask(__name__)

# Load data once
df = pd.read_csv('ipl_data.csv')
available_batsmen = sorted(df['Batsman'].dropna().unique())
bowler_types = ["RAF", "LAF", "Off Break", "Leg Spin", "LAO"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IPL Game Prep</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #2d3748;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #718096;
            margin-bottom: 30px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #2d3748;
        }
        select, input {
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        #output {
            margin-top: 30px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 8px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            min-height: 200px;
            max-height: 600px;
            overflow-y: auto;
            border: 2px solid #e2e8f0;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-weight: 600;
        }
        .error {
            color: #e53e3e;
            background: #fff5f5;
            border-color: #feb2b2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 IPL Professional Scouting & Game Prep</h1>
        <p class="subtitle">Generate comprehensive scouting briefs for batsmen vs specific bowler types</p>
        
        <form id="briefForm">
            <div class="form-grid">
                <div class="form-group">
                    <label for="season">📅 Season</label>
                    <select id="season" name="season">
                        <option value="All">All Seasons</option>
                        <option value="2024">2024 Season</option>
                        <option value="2025">2025 Season</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="batsman">🏏 Select Batsman</label>
                    <select id="batsman" name="batsman">
                        {% for bat in batsmen %}
                        <option value="{{ bat }}">{{ bat }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="bowler">🎳 vs Bowler Type</label>
                    <select id="bowler" name="bowler">
                        {% for bt in bowler_types %}
                        <option value="{{ bt }}">{{ bt }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="minBalls">📊 Minimum Balls: <span id="ballsValue">20</span></label>
                    <input type="range" id="minBalls" name="minBalls" min="10" max="100" value="20" step="5"
                           oninput="document.getElementById('ballsValue').textContent = this.value">
                </div>
            </div>
            
            <button type="submit">🎯 Generate Scouting Brief</button>
        </form>
        
        <div id="output"></div>
    </div>
    
    <script>
        document.getElementById('briefForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const output = document.getElementById('output');
            const button = document.querySelector('button');
            
            button.disabled = true;
            output.innerHTML = '<div class="loading">⏳ Generating scouting brief...</div>';
            output.className = '';
            
            const formData = new FormData(e.target);
            const params = new URLSearchParams(formData);
            
            try {
                const response = await fetch('/generate?' + params);
                const data = await response.json();
                
                if (data.success) {
                    output.textContent = data.brief;
                } else {
                    output.innerHTML = '<div class="error">❌ ' + data.error + '</div>';
                }
            } catch (error) {
                output.innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
            } finally {
                button.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, batsmen=available_batsmen, bowler_types=bowler_types)

@app.route('/generate')
def generate():
    try:
        batsman = request.args.get('batsman')
        bowler_type = request.args.get('bowler')
        min_balls = int(request.args.get('minBalls', 20))
        season = request.args.get('season')
        
        # Set up filters
        filters = {}
        if season != 'All':
            filters['season'] = int(season)
        
        # Create engine and generate brief
        engine = CorrectedIPLStrategyEngine(filters=filters)
        engine._ensure_data_loaded()
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        engine.generate_scouting_brief(batsman, bowler_type, min_balls)
        
        output = buffer.getvalue()
        sys.stdout = old_stdout
        
        if not output or "No data available" in output:
            return jsonify({
                'success': False,
                'error': f'No data available for {batsman} vs {bowler_type} with minimum {min_balls} balls'
            })
        
        return jsonify({'success': True, 'brief': output})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 IPL Game Prep Interface Starting...")
    print("="*60)
    print("\n📱 Open in browser: http://127.0.0.1:5000")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
