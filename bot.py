import os
import re
import praw
from dotenv import load_dotenv
import logging
from typing import Optional, Tuple
from local_detection import (
    perplexity, coherence_score, named_entity_density
)
from ai_judge import judge_text

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_debug.log', encoding='utf-8')
    ]
)

import time
from praw.exceptions import APIException

# --- User Audit Logger ---
def setup_user_logger():
    """Sets up a dedicated logger for user interactions."""
    user_logger = logging.getLogger('UserLogger')
    user_logger.setLevel(logging.INFO)
    user_logger.propagate = False
    handler = logging.FileHandler('user_log.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - User: %(message)s')
    handler.setFormatter(formatter)
    user_logger.addHandler(handler)
    return user_logger

user_logger = setup_user_logger()


def load_config() -> dict:
    """
    Loads environment variables and validates required config.
    Returns a config dictionary.
    """
    load_dotenv()
    config = {
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
        'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT'),
        'REDDIT_USERNAME': os.getenv('REDDIT_USERNAME'),
        'REDDIT_PASSWORD': os.getenv('REDDIT_PASSWORD'),
        'SUBREDDITS': os.getenv('REDDIT_SUBREDDITS', 'all'),
    }
    missing = [k for k, v in config.items() if v is None and k != 'SUBREDDITS']
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    return config


def create_reddit_client(config: dict) -> praw.Reddit:
    """
    Creates and returns a PRAW Reddit client using the provided config.
    """
    return praw.Reddit(
        client_id=config['REDDIT_CLIENT_ID'],
        client_secret=config['REDDIT_CLIENT_SECRET'],
        user_agent=config['REDDIT_USER_AGENT'],
        username=config['REDDIT_USERNAME'],
        password=config['REDDIT_PASSWORD']
    )


def get_account_metrics(reddit: praw.Reddit, author: str, skip_account: bool = False) -> Tuple[Optional[int], Optional[int]]:
    """
    Fetches account age (in days) and total karma for a Reddit user using PRAW.
    Returns (account_age_days, karma_score) or (None, None) if unavailable or skip_account is True.
    """
    if skip_account:
        return None, None
    try:
        if not author or author.lower() in ["[deleted]", "[removed]", "anonymous"]:
            return None, None
        redditor = reddit.redditor(author)
        created_utc = getattr(redditor, 'created_utc', None)
        if created_utc is None:
            return None, None
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).timestamp()
        account_age_days = (now - created_utc) / 86400
        try:
            karma = redditor.link_karma + redditor.comment_karma
        except Exception:
            karma = None
        return int(account_age_days), karma
    except Exception:
        return None, None


def _reddit_story_signals(text: str) -> int:
    """Counts weak human-authorship signals typical of Reddit relationship/advice posts."""
    text_lower = text.lower()
    signals = 0
    if any(trigger in text_lower for trigger in ["aita", "am i the asshole"]):
        signals += 1
    if any(rel in text_lower for rel in ["my fiancé", "my fiance", "my husband", "my wife", "my sister", "my brother", "my parents", "my mom", "my dad", "wedding", "drama"]):
        signals += 1
    if re.search(r"\b\d{1,2}[mf]\b", text_lower):
        signals += 1
    if text_lower.strip().endswith("?"):
        signals += 1
    return signals


