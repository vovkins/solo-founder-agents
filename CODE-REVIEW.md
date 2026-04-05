# Code Review: solo-founder-agents

**Дата:** 2026-04-05  
**Reviewer:** Джарвис (15 лет опыта)  
**Проект:** Multi-agent AI system for solo founders

---

## 📊 Общая оценка: 7.5/10

**Плюсы:**
- Хорошая архитектура с разделением ответственности
- Thread-safety внедрена (Lock, RLock, LRUCache)
- Система permissions для файлов
- Event-driven архитектура заложена
- Type hints и docstrings в ключевых местах
- Error handling с retry логикой

**Минусы:**
- Мертвый код (неиспользуемые модули)
- Дублирование system prompts
- Inconsistent error handling в некоторых местах
- Hardcoded values
- Race conditions в Telegram bot
- Memory leaks (кэш без очистки)
- Нет валидации input в критичных местах

---

## 🚨 BLOCKER-ы (Критичные проблемы)

### 1. Race Condition в Pipeline (telegram.py:203-292)

**Проблема:**
В методе `run_command` есть race condition при проверке `active_pipelines`:

```python
# Check if already running
issue_key = str(issue_number)
if issue_key in self.active_pipelines and self.active_pipelines[issue_key].is_alive():
    await update.message.reply_text(f"⏳ Задача #{issue_number} уже выполняется")
    return

# Start thread
thread = threading.Thread(target=run_pipeline_thread, daemon=True)
self.active_pipelines[issue_key] = thread
thread.start()
```

Между проверкой и добавлением может пройти время, и другой запрос может пройти.

**Решение:**
```python
# Добавить lock
self._pipeline_lock = threading.Lock()

# В run_command:
with self._pipeline_lock:
    if issue_key in self.active_pipelines and self.active_pipelines[issue_key].is_alive():
        await update.message.reply_text(f"⏳ Задача #{issue_number} уже выполняется")
        return
    
    thread = threading.Thread(target=run_pipeline_thread, daemon=True)
    self.active_pipelines[issue_key] = thread
    thread.start()
```

**Файл:** `src/bot/telegram.py:203-232`

---

### 2. Error Handling в GitHub клиенте (github_client.py)

**Проблема:**
Декораторы `retry_on_rate_limit` и `handle_github_errors` используются, но не на всех методах:

```python
# Есть декораторы:
@retry_on_rate_limit()
@handle_github_errors
def get_issue(self, issue_number: int) -> Issue.Issue:
    ...

# Нет декораторов:
def create_branch(self, branch_name: str, base_branch: str = "main") -> str:
    # Что если branch уже существует?
    # Что если rate limit?
    # Что если network error?
```

**Решение:**
Добавить декораторы на ВСЕ методы, которые делают GitHub API calls:
- `create_branch()`
- `delete_branch()`
- `get_pull_request()`
- `merge_pull_request()`

**Файл:** `src/tools/github_client.py:268-343`

---

### 3. Memory Leak в LLM Cache (crews/base.py)

**Проблема:**
LRUCache для LLM имеет TTL 1 час, но НЕТ автоматической очистки. Если запущено много pipeline-ов, старые LLM instances будут висеть в памяти до следующего доступа.

```python
class LRUCache:
    def get(self, model_name: str) -> Optional[LLM]:
        # TTL check происходит только при get()
        # Если модель больше не используется, она УЖЕ в памяти
```

**Решение:**
Добавить background cleanup thread или периодический вызов cleanup:

```python
import threading
import time

class LRUCache:
    def __init__(self, max_size: int = 10, ttl_seconds: int = 3600):
        # ... existing code ...
        self._cleanup_thread = None
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_loop():
            while True:
                time.sleep(300)  # Every 5 minutes
                self._cleanup_expired()
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        with self._lock:
            expired = [
                k for k, (_, ts) in self._cache.items()
                if time.time() - ts > self.ttl_seconds
            ]
            for k in expired:
                del self._cache[k]
                logger.info(f"Cleaned up expired cache entry: {k}")
```

**Файл:** `src/crews/base.py:29-91`

---

