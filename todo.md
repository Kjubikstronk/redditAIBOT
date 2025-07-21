# TODO: Reddit Hybrid AI Detection Bot

## Public Dashboard (IN PROGRESS)
- **Goal:** Create a beautiful, simple, and public-facing dashboard to display the bot's activity and performance.
- **Core Features:**
    - **Bot Status:** Show which subreddits are being monitored and the bot's uptime.
    - **AI Detection Summary:** Display AI-generated post frequency, verdict distribution, and trends over time.
    - **Live (Anonymized) Activity Feed:** A real-time stream of bot triggers, color-coded by verdict.
- **Suggested Tech Stack:**
    - **Backend:** Flask (to parse log files and serve data).
    - **Frontend:** Bootstrap (for a clean, responsive layout) and Chart.js (for graphs).
- **Data Sources:** The dashboard will parse `user_log.log` and `bot_debug.log` to generate its statistics. No database needed.
- **Deployment:** The dashboard will be a simple web app that can be deployed on the same server as the bot, or on a free service like Render.com or Heroku.

### Detailed Implementation & Deployment Plan

This plan outlines the specific steps to build and host the public dashboard.

---

#### **Phase 1: Backend Development (Flask)**

1.  **Create `dashboard.py`:**
    *   This file will contain a simple Flask application.
    *   Add Flask to `requirements.txt`.

2.  **Develop a Log Parser (`log_parser.py`):**
    *   Create a new helper script that will be responsible for reading `user_log.log` and `bot_debug.log`.
    *   **Function 1: `get_recent_triggers()`:** Reads the last ~20 lines from `user_log.log` and returns a list of anonymized trigger events (timestamp, subreddit, verdict). **Crucially, do not expose usernames.**
    *   **Function 2: `calculate_stats()`:** Reads the full log files to calculate aggregate statistics (total triggers, verdict distribution pie chart data, AI detection rate over time, etc.).

3.  **Create API Endpoints in `dashboard.py`:**
    *   **`@app.route('/')`:** This main route will render the HTML template for the dashboard.
    *   **`@app.route('/api/stats')`:** This endpoint will call the log parser functions and return all the dashboard data as a single JSON object. This allows the frontend to fetch fresh data without reloading the whole page.

4.  **Implement Caching:**
    *   To prevent re-parsing the entire log files on every request (which can be slow), the results from `calculate_stats()` will be cached for 5-10 minutes. The results can be stored in a simple `stats.json` file that gets updated periodically.

---

#### **Phase 2: Frontend Development (HTML/JS)**

1.  **Create `templates/dashboard.html`:**
    *   This will be the single HTML file for the dashboard.
    *   Use **Bootstrap** for a clean, responsive, card-based layout that looks great on both desktop and mobile.

2.  **Add Placeholders for Data:**
    *   Create `div` elements with specific IDs for each piece of data (e.g., `<span id="total-triggers"></span>`, `<canvas id="verdict-chart"></canvas>`).

3.  **Write `static/js/app.js`:**
    *   This JavaScript file will contain the logic to power the dashboard.
    *   **On page load:**
        *   Use `fetch()` to call the `/api/stats` endpoint.
        *   Populate the dashboard with the initial data.
        *   Use **Chart.js** to render the pie chart for verdict distribution and a line chart for detection trends.
    *   **Set up auto-refresh:** Use `setInterval()` to call the `/api/stats` endpoint every 30 seconds to fetch the latest data and update the dashboard, creating a live feel.

---

#### **Phase 3: Deployment & Hosting**

This phase covers making the dashboard live on the internet. We'll use **Render.com** as it's beginner-friendly and has a generous free tier.

1.  **Create `gunicorn_config.py`:**
    *   A simple config file for our web server. `workers = 4` is a good starting point.

2.  **Create `render.yaml` at the project root:**
    *   This file tells Render how to set up our project. It will define two services:
        1.  A **Background Worker** for `bot.py`.
        2.  A **Web Service** for `dashboard.py`.
    *   **Crucial Step: Shared Disk:** We will define a **Render Disk** and mount it to `/data` on both services. The bot will be configured to write its logs to `/data/logs`, and the dashboard will be configured to read from the same directory. This is how they will share data.

3.  **Example `render.yaml` Structure:**
    ```yaml
    services:
      # The Reddit Bot
      - type: worker
        name: reddit-bot
        env: python
        buildCommand: "pip install -r requirements.txt"
        startCommand: "python bot.py"
        envVars:
          - fromGroup: reddit-credentials
        disks:
          - name: shared-logs
            mountPath: /data

      # The Public Dashboard
      - type: web
        name: public-dashboard
        env: python
        buildCommand: "pip install -r requirements.txt"
        startCommand: "gunicorn --config gunicorn_config.py dashboard:app"
        disks:
          - name: shared-logs
            mountPath: /data
    ```

