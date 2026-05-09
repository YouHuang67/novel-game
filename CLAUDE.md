# Novel Game --- Development Reference

Claude Code skill for interactive novel gaming.
Core idea: drop a novel .txt → AI analyzes the world → player types freely → AI continues the story.

## Project Structure

```
skills/novel-game/
├── SKILL.md              # Skill definition (AI instructions)
└── scripts/
    ├── state.py          # Save file manager (gamestate.json + turns/)
    ├── lore.py           # Progressive disclosure tool (lore index/read/search)
    └── reference.md      # Detailed phase instructions (loaded on demand)
```

## How It Works

1. User places a novel .txt in a directory at repo root (e.g., `doupo/斗破苍穹.txt`)
2. User invokes `/novel-game doupo`
3. Phase 1: AI reads the novel, auto-builds `lore/` directory and `CLAUDE.md`
4. Phase 2: Interactive character creation
5. Phase 3: Game loop --- player types, AI writes, state saved to `gamestate.json` + `turns/`

## Design Principles

- **Progressive disclosure**: lore.py index for overview, read/search for details on demand
- **Descriptive state**: gamestate.json uses natural language, compatible with any novel genre
- **Skill is project-scoped**: registered in .claude/skills/novel-game, only active in this repo
