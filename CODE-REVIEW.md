# CODE REVIEW — Solo Founder Agents

**Дата:** 2026-04-05  
**Рецензент:** Джарвис (AI-ассистент)  
**Проект:** solo-founder-agents  
**Репозиторий:** GitHub (vovkins/solo-founder-agents)

---

## 📋 Краткое резюме

Проект представляет собой multi-agent систему на базе CrewAI для автоматизации разработки соло-основателей. Архитектура выглядит хорошо продуманной, с четким разделением ролей (PM, Analyst, Architect, Designer, Developer, Reviewer, QA, Tech Writer) и checkpoint-системой для контроля качества.

**Общее впечатление:** Проект имеет хорошую архитектурную основу, но содержит несколько критичных проблем, которые могут привести к багам в рантайме, утечкам ресурсов и сложностям в поддержке.

---

## 🚨 КРИТИЧНО (BLOCKER) — Исправить немедленно

### 1. **Race condition в глобальном состоянии pipeline**

**Файл:** `src/pipeline.py:30-40`

```python
class Pipeline:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.current_stage = PipelineStage.REQUIREMENTS
        self.state = {...}
```

**Проблема:** Глобальный инстанс `pipeline` (строка 299) используется во всем проекте, но не имеет защиты от concurrent access. Если два pipeline запущены одновременно (например, два `/run` команды), они будут разделять состояние.

**Решение:**
- Использовать thread-safe обертку или блокировки
- Или создать отдельный инстанс Pipeline на каждый запуск

**Критичность:** 🔴 HIGH — Может привести к непредсказуемому поведению при параллельных запусках

---

### 2. **Отсутствие обработки ошибок в GitHub клиенте**

**Файл:** `src/tools/github_client.py:62-75`

```python
def update_issue(...):
    issue = self.get_issue(issue_number)
    kwargs = {}
    if title:
        kwargs["title"] = title
    # ...
    issue.edit(**kwargs)
    return self.get_issue(issue_number)  # Re-fetch
```

**Проблема:** 
- Если `issue.edit()` упадет с network error, исключение не обрабатывается
- Re-fetch после edit может быть избыточным (PyGithub уже возвращает объект)

**Решение:**
- Обернуть в try-except с логированием
- Добавить retry логику для network errors

**Критичность:** 🔴 HIGH — Может привести к падению пайплайна при временных проблемах с GitHub API

---

### 3. **Memory leak в `_llm_cache`**

**Файл:** `src/crews/base.py:14-22`

```python
_llm_cache: dict = {}

def _get_or_create_llm(model_name: str) -> LLM:
    if model_name not in _llm_cache:
        _llm_cache[model_name] = create_llm(model_name)
    return _llm_cache[model_name]
```

**Проблема:** 
- Глобальный кеш LLM инстансов никогда не чистится
- При длительной работе сервисов память будет расти
- Если LLM объекты держат connections/sockets, возможен resource leak

**Решение:**
- Добавить TTL или LRU eviction
- Или сделать кеш per-session с cleanup

**Критичность:** 🔴 MEDIUM-HIGH — Может привести к утечке памяти в long-running процессе

---

### 4. **Deadlock в StateManager при одновременном доступе**

**Файл:** `src/tools/state.py:31-37`

```python
def _load_state(self) -> Dict[str, Any]:
    with self._lock:
        ensure_state_dir()
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
```

**Проблема:**
- `_load_state()` вызывается в `__init__` с локом, но `save_state()` тоже использует тот же лок
- Если один поток держит лок при save, а другой вызывает load, возможен deadlock

**Решение:**
- Перепроверить логику локов
- Возможно, использовать RLock (reentrant lock)

**Критичность:** 🔴 MEDIUM — Может привести к зависанию при конкурентном доступе

---

## ⚠️ ВЫСОКИЙ ПРИОРИТЕТ

### 5. **Дублирование system prompts в агентах**

**Файлы:** `src/agents/pm.py`, `src/agents/analyst.py`, `src/agents/architect.py`, etc.

**Проблема:** Каждый агент содержит полный system prompt как строку в коде:
- `PM_SYSTEM_PROMPT = """..."""`
- `ANALYST_SYSTEM_PROMPT = """..."""`
- и т.д.