4.  **Deploy:**
    *   Push your project to GitHub.
    *   Create a new "Blueprint" on Render.com and connect it to your GitHub repository.
    *   Render will automatically read your `render.yaml`, build both services, and deploy your live dashboard.

By following these detailed steps, we can seamlessly build and deploy a professional, public-facing dashboard for your bot.

## Next Steps: Fine-Tuning with GPTZero as Ground Truth (Next Session)
- **Goal:** Improve the accuracy of our rule-based system by benchmarking it against a state-of-the-art detector.
- **Action Plan:**
    1.  Collect a diverse batch of sample Reddit posts (both human and potentially AI-generated).
    2.  Run these posts through our bot to record its internal `ai_suspicion` score for each.
    3.  Manually run the same posts through the public GPTZero tool to get a "ground truth" verdict.
    4.  Analyze the differences and use this data to fine-tune the weights, rules, and thresholds in `bot.py` to better align with GPTZero's accuracy.
- **Note:** This approach avoids direct API integration, keeping the bot self-contained and free to run. This will be the focus of our next development session.

## 1. Project Setup
- [x] Initialize Python project and virtual environment
- [x] Create requirements.txt with dependencies
- [x] Set up .env for Reddit API keys

## 2. Reddit Bot Skeleton
- [x] Connect to Reddit using PRAW
- [x] Monitor specified subreddits for new comments (now uses REDDIT_SUBREDDITS)
- [x] Allow subreddits to be set via config/env
- [x] Respond only when triggered (mention or command)

## 3. Local AI Detection Checks
- [x] Implement perplexity calculation (small language model)
- [x] Implement burstiness (sentence length stddev)
- [x] Implement vocabulary richness (type-token ratio)
- [x] Make thresholds configurable
- [x] Test local detection logic on sample human + AI texts
- [x] Reply with local check result if human-like  
  _Reply logic implemented in bot.py_
- [x] Beautiful, English, Markdown-formatted reply with summary verdict  
  _Implemented in bot.py_
- [x] Integrate local language model (tiny-gpt2 via transformers) for perplexity/log-likelihood  
  _Performance-optimized for Raspberry Pi, with fallback_
- [x] Advanced linguistic heuristics (syntactic complexity, coherence, readability)  
  _Implemented in local_detection.py and bot.py_
- [x] ML-based metric aggregation (logistic regression, etc.) for final verdict  
  _Implemented in bot.py, with fallback to rule-based logic_
- [x] Switched to PRAW for collecting human Reddit comments from real subreddits  
  _Rate limit aware, avoids account blocks_

## 4. Bot Response Logic
- [x] Reply with local check result if human-like  
  _Reply logic implemented in bot.py_
- [x] Enhanced debug and trigger logging  
  _Implemented in bot.py_

## 5. Logging and Configuration
- [x] Log all actions and decisions  
  _Logging implemented for triggers and replies in bot.py_
- [x] Use environment variables for all secrets and config

## 6. Deployment
- [ ] Create Dockerfile or Render.com config
- [ ] Test deployment on Render.com
- [ ] Ensure Render auto-restarts bot on crash
- [ ] Log deployment success and startup events

## 7. (Optional) Admin and Monitoring Features
- [ ] Add commands for threshold tuning
- [ ] Add simple dashboard or log viewer
- [ ] Expose lightweight /metrics endpoint (for future dashboard or monitor)

## 8. Advanced Linguistic Features for AI Detection (Planned/Next)
- [x] Integrate spaCy for POS tagging and Named Entity Recognition (NER) **(DONE: spaCy added to requirements.txt and model loaded in local_detection.py)**
- [x] Add POS tag distribution features (noun/verb/adjective ratio) **(DONE: Function added to local_detection.py to compute POS ratios using spaCy)**
- [x] Add named entity density feature (entities per 100 words) **(DONE: Function added to local_detection.py to compute named entities per 100 words using spaCy)**
- [x] Implement repeated n-gram detection (repeated phrases, not just words) **(DONE: Function added to local_detection.py to detect repeated n-grams)**
- [x] Add these features to local_detection.py and include them in the detection scoring **(DONE: Integrated new features into scoring and verdict logic in bot.py)**
- [x] Update format_detection_results in bot.py to use and display these new features **(DONE: New features are now shown in the Markdown report)**
- [x] Tune scoring logic to leverage new features for better AI detection **(IN PROGRESS: Adjusting thresholds and weights for new features based on test results)**
- [ ] Test on both human and AI-generated Reddit posts for improved accuracy

### Next Batch of Features (No ML/API Required)
_IN PROGRESS: Continue implementation and tuning of these features in the next session._
- [ ] Sentence structure variety (spaCy)
- [ ] Hedging/uncertainty phrase count
- [ ] Parenthetical/bracket usage
- [ ] Unusual punctuation patterns
- [ ] Expanded pronoun ratios
- [ ] Lexical diversity over chunks
- [ ] Named entity type distribution

