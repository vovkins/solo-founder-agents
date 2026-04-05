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
| 🟠 Серьёзные | 6 | 5 | 1 |
| 🟡 Улучшения | 9 | 0 | 9 |
| 🟢 Минорные | 4 | 0 | 4 |
| **Итого** | **23** | **9** | **14** |

---

## ✅ Phase 1 — КРИТИЧЕСКИЕ (commit `aa0d63d`)

1. ✅ Permissions встроены в system prompts всех 7 агентов (раньше были в module docstring)
2. ✅ SyncArtifactsTool убран из `get_artifact_tools()`, добавлена `get_readonly_artifact_tools()`
3. ✅ Reviewer → readonly tools
4. ✅ `github_client.update_issue()` — re-fetch после edit()

---

## ✅ Phase 2 — СЕРЬЁЗНЫЕ (commit `05e1d23`, -504 строки)

5. ✅ Удалён `storage.py` (163 строки мёртвого кода)
6. ✅ Удалены `core_crew.py` + `dev_crew.py` (249 строк legacy)
7. ✅ Убран dead `filepath` из `SaveArtifactTool._run()` (30 строк)
8. ✅ Убран неиспользуемый `task_description` из `developer_crew.py` + `pipeline.py`
9. ✅ Убраны неиспользуемые импорты из `reviewer_crew.py`
10. 🔲 Lazy agent initialization (пропущено — требует больше рефакторинга)

---

## 🟡 Phase 3 — УЛУЧШЕНИЯ (9 задач, НЕ НАЧАТО)

### 11. `cli.py` — `--interactive` флаг не используется
Флаг парсится, но нигде не применяется.

### 12. Thread-safety `state_manager`
`StateManager` пишет JSON без `threading.Lock()`. Race condition между pipeline thread и Telegram thread.
**Решение:** Добавить `threading.Lock()`.

### 13. Exception-based branching в `artifact_manager.save_artifact()`
```python
try:
    read_file_from_repo(path)
    update_file_in_repo(...)
except Exception:  # ЛЮБАЯ ошибка → create
    create_file_in_repo(...)
```
**Решение:** Catch только FileNotFoundError / 404.

### 14. Несогласованные пути в system prompts и tasks
- `docs/prd.md` vs `docs/requirements/prd.md`
- `docs/system-design.md` vs `docs/design/system-design.md`
**Решение:** Единый `PATHS` dict в `file_permissions.py`.

### 15. Unused imports в `pm.py`
`get_issue_details`, `list_open_issues`, `create_github_issue` импортируются, но не вызываются.

### 16. `LLMProvider` — новый instance при каждом вызове
**Решение:** `@functools.lru_cache` или dict.

### 17. Нет error handling при `kickoff()` в crew runners
**Решение:** try/except с возвратом `{"status": "error"}`.

### 18. `qa_crew.py` — тип hint `list = None`
**Решение:** `Optional[List[str]] = None`.

### 19. Неиспользуемый `ARTIFACT_TOOLS` list в `artifact_tools.py`
Переменная экспортируется, но нигде не используется.

---

## 🟢 Phase 4 — МИНОРНЫЕ (4 задачи, НЕ НАЧАТО)

### 20. `utils/helpers.py` — мёртвый код
### 21. `cli.py` (313 строк) — не используется в production
### 22. `src/__init__.py` — пустой файл
### 23. Dockerfile — app образ не используется
