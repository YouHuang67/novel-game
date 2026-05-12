# Phase Reference

## Shared vs Isolated

lore/ 和 CLAUDE.md 是小说提炼内容，所有存档共享。
gamestate.json、saves/、turns/ 是玩家自定义设定和情节进度，每个存档完全独立。

新建存档时：复用 lore/ 和 CLAUDE.md，重新走 Phase 2 完整捏人流程。不从其他存档复制任何 settings、timeline、flags。

## Phase 1 --- Auto-build world

Directory has .txt only. Two passes over the novel, all silent.

### Pass 1: Deep style study (first 200K+ chars)

Read the first 200000 Chinese characters minimum. This is not skimming. Read carefully to internalize:

- Sentence rhythm: average sentence length, paragraph structure, how action and description alternate
- Dialogue patterns: how characters speak, tone markers used, dialogue-to-narration ratio
- Description density: how much sensory detail per scene, which senses are favored
- Combat cadence: how fights unfold step by step, the vocabulary of power and impact
- Transition habits: how the author moves between scenes, handles time skips, introduces new characters
- Emotional palette: how feelings are expressed (body reactions, internal monologue, dialogue)

Write these observations into CLAUDE.md as concrete writing rules with examples from the text.

### Pass 2: Full extraction

After the style study, read through the complete novel and build lore/:

- `lore/world.md` — world setting, rules, history
- `lore/power.md` — power/leveling system with concrete progression data
- `lore/characters/protagonist.md` — detailed protagonist profile with speech patterns and behavioral traits
- `lore/characters/<name>.md` — each major character with distinctive traits and speaking style
- `lore/characters/index.md` — quick reference
- `lore/factions/` — organizations with hierarchy and goals
- `lore/locations/` — key places with atmosphere notes
- `lore/plot/arcs.md` — major story arcs with emotional stakes
- `lore/plot/chapters.md` — chapter index with one-line summaries
- `CLAUDE.md` — consolidated writing rules from Pass 1 observations

### Pass 3: Index the full text

Split the complete novel into chapter files under `chapters/` if not already done. This enables lore.py to read specific chapters on demand during gameplay for style reference.

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
