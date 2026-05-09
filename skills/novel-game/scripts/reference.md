# Phase Reference

## Shared vs Isolated

lore/ 和 CLAUDE.md 是小说提炼内容，所有存档共享。
gamestate.json、saves/、turns/ 是玩家自定义设定和情节进度，每个存档完全独立。

新建存档时：复用 lore/ 和 CLAUDE.md，重新走 Phase 2 完整捏人流程。不从其他存档复制任何 settings、timeline、flags。

## Phase 1 --- Auto-build world

Directory has .txt only. Read all, extract everything, build lore/ and CLAUDE.md silently.

After building: ask language preference via AskUserQuestion (zh/en), save to gamestate.json.

## Phase 2 --- First game (character creation)

If lang not set, ask language preference first. Then AskUserQuestion: starting point, protagonist extras, scene tweaks. state.py init + timeline-add turn 0.

## Phase 3 --- Save selector

Read lang from gamestate.json, auto-switch UI language. AskUserQuestion:
- Each existing save (show chapter, turn count, last played)
- Start new save (go to Phase 2 with new save name, lore and CLAUDE.md are reused, nothing else)
- Reset current save (timeline-truncate, then Phase 2 keeping same save name)

## Rewind

Show last 5 timeline entries, AskUserQuestion to pick rewind point, timeline-truncate.