def format_detection_results(
    text: str,
    author: Optional[str] = None,
    reddit: Optional[praw.Reddit] = None,
    skip_account: bool = False
) -> Tuple[str, str]:
    """
    Judges whether `text` is likely AI-generated. Primary path calls an LLM judge
    (Claude Sonnet 5) with local heuristics passed in as supporting, non-authoritative
    context — statistical detectors alone are unreliable against modern AI writing.
    Falls back to local heuristic scoring only if the LLM judge is unavailable (no
    API key) or the call fails, so the bot degrades gracefully instead of going silent.
    Logs the exact raw text and final verdict for post-analysis and tuning.
    """
    logging.debug(f"[COMPARE] RAW TEXT: {repr(text)}")

    perp = perplexity(text)
    coherence = coherence_score(text)
    entity_density = named_entity_density(text)
    account_age_days, karma_score = get_account_metrics(reddit, author, skip_account=skip_account) if author and reddit else (None, None)
    account_age_str = f"{account_age_days} days" if account_age_days is not None else "N/A"
    has_contractions = bool(re.search(r"\b(?:[A-Za-z]+n't|[A-Za-z]+'ll|[A-Za-z]+'ve|[A-Za-z]+'re|[A-Za-z]+'d|[A-Za-z]+'m|[A-Za-z]+'s)\b", text))
    reddit_signals = _reddit_story_signals(text)
    word_count = len(text.split())

    if word_count < 15:
        verdict = "🟢 Likely Human"
        logging.info(f"[DEBUG] Verdict: {verdict} | Reason: text too short to judge ({word_count} words)")
        report = f"""
{verdict}
_*Text too short to judge reliably.*_
***
*   **Account Age:** `{account_age_str}`
***
^I'm ^an ^experimental ^bot. ^Verdicts ^are ^an ^educated ^guess ^and ^may ^be ^inaccurate.
"""
        return report, verdict

    heuristic_context = {
        "perplexity": round(perp, 2),
        "coherence_score": round(coherence, 2),
        "named_entity_density_per_100_words": round(entity_density, 2),
        "has_contractions": has_contractions,
        "reddit_story_signal_count": reddit_signals,
        "word_count": word_count,
    }

    judged = judge_text(text, heuristic_context)

    if judged is not None:
        verdict = judged["verdict"]
        confidence = judged["confidence"]
        reasoning = judged["reasoning"]
        logging.info(
            f"[LLM JUDGE] Verdict: {verdict} | Confidence: {confidence} | Reasoning: {reasoning} | "
            f"Text: {text[:120].replace(chr(10), ' ')}..."
        )
        report = f"""
{verdict}
_{reasoning}_
***
*   **Confidence:** `{confidence}`
*   **Account Age:** `{account_age_str}`
***
^I'm ^an ^experimental ^bot. ^Verdicts ^are ^an ^educated ^guess ^and ^may ^be ^inaccurate.
"""
        return report, verdict

    # --- Fallback: local heuristic scoring, used only if the LLM judge is unavailable ---
    logging.warning("LLM judge unavailable (no API key or request failed) — falling back to local heuristics.")
    ai_suspicion = 0
    if entity_density < 1 and perp < 10 and coherence > 0.9:
        ai_suspicion += 2
    if entity_density < 3 and perp > 35 and coherence < 0.2:
        ai_suspicion += 2
    if entity_density < 4 and (perp > 30 or coherence < 0.3):
        ai_suspicion += 1
    if perp > 80 and coherence < 0.25:
        ai_suspicion += 1
    if reddit_signals >= 2 and word_count > 80 and coherence > 0.8:
        ai_suspicion += 2
    if not has_contractions and word_count > 10:
        ai_suspicion += 1
    if entity_density > 6:
        ai_suspicion = max(0, ai_suspicion - 1)
    if reddit_signals >= 3:
        ai_suspicion = max(0, ai_suspicion - 1)

    if ai_suspicion >= 2:
        verdict = "🔴 Potentially AI-Generated"
        verdict_explanation = "*Based on a high AI signal score (fallback heuristic — LLM judge unavailable).*"
    elif ai_suspicion == 1:
        verdict = "🟡 Possibly AI-Generated"
        verdict_explanation = "*Based on a moderate AI signal score (fallback heuristic — LLM judge unavailable).*"
    else:
        verdict = "🟢 Likely Human"
        verdict_explanation = "*Based on a low AI signal score (fallback heuristic — LLM judge unavailable).*"

    logging.info(
        f"[DEBUG][FALLBACK] Verdict: {verdict} | Perplexity: {perp:.2f}, Entity Density: {entity_density:.2f}, "
        f"Coherence: {coherence:.2f}, Reddit Signals: {reddit_signals}, Has Contractions: {has_contractions}, "
        f"AI Suspicion: {ai_suspicion}, Text: {text[:120].replace(chr(10), ' ')}..."
    )

    report = f"""
{verdict}
_{verdict_explanation}_
***
*   **AI Signal Score:** `{ai_suspicion}`
*   **Account Age:** `{account_age_str}`
***
^I'm ^an ^experimental ^bot. ^Verdicts ^are ^an ^educated ^guess ^and ^may ^be ^inaccurate.
"""
    return report, verdict