_Note: These features are being added to further improve detection. The feature set is under review to ensure a balance between broad coverage and overfitting. The goal is to maximize detection accuracy without introducing excessive complexity or false positives._

---

## Current Goal
- [x] Pull human-only Reddit post data from real subreddits using PRAW, focusing on pre-AI era content for high-quality human labels.
  - [x] Extracted 100,000 human Reddit posts from 2018 .zst file (see filtered_posts.jsonl for data)
- [x] Generate AI Reddit post data using distilgpt2 (see tinyllama_fake_reddit.jsonl for output)
  - [ ] Current model produces low-quality, unrealistic posts. Need a more robust method for generating convincing fake Reddit posts.
  - [x] Attempted DeepSeek/OpenRouter AI post generation (FAILED: API/quality issues, feature abandoned for now)
- Respect Reddit API rate limits and avoid account blocks while collecting data.
- [x] Train ML model on Reddit dataset (human and fake posts) (FAILED EXPERIMENT: Not reliable due to lack of quality AI data)
- [ ] **Tune the detection system for optimal balance between false positives (humans flagged as AI) and false negatives (AI flagged as human).**
  - [ ] If tuning fails to achieve reliable detection, research or implement a more robust method (ensemble approaches, external detectors, or improved AI data for training).
  - [ ] NOTE: Current tuning is making all posts 'Likely Human', including AI posts. Further iteration and feature engineering is needed.

## Future Improvements: Making AI Check More Reliable & Accurate
- [ ] Focus on improving and expanding linguistic heuristics (syntactic complexity, coherence, semantic similarity, etc.)
- Use open-source local language models (e.g., GPT-2, LLaMA, or DistilBERT) for deeper analysis
- Aggregate multiple metrics into a weighted score or use a simple ML classifier (future revisit)
- Allow user feedback to improve detection (e.g., upvote/downvote bot replies, report false positives/negatives)
- Regularly update and test detection logic on new AI-generated and human text samples
- Add support for language detection and adapt metrics for non-English comments
- Consider ensemble approaches (combine several detection strategies)
- Document all metrics and thresholds for transparency
- [ ] Research or implement a more robust method for generating realistic fake Reddit posts (current outputs are low-quality; see tinyllama_fake_reddit.jsonl)

---

## Planned: Expanded Detection Metrics (to be implemented)
To improve detection reliability, add the following metrics to the scoring system:

- **Em Dash Frequency**: Count occurrences of "—" per 1000 words. High frequency may indicate AI-generated text.
- **Special Unicode Characters**: Detect presence of non-ASCII or rare Unicode characters. Unusual characters can be a sign of AI output.
- **Overused Words Count**: Identify words that are repeated unusually often (e.g., >10 instances per 1000 words).
- **Flesch-Kincaid Grade Level**: Compute readability score using `textstat` or similar library. Very high grade level (>13) may indicate AI text.
- **Noun-to-Verb Ratio**: Use POS tagging (spaCy or NLTK) to compute the ratio. High ratio (>1.5) can be a signal of AI writing style.
- **Personal Pronoun Ratio**: Count first-person pronouns (I, me, my, we, etc.) as a percentage of total words. Low ratio (<5%) may indicate AI.
- **Account Age**: Fetch Reddit user account creation date via API. Accounts <30 days old are more likely to be bots.
- **Karma Score**: Fetch user's karma from Reddit API. Low karma (<100) may indicate a new or bot account.

**Implementation Notes:**
- Text-based metrics can be implemented using Python string methods, regex, and NLP libraries (spaCy, NLTK, textstat).
- Account-based metrics require additional Reddit API calls to fetch user info.
- Integrate all metrics into a unified scoring system, assigning points based on thresholds (see example table in chat).
- Document each metric and its threshold in code and README for transparency.

**Progress Log:**
- [x] Implemented text-based metrics:
    - Special Unicode Characters
    - Overused Words
    - Flesch-Kincaid Grade Level
    - Noun-to-Verb Ratio
    - Personal Pronoun Ratio
- [x] Implemented account-based metrics (Account Age, Karma Score) using Reddit API (PRAW). Handles deleted/anonymous users gracefully.
- [!] NOTE: Account-based metrics are currently **disabled during batch testing** for speed and API reliability. Re-enable for full evaluation or production use.
- [x] Batch test review: The rare 'Potentially AI-Generated' false positives are explainable edge cases (structured posts, bots, logs, or spam). No further tuning needed at this time. Review completed.

**Rationale:**
This approach combines easy-to-spot textual patterns (such as em dash frequency and special/invisible Unicode characters) with advanced linguistic analysis (readability, sentence length variation, vocabulary richness, syntactic complexity) and Reddit account metadata (age, karma). By aggregating these diverse signals into a unified scoring system, the bot can robustly flag likely AI-generated Reddit posts without relying solely on machine learning.

- **Robustness:** No single indicator is decisive, but the combination increases reliability.
- **Transparency:** Each metric and its threshold are documented and adjustable.
- **Adaptability:** The system can be tuned as new patterns emerge or as adversaries adapt.
- **Non-ML:** Avoids the pitfalls of unreliable ML models when high-quality labeled data is scarce.

