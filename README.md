## [中文](README_CN.md)

<h1 align="center">Novel Game</h1>

<p align="center">
  Turn any novel <code>.txt</code> into a playable interactive-fiction skill for Claude Code.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-7C3AED?style=for-the-badge" alt="Claude Code Skill">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#what-it-does">What it does</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#current-skill-design">Design</a> ·
  <a href="#generated-files">Generated files</a> ·
  <a href="#repo-layout">Repo layout</a>
</p>

Novel Game is a repo-scoped Claude Code skill. Put a novel into a folder, run `/novel-game <novel-folder>`, and the AI will analyze the source material, build reusable lore files, and continue the story around your choices in the novel's own style.

<a id="what-it-does"></a>
## What you can do with it

- Turn a plain-text novel into an interactive story game
- Extract characters, worldbuilding, factions, and progression rules from source text
- Generate a novel-specific `CLAUDE.md` so the AI keeps the right tone and narrative constraints
- Play with free-text actions instead of rigid command menus
- Write one meaningful scene at a time instead of rushing through the whole plot
- End each turn with a short situation summary, suggested next moves, and free input
- Keep multiple saves and branch into different routes
- Rewind to earlier turns and replay from a different decision point
- Load lore on demand with lightweight tools instead of dumping the whole setting into context
- Keep narrative pacing under control and resist skip-to-the-end power gaming
- Use either Chinese or English for the game UI

<a id="quick-start"></a>
## Quick start

```bash
git clone https://github.com/YouHuang67/novel-game.git
cd novel-game
```

This repository already includes the project-scoped skill link at `.claude/skills/novel-game`, so Claude Code can use it directly inside this repo.

Create a folder at the repo root and put your novel inside it:

```text
my-novel/
└── novel.txt
```

Then start Claude Code in the repo:

```bash
claude
```

If you want a smoother, more automated session, you can also use:

```bash
claude --dangerously-skip-permissions
```

Then run in Claude Code:

```text
/novel-game my-novel              # start or continue the default save
/novel-game my-novel evil-run     # start or continue a named save
/novel-game list my-novel         # show available saves
```

<a id="current-skill-design"></a>
## Current skill design

The exact runtime flow is still evolving, but the current skill is built around a few stable ideas:

- **Novel-specific writing rules**: each novel gets its own `CLAUDE.md`
- **Scene-first pacing**: the skill favors one strong beat per turn, not a rushed multi-event summary
- **Guided turn output**: story text is followed by a short recap and next-step guidance
- **Progressive lore loading**: setting files are read on demand to keep context smaller
- **Persistent state**: saves, timeline summaries, rewind, and remembered language are part of the play loop

<a id="generated-files"></a>
## Files created during play

After the first playable run, a novel folder will typically look like this:

```text
my-novel/
├── novel.txt
├── CLAUDE.md          # novel-specific writing rules
├── lore/              # characters, factions, world rules, etc.
├── gamestate.json     # default save
├── saves/             # named saves
└── turns/             # full turn text grouped by save
```

<a id="repo-layout"></a>
## Repo layout

```text
skills/novel-game/
├── SKILL.md              # main Claude Code skill definition
└── scripts/
    ├── lore.py           # lore index / read / search
    ├── state.py          # save state, timeline, rewind helpers
    └── reference.md      # phase-specific runtime guidance
```

## License

MIT