### 4. Deadlock в StateManager (tools/state.py)

**Проблема:**
StateManager использует `threading.Lock()`, но методы могут вызывать друг друга:

```python
class StateManager:
    def __init__(self):
        self._lock = threading.Lock()
    
    def set_checkpoint(self, checkpoint_id: str, status: str, artifacts: list):
        with self._lock:
            # ...
    
    def get_checkpoint_status(self, checkpoint_id: str) -> Optional[str]:
        with self._lock:
            # Если другой поток вызывает set_checkpoint изнутри get_checkpoint_status → DEADLOCK
```

**Решение:**
Использовать `RLock` (reentrant lock):

```python
class StateManager:
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant lock
```

**Файл:** `src/tools/state.py:30-35`

---

## ⚠️ ВЫСОКИЙ ПРИОРИТЕТ

### 5. Дублирование System Prompts (agents/*.py)

**Проблема:**
System prompts дублируются в двух местах:
1. В файлах `src/agents/pm.py`, `analyst.py`, etc.
2. В файле `config/agents.yaml` (backstory_file: prompts/pm/system-prompt.md)

При этом:
- Папка `prompts/` ПУСТАЯ (нет файлов!)
- AgentFactory пытается загрузить из `prompts/pm/system-prompt.md`, но файлы не существуют

**Решение:**
1. Либо удалить `AgentFactory` (не используется)
2. Либо создать файлы в `prompts/*/system-prompt.md`
3. Либо убрать дублирование — оставить только в Python файлах

**Файлы:**
- `src/agents/pm.py:9-55`
- `src/agents/analyst.py:9-52`
- `config/agents.yaml:7-9`

---

### 6. Inconsistent Return Types в crews

**Проблема:**
Разные crews возвращают разные типы:

```python
# pm_crew.py возвращает dict:
return {
    "status": "completed",
    "result": str(result),
    "artifacts": {"prd": "docs/requirements/prd.md"},
}

# analyst_crew.py может вернуть CrewOutput:
result = crew.kickoff()
return result  # Что это? Dict? Object?
```

**Решение:**
Использовать TypedDict `CrewResult` везде:

```python
from src.crews.types import CrewResult

def run_pm_crew(founder_vision: str) -> CrewResult:
    try:
        crew = create_pm_crew(founder_vision)
        result = crew.kickoff()
        return {
            "status": "completed",
            "result": str(result),
            "artifacts": {"prd": "docs/requirements/prd.md"},
        }
    except Exception as e:
        logger.error(f"PM crew failed: {e}")
        return {"status": "error", "error": str(e)}
```

**Файлы:**
- `src/crews/pm_crew.py:61-71`
- `src/crews/analyst_crew.py`
- `src/crews/types.py`

---

### 7. Hardcoded Branch Name (github_tools.py)

**Проблема:**
В нескольких местах hardcoded `"main"`:

```python
def create_file_in_repo(path: str, content: str, message: str, branch: str = "main"):
    #                                                    ^^^^^ hardcoded

def read_file_from_repo(path: str, branch: str = "main"):
    #                                      ^^^^^ hardcoded
```

Но в `config/settings.py` есть `github_default_branch`!

**Решение:**
Использовать settings:

```python
from config.settings import settings

def create_file_in_repo(path: str, content: str, message: str, branch: str = None):
    branch = branch or settings.github_default_branch
    # ...
```

**Файл:** `src/tools/github_tools.py:80-111`

---

### 8. Отсутствие валидации в Telegram Bot (telegram.py:42-48)

**Проблема:**
Authorization проверка имеет баг:

```python
def is_authorized(self, user_id: int) -> bool:
    if not self.authorized_users or not self.authorized_users:
        #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ DUPLICATE CHECK!
        logger.warning(f"No authorized users configured. Allowing user {user_id}")
        return True  # ⚠️ SECURITY RISK: Allows ANYONE if not configured!
    return user_id in self.authorized_users
```

**Решение:**

```python
def is_authorized(self, user_id: int) -> bool:
    # SECURITY: Require explicit authorization
    if not self.authorized_users:
        logger.error(f"SECURITY: No authorized users configured. Denying user {user_id}")
        return False  # ⚠️ DENY by default for security
    return user_id in self.authorized_users
```

