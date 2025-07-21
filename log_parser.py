import re
from collections import deque, Counter, defaultdict
import json
from datetime import datetime

USER_LOG_FILE = 'user_log.log'
DEBUG_LOG_FILE = 'bot_debug.log'

def get_recent_triggers(limit=20):
    """
    Parses the user_log.log file to get the most recent trigger events.
    Now includes subreddit and anonymized user info.

    Args:
        limit (int): The maximum number of recent triggers to return.

    Returns:
        list: A list of dictionaries, each representing a trigger event.
    """
    recent_triggers = deque(maxlen=limit)
    # This regex now parses the richer user_log.log format
    log_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s+-\s+User:\s+(.*?)\s+in\s+r/(\w+)\s+\(Comment\s+ID:\s+\w+\)\s+-\s+Verdict:\s+(.*)"
    )

    try:
        with open(USER_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                match = log_pattern.search(line)
                if match:
                    timestamp, _, subreddit, verdict = match.groups()
                    recent_triggers.append({
                        "timestamp": timestamp.strip(),
                        "subreddit": subreddit.strip(),
                        "verdict": verdict.strip()
                    })
    except FileNotFoundError:
        print(f"Warning: {USER_LOG_FILE} not found.")
        return []

    return list(recent_triggers)

def calculate_stats():
    """
    Calculates aggregate statistics from user_log.log.
    Now includes total triggers, verdict distribution, subreddit activity,
    and daily verdict trends.
    """
    total_triggers = 0
    verdict_distribution = Counter()
    subreddit_activity = Counter()
    daily_trends = defaultdict(Counter)

    log_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}).*?r/(\w+).*?-\s+Verdict:\s+(.*)"
    )

    try:
        with open(USER_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                total_triggers += 1
                match = log_pattern.search(line)
                if match:
                    timestamp_str, subreddit, verdict = match.groups()
                    verdict = clean_text(verdict)
                    subreddit = subreddit.strip()

                    # Aggregate overall stats
                    subreddit_activity[subreddit] += 1
                    verdict_distribution[verdict] += 1

                    # Aggregate daily trends
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        day_str = timestamp.strftime('%Y-%m-%d')
                        daily_trends[day_str][verdict] += 1
                    except ValueError:
                        continue # Ignore lines with malformed dates

    except FileNotFoundError:
        print(f"Warning: {USER_LOG_FILE} not found.")

    # Sort subreddit activity by count
    sorted_subreddit_activity = dict(subreddit_activity.most_common(10))

    # Format daily trends for Chart.js
    # Sort dates chronologically
    sorted_dates = sorted(daily_trends.keys())
    formatted_trends = {
        "labels": sorted_dates,
        "datasets": {
            "🟢 Likely Human": [daily_trends[date]["🟢 Likely Human"] for date in sorted_dates],
            "🟡 Possibly AI-Generated": [daily_trends[date]["🟡 Possibly AI-Generated"] for date in sorted_dates],
            "🔴 Potentially AI-Generated": [daily_trends[date]["🔴 Potentially AI-Generated"] for date in sorted_dates],
        }
    }

    return {
        "total_triggers": total_triggers,
        "verdict_distribution": dict(verdict_distribution),
        "subreddit_activity": sorted_subreddit_activity,
        "verdict_trends": formatted_trends
    }

def clean_text(text):
    """Remove emojis and other non-ASCII characters."""
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()

if __name__ == '__main__':
    # For testing the parser
    print("--- Recent Triggers ---")
    triggers = get_recent_triggers()
    print(json.dumps(triggers, indent=4))

    print("\n--- Aggregate Stats ---")
    stats = calculate_stats()
    print(json.dumps(stats, indent=4))
