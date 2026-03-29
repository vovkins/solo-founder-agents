# Solo Founder Agents

Multi-agent AI system for solo founders to manage product development.

## Quick Start

```bash
# Install dependencies
poetry install

# Run CLI
poetry run solo-founder-agents status
poetry run solo-founder-agents issues
poetry run solo-founder-agents run <issue-number>

# Run with Docker
docker compose up -d
docker exec solo-founder-agents python -m src.cli status
```

## Agents

| Agent | Role | Model |
|-------|------|-------|
| PM | Product Manager | z-ai/glm-5 |
| Analyst | Requirements Analyst | z-ai/glm-5 |
| Architect | System Architect | z-ai/glm-5 |
| Designer | UI/UX Designer | z-ai/glm-5 |
| Developer | Code Implementation | z-ai/glm-5 |
| Reviewer | Code Review | openai/gpt-5.1-codex-mini |
| QA | Quality Assurance | z-ai/glm-5 |
| Tech Writer | Documentation | z-ai/glm-5 |

## Telegram Bot

### Setup

1. **Create bot via @BotFather:**
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Configure environment:**
   ```bash
   # Add to .env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

3. **Get your Telegram User ID:**
   - Write `/start` to your bot
   - Check logs: `docker logs sfa-telegram --tail 20`
   - Look for "User ID: XXXXXXXXX"

4. **Authorize users:**
   Edit `src/bot/telegram.py` and add your ID:
   ```python
   self.authorized_users = [123456789]  # Your Telegram ID
   ```

5. **Start the bot:**
   ```bash
   docker compose --profile bot up -d telegram-bot
   ```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/status` | Project status |
| `/issues` | List open issues |
| `/run <issue>` | Start working on issue |
| `/checkpoint` | Checkpoint status |
| `/approve` | Approve checkpoint |
| `/reject <reason>` | Reject checkpoint |
| `/help` | Help message |

## Environment Variables

Create `.env` file:

```bash
# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_key

# GitHub
GITHUB_TOKEN=your_github_pat
GITHUB_REPO=owner/product-repo

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
```

## Architecture

```
solo-founder-agents (this repo)
├── src/agents/          # Agent definitions
├── src/tasks/           # Task definitions
├── src/crews/           # CrewAI crews
├── src/tools/           # GitHub, state tools
├── src/bot/             # Telegram bot
└── config/              # Settings

product-repo (target repo)
├── src/                 # Product code (React Native)
├── docs/artifacts/      # PRD, System Design, etc.
└── .github/workflows/   # CI/CD
```

## Development Workflow

1. **Create issue** in product repo
2. **Run agents:** `/run <issue>` or CLI
3. **Review checkpoints** via Telegram
4. **Approve/Reject** artifacts
5. **Merge PR** after QA passes

## License

MIT
