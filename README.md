# Novel Game

Claude Code skill. Turns a novel `.txt` into an interactive game — type what your character does, AI continues the story.

## Install

```bash
git clone https://github.com/<user>/novel-game.git
cd novel-game
```

Requires Python 3 and Claude Code. The skill activates automatically when you enter the directory.

## Usage

Put a novel `.txt` in a directory at repo root:

```
my-novel/
└── novel.txt
```

Then:

```
/novel-game my-novel
```

First run: AI reads the novel, extracts world/characters/plot, then guides you through character creation.  
Later runs: pick a save to continue, start fresh, or reset.

Each turn you describe what to do. AI writes 500-1500 words, then shows a summary and options for next direction (always includes free input).

```
/novel-game my-novel evil-run    # named save
/novel-game list my-novel        # list saves
```

## License

MIT