Это:
- Дублирует информацию о file permissions (копипаста из `file_permissions.py`)
- Усложняет изменения (нужно менять в 2 местах)
- Загромождает код

**Решение:**
- Вынести prompts в отдельные `.md` файлы
- Или генерировать программно из `ROLE_FILE_PERMISSIONS`

**Критичность:** 🟡 MEDIUM — Поддерживаемость

---

### 6. **Inconsistent return types в crews**

**Файл:** `src/crews/pm_crew.py` vs `src/crews/developer_crew.py`

```python
# pm_crew.py
def run_pm_crew(founder_vision: str) -> dict:
    return {"status": "completed", "result": str(result), "artifacts": {...}}

# developer_crew.py
def run_developer_crew(issue_number: int) -> dict:
    return {"status": "completed", "result": str(result), "issue_number": issue_number}
```

**Проблема:** Разные ключи в возвращаемых словарях (`artifacts` vs `issue_number`), что затрудняет унифицированную обработку.

**Решение:**
- Стандартизировать return type: `{"status", "result", "artifacts", "error", "metadata"}`
- Использовать TypedDict или dataclass

**Критичность:** 🟡 MEDIUM — Поддерживаемость

---

### 7. **Hardcoded branch name "main"**

**Файлы:** `src/tools/github_tools.py:107`, `src/tools/artifact_manager.py:38`

```python
def create_file_in_repo(..., branch: str = "main"):
    ...

class ArtifactManager:
    def __init__(self, ..., branch: str = "main"):
        ...
```

**Проблема:** 
- Branch "main" захардкожен во многих местах
- Если репозиторий использует "master" или другие имена, все сломается

**Решение:**
- Вынести в `settings.py`: `GITHUB_DEFAULT_BRANCH = "main"`
- Использовать везде

**Критичность:** 🟡 MEDIUM — Совместимость

---

### 8. **Отсутствие валидации в Telegram bot**

**Файл:** `src/bot/telegram.py:79-85`

```python
def is_authorized(self, user_id: int) -> bool:
    if not self.authorized_users:
        logger.warning(f"No authorized users configured. Allowing user {user_id}")
        return True
    return user_id in self.authorized_users
```

**Проблема:** Если `AUTHORIZED_USERS` не настроен, бот разрешает доступ ВСЕМ. Это insecure default.

**Решение:**
- Требовать явную настройку `AUTHORIZED_USERS`
- Или добавить в settings.py обязательное поле

**Критичность:** 🟡 MEDIUM — Безопасность

---

## 📝 СРЕДНИЙ ПРИОРИТЕТ

### 9. **Избыточное использование global instances**

**Файлы:** `src/tools/github_client.py:140`, `src/tools/state.py:180`, `src/pipeline.py:299`

```python
# Global instances
github_client = GitHubClient()
state_manager = StateManager()
pipeline = Pipeline()
```

**Проблема:** 
- Глобальные инстансы затрудняют тестирование
- Невозможно создать изолированные окружения

**Решение:**
- Использовать dependency injection
- Или фабричные функции вместо глобальных переменных

**Критичность:** 🟢 LOW-MEDIUM — Тестируемость

---

### 10. **Дублирование logic в tasks**

**Файлы:** `src/tasks/pm_tasks.py`, `src/tasks/analyst_tasks.py`, etc.

**Проблема:** Во многих task descriptions есть повторяющиеся куски:
- "Your job is to: ..."
- "Use templates/..."
- "Save to docs/..."

**Решение:**
- Вынести общие части в helper functions
- Или использовать template strings

**Критичность:** 🟢 LOW — DRY principle

---

### 11. **Artifact path generation magic**

**Файл:** `src/tools/artifact_manager.py:145-180`

```python
if artifact_type == ArtifactType.PRD:
    path = "docs/requirements/prd.md"
elif artifact_type == ArtifactType.SYSTEM_DESIGN:
    path = "docs/design/system-design.md"
# ... 10+ elif
```

**Проблема:** 
- Логика путей захардкожена в if-else цепочке
- Дублирует информацию из `ROLE_FILE_PERMISSIONS`
- Сложно менять структуру директорий

**Решение:**
- Вынести в конфигурационный словарь: `ARTIFACT_PATHS = {ArtifactType.PRD: "docs/requirements/prd.md"}`
- Или использовать naming convention

**Критичность:** 🟢 LOW — Поддерживаемость

