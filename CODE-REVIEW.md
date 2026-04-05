# Code Review — solo-founder-agents

**Дата:** 2026-04-03  
**Ревьюер:** Джарвис  
**Объём:** ~7500 строк Python, 45 файлов  
**Последнее обновление:** 2026-04-05

---

## 📊 Сводка

| Критичность | Кол-во | Исправлено | Осталось |
|---|---|---|---|
| 🔴 Критические | 4 | 4 | 0 |
| 🟠 Серьёзные | 6 | 0 | 6 |
| 🟡 Улучшения | 9 | 0 | 9 |
| 🟢 Минорные | 4 | 0 | 4 |
| **Итого** | **23** | **4** | **19** |

---

## ✅ Phase 1 — ИСПРАВЛЕНО (commit `aa0d63d`)

### 1. ✅ Permissions НЕ были встроены в system prompts агентов
**Проблема:** Permissions записаны в module docstring (строка перед import), а не в `XXX_SYSTEM_PROMPT` — переменную, которую получает CrewAI. Агенты не знали о своих правах.
**Исправление:** Перенесли блок permissions в `XXX_SYSTEM_PROMPT` для всех 7 агентов (PM уже был OK).

### 2. ✅ SyncArtifactsTool обходил permission систему
**Проблема:** `SyncArtifactsTool` был доступен всем агентам через `get_artifact_tools()`. Пушит ВСЕ файлы в GitHub без проверки прав.
**Исправление:** Убран из `get_artifact_tools()`. Добавлена `get_readonly_artifact_tools()`.

### 3. ✅ Reviewer получал SaveArtifactTool, но не может создавать файлы
**Проблема:** Reviewer (`can_create: []`) получал SaveArtifactTool — тратил токены на ошибки.
**Исправление:** Reviewer теперь использует `get_readonly_artifact_tools()` (ReadArtifactTool + ListMyFilesTool).

### 4. ✅ `github_client.update_issue()` возвращал None
**Проблема:** PyGithub `issue.edit()` возвращает None, а код обращался к `.html_url` → AttributeError.
**Исправление:** После `edit()` делается re-fetch issue через `get_issue()`.

---

## 🟠 Phase 2 — СЕРЬЁЗНЫЕ (6 задач)

### 5. `storage.py` — 163 строки мёртвого кода
**Файл:** `src/tools/storage.py`
**Проблема:** Дублирует `artifact_manager.py`. Нигде не используется, но экспортируется через `__init__.py`.
**Решение:** Удалить файл, убрать из `src/tools/__init__.py`.

### 6. `core_crew.py` + `dev_crew.py` — legacy код
**Файлы:** `src/crews/core_crew.py`, `src/crews/dev_crew.py`
**Проблема:** Создают multi-agent crews — нарушают role isolation. Содержат неиспользуемые `create_review_cycle_crew()`, `create_qa_cycle_crew()`.
**Решение:** Удалить оба файла, убрать из `src/crews/__init__.py`.

### 7. Дублирование path mapping
**Файлы:** `src/tools/artifact_tools.py`, `src/tools/artifact_manager.py`
**Проблема:** Путь артефакта вычисляется дважды: `filepath` в `SaveArtifactTool._run()` (мёртвый код) и в `ArtifactManager.create_artifact()`.
**Решение:** Удалить вычисление `filepath` из `SaveArtifactTool._run()`.

### 8. `developer_crew.py` — параметр `task_description` не используется
**Файл:** `src/crews/developer_crew.py`
**Проблема:** `create_developer_crew()` принимает `task_description: str`, но никогда не передаёт его в задачи.
**Решение:** Либо использовать параметр, либо убрать.

### 9. `reviewer_crew.py` — импортирует 3 задачи, использует 1
**Файл:** `src/crews/reviewer_crew.py`
**Проблема:** Импортирует `create_check_standards_task`, `create_security_check_task`, но не использует.
**Решение:** Убрать неиспользуемые импорты или добавить задачи в crew.

