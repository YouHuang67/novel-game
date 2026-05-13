# Phase Reference

## 三层初始化结构

```
Layer 1: 全书提取（自动，无交互，产物共享）
  读小说 → 提取世界观/等级/人物/势力/剧情 → lore/ + CLAUDE.md

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

### Stage 1: 深度风格研读

逐字阅读小说前 200000 个中文字符。不是扫描，不是提取关键词。是作为学徒阅读一位作家的作品。

研究内容：
- 叙事节奏：句子长短交替规律，动作与描写的交替频率，段落呼吸感
- 对话工艺：每个主要人物的说话方式有何不同，语气标注习惯，对话与叙述的比例
- 人物内心：思想情感如何呈现（内心独白、身体反应、旁白总结），每种情绪对应的具体写法
- 描写技法：人物出场如何描写（眼睛、姿态、衣着、气场），场景如何建立氛围，哪些感官被调用
- 战斗节奏：战斗如何逐招展开，威力如何呈现，旁观者如何反应
- 转场习惯：场景间如何过渡，时间跳跃如何处理，新人物如何引入

将观察和原文例句写入 CLAUDE.md。这些规则是所有后续写作的宪法。

### Stage 2: 全书结构化提取

通读完整小说，构建 lore/ 目录：

- `lore/world.md` — 世界观、核心规则、历史背景
- `lore/power.md` — 完整力量体系，含升级路径、瓶颈条件、突破方式
- `lore/characters/protagonist.md` — 主角完整档案：身份、外貌、性格、说话方式、行为习惯、关键关系、角色弧线
- `lore/characters/<name>.md` — 每个重要角色独立文件，含其独特声音和特征
- `lore/characters/index.md` — 人物快速索引
- `lore/factions/<name>.md` — 势力组织，含结构、目标、关键成员
- `lore/locations/<name>.md` — 关键地点，含氛围、意义、典型事件
- `lore/plot/arcs.md` — 主要剧情弧线，含情感筹码和关键事件
- `lore/plot/chapters.md` — 章节索引，每章一行摘要

### Stage 3: 文本索引

将全书按章节切分存入 `chapters/` 目录（如果原文未分章）。运行 `lore.py index` 验证。

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
