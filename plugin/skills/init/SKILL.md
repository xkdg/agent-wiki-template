---
name: init
description: "Развернуть кит agent-wiki-template в проекте — протокол CLAUDE.md и вики (INDEX, RULES, QUICK_REF, PRODUCT, CONVENTIONS, шаблоны ADR и ТЗ) — или перевести на кит проект со старым шаблоном. Вызывать на новый проект, «разверни шаблон», «подключи вики», «поставь agent-wiki», «перенеси проект на кит», даже если слово «скилл» не звучит. Если есть wiki/.kit-version — не этот скилл, а sync."
---

# Развернуть кит в проекте

1. Корень — рабочий каталог, если владелец не назвал другой. Есть `wiki/.kit-version` — предложить `/agent-wiki:sync` и остановиться. Есть `CLAUDE.md` или `wiki/` без отметки — это миграция: сказать, что существующее не перезапишется, и спросить, мигрировать ли.
2. Получить кит:

```bash
KIT="${CLAUDE_PLUGIN_DATA}/kit"   # не подставилось — временный каталог; нужен полный клон
if [ -d "$KIT/.git" ]; then git -C "$KIT" fetch -q origin && git -C "$KIT" checkout -q --detach origin/main; else git clone -q https://github.com/xkdg/agent-wiki-template "$KIT"; fi
```

3. Выполнить `$KIT/kit/INSTALL.md §init` — или `§Миграция` целиком, если это миграция: одного `init` мало, без переноса `CLAUDE.md` и правки `INDEX` проект останется на старом протоколе с отметкой новой версии. Скрипт — `python "$KIT/kit/kit.py"` (нет `python` — `python3`).
4. Отчёт: что создано, что осталось заполнить, версия из `wiki/.kit-version`. Не коммитить без согласия владельца.
