# Solo Founder Agents

Multi-agent AI system for solo founders to build digital products.

## Concept

One person (solo founder) manages a team of AI agents that autonomously develop digital products (mobile apps, websites, etc.). The founder sets goals and reviews artifacts at checkpoints; agents do the rest.

## Agent Roles

| Role | Responsibility |
|------|----------------|
| 🎯 Product Manager | Requirements, backlog, priorities |
| 📊 Analyst | Feature decomposition into tasks |
| 🏗️ Architect | System design, ADR |
| 🎨 Designer | UI/UX, design system |
| 💻 Developer | Code (React/RN + Node.js) |
| 🧪 QA | Tests, validation |
| 📝 Tech Writer | Documentation |

## Tech Stack

- **Framework:** CrewAI
- **LLM:** OpenRouter (GPT-4o, Claude Sonnet)
- **Infrastructure:** VPS + Docker
- **Storage:** Markdown/JSON files
- **Interface:** CLI + Telegram Bot
- **Integration:** GitHub API

## Documentation

- [ARTIFACTS.md](./ARTIFACTS.md) — Artifact definitions
- [docs/LLM-CONFIG.md](./docs/LLM-CONFIG.md) — LLM models per role
- [docs/INFRASTRUCTURE.md](./docs/INFRASTRUCTURE.md) — Infrastructure design
- [docs/MVP.md](./docs/MVP.md) — MVP definition

## Templates

All artifact templates are in the `templates/` directory.

## Status

🟡 In Development — Phase 1: Foundation

## License

MIT
