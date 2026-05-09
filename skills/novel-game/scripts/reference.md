# Phase Reference

## Phase 1 --- Auto-build world

Directory has .txt only. Read all, extract everything, build lore/ and CLAUDE.md silently.

After building: ask language preference via AskUserQuestion (zh/en), save to gamestate.json.

## Phase 2 --- First game (character creation)

If lang not set, ask language preference first. Then AskUserQuestion: starting point, protagonist extras, scene tweaks. state.py init + timeline-add turn 0.

## Phase 3 --- Save selector

Read lang from gamestate.json, auto-switch UI language. AskUserQuestion: existing saves + new + reset.

## Rewind

Show last 5 timeline entries, AskUserQuestion to pick rewind point, timeline-truncate.
