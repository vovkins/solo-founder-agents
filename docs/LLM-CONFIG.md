# LLM Configuration

## Провайдер

**OpenRouter** — единая точка доступа к различным LLM моделям.

Документация: https://openrouter.ai/docs

---

## Модели по ролям

| Роль | Модель | Причина |
|------|--------|---------|
| Product Manager | openai/gpt-4o | Анализ, структурирование требований |
| Analyst | openai/gpt-4o | Декомпозиция, логика |
| Architect | openai/gpt-4o | Системное мышление |
| Designer | openai/gpt-4o | Креативность, дизайн-решения |
| **Developer (код)** | anthropic/claude-sonnet | Лучший для написания кода |
| **Developer (reviewer)** | openai/gpt-4o | Другая модель для code review |
| QA | openai/gpt-4o | Аналитика, тест-кейсы |
| Tech Writer | openai/gpt-4o | Тексты, документация |

---

## Конфигурация CrewAI

CrewAI поддерживает OpenRouter через OpenAI-совместимый API:

```python
from crewai import Agent

developer = Agent(
    role="Developer",
    goal="Write clean, efficient code",
    backstory="Experienced software developer",
    llm="openrouter/anthropic/claude-sonnet"
)
```

---

## Переменные окружения

```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

---

## Примечания

- Список моделей будет меняться по результатам экспериментов
- OpenRouter позволяет менять модели без изменения кода
- Можно тестировать разные модели для одной роли

---

## Полезные ссылки

- OpenRouter Models: https://openrouter.ai/models
- OpenRouter Docs: https://openrouter.ai/docs
- CrewAI LLM Connections: https://docs.crewai.com/how-to/LLM-Connections