**Файл:** `src/bot/telegram.py:53-57`

---

### 9. Global Instances vs Dependency Injection

**Проблема:**
Смешанный подход:
- `pipeline` — глобальный instance в `src/pipeline.py`
- `state_manager` — глобальный instance в `src/tools/state.py`
- `agent_factory` — глобальный instance, но НЕ используется
- `artifact_manager` — глобальный instance через функцию `get_artifact_manager()`

Это делает тестирование сложным.

**Решение:**
Использовать Dependency Injection через фабричные функции:

```python
# Вместо:
from src.tools.state import state_manager

# Использовать:
from src.tools.state import get_state_manager

state_manager = get_state_manager()
```

**Файлы:**
- `src/tools/state.py:101`
- `src/pipeline.py:400`
- `src/tools/artifact_manager.py:192`

---

## 📝 СРЕДНИЙ ПРИОРИТЕТ

### 10. Мертвый код: pipeline/runner.py

**Проблема:**
Файл `src/pipeline/runner.py` (228 строк) НЕ ИСПОЛЬЗУЕТСЯ:
- Нет импортов в других файлах
- Pipeline использует собственные методы напрямую

**Решение:**
- Удалить файл
- Или интегрировать в `src/pipeline.py`

**Файл:** `src/pipeline/runner.py`

---

### 11. Мертвый код: agents/factory.py

**Проблема:**
`AgentFactory` (204 строки) СОЗДАЕТСЯ, но НЕ ИСПОЛЬЗУЕТСЯ:
- Глобальный instance `agent_factory` не импортируется нигде
- Agents создаются напрямую через `create_*_agent()` функции

**Решение:**
- Удалить файл
- Или использовать везде вместо прямого создания

**Файл:** `src/agents/factory.py`

---

### 12. Event Bus не используется

**Проблема:**
Event-driven архитектура реализована, но НЕ ИСПОЛЬЗУЕТСЯ:
- `src/events/bus.py` (176 строк)
- `src/events/handlers.py` (162 строк)
- Pipeline использует callbacks напрямую

**Решение:**
- Интегрировать в Pipeline
- Или удалить

**Файлы:**
- `src/events/bus.py`
- `src/events/handlers.py`

---

### 13. Отсутствие Type Hints в критичных методах

**Проблема:**
Многие методы не имеют type hints:

```python
def create_pm_crew(founder_vision: str, verbose: bool = True) -> Crew:
    # OK

def run_pm_crew(founder_vision: str) -> CrewResult:
    # OK

# Но в других местах:
def get_agent_cache_stats():  # ❌ No return type
    return agent_cache.stats()
```

**Решение:**
Добавить type hints везде:

```python
def get_agent_cache_stats() -> Dict[str, Any]:
    return agent_cache.stats()
```

**Файлы:**
- `src/agents/_agent_cache.py:47-51`
- `src/tools/artifact_tools.py:150-180`

---

### 14. Отсутствие Docstrings в Pipeline

**Проблема:**
Pipeline имеет только короткие docstrings:

```python
def run_full_pipeline(self, ...):
    """Run full pipeline from requirements to documentation."""
    # ❌ Не описаны параметры, return type, exceptions
```

**Решение:**
Добавить полные docstrings:

```python
def run_full_pipeline(
    self,
    issue_number: int,
    founder_vision: str,
    on_checkpoint: Optional[Callable] = None,
    on_progress: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Run full pipeline from requirements to documentation.
    
    Args:
        issue_number: GitHub issue number to process
        founder_vision: Initial product vision from founder
        on_checkpoint: Callback for checkpoint events (checkpoint, artifacts)
        on_progress: Callback for progress updates (phase, message)
    
    Returns:
        Dictionary with keys:
            - status: "complete" or "error"
            - phases: Dict of phase results
            - error: Error message if status == "error"
    
    Raises:
        ValueError: If issue_number is invalid
        RuntimeError: If checkpoint rejected or timed out
    """
```

