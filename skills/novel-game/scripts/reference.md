# Phase Reference

## 三层初始化结构

```
Layer 1: 全书提取（自动，无交互，产物共享）
  切分20章/batch → 并行haiku agent逐batch提取JSON → merge_synthesis.py合并 → lore/ + CLAUDE.md

Layer 2: 存档初始化（交互，每个存档独立）
  介绍世界背景+主角设定 → 玩家自定义 → gamestate.json + turn 0

Layer 3: 会话恢复（自动，每次新对话执行）
  重读原文前20万字恢复风格感知 → 加载 lore/ + gamestate.json → 进入循环
```

## 共享与隔离

lore/ 和 CLAUDE.md 是全书提取产物，所有存档共享。
gamestate.json、saves/、turns/ 是玩家自定义和情节进度，每个存档完全独立。
新建存档时复用共享文件，重新走 Layer 2，不从其他存档复制任何内容。

---

## Phase 1 --- Layer 1: 全书自动提取

目录下有 .txt 原文。无交互，全部静默完成。

### Stage 1: 批量并行提取

```bash
# Step 1: 切分章节为20章/batch，生成带提取prompt的batch文件
python3 skills/novel-game/scripts/split_batches.py <novel-name>/<novel>.txt --batch-size 20

# Step 2: 对每个batch并行启动haiku agent提取
# 每个agent读取 batch_NNN_prompt.md（含提取指令+该批正文），输出 batch_NNN.json
# N个batch = N个并行agent，全部完成后进入Stage 2
```

每个 batch agent 提取的 JSON 包含：scenes（场景/章节/行号/地点/人物/事件/等级）、key_events（3-5条关键事件）、new_characters/new_locations、power_progression。

### Stage 2: 合并合成

```bash
python3 skills/novel-game/scripts/merge_synthesis.py <novel-name>/_batches --output-dir <novel-name>/lore/plot
```

自动生成：
- `lore/plot/timeline.md` — 编号场景完整时间线，行号定位
- `lore/plot/all_key_events.md` — 全部关键事件，按batch排列，每条带场景范围引用
- `lore/characters/INDEX.md` — 人物汇总

### Stage 3: 深度风格研读

merge完成后，逐字阅读小说前 200000 个中文字符，研究叙事节奏、对话工艺、人物内心描写、战斗节奏、转场习惯。将观察和原文例句写入 CLAUDE.md。这是所有后续写作的宪法。

### Stage 4: 提炼 arcs + 补充 lore

阅读 all_key_events.md 和 timeline.md，识别小说的大剧情弧线（按地图/篇章分段），创建 `lore/plot/arcs.md`。每条弧线标注场景范围引用。

然后补充：
- `lore/world.md` — 世界观、核心规则
- `lore/power.md` — 完整力量体系
- `lore/characters/protagonist.md` — 主角完整档案
- `lore/factions/` — 主要势力
- `lore/locations/` — 关键地点

完成后进入 Phase 2。

---

## Phase 2 --- Layer 2: 存档初始化

配置已就绪。向玩家介绍背景并引导角色创建。

### Step 1: 介绍世界观和主角

向玩家介绍以下内容（控制在 8-12 句以内）：

- 这是什么世界，核心规则是什么
- 主角是谁：身份、性格、处境、能力特点
- 主角在故事开始时的位置和面临的局面

**只介绍主角。** 不在此阶段罗列其他人物、势力或地点。除非小说本质上是群像多主角结构（如多个第一人称视角交替），否则只聚焦第一主角。

### Step 2: 语言和自定义

AskUserQuestion 询问语言偏好（zh/en），存入 gamestate.json。

AskUserQuestion 引导自定义：
- 从哪个时间点/地点开始
- 主角额外设定（开局道具、性格偏向、特殊背景）
- 初始场景调整

### Step 3: 写入存档

```bash
python3 skills/novel-game/scripts/state.py init <novel-name> --save <save-name> \
    --lang <zh|en> --chapter <N> \
    --protagonist "<描述>" --custom "<自定义>" \
    --cast "<初始人物>" --inventory "<初始物品>"
```

写 turn 0（save-content + save-options），进入游戏循环。

---

## Phase 3 --- Layer 3: 会话恢复

已有一个或多个存档。**每次新对话进入都必须先执行 Layer 3。**

### Step 1: 重读原文恢复风格感知

**在加载任何存档数据之前**，先重新逐字阅读小说前 200000 个中文字符。这是恢复风格感知的必需步骤。新对话的上下文是空的，CLAUDE.md 里的规则摘要无法替代原文的语感体验。

### Step 2: 加载配置和存档

静默执行：
```bash
python3 skills/novel-game/scripts/lore.py index <novel-name>
python3 skills/novel-game/scripts/state.py list <novel-name>
```

### Step 3: 展示存档选择器

AskUserQuestion 展示：
- 每个已有存档（显示章节参考、轮数、最后游玩时间）
- 开始新存档（走 Phase 2，lore 和 CLAUDE.md 复用，其他全新）
- 重置当前存档（timeline-truncate 后走 Phase 2，保留 save name）

选择已有存档后，静默 load，恢复上下文（gamestate.json 的 settings + timeline），进入循环。

---

## Rewind

展示 timeline 最后 5 条，AskUserQuestion 选回退点，timeline-truncate。
