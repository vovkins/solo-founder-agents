# Solo Founder Agents

**Multi-agent AI system for solo founders to build digital products.**

## Overview

Solo Founder Agents is a system that enables one person (solo founder) to manage a team of AI agents that autonomously develop digital products. The founder reviews artifacts at checkpoints rather than writing code directly.

## Architecture

### Agents (8 total)

| Agent | Model | Role |
|-------|-------|------|
| 🎯 **PM** | GPT-4o | Requirements, PRD, Backlog |
| 📊 **Analyst** | GPT-4o | Task decomposition, specs |
| 🏗️ **Architect** | GPT-4o | ADR, System Design |
| 🎨 **Designer** | GPT-4o | Design System, UI specs |
| 💻 **Developer** | Claude Sonnet | Implementation |
| 👀 **Reviewer** | GPT-4o | Code review |
| ✅ **QA** | GPT-4o | Testing, sign-off |
| 📝 **Tech Writer** | GPT-4o | Documentation |

> **Note:** Developer and Reviewer use different LLM models for cross-validation.

### Checkpoints

The pipeline pauses at 5 checkpoints for founder review:

1. **Checkpoint 1** — After PRD creation
2. **Checkpoint 2** — After System Design
3. **Checkpoint 3** — After Implementation
4. **Checkpoint 4** — After QA testing
5. **Checkpoint 5** — Final release

## Installation

```bash
# Clone the repository
git clone https://github.com/vovkins/solo-founder-agents.git
cd solo-founder-agents

# Install with Poetry
poetry install

# Or with pip
pip install -e .
```

## Configuration

Create a `.env` file:

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key
GITHUB_TOKEN=your-github-token
GITHUB_REPO=owner/repo

# Optional
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### LLM Models

Configure models in `.env` (defaults shown):

```env
LLM_PM=openai/gpt-4o
LLM_ANALYST=openai/gpt-4o
LLM_ARCHITECT=openai/gpt-4o
LLM_DESIGNER=openai/gpt-4o
LLM_DEVELOPER=anthropic/claude-sonnet
LLM_REVIEWER=openai/gpt-4o
LLM_QA=openai/gpt-4o
LLM_TECH_WRITER=openai/gpt-4o
```

## Usage

### CLI

```bash
# Initialize project
solo-founder-agents init

# Check status
solo-founder-agents status

# List issues
solo-founder-agents issues

# Run a task
solo-founder-agents run 42

# Interactive mode (pauses at checkpoints)
solo-founder-agents run 42 --interactive

# Manage checkpoints
solo-founder-agents checkpoint
solo-founder-agents approve checkpoint_1
solo-founder-agents reject checkpoint_1 "Needs revision"

# Create issue
solo-founder-agents new-issue --title "Feature" --label feature
```

### Telegram Bot

```bash
# Run the bot
python -m src.bot.telegram
```

Commands:
- `/start` — Start interaction
- `/status` — Project status
- `/issues` — Open issues
- `/run <issue>` — Run a task
- `/checkpoint` — Checkpoint status
- `/approve` — Approve checkpoint
- `/reject <reason>` — Reject checkpoint

### Programmatic

```python
from src.pipeline import pipeline, Checkpoint
from src.crews import run_core_crew, run_dev_crew

# Run requirements phase
result = run_core_crew("Build a task management app")
print(result["artifacts"]["prd"])

# Run development for a task
result = run_dev_crew(42, "Implement login feature")
print(result["status"])

# Manage checkpoints
pipeline.approve_checkpoint(Checkpoint.CHECKPOINT_1)
```

## Project Structure

```
solo-founder-agents/
├── config/
│   └── settings.py          # Configuration
├── src/
│   ├── agents/              # Agent definitions
│   │   ├── pm.py
│   │   ├── analyst.py
│   │   ├── architect.py
│   │   ├── designer.py
│   │   ├── developer.py
│   │   ├── reviewer.py
│   │   ├── qa.py
│   │   └── tech_writer.py
│   ├── tasks/               # Task definitions
│   ├── crews/               # Crew orchestrations
│   ├── tools/               # GitHub, storage tools
│   ├── bot/                 # Telegram bot
│   ├── pipeline.py          # Pipeline orchestration
│   └── cli.py               # CLI interface
├── tests/
├── data/
│   ├── artifacts/           # Generated artifacts
│   └── state/               # Pipeline state
└── docs/                    # Documentation
```

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black src tests

# Lint
poetry run ruff check src tests

# Run with Docker
docker-compose up --build
```

## Tech Stack

- **Framework:** CrewAI
- **LLM Provider:** OpenRouter
- **Frontend (generated):** React Native
- **Backend (generated):** Node.js
- **State:** Local Markdown/JSON (PostgreSQL later)
- **GitHub:** PAT for integration
- **Interface:** CLI + Telegram Bot

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines.

---

Built with ❤️ for solo founders.
