# Novel Game

Turn any novel `.txt` into an interactive game with Claude Code. Drop in a novel, type one command, and play as the protagonist — the AI writes the story around your every move.

## Quick Start

### 1. Add your novel

Create a directory with your novel `.txt` at the repo root:

```
doupo/
└── 斗破苍穹.txt
```

### 2. Launch

```
/novel-game doupo
```

The AI auto-detects where you are and what to do:

| Novel state | What happens |
|------------|-------------|
| Only `.txt` | Reads the full novel → extracts world, characters, power system, plot — silently |
| Config ready | Shows world summary → interactive character creation → starts the game |
| Has saves | Lists saves → continue / new / reset |

### 3. Play

```
You: Head into the mountains to find that beast
AI:  (writes 800 words of combat scene)
You: Turn to her and say — come with me
AI:  (writes 600 words of dialogue)
```

After each turn the AI summarizes where you are and suggests directions — always with a "free input" option. You're never locked into preset choices.

## Installation

```bash
git clone https://github.com/<user>/xiaoshuo-game.git
cd xiaoshuo-game
```

That's it. The skill lives in `.claude/skills/novel-game` (a relative symlink committed to the repo). Claude Code scans this directory when you enter the project — no global install, no manual linking.

Requires: Python 3, Claude Code.

## Multiple Saves

```
/novel-game doupo              # Default save
/novel-game doupo evil-run     # Named save
/novel-game list doupo         # List all saves
```

## Design

**Progressive disclosure.** The AI doesn't cram the entire novel into context. It uses `lore.py` to query specific topics — characters, locations, power systems — only when needed.

**Story guardian, not yes-man.** The AI enforces narrative pacing and world consistency. It pushes back when you try to skip conflicts or power-level into oblivion — but in the story's own voice, never with DM meta-talk.

**Descriptive state, not kv pairs.** Game state is natural language in `gamestate.json` — works for xianxia, VR-MMO, palace intrigue, or any genre without changing the schema.

## License

MIT
