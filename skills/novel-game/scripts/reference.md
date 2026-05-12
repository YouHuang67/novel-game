# Phase Reference

## Shared vs Isolated

lore/ 和 CLAUDE.md 是小说提炼内容，所有存档共享。
gamestate.json、saves/、turns/ 是玩家自定义设定和情节进度，每个存档完全独立。

新建存档时：复用 lore/ 和 CLAUDE.md，重新走 Phase 2 完整捏人流程。不从其他存档复制任何 settings、timeline、flags。

## Phase 1 --- Auto-build world

Directory has .txt only. Two distinct stages: deep style study by the agent, then structured extraction by scripts.

### Stage 1: Deep style internalization (agent reads, no scripts)

This is the most critical stage. You, the agent, must read the first 200000 Chinese characters word by word. Not skim. Not extract bullet points. Read as a careful student of this author's craft.

What you are studying:

**Narrative voice and rhythm.**
How long are the sentences? How do short and long sentences alternate within a paragraph? How does the author transition between action, description, and internal monologue? Count the beats: in a typical action paragraph, how many sentences of physical action before a sentence of reaction or reflection?

**Dialogue craft.**
How do characters speak? What tone markers are used (冷笑道, 淡淡道, 沉声道)? How much dialogue versus narration in a typical scene? What is the ratio of spoken words to narrative description around the dialogue? How does each major character have a DISTINCTIVE speaking pattern?

**Character interiority.**
How does the author reveal what characters are thinking and feeling? Through internal monologue? Through physical reactions (手抖, 瞳孔收缩, 呼吸急促)? Through narrated summary of emotion? Collect specific examples of how different emotions are rendered.

**Description technique.**
How are people described when first introduced? What details are chosen (eyes, posture, clothing, aura)? How are locations established? Which senses are used and in what proportion? How does description vary between action scenes and quiet scenes?

**Scene construction.**
How does a typical scene begin and end? How does the author build tension within a scene? How are multiple characters managed in a crowded scene? How are time transitions handled?

Write concrete observations with quoted examples into CLAUDE.md. These become the writing constitution for all subsequent gameplay.

### Stage 2: Structured data extraction (scripts)

After deeply internalizing the style, process the full novel to build the lore/ directory:

```bash
# Split novel into chapters for indexed retrieval
# Extract structured data into lore/ files
```

Build these files:

- `lore/world.md` — world setting with concrete rules and history
- `lore/power.md` — complete power system with progression data, bottlenecks, breakthrough conditions
- `lore/characters/protagonist.md` — full profile: identity, appearance, personality, speech patterns, behavioral traits, key relationships, character arc
- `lore/characters/<name>.md` — each major character with their distinctive voice, appearance, role, and relationship to protagonist
- `lore/characters/index.md` — quick reference list
- `lore/factions/<name>.md` — each organization with structure, goals, key members
- `lore/locations/<name>.md` — each key location with atmosphere, significance, and typical events
- `lore/plot/arcs.md` — major story arcs with emotional stakes and key events
- `lore/plot/chapters.md` — chapter-by-chapter index with one-line summaries

After building, run `lore.py index` to verify.

### Stage 3: Language and launch

Ask language preference via AskUserQuestion (zh/en). Save to gamestate.json. Proceed to Phase 2.

## Phase 2 --- First game (character creation)

If lang not set, ask language preference first. Then AskUserQuestion: starting point, protagonist extras, scene tweaks. state.py init + timeline-add turn 0 with --guided true and --guidance-text.

## Phase 3 --- Save selector

Read lang from gamestate.json, auto-switch UI language. AskUserQuestion:
- Each existing save (show chapter, turn count, last played)
- Start new save (go to Phase 2 with new save name, lore and CLAUDE.md are reused, nothing else)
- Reset current save (timeline-truncate, then Phase 2 keeping same save name)

## Rewind

Show last 5 timeline entries, AskUserQuestion to pick rewind point, timeline-truncate.