**Файл:** `src/pipeline.py:200-350`

---

### 15. Magic Strings в Pipeline

**Проблема:**
Pipeline stages как строки:

```python
if result.get("status") == "complete":  # ❌ Magic string
    ...

# Вместо:
if result.get("status") == PipelineStage.COMPLETE.value:  # ✅ Enum
```

**Решение:**
Использовать enum values везде:

```python
# В crews возвращать:
return {"status": PipelineStage.COMPLETE.value, ...}

# В проверках:
if result.get("status") == PipelineStage.COMPLETE.value:
```

**Файл:** `src/pipeline.py:200-350`

---

### 16. Дублирование Logic в Artifact Tools

**Проблема:**
Маппинг `artifact_type` в `SaveArtifactTool` дублируется:

```python
# В SaveArtifactTool._run():
type_map = {
    "prd": ArtifactType.PRD,
    "system-design": ArtifactType.SYSTEM_DESIGN,
    # ...
}

# В ArtifactManager.create_artifact():
# Тоже есть логика маппинга!
```

**Решение:**
Вынести в общую функцию:

```python
# В artifact_manager.py:
def get_artifact_type(type_str: str) -> Optional[ArtifactType]:
    """Convert string to ArtifactType enum."""
    type_map = {
        "prd": ArtifactType.PRD,
        "system-design": ArtifactType.SYSTEM_DESIGN,
        "adr": ArtifactType.ADR,
        # ...
    }
    return type_map.get(type_str)
```

**Файл:** `src/tools/artifact_tools.py:49-62`

---

## 📚 НИЗКИЙ ПРИОРИТЕТ

### 17. Отсутствие Unit Tests для критичных модулей

**Проблема:**
Тесты есть только для:
- `test_pipeline.py` — базовые тесты
- `test_github_tools.py` — простые тесты
- `test_storage.py` — тесты storage

Но НЕТ тестов для:
- `artifact_manager.py` — критичный модуль
- `file_permissions.py` — критичный для security
- `state.py` — критичный для concurrency

**Решение:**
Добавить тесты для критичных модулей.

**Файлы:** `tests/`

---

### 18. Отсутствие Logging в критичных местах

**Проблема:**
В некоторых местах нет логирования:

```python
# В pipeline.py:
def run_full_pipeline(self, ...):
    # ❌ Нет логирования старта
    # ❌ Нет логирования завершения
    # Только внутри phases
```

**Решение:**
Добавить логирование:

```python
def run_full_pipeline(self, ...):
    logger.info(f"Starting full pipeline for issue #{issue_number}")
    # ... logic ...
    logger.info(f"Pipeline completed for issue #{issue_number}: {result.get('status')}")
```

**Файл:** `src/pipeline.py`

---

### 19. Отсутствие Configuration Validation

**Проблема:**
Settings не валидируются при старте:

```python
class Settings(BaseSettings):
    github_token: str = ""
    # ❌ Нет проверки что token не пустой
    # ❌ Нет проверки что repo валидный
```

**Решение:**
Добавить validation:

```python
from pydantic import validator

class Settings(BaseSettings):
    github_token: str = ""
    
    @validator("github_token")
    def validate_github_token(cls, v):
        if not v:
            raise ValueError("GITHUB_TOKEN is required")
        return v
```

**Файл:** `config/settings.py`

---

### 20. Отсутствие Retry Logic в Pipeline

**Проблема:**
Pipeline не имеет retry logic при временных ошибках:

```python
result = pipeline.run_requirements_phase(founder_vision)
# ❌ Если network error, весь pipeline упадет
```

**Решение:**
Добавить retry decorator или try-catch с retry:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def run_requirements_phase(self, founder_vision: str):
    # ...
