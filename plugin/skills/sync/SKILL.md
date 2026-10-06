---
name: sync
description: "Обновить ядро кита agent-wiki-template в проекте — CLAUDE.md, wiki/RULES.md, шаблоны ADR и ТЗ — не трогая проектную вики; показать версию и что нового. Вызывать на «обнови шаблон», «подтяни кит», «синхронизируй протокол», «что нового в ките», «какая версия кита», даже если слово «скилл» не звучит. Нет wiki/.kit-version — не этот скилл, а init."
---

# Обновить ядро кита в проекте

1. Получить свежий кит:

```bash
KIT="${CLAUDE_PLUGIN_DATA}/kit"   # не подставилось — временный каталог; нужен полный клон
if [ -d "$KIT/.git" ]; then git -C "$KIT" fetch -q origin && git -C "$KIT" checkout -q --detach origin/main; else git clone -q https://github.com/xkdg/agent-wiki-template "$KIT"; fi
```

2. Выполнить `$KIT/kit/INSTALL.md §sync`: `python "$KIT/kit/kit.py" sync --project "<корень>" --dry-run`, затем без `--dry-run`. Только вопрос «какая версия / что нового» — `status` и `CHANGELOG.md`.
3. Конфликты решает владелец — по `§Конфликты`: для каждого показать оба diff и три исхода (проектное → `QUICK_REF` и `take`; общее улучшение → `/agent-wiki:upstream`; устаревшее → `take`). Все разрешены — `stamp`, который напечатал sync.
4. Отчёт: версия «было → стало», обновлённое, конфликты и решения, что из `CHANGELOG.md` касается проекта. Не коммитить без согласия владельца.