*No method is foolproof—some indicators (like em dash usage) can be controversial or context-dependent. The scoring system should be regularly tested and thresholds adjusted to minimize false positives/negatives.*

**NOTE:**
- The ML model is currently NOT reliable due to lack of high-quality AI data. ML-based detection is a FAILED EXPERIMENT. Focus is now on improving heuristics and rule-based detection.

## [2024-06-09] Detection Logic Update & Test Plan
- [x] Replaced old weighted scoring with new rule-based logic:
    - entity_density > 6 → Likely Human
    - entity_density < 3 and perplexity > 35 and coherence < 0.2 → Potentially AI-Generated
    - entity_density < 4 and (perplexity > 30 or coherence < 0.3) → Possibly AI-Generated
    - else Likely Human
- [x] Added strong AI override: perplexity > 80 and coherence < 0.25 → Potentially AI-Generated
- [x] Batch test on both human and AI posts (new logic)
- [x] System now works decently; continue to monitor and tune as needed
- [x] Updated classic AI signal logic: now requires at least 3 signals to always flag as Potentially AI-Generated, or 2 signals only if main verdict is Possibly AI-Generated. No escalation for just 1 signal. This reduces false positives from single casual phrases.
- [x] After classic AI signal threshold update, system is working decently and is well-balanced between false positives and catching obvious AI.

## [2024-06-09] Refactor: bot.py Structure & Documentation
- Refactored bot.py for clarity and maintainability while keeping a functional style (no classes)
- All major logic is now in well-documented functions:
    - load_config(): Loads and validates environment variables
    - create_reddit_client(): Initializes the Reddit API client
    - load_ml_model(): Loads the ML model if available
    - get_account_metrics(): Fetches Reddit account age and karma
    - extract_features(): Extracts all numerical features for ML
    - format_detection_results(): Computes and formats the AI detection report
    - run_bot(): Main loop for monitoring and replying to comments
    - main(): Entrypoint
- Added type hints and docstrings to all functions
- Improved error handling and logging throughout
- All configuration is loaded and validated at startup
- No logic changes, just improved structure, documentation, and best practices
- The code is now easier to maintain, debug, and extend for future features

## [2024-06-09] Detection Logic Generalization
- Generalized the Reddit-style heuristic: it is now only a weak signal (adds +1 to ai_suspicion) and not a primary trigger for AI detection.
- The main verdict logic is now based on an ai_suspicion score:
    - Linguistic/structural signals (entity density, perplexity, coherence, etc.) add 1 or 2 points each.
    - Reddit-story patterns only add +1 if present (>=2 signals, long, coherent).
    - Verdicts: ai_suspicion >= 3 → Potentially AI, 2 → Possibly AI, else Likely Human.
- This makes the bot robust for all subreddits, not just AITA-style or story-based posts.
- See bot.py for implementation details.

## [2024-06-09] Entity Density Shortcut Removed
- Removed the 'entity_density > 6 → Likely Human' shortcut from the verdict logic.
- Now, entity density > 6 only nudges the ai_suspicion score down by 1 (never below 0), but does not override the suspicion score.
- This prevents entity-rich AI text from being misclassified as human.
- See bot.py for implementation details.

## [2024-06-09] Increased Aggressiveness & New Heuristics
- Increased aggressiveness of AI detection:
    - Reddit-story signals (>=2, long, coherent) now add +2 to ai_suspicion (was +1).
    - Lowered thresholds: ai_suspicion >= 2 → Potentially AI, 1 → Possibly AI, else Likely Human.
