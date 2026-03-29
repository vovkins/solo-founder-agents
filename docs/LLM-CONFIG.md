# LLM Configuration

## Провайдер

**OpenRouter** — единая точка доступа к различным LLM моделям.

Документация: https://openrouter.ai/docs

---

## Модели по ролям

| Роль | Модель | Причина |
|------|--------|---------|
| Product Manager | z-ai/glm-5 | Основная модель для всех ролей |
| Analyst | z-ai/glm-5 | Основная модель для всех ролей |
| Architect | z-ai/glm-5 | Основная модель для всех ролей |
| Designer | z-ai/glm-5 | Основная модель для всех ролей |
| **Developer (код)** | z-ai/glm-5 | Основная модель для всех ролей |
| **Developer (reviewer)** | openai/gpt-5.1-codex-mini | Другая модель для code review |
| QA | z-ai/glm-5 | Основная модель для всех ролей |
| Tech Writer | z-ai/glm-5 | Основная модель для всех ролей |

---

## Важно: Developer vs Reviewer

Developer (coder) и Reviewer используют **разные модели** — это критически важно для качественного code review.

---

## Конфигурация CrewAI

CrewAI поддерживает OpenRouter через OpenAI-совместимый API:

```python
from crewai import Agent

developer = Agent(
    role="Developer",
    goal="Write clean, efficient code",
    backstory="Experienced software developer",
    llm="openrouter/z-ai/glm-5"
)

reviewer = Agent(
    role="Reviewer", 
    goal="Review code quality",
    backstory="Senior code reviewer",
    llm="openrouter/openai/gpt-5.1-codex-mini"
)
```

---

## Переменные окружения

```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

---

## Обновлено

- **Дата:** 2026-03-29
- **Изменение:** Перевод всех ролей на z-ai/glm-5, Reviewer на openai/gpt-5.1-codex-mini
