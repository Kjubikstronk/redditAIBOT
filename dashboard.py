from flask import Flask, jsonify, render_template
from flask_cors import CORS
import log_parser

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# --- Caching (simple implementation) ---
# In a real app, you might use Flask-Caching or another library.
# For this MVP, we'll just cache in memory.
stats_cache = None
cache_timestamp = 0
CACHE_DURATION = 300 # Cache for 5 minutes (300 seconds)

def get_cached_stats():
    """
    Returns cached stats if they are not stale, otherwise recalculates.
    """
    import time
    global stats_cache, cache_timestamp

    now = time.time()
    if stats_cache and (now - cache_timestamp < CACHE_DURATION):
        return stats_cache

    # Cache is stale or empty, recalculate
    stats = log_parser.calculate_stats()
    stats_cache = stats
    cache_timestamp = now
    return stats

@app.route('/')
def dashboard():
    """
    Renders the main dashboard page.
    """
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """
    API endpoint to get bot statistics.
    """
    stats = get_cached_stats()
    recent_triggers = log_parser.get_recent_triggers()

    response_data = {
        'total_triggers': stats.get('total_triggers', 0),
        'verdict_distribution': stats.get('verdict_distribution', {}),
        'subreddit_activity': stats.get('subreddit_activity', {}),
        'verdict_trends': stats.get('verdict_trends', {}),
        'recent_triggers': recent_triggers
    }
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
