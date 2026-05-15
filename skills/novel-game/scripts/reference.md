# Phase Reference

## 三层初始化结构

```
Layer 1: 全书提取（全自动不间断，无交互，产物共享）
  找txt → split_batches切分 → 一次性并行启动N个haiku agent → 轮询等待完成 → merge合并 → lore/ + CLAUDE.md

Layer 2: 存档初始化（交互，每个存档独立）
  介绍世界背景+主角设定 → 玩家自定义 → gamestate.json + turn 0

Layer 3: 会话恢复（自动，每次新对话执行）
  读 CLAUDE.md + lore.py index + 原文前几章恢复风格感知 → 加载 gamestate.json → 进入循环
```

## 共享与隔离

lore/ 和 CLAUDE.md 是全书提取产物，所有存档共享。
gamestate.json、saves/、turns/ 是玩家自定义和情节进度，每个存档完全独立。
新建存档时复用共享文件，重新走 Layer 2，不从其他存档复制任何内容。

---

## Phase 1 --- Layer 1: 全书自动提取

目录下有 .txt 原文。无交互，全部静默完成。

### Stage 1: 批量并行提取（全自动，不中断）

**Step 1.1** — 找到小说 .txt 文件并切分：

```bash
# 找到txt文件
ls <novel-name>/*.txt
# 切分（输出batch总数到index.json）
python3 skills/novel-game/scripts/split_batches.py <novel-name>/<novel>.txt --batch-size 20
# 读取batch总数
python3 -c "import json; d=json.load(open('<novel-name>/_batches/index.json')); print(d['total_chapters'], 'chapters,', len(d['batches']), 'batches')"
```

**Step 1.2** — 读取 index.json 获取 batch 总数 N，然后**一次性并行启动 N 个 haiku agent**：

对每个 batch_i（i=001, 002, ..., N），用 Agent 工具启动，subagent_type="general-purpose"，model="haiku"，run_in_background=true。prompt 内容：

> Read <novel-name>/_batches/batch_NNN_prompt.md. Follow the extraction instructions at the top. Output ONLY valid JSON to <novel-name>/_batches/batch_NNN.json. No explanation.

**所有 agent 必须在一条消息中一次性全部启动。** 不逐个启动，不等待单个完成。

**Step 1.3** — 等待全部完成。轮询检查：

```bash
ls <novel-name>/_batches/batch_*.json 2>/dev/null | wc -l
```

当 JSON 文件数等于 N 时，全部完成。每个 JSON 文件大小应 > 2000 bytes。若有文件过小或缺失，重启动对应 batch 的 agent。

全部完成后进入 Stage 2。

### Stage 2: 合并合成（自动）

```bash
python3 skills/novel-game/scripts/merge_synthesis.py <novel-name>/_batches --output-dir <novel-name>/lore/plot
```

验证产物：
```bash
wc -l <novel-name>/lore/plot/timeline.md <novel-name>/lore/plot/all_key_events.md <novel-name>/lore/characters/INDEX.md
```

timeline.md 应 > 500 行，all_key_events.md 应 > 20 行，INDEX.md 应 > 30 行。不满足则说明提取失败，检查 batch JSON 质量。

生成文件：
- `lore/plot/timeline.md` — 编号场景时间线，行号定位
- `lore/plot/all_key_events.md` — 全部关键事件，按batch排列
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

AskUserQuestion 三个选项：语言（zh/en）、补充定义（自由输入任何想调整的设定）、开始游戏。玩家选"补充定义"则处理后重新问，直到选"开始游戏"。

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

### Step 1: 恢复风格感知

读取 CLAUDE.md 恢复写作规则，读取 lore.py index 了解设定概览，读取原文前几章恢复语感。新对话上下文是空的，需要重新建立对小说世界的认知。

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
- 重新初始化（删除 lore/ 和 CLAUDE.md，从头走 Phase 1 重建全部世界观。用于原文切换或之前提取不完整时）

选择已有存档后，静默 load，恢复上下文（gamestate.json 的 settings + timeline），进入循环。

---

## Rewind

展示 timeline 最后 5 条，AskUserQuestion 选回退点，timeline-truncate。
