# Novel Game

[中文](README_CN.md)

Claude Code skill. Turns a novel `.txt` into an interactive game: type what your character does, AI continues the story.

## Install

Requires Python 3 and Claude Code. The repo contains a `.claude/skills/novel-game` symlink. Claude Code auto loads project scoped skills on enter. No global install or MCP config needed.

## Usage

Put a novel `.txt` in a directory at repo root and invoke the skill:

```
/novel-game my-novel
```

First run extracts world, characters, and plot from the novel, then guides you through character creation. Later runs present a save selector: continue, new save, or reset.

Each turn you type what to do. AI writes 500 to 1500 words, then shows options for the next direction (always includes free input).

```
/novel-game my-novel evil-run    # named save
/novel-game list my-novel        # list saves
```

## License

MIT