---

### 12. **Logging without structured context**

**Файлы:** Все логи используют f-strings

```python
logger.error(f"Pipeline error: {e}")
logger.info(f"Role context set to: {role}")
```

**Проблема:** 
- Нет structured logging
- Сложно парсить логи для анализа
- Нет request_id для трейсинга

**Решение:**
- Добавить `structlog` или `logging.JsonFormatter`
- Добавить `request_id` или `session_id` в контекст

**Критичность:** 🟢 LOW — Операции

---

## 🧹 НИЗКИЙ ПРИОРИТЕТ (Code Quality)

### 13. **Длинные system prompts в коде**

**Файлы:** Все agents/*.py

**Проблема:** System prompts на 50-100 строк в triple-quoted strings загромождают код.

**Решение:**
- Вынести в `prompts/pm.md`, `prompts/analyst.md` и т.д.
- Загружать при инициализации

---

### 14. **Type hints не везде**

**Файлы:** Некоторые функции без type hints

**Пример:** `src/tools/file_permissions.py:90` — `check_file_permission(role: str, filepath: str, action: str = "create") -> bool:` ✅  
Но: `src/pipeline.py:45` — `def run_requirements_phase(self, founder_vision: str) -> dict:` — `dict` слишком общий

**Решение:**
- Использовать `TypedDict` или `dataclass` для структур данных
- Добавить return type hints везде

---

### 15. **Отсутствие docstrings в некоторых местах**

**Примеры:** `src/crews/base.py:16` — `_get_or_create_llm` без docstring

---

### 16. **Magic strings в pipeline stages**

**Файл:** `src/pipeline.py:18-28`

```python
class PipelineStage(str, Enum):
    REQUIREMENTS = "requirements"
    ANALYSIS = "analysis"
    ...
```

Хорошо, но некоторые строки дублируются в `state_manager.update_agent_state()`.

---

## 🏗️ АРХИТЕКТУРНЫЕ ПРЕДЛОЖЕНИЯ

### A. Разделение concerns для AgentCache

**Файл:** `src/agents/_agent_cache.py`

**Предложение:** Вынести кеширование агентов в отдельный модуль с TTL и eviction policy.

---

### B. Pipeline runner как отдельный класс

**Проблема:** `Pipeline.run_full_pipeline()` делает слишком много (50+ строк).

**Предложение:**
```python
class PipelineRunner:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
    
    def run_phase(self, phase_name: str, **kwargs) -> dict:
        ...
    
    def run_all(self, issue_number: int) -> dict:
        ...
```

---

### C. Event-driven архитектура для checkpoints

**Проблема:** Checkpoint approval через polling (`wait_for_checkpoint_approval` с `time.sleep(5)`).

**Предложение:**
- Использовать event bus (например, `asyncio.Event`)
- Или webhook-based approach

---

### D. Configuration-driven agent creation

**Предложение:** Описать агентов в YAML/JSON конфигурации, а не в коде:

```yaml
agents:
  - name: pm
    role: "Product Manager"
    llm: "openrouter/quasar-alpha"
    tools: ["save_artifact", "create_github_issue", "list_open_issues"]
    permissions: "pm"
```

---

## 📊 ИТОГОВАЯ ОЦЕНКА

| Критичность | Количество |
|-------------|------------|
| 🔴 BLOCKER/HIGH | 4 |
| 🟡 MEDIUM | 5 |
| 🟢 LOW | 7 |
| **Всего** | **16** |

---

## 🎯 Рекомендуемый порядок исправлений

1. **Неделя 1:** Исправить BLOCKER-ы (1-4)
2. **Неделя 2:** Средний приоритет (5-8)
3. **Неделя 3:** Code quality (9-16)
4. **Спринт 2:** Архитектурные улучшения (A-D)

---

## ✅ Положительные моменты

1. **Четкое разделение ролей** — Каждый агент имеет свою зону ответственности
2. **File permissions system** — Хорошая защита от записи не в те файлы
3. **Checkpoint система** — Контроль качества на каждом этапе
4. **LLM caching** — Экономия API calls
5. **Tests** — Есть базовые тесты для критичных модулей

---

**Следующий шаг:** Обсудить приоритеты и начать с исправления BLOCKER-ов.

---

*Сгенерировано: 2026-04-05*