def run_bot(config: dict):
    """
    Main bot loop: monitors subreddits and replies to trigger comments with AI detection report.
    Now analyzes the parent post (submission) content, not the comment itself.
    """
    print("Loaded subreddits from config:", config['SUBREDDITS'])
    logging.info(f"Loaded subreddits from config: {config['SUBREDDITS']}")
    reddit = create_reddit_client(config)
    REPLY_COOLDOWN = 12  # seconds between replies
    last_reply_time = 0
    try:
        logging.info(f"Logged in as: {reddit.user.me()}")
        logging.info(f"Bot username (from .env): {config['REDDIT_USERNAME']}")
        subreddits = [s.strip() for s in config['SUBREDDITS'].split(',') if s.strip()]
        subreddit_str = '+'.join(subreddits)
        logging.info(f"Monitoring subreddits: {subreddit_str}")
        subreddit = reddit.subreddit(subreddit_str)
        logging.info("--- Comment stream is now active ---")
        for comment in subreddit.stream.comments(skip_existing=True):
            try:
                # Ignore the bot's own comments
                if str(comment.author).lower() == config['REDDIT_USERNAME'].lower():
                    continue

                # Check for triggers without logging every comment
                trigger_username = f"u/{config['REDDIT_USERNAME'].lower()}"
                trigger_command = '!aicheck'
                trigger_type = None

                if trigger_command in comment.body.lower():
                    trigger_type = trigger_command
                elif trigger_username in comment.body.lower():
                    trigger_type = "username mention"

                if trigger_type:
                    # A trigger was found, so now we log the details.
                    logging.info(f"--- Trigger '{trigger_type}' activated by {comment.author} in r/{comment.subreddit} (Comment ID: {comment.id}) ---")

                    now = time.time()
                    if now - last_reply_time < REPLY_COOLDOWN:
                        logging.info(f"Cooldown active. Skipping reply.")
                        continue
                    
                    try:
                        logging.info(f"Fetching parent submission for analysis...")
                        submission = comment.submission
                        logging.info(f"Fetched submission {getattr(submission, 'id', 'N/A')} for comment {comment.id}")
                        post_text = (getattr(submission, 'title', '') or "") + "\n" + (getattr(submission, 'selftext', '') or "")
                        logging.info(f"Post text to analyze (first 200 chars): {repr(post_text[:200])}")
                        if not post_text.strip():
                            logging.warning(f"Submission {getattr(submission, 'id', 'N/A')} has no text to analyze. Skipping reply.")
                            continue
                        summary, verdict = format_detection_results(post_text, str(getattr(submission, 'author', 'N/A')), reddit)
                        
                        # Log the successful trigger to the user audit log WITH the verdict
                        user_logger.info(f"{comment.author} in r/{comment.subreddit} (Comment ID: {comment.id}) - Verdict: {verdict}")

                        try:
                            comment.reply(summary)
                            last_reply_time = time.time()
                            logging.info(f"Reply sent to comment {comment.id} by {comment.author} in r/{comment.subreddit}")
                        except APIException as e:
                            if getattr(e, 'error_type', None) == "RATELIMIT":
                                m = re.search(r'(\d+) (minutes?|seconds?)', str(e))
                                if m:
                                    val, unit = int(m.group(1)), m.group(2)
                                    sleep_time = val * 60 if 'minute' in unit else val
                                else:
                                    sleep_time = 60  # fallback
                                logging.warning(f"Rate limit hit. Sleeping for {sleep_time} seconds.")
                                time.sleep(sleep_time)
                            else:
                                logging.error(f"APIException: {e}")
                        except Exception as reply_err:
                            logging.error(f"Error replying to comment {comment.id}: {reply_err}")
                    except Exception as sub_err:
                        logging.error(f"Error fetching or processing submission for comment {comment.id}: {sub_err}")
            except Exception as e:
                logging.error(f"Error analyzing a comment: {e}")
    except Exception as e:
        import traceback
        logging.error(f"Bot failed to start: {e}\n{traceback.format_exc()}")


def main():
    """
    Main function to load config and run the bot.
    """
    try:
        config = load_config()
        run_bot(config)
    except Exception as e:
        logging.critical(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main() 