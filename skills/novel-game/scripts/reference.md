# Phase Reference

## Phase 1 --- 全自动构建世界观

目录下有 .txt 原文。全程静默，处理完后再对话。

1. Read 所有 .txt，完整阅读
2. 自动提取并写入以下文件（不逐层询问）：

lore/world.md, lore/power.md, lore/characters/protagonist.md,
lore/characters/<name>.md, lore/characters/index.md,
lore/factions/, lore/locations/,
lore/plot/arcs.md, lore/plot/chapters.md, CLAUDE.md

3. 全部完成后展示摘要，AskUserQuestion：确认 / 调整 / 补充

## Phase 2 --- 首次游戏（捏人）

AskUserQuestion 引导自定义起始点/主角设定/初始场景。
state.py init + timeline-add turn 0，进入循环。

## Phase 3 --- 选档

AskUserQuestion：已有存档 + 新存档 + 重置。

## 回滚

展示 timeline 最后 5 条 → AskUserQuestion → timeline-truncate。