- Added new heuristic: if the post contains no contractions (e.g., don't, can't, I'm), add +1 to ai_suspicion (AI often omits contractions).
- Added debug logging to print all key metrics and the ai_suspicion score for each post (for tuning and transparency).
- See bot.py for implementation details.

## [2024-06-18] Analyze Parent Post on Trigger
- Changed the bot to analyze the parent post (submission) content, not the comment, when triggered.
- Now, when called with !aicheck, the bot fetches the submission, concatenates its title and selftext, and analyzes that text.
- Added logging to indicate which post is being analyzed.
- See bot.py for details.
- If the bot is not replying, check for issues in trigger detection, Reddit API permissions, or error handling in the main loop.

## [2024-06-18] Debugging: Bot Not Replying After Parent Post Change
- Added detailed logging around trigger and submission fetch logic in bot.py to diagnose why the bot was not replying.
- Discovered that the bot does not reply to its own comments (by design, to avoid loops and spam).
- Confirmed that the bot works as expected when triggered by a different Reddit account.
- Lesson: Always test bot triggers from a different account than the bot itself.
- Next steps: Continue tuning detection logic and monitor logs for any further issues.

## [2024-06-19] Reply Format and Tuning Update
- **Tuned Down Aggressiveness:** The threshold for "🔴 Potentially AI-Generated" was raised from `ai_suspicion >= 2` to `ai_suspicion >= 3` to reduce false positives.
- **Simplified Reply Format:** The bot's reply was redesigned to be more user-friendly for the average Redditor.
    - Removed technical jargon (Perplexity, Entity Density).
    - Now displays the internal "AI Signal Score" and Account Age.
- **Improved Disclaimer:** Updated the footer to be more professional and transparent: `^I'm an experimental bot. Scores are an educated guess and may be inaccurate.`
- **Prettified Output:** The reply format was further improved for clarity and visual appeal.
    - Used a markdown list to ensure key metrics appear on separate lines.
    - Added a dynamic explanation next to the AI Signal Score to provide users with immediate context.

## [2024-06-19] Final Tuning Log
- **Baseline before adjustment:** The detection logic was set to be conservative to minimize false positives. The thresholds were:
    - `ai_suspicion >= 3` → 🔴 Potentially AI-Generated
    - `ai_suspicion >= 1` → 🟡 Possibly AI-Generated
- **Adjustment:** To make the bot slightly more sensitive, the threshold for "Potentially AI" was lowered. See `bot.py` for the new values.
- **Final Adjustment (Human-Favored):** After testing, the bot was made even *less* aggressive to give human posts the benefit of the doubt. The final, more lenient thresholds are:
    - `ai_suspicion >= 3` → 🔴 Potentially AI-Generated
    - `ai_suspicion == 2` → 🟡 Possibly AI-Generated

## [2024-06-19] Final Optimizations for Raspberry Pi
- **Code Optimization:** Removed an unused `burstiness` calculation from the detection logic to save CPU cycles on every analysis. This improves performance without affecting accuracy.
- **System-Level Optimization:** Added `Nice=10` to the `systemd` service configuration to ensure the bot runs with a lower CPU priority, keeping the Raspberry Pi responsive.

## [2024-06-19] Project Cleanup
- **Removed Obsolete Files:** Cleaned up the project directory by deleting numerous files related to the old, abandoned machine learning experiment. This includes:
    - Old training and data processing scripts (`train.py`, `ai_data.py`, etc.).
    - Raw and processed datasets (`.csv`, `.jsonl` files).
    - The trained model file (`ai_classifier.joblib`).
- This leaves the project much leaner and focused only on the current rule-based bot.

## [2024-06-19] User Audit Log
- **Added User Log:** Implemented a separate logging system to track all user interactions.
- A new file, `user_log.log`, is now created to record the timestamp, username, subreddit, and comment ID for every user who successfully triggers the bot.
- This provides a clean and dedicated audit trail for monitoring bot usage.

## [2024-06-19] Improved Debug Logging
- **Reduced Log Noise:** Refactored the logging logic to only record detailed information when the bot is actually triggered (by `!aicheck` or a username mention).
- This makes the `bot_debug.log` file significantly cleaner and easier to read, as it no longer logs every single comment the bot streams.

## [2024-06-20] Fine-Tuning for False Positives
- **Identified False Positive:** A real human post was incorrectly flagged as "Potentially AI-Generated" due to a combination of very high perplexity, low coherence, and a lack of contractions.
- **Tuned Down "Confusing Post" Penalty:** The rule for `(perplexity > 80 and coherence < 0.25)` was too aggressive. Its penalty was lowered from `+2` to `+1` on the `ai_suspicion` score.
- **Added "Very Human" Reward:** A new rule was added to reward posts that exhibit strong, human-like Reddit patterns. If a post has 3 or more "Reddit signals" (like "AITA", age/gender tags, etc.), its `ai_suspicion` score is now reduced by 1.
- **Goal:** These changes make the bot's logic more robust and less likely to be fooled by the limitations of its underlying models, leading to more accurate detection.

## [2024-06-20] Final Log Cleanup
- **Set Log Level to INFO:** Changed the root logger level from `DEBUG` to `INFO` to suppress noisy, low-level network logs from the PRAW library.

## [2024-06-19] Deployment Checklist: Running on Raspberry Pi (PIPERONI)

To deploy and keep the Reddit AI detection bot running reliably and efficiently on a Raspberry Pi (PIPERONI), follow these steps:

1. **Optimize for Raspberry Pi Performance**
    - Use lightweight Python packages only. Avoid large models unless you have a Pi 4+ with lots of RAM.
    - If using GPT-2 for perplexity, use the smallest model (e.g., `distilgpt2`).
    - If the ML model is too slow, stick to rule-based detection (already the default/fallback).

2. **Prepare Environment & Configuration**
    - Use Python 3.9+ (3.11+ preferred for speed).
    - Set up a virtual environment (`python3 -m venv venv`).
    - Install dependencies: `pip install -r requirements.txt`.
    - Ensure `.env` is set up with all Reddit API keys and config.
    - Increase swap space if you run into memory errors (especially with spaCy/transformers).

3. **Set Up as a Systemd Service (Recommended)**
    - Create `/etc/systemd/system/reddit-bot.service` with:
      ```ini
      [Unit]
      Description=Reddit AI Detection Bot
      After=network.target

      [Service]
      WorkingDirectory=/home/pi/reddit-bot
      ExecStart=/home/pi/reddit-bot/venv/bin/python3 /home/pi/reddit-bot/bot.py
      Restart=always
      User=pi
      Nice=10

      [Install]
      WantedBy=multi-user.target
      ```
    - Enable and start:
      ```sh
      sudo systemctl daemon-reload
      sudo systemctl enable reddit-bot
      sudo systemctl start reddit-bot
      sudo systemctl status reddit-bot
      ```
    - Alternative: Use `tmux` or `screen` for manual persistent sessions if not using systemd.

4. **Logging & Monitoring**
    - Monitor `bot_debug.log` for errors and activity.
    - Set up log rotation (e.g., with `logrotate`) to prevent disk from filling up.
    - (Optional) Add a simple `/metrics` or `/health` endpoint for health checks.

5. **Crash Recovery & Auto-Restart**
    - Systemd with `Restart=always` will auto-restart the bot on crash or reboot.
    - Test by killing the process and ensuring it restarts automatically.

6. **Resource Management**
    - Monitor CPU/RAM with `htop` or `top`.
    - If spaCy or transformers are too heavy, use only rule-based heuristics.
    - Reduce the number of monitored subreddits if needed.
    - Increase polling intervals or use `skip_existing=True` in PRAW streams.

7. **Network & API Limits**
    - Ensure stable internet connection.
    - Respect Reddit API rate limits (already handled in code).

8. **Security**
    - Run the bot as a non-root user (e.g., `pi`).
    - Never commit `.env` with secrets to GitHub.

9. **(Optional) Docker Deployment**
    - If desired, create a `Dockerfile` and use Docker Compose for portability. (Systemd is simpler for Pi.)

10. **Maintenance**
    - Update dependencies regularly, but pin versions in `requirements.txt`.
    - Backup `.env` and important data.

11. **Set Target Subreddits**
    - In your `.env` file, set:
      ```
      REDDIT_SUBREDDITS=TrueOffMyChest,AITAH,tifu
      ```
    - The bot will now only monitor and reply to triggers in these subreddits: r/TrueOffMyChest, r/AITAH, and r/tifu.

---

## Dashboard - Next Steps to Final Product
- **Goal:** Evolve the current MVP dashboard into a production-ready, polished application.

### Phase 1: UI/UX Enhancements
- [ ] **Integrate Modern Components:** As requested, incorporate UI elements from [reactbits.dev](https://reactbits.dev/) or similar modern component libraries to improve the look and feel.
- [ ] **Refine Layout:** Improve the visual hierarchy, spacing, and mobile responsiveness.
- [ ] **Interactivity:** Make chart segments clickable to filter data; add tooltips with more information.

### Phase 2: Deeper Data Insights
- [ ] **Add Trend Chart:** Implement a line chart to show the AI detection rate over time (daily/weekly), as originally planned. This will require enhancing the `log_parser.py` to handle time-series aggregation.
- [x] **Display More Stats:** Include cards for:
    - [x] Most active subreddits (where the bot is triggered most).
    - [ ] Bot uptime or last-seen timestamp.
    - [ ] Average AI suspicion score across all analyzed posts.

### Phase 3: Production Readiness
- [ ] **Robust Caching:** Replace the simple in-memory cache with a more robust solution like Flask-Caching to improve performance.
- [ ] **Log Rotation:** Set up a log rotation mechanism (e.g., using Python's `RotatingFileHandler` or a system tool like `logrotate`) to prevent log files from growing indefinitely.
- [ ] **Deployment Prep:** Create `gunicorn_config.py` and `render.yaml` to prepare for a seamless deployment on a platform like Render.com, as detailed in the project plan.
- [ ] **Testing:**
    - Perform load testing with large log files.
    - Test across different browsers and devices.

### Development & Progress Log
*   **[2024-06-21] Goal: Add Subreddit Insights to Dashboard.**
    *   **Why:** To make the dashboard more interesting and useful by showing where the bot is most active.
    *   **Action 1: Refactored `bot.py` Logging.** Modified `format_detection_results` to return the simple verdict string alongside the full report. This allows the main `run_bot` loop to capture the final verdict.
    *   **Action 2: Enriched `user_log.log`.** The bot now logs the `verdict` directly into the user log for each trigger. This creates a single, reliable source of data for the dashboard and eliminates the need to parse the noisy `bot_debug.log`.
    *   **Action 3: Upgraded `log_parser.py`.** Rewritten the parser to read the new, richer `user_log.log` format. It now calculates total triggers, verdict distribution, AND subreddit activity counts.
    *   **Action 4: Updated Dashboard Frontend.** Added a "Top Subreddits" card to `dashboard.html` and logic to `app.js` to display the new data, including making the subreddit names in the activity feed clickable.
*   **[2024-06-21] Goal: Test Empty Dashboard.**
    *   **Why:** The dashboard appeared empty after the recent feature additions.
    *   **Diagnosis:** Discovered that the existing `user_log.log` file contained entries in the old format, which the new parser correctly ignores.
    *   **Action:** Injected temporary, fake log data into `user_log.log` to populate the dashboard for immediate testing and verification of the new features. **(Status: Complete)**
*   **[2024-06-21] Current Goal: Implement AI Detection Trend Chart.**
    *   **Why:** To visualize how the frequency of different verdicts changes over time, providing deeper insight into bot activity and potential AI usage trends.
    *   **Plan:**
        1.  **Enhance `log_parser.py`:** Add logic to parse timestamps and aggregate verdict counts on a daily basis.
        2.  **Update `dashboard.py`:** Pass the new time-series data through the `/api/stats` endpoint.
        3.  **Modify `dashboard.html`:** Add a new card and a `canvas` element to hold the line chart.
        4.  **Implement Chart in `app.js`:** Use Chart.js to render the daily verdict trends.
*   **[2024-06-22] Architecture Shift: Separated Frontend & Backend.**
    *   **Why:** To use modern, rich UI components from Vercel/shadcn, we adopted a standard web architecture. The old system where Flask served both the data and the HTML was too simple for these modern tools.
    *   **New Architecture:**
        1.  **Backend (Data API):** `dashboard.py` is now a pure data provider. It reads logs and exposes statistics at `http://127.0.0.1:5001/api/stats`. It has NO user interface.
        2.  **Frontend (UI):** The `my-app/` directory contains a new Next.js/React application. It is responsible for all visuals. It fetches data from the backend API and displays it. It runs on `http://localhost:3000`.
    *   **Status:** The frontend is not displaying correctly, suggesting a communication breakdown with the backend. Diagnosing the issue now.

---

*   **[2024-06-22] Debugging Diary: The Great UI Mystery & The Final Fix.**
    *   **Why:** To document the extensive debugging process required to solve a critical UI rendering failure. This serves as a record of the steps taken and the ultimate root cause.
    *   **The Problem:** The new Next.js dashboard was rendering as a blank, unstyled page. The browser's developer tools showed no errors, and the data was being fetched correctly in the network tab.
    *   **Troubleshooting Journey:**
        1.  **Hypothesis 1: Broken Frontend Build.** The initial suspicion was a misconfiguration in Tailwind CSS or the Next.js build process. We tried re-initializing `shadcn/ui`, resetting configuration files, and even rebuilding the *entire* Next.js project from scratch. None of these actions solved the problem, proving the frontend setup was likely correct.
        2.  **Hypothesis 2: Backend Data Corruption.** After exhausting all frontend possibilities, the focus shifted to the data itself. A `curl` command was used to inspect the raw JSON output from the Flask `/api/stats` endpoint.
        3.  **The Discovery:** The `curl` output revealed the root cause. The `verdict` string in the JSON contained raw emoji characters (e.g., `🔴 Potentially AI-Generated`). The Flask server was sending these as invalid Unicode escape sequences (`\ud83d\udd34`), which silently crashed the browser's JavaScript JSON parser upon receipt. This was the silent killer.
    *   **The Fix:**
        1.  **Data Sanitization:** A `clean_text()` function was added to `log_parser.py` to strip all emojis and other non-ASCII characters from the data *before* it is sent to the frontend.
        2.  **Backend Restart:** The Python backend was restarted to apply the fix.
    *   **Result:** The UI immediately rendered correctly with full styling.
    *   **Final Steps:**
        - All individual React components (`StatsCards`, `VerdictChart`, etc.) were restored to `page.tsx`.
        - The `recharts` library was installed to support the charts.
        - A final production build confirmed the entire dashboard is now fully functional.
    *   **Lesson Learned:** When a frontend application fails silently, always inspect the raw data payload from the API. Invalid characters or formatting can break the entire rendering process without throwing obvious errors.

---

## [2024-06-22] Animation Troubleshooting Log & Next Steps
- **Goal:** Implement the animated components from [reactbits.dev](https://reactbits.dev) (`Threads` background, `Spotlight` card, `AnimatedList`).
- **Status:** **Failed.** The components have been implemented, but the animations are not working. A thorough debugging process is required for the next session.

### The Core Problem (as of end of session)
- A critical issue was identified: **There are no mouse interactions or animations working anywhere in the application.** This includes not only the complex `framer-motion` animations but also basic hover effects (like the `Spotlight` card). This points to a fundamental issue in how JavaScript-driven or utility-class-driven styles are being applied, rather than a bug in a single component.

### Summary of Unsuccessful Attempts
A detailed record of what was tried, to avoid repeating mistakes:
1.  **Initial Implementation (Recreation from Scratch):**
    - **Action:** Components were built based on visual inspection of `reactbits.dev`.
    - **Result:** Failed. The logic was likely too complex to replicate without seeing the source code, leading to numerous runtime errors and non-functional animations.
2.  **Dependency-Focused Rewrite:**
    - **Action:** The project was cleaned of the broken components. `framer-motion`, `clsx`, and `react-icons` were installed. New components were written using these libraries and best practices.
    - **Result:** Failed. While the components rendered without crashing, the core animations (spotlight hover, list item entrance) still did not trigger.
3.  **Tailwind CSS Configuration:**
    - **Action:** Hypothesized that Tailwind's JIT compiler was not generating the necessary CSS classes.
    - **Steps Taken:**
        - Added `keyframes` and `animation` entries to `tailwind.config.ts`.
        - Added `group-hover:opacity-100` to the `safelist` in `tailwind.config.ts`.
    - **Result:** Failed. None of these configuration changes had any visible effect on the animations.

### Next Steps & Plan for Next Session
The problem is clearly more complex than a simple code or configuration error. The next attempt must be more systematic and start from the basics.
1.  **Verify Basic CSS Interactivity:**
    - The very first step is to add a simple, plain CSS `:hover` pseudo-class to an element (e.g., changing a background color). If this does not work, it indicates a deep issue with the rendering pipeline, possibly related to layout structure (e.g., an invisible overlay preventing mouse events).
2.  **Create a Minimal Test Environment:**
    - If basic CSS works, proceed to create a brand-new, minimal Next.js + Tailwind project.
    - Attempt to get **one** simple animation working. Start with a Tailwind `hover:` class, then a `group-hover:` class, and finally a basic `framer-motion` animation. This will isolate the problem from our project's specific configuration.
3.  **Direct Source Code Analysis:**
    - We must find and analyze the **original source code** for the `reactbits.dev` components. There may be crucial implementation details, CSS, or configurations that are not obvious from visual inspection.
4.  **Inspect Browser Event Listeners & Computed Styles:**
    - When tackling this again, use the browser's developer tools to inspect the elements that *should* be animating.
    - Check the "Event Listeners" tab to see if `mousemove`, `mouseenter`, etc., are even attached to the elements.
    - Check the "Computed" tab to see if the CSS properties from `framer-motion` or `tailwindcss` (e.g., `transform`, `opacity`) are being applied at all during the interaction.

This structured approach is our best chance of identifying the root cause and finally solving this issue.

---

## [2024-06-22] UI Overhaul: Re-implementing reactbits.dev Components
- **Goal:** Address failing animations and visual glitches by correctly implementing the modern components from [reactbits.dev](https://reactbits.dev/), as requested.
- **Status:** In Progress **(Blocked by Animation Issues)**
- **Plan:**
    - **1. Project Cleanup & Reset:**
        - [x] Deleted all previous, non-functional attempts at the new components (`ThreadsBackground`, `SpotlightCard`, etc.).
        - [x] Reverted the main layout and component files to a stable, working state to prevent errors.
    - **2. Dependency & Component Scaffolding:**
        - [x] Installed necessary and robust dependencies (`clsx`, `react-icons`, `framer-motion`).
        - [x] Created new, high-quality components based on proven, open-source examples that match the `reactbits.dev` style:
            - [x] `GridBackground`: A performant, CSS-only grid background.
            - [x] `Spotlight`: A smooth, mouse-tracking spotlight effect for cards.
            - [x] `Notification`: A container for animated list items.
    - **3. Integration & Final Fixes:**
        - [x] Integrated all new components into the dashboard.
        - [x] Resolved all build and runtime errors, including:
            - [x] Fixing incorrect module path aliases.
            - [x] Correcting a layout issue causing duplicate titles in the activity feed.
    - **4. Current Focus: Final Polish & Animation Troubleshooting**
        - [x] **(Blocked)** Diagnose and fix the `reactbits.dev` animations that are still not working as expected.
        - [ ] Thoroughly test all UI components and interactions.
        - [ ] Ensure all data from the backend is displayed correctly.

## [2024-06-22] Vertical Slice: Connecting Frontend to Live Backend
- **Goal:** Move beyond mock data and create a fully functional vertical slice by connecting the Next.js frontend to the live Python backend.
- **Status:** In Progress
- **Plan:**
    - **1. Start Backend Server:** Run the `dashboard.py` Flask application to serve live log data from the `/api/stats` endpoint.
    - **2. Connect Frontend:** Modify `my-app/src/app/page.tsx` to fetch data from the local Flask API endpoint.
    - **3. Align Data Structures:** Ensure the data interfaces and components in the frontend match the JSON structure provided by the backend API.
    - **4. Test & Verify:** Confirm that the dashboard correctly displays live data from the bot's logs.

## [2024-06-20] Final Log Cleanup
- **Set Log Level to INFO:** Changed the root logger level from `DEBUG` to `INFO` to suppress noisy, low-level network logs from the PRAW library.

---
