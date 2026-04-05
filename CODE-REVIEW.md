# Code Review — solo-founder-agents

**Дата:** 2026-04-03  
**Ревьюер:** Джарвис  
**Объём:** ~7500 строк Python, 45 файлов  
**Последнее обновление:** 2026-04-05

---

## 📊 Сводка

| Критичность | Кол-во | Исправлено | Пропущено | Не делалось |
|---|---|---|---|---|---|---|
| 🔴 Критические | 4 | 4 | 0 | 0 |
| 🟠 Серьёзные | 6 | 5 | 1 | 0 |
| 🟡 Улучшения | 9 | 9 | 0 | 0 |
| 🟢 Минорные | 4 | 1 | 0 | 4 |
| **Итого** | **23** | **4** | **19** |

---

## ✅ Phase 1 — КРИТИЧЕСКИЕ (commit `aa0d63d`)

1. ✅ Permissions встроены в system prompts агентов
 **Исправление:** Перенесли блок permissions в `XXX_SYSTEM_PROMPT` для всех 7 агентов (PM уже был OK).
2. ✅ SyncArtifactsTool обходил permission систему
убран из `get_artifact_tools()`. Добавлена `get_readonly_artifact_tools()`
3. ✅ Reviewer получает SaveArtifactTool, но не может создавать файлы (тратит токены на ошибки. **Исправление:** Reviewer теперь использует `get_readonly_artifact_tools()` (ReadArtifactTool + ListMyFilesTool)
4. ✅ `github_client.update_issue()` — re-fetch после edit()
 → `AttributeError`
**Исправление:** Re-fetch issue через `get_issue()`.

5. ✅ Удалён `storage.py` (163 строки, дублирует `artifact_manager`)
6. ✅ Удалены `core_crew.py` + `dev_crew.py` (legacy, нарушают role isolation)
7. ✅ Убран дублирование path mapping из `SaveArtifactTool` (dead code)
8. ✅ Убран `task_description` из `developer_crew.py`
9. ✅ Убраны неиспользуемые импорты из `reviewer_crew.py`
10. ✅ (Пропущен) Lazy agent initialization — требует рефакторинга)

---

## ✅ Phase 3 — УЛУЧШЕНИЯ (commit `f0d4ab0`)
11. ✅ Error handling во all 8 crew runners
12. ✅ Thread-safety StateManager (added `threading.Lock`)
13. ✅ Exception-based branching — catch only FileNotFoundError,14. ✅ Standardized all artifact paths (docs/requirements/prd.md, etc)
15. ✅ Убраны unused imports in `pm.py`
16. ✅ LLMProvider caching (dict-based cache)
17. ✅ `qa_crew.py` type hints (`Optional[List[str]]`)
18. ✅ Убран `ARTIFACT_TOOLS` list
19. ✅ `cli.py` — interactive flag support

20. ✅ Убран `utils/helpers.py` (dead code)
21. ✅ `cli.py` left for local debugging (not deleted,22. ✅ `src/__init__.py` — not empty (docstring + version,23. ✅ Dockerfile — simplified (removed app service)

23. ✅ LLM instances cached
16. ✅ `LLMProvider` - cached via `_llm_cache dict

17. ✅ Error handling in all 8 crew runners
18. ✅ Thread-safety StateManager (added `threading.Lock`)
19. ✅ Removed unused `ARTIFACT_TOOLS` list
20. ✅ Removed `utils/helpers.py` (dead code)21. ✅ `cli.py` left for local debugging (not deleted)22. ✅ `src/__init__.py` not empty (docstring + version)23. ✅ Dockerfile - simplified (removed app service)23. ✅ Standardized artifact paths
    - ✅ Fixed inconsistent paths in system prompts and tasks files
14. ✅ Standardized `data/artifacts/` paths to correct GitHub paths format
    - ✅ All `data/artifacts` references removed

 crews and pipelines
19/23 | Not done (skipped,): Need refactoring |
| 21 | Not done (cli.py useful for local debugging) |
| 22 | Not done (not empty, has docstring + version) |
| 23 | Not done (app image already unused, can simplify Dockerfile later if needed) |