```

**Файл:** `src/pipeline.py`

---

## 🏗️ АРХИТЕКТУРНЫЕ УЛУЧШЕНИЯ

### 21. Agent Cache с TTL и Eviction

**Реализовано:**
✅ `AgentCache` с TTL и LRU eviction уже есть в `src/agents/agent_cache.py`

**Но:**
- Нет автоматической очистки expired entries
- Нет metrics/logging

**Решение:**
Добавить background cleanup (как в проблеме #3).

---

### 22. Pipeline Runner Class

**Проблема:**
Pipeline содержит и orchestration logic, и business logic.

**Решение:**
Использовать `PipelineRunner` из `src/pipeline/runner.py` (сейчас мертвый код).

**Преимущества:**
- Separation of concerns
- Легче тестировать
- Легше расширять

---

### 23. Event-Driven Architecture

**Проблема:**
Event bus не используется.

**Решение:**
Интегрировать в Pipeline:

```python
# В pipeline.py:
from src.events.bus import event_bus
from src.events.handlers import checkpoint_handler

def run_full_pipeline(self, ...):
    # Publish event
    event_bus.publish("pipeline.started", {"issue_number": issue_number})
    
    # ...
    
    # Checkpoint через events
    checkpoint_handler.create_checkpoint("checkpoint_1", ["docs/requirements/prd.md"])
    approved = checkpoint_handler.wait_for_approval("checkpoint_1")