### 10. Module-level agent instantiation
**Файлы:** `src/agents/*.py`
**Проблема:** Все 8 агентов создаются при импорте модуля (`pm_agent = create_pm_agent()`). Тяжёлый импорт, 8 LLM-клиентов.
**Решение:** Lazy initialization через фабрики. Убрать pre-configured instances.

---

## 🟡 Phase 3 — УЛУЧШЕНИЯ (9 задач)

### 11. `cli.py` — `run` команда не использует `--interactive` флаг
Флаг парсится, но нигде не используется.

### 12. Thread-safety `state_manager`
`StateManager` пишет JSON без `threading.Lock()`. Race condition между pipeline thread и Telegram thread.

### 13. Exception-based branching в `artifact_manager.save_artifact()`
```python
try:
    read_file_from_repo(path)  # пробует прочитать
    update_file_in_repo(...)   # если OK — update
except Exception:               # ЛЮБАЯ ошибка → create
    create_file_in_repo(...)
```
Антипаттерн: catch ALL exceptions. Если GitHub API упал с 500 — код попробует create, что тоже упадёт.
**Решение:** Catch только 404 / FileNotFoundError.

### 14. Несогласованные пути в system prompts и tasks
- `docs/prd.md` vs `docs/requirements/prd.md`
- `docs/system-design.md` vs `docs/design/system-design.md`
- `data/artifacts/docs/prd.md` vs `docs/requirements/prd.md`
**Решение:** Единый source of truth — `PATHS` dict в `file_permissions.py`.

### 15. Unused imports в `pm.py`
`get_issue_details`, `list_open_issues`, `create_github_issue` импортируются, но не вызываются (используются tool-обёртки).

### 16. `LLMProvider` — новый LLM instance при каждом вызове
`LLMProvider.get_pm_llm()` создаёт новый `LLM(...)` каждый раз.
**Решение:** `@functools.lru_cache` или dict.

### 17. Нет error handling при `kickoff()` в crew runners
Все `run_*_crew()` вызывают `crew.kickoff()` без try/except. Если LLM упадёт — исключение без очистки state.
**Решение:**
```python
try:
    result = crew.kickoff()
    return {"status": "completed", ...}
except Exception as e:
    return {"status": "error", "error": str(e)}
```

### 18. `qa_crew.py` — тип hint `list = None`
Стоит использовать `Optional[List[str]] = None` для type safety.

### 19. Неиспользуемый `ARTIFACT_TOOLS` list в `artifact_tools.py`
Переменная `ARTIFACT_TOOLS` экспортируется, но нигде не используется после добавления `get_artifact_tools()`.

---

## 🟢 Phase 4 — МИНОРНЫЕ (4 задачи)

### 20. `utils/helpers.py` — вероятно мёртвый код
Функции `save_json`, `load_json`, `format_datetime`, `truncate_text` нигде не используются.

### 21. `cli.py` (313 строк) — весь CLI не используется в production
Бот работает через Telegram. CLI только для отладки.

### 22. `src/__init__.py` — пустой файл
Можно удалить.

### 23. Dockerfile — app образ не используется
Собирается 2 образа (app + telegram-bot), но app нигде не запускается.

---

## 🏗️ Рекомендуемый порядок исправлений

### Phase 2 (следующий приоритет):
1. Удалить `storage.py` и убрать из `__init__.py`
2. Удалить `core_crew.py` + `dev_crew.py` и убрать из `__init__.py`
3. Убрать dead `filepath` из `SaveArtifactTool._run()`
4. Исправить `developer_crew.py` (использовать или убрать `task_description`)
5. Убрать неиспользуемые импорты из `reviewer_crew.py`
6. (Опционально) Lazy agent initialization

### Phase 3 (quality):
7. Добавить error handling в crew runners
8. Исправить exception-based branching в `artifact_manager`
9. Стандартизировать пути через `PATHS` dict
10. Убрать unused imports в `pm.py`
11. Кэшировать LLM instances
12. Добавить `threading.Lock` в StateManager

### Phase 4 (minor):
13. Удалить `utils/helpers.py`
14. Удалить пустой `src/__init__.py`
15. Убрать app образ из Dockerfile
