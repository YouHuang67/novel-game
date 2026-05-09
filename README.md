# Novel Game

An interactive novel game engine powered by Claude Code. Drop a novel `.txt` into the repo, type one command, and start playing as the protagonist — the AI writes the story around your every move.

## Quick Start

### 1. Add your novel

Create a directory at the repo root with your novel text file:

```
doupo/
└── 斗破苍穹.txt
```

### 2. Launch

```
/novel-game doupo
```

The AI auto-detects the phase:

| State | What happens |
|-------|-------------|
| Only .txt, no config | Reads the full novel → extracts world, characters, power system, plot → builds lore files |
| Config ready, no save | Shows world summary → interactive character creation → starts game |
| Save exists | Lists saves → continue / new save / reset |

### 3. Play

```
You: Head into the魔兽山脉 to find that Purple Crystal Winged Lion
AI:  (writes 800 words of combat scene)
You: Turn to Yun Yun and say — come with me
AI:  (writes 600 words of dialogue)
```

High freedom. The original novel's chapters are background reference, not a track you must follow.

## Installation

Clone this repo and enter it. The skill is project-scoped and activates automatically.

```bash
git clone https://github.com/<your-username>/xiaoshuo-game.git
cd xiaoshuo-game
```

No dependencies. Just Python 3 and Claude Code.

## Multiple Saves

```
/novel-game doupo              # Default save
/novel-game doupo evil-run     # Named save
/novel-game list doupo         # List all saves
```

## How It Works

```
Player input → Silent narrative judgment → Query lore on demand → Write 500-1500 words → Save → Loop
```

**Progressive disclosure**: The AI doesn't load the entire novel into context. It reads a lore index first, then queries specific topics (characters, locations, power systems) only when needed.

**The AI is a story guardian, not a yes-man.** It enforces narrative pacing and world consistency — no skipping conflicts, no infinite power-leveling montages. But it pushes back in the story's own voice, not with DM meta-talk.

## File Structure

```
skills/novel-game/
├── SKILL.md              # Skill definition
└── scripts/
    ├── state.py          # Save file manager
    ├── lore.py           # Progressive disclosure tool
    └── reference.md      # Phase instructions
```

## License

MIT