```

**Преимущества:**
- Decoupled components
- Легко добавлять new handlers
- Better observability

---

### 24. Configuration-Driven Agents

**Проблема:**
Agents создаются программно, хотя есть `config/agents.yaml`.

**Решение:**
Использовать `AgentFactory` из `src/agents/factory.py` (сейчас мертвый код).

**Преимущества:**
- Конфигурация без кода
- Легко менять LLM модели
- Можно создавать agents динамически

---

## 📈 МЕТРИКИ

### Coverage Analysis

| Модуль | Строк | Используется | % |
|--------|-------|--------------|---|
| `src/pipeline/runner.py` | 228 | ❌ | 0% |
| `src/agents/factory.py` | 204 | ❌ | 0% |
| `src/events/bus.py` | 176 | ❌ | 0% |
| `src/events/handlers.py` | 162 | ❌ | 0% |
| `src/bot/telegram.py` | 716 | ✅ | 100% |
| `src/pipeline.py` | 428 | ✅ | 100% |
| `src/tools/github_client.py` | 353 | ✅ | 90% |

**Мертвый код:** ~770 строк (9% от общего кода)

---

## 🎯 ПЛАН ИСПРАВЛЕНИЯ (по убыванию критичности)

### Phase 1: BLOCKER-ы (ОБЯЗАТЕЛЬНО)

1. **Race Condition в Pipeline** — `telegram.py`
   - Добавить lock для `active_pipelines`
   - Time: 30 мин
   - Impact: CRITICAL

2. **Error Handling в GitHub клиенте** — `github_client.py`
   - Добавить декораторы на все методы
   - Time: 1 час
   - Impact: CRITICAL

3. **Memory Leak в LLM Cache** — `crews/base.py`
   - Добавить background cleanup
   - Time: 2 часа
   - Impact: HIGH

4. **Deadlock в StateManager** — `tools/state.py`
   - Изменить Lock → RLock
   - Time: 15 мин
   - Impact: CRITICAL

---

### Phase 2: ВЫСОКИЙ ПРИОРИТЕТ

5. **Дублирование System Prompts** — `agents/*.py`, `config/agents.yaml`
   - Удалить дубликаты или создать недостающие файлы
   - Time: 2 часа
   - Impact: MEDIUM

6. **Inconsistent Return Types** — `crews/*.py`
   - Использовать `CrewResult` везде
   - Time: 3 часа
   - Impact: MEDIUM

7. **Hardcoded Branch Name** — `github_tools.py`
   - Использовать `settings.github_default_branch`
   - Time: 30 мин
   - Impact: LOW

8. **Security в Telegram Bot** — `telegram.py`
   - Изменить логику `is_authorized()`
   - Time: 30 мин
   - Impact: HIGH

9. **Dependency Injection** — `state.py`, `pipeline.py`
   - Добавить фабричные функции
   - Time: 4 часа
   - Impact: MEDIUM

---

### Phase 3: СРЕДНИЙ ПРИОРИТЕТ

10. **Мертвый код** — `pipeline/runner.py`, `agents/factory.py`, `events/*`
    - Удалить или интегрировать
    - Time: 1 час
    - Impact: LOW

11. **Type Hints** — все модули
    - Добавить type hints везде
    - Time: 4 часа
    - Impact: MEDIUM

12. **Docstrings** — `pipeline.py`
    - Добавить полные docstrings
    - Time: 2 часа
    - Impact: LOW

13. **Magic Strings** — `pipeline.py`
    - Использовать enum values
    - Time: 1 час
    - Impact: LOW

14. **Logic Duplication** — `artifact_tools.py`
    - Вынести общую функцию
    - Time: 30 мин
    - Impact: LOW

---

### Phase 4: НИЗКИЙ ПРИОРИТЕТ

15. **Unit Tests** — критичные модули
    - Добавить тесты
    - Time: 8 часов
    - Impact: MEDIUM

16. **Logging** — `pipeline.py`
    - Добавить логирование
    - Time: 1 час
    - Impact: LOW

17. **Configuration Validation** — `settings.py`
    - Добавить validators
    - Time: 1 час
    - Impact: LOW

18. **Retry Logic** — `pipeline.py`
    - Добавить retry decorator
    - Time: 2 часа
    - Impact: MEDIUM

---

### Phase 5: АРХИТЕКТУРНЫЕ УЛУЧШЕНИЯ

19. **Agent Cache** — `agent_cache.py`
    - Добавить cleanup + metrics
    - Time: 2 часа
    - Impact: LOW

20. **Pipeline Runner** — интегрировать `runner.py`
    - Refactor pipeline
    - Time: 8 часов
    - Impact: MEDIUM

21. **Event-Driven** — интегрировать `events/*`
    - Refactor pipeline + telegram
    - Time: 12 часов
    - Impact: HIGH

22. **Config-Driven Agents** — использовать `factory.py`
    - Refactor agent creation
    - Time: 6 часов
    - Impact: MEDIUM

---

## 🏁 РЕКОМЕНДАЦИИ

### Immediate Actions (Сделать СЕЙЧАС)

1. ✅ Исправить race condition в telegram.py (30 мин)
2. ✅ Исправить deadlock в state.py (15 мин)
3. ✅ Добавить error handling в github_client.py (1 час)
4. ✅ Исправить security issue в telegram.py (30 мин)

**Total:** ~2.5 часа критичных фиксов

### Short-term (Следующая неделя)

5. ✅ Исправить memory leak в LLM cache (2 часа)
6. ✅ Унифицировать return types (3 часа)
7. ✅ Удалить мертвый код (1 час)
8. ✅ Исправить hardcoded values (1 час)

**Total:** ~7 часов

### Long-term (Следующий месяц)

9. ✅ Добавить unit tests (8 часов)
10. ✅ Refactor в event-driven architecture (12 часов)
11. ✅ Configuration-driven agents (6 часов)
12. ✅ Добавить retry logic (2 часа)

**Total:** ~28 часов

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

- **Всего проблем:** 24
- **BLOCKER-ы:** 4
- **Высокий приоритет:** 5
- **Средний приоритет:** 5
- **Низкий приоритет:** 4
- **Архитектурные:** 4

- **Мертвый код:** ~770 строк (9%)
- **Среднее качество кода:** 7.5/10
- **Оценка после исправлений:** 9.0/10

---

## ✅ ЗАКЛЮЧЕНИЕ

Проект имеет хорошую архитектурную основу, но требует исправления критичных проблем:

1. **Race conditions и deadlocks** — могут привести к краху в production
2. **Memory leaks** — будут потреблять память со временем
3. **Security issues** — риск unauthorized access
4. **Error handling** — нестабильность при ошибках

После исправления BLOCKER-ов и высокоприоритетных проблем, проект будет **production-ready**.

**Рекомендуемый порядок:**
1. Phase 1 (BLOCKER-ы) — сделать немедленно
2. Phase 2 (ВЫСОКИЙ) — на этой неделе
3. Phase 3-4 — в следующем спринте
4. Phase 5 (архитектура) — при рефакторинге

---

*Review completed by Джарвис, 2026-04-05*
