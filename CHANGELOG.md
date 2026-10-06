# Changelog

Версия — `kit/VERSION`. Проект знает свою версию по `wiki/.kit-version`; `/agent-wiki:sync` показывает, что изменилось.

## 2.0.0 — 2026-10-06

Кит вместо копируемого шаблона: развёртывание и обновление командой, роли и бриф — плагином.

**Структура (major — для проектов на шаблоне 1.x нужна миграция, `kit/INSTALL.md §Миграция`):**
- Файлы проекта переехали в `template/`; состав и тип (ядро / заготовка) — `kit/MANIFEST`; `kit/kit.py init | sync | status | take | stamp`.
- Новый файл ядра `wiki/RULES.md`: из `INDEX.md` вынесены общие части — условия ADR, маршруты после задачи, принципы документирования. В `INDEX.md` остались проектные секции: `§Области ADR` (таблица признаков) и `§Проектные маршруты`.
- `CLAUDE.md` — ядро, одинаковое во всех проектах; проектные договорённости — в `QUICK_REF.md`. Импортирует `INDEX`, `RULES`, `QUICK_REF`, поэтому вики гарантированно в контексте, в том числе после `/clear`.

**Протокол:**
- Пункт 9 «Измеряй, не угадывай» (прецедент — SEGMENTATOR-TECHSTEK-CRAWL).
- Скиллы как жанр: условия заведения, форма, жизненный цикл — `RULES.md §Когда предлагать скилл`; таблица скиллов проекта в `INDEX.md` (прецедент — скиллы `verified-orgs-increment`, `phone-reverse-lookup`).
- Роли субагентов и конвейер; интервью с владельцем остаётся за главным агентом — субагенты не могут задавать вопросы.
- Файлы ядра в проекте не правятся: улучшение — `propose_new`: изменение кита → `upstream`.

**Плагин `agent-wiki`:**
- Роли: `scout`, `implementer`, `reviewer`, `verifier`, `investigator`, `doc-auditor`.
- Скиллы: `brief` — бриф фичи (паттерны из obra/superpowers `brainstorming`, github/spec-kit `clarify`, ECC `intent-driven-development`); `init`, `sync`, `upstream`.

## 1.0.0 — 2026-08-24

Шаблон: `CLAUDE.md` с протоколом `documentation_action`, вики (`INDEX`, `QUICK_REF`, `PRODUCT`, `CONVENTIONS`, ADR, ТЗ, `BACKLOG`). Разворачивался копированием.
