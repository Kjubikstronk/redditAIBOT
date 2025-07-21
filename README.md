# Reddit Hybrid AI Detection Bot

A cost-efficient Reddit bot that detects AI-generated comments using a hybrid approach:
- **Local checks** (perplexity, burstiness, vocabulary richness)
- **ZeroGPT API** for suspicious cases

Designed for easy deployment on [Render.com](https://render.com/) or similar platforms.

## Features
- Trigger-based comment analysis (mention or command)
- Local statistical checks to minimize API calls
- ZeroGPT API integration for advanced detection
- Configurable thresholds for local checks
- Logging for transparency
- Environment variable support for secrets

## Setup
1. **Clone the repository**
2. **Create and activate a virtual environment**
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in Reddit and ZeroGPT API keys

## Running the Bot
```bash
python bot.py
```

## Deployment
- Ready for deployment on [Render.com](https://render.com/) (Dockerfile or native Python)
- Minimal resource usage for free/cheap hosting

## Project Structure
- `bot.py` — Main bot logic
- `requirements.txt` — Python dependencies
- `.env.example` — Environment variable template
- `todo.md` — Development task list

## License
MIT 