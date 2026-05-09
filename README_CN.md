## [English](README.md)

<h1 align="center">Novel Game</h1>

<p align="center">
  把任意小说 <code>.txt</code> 变成可游玩的 Claude Code 互动小说 skill。
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-7C3AED?style=for-the-badge" alt="Claude Code Skill">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#what-it-does">功能</a> ·
  <a href="#quick-start">快速开始</a> ·
  <a href="#current-skill-design">设计</a> ·
  <a href="#generated-files">生成文件</a> ·
  <a href="#repo-layout">仓库结构</a>
</p>

Novel Game 是一个仓库级 Claude Code skill。把小说放进一个目录后，运行 `/novel-game <小说目录>`，AI 会先分析原作、生成可复用的设定资料，再围绕你的选择按原小说文风继续写下去。

<a id="what-it-does"></a>
## 本项目能做什么

- 把普通纯文本小说直接变成互动小说游戏
- 从原文中提取人物、世界观、势力、升级体系等关键信息
- 自动生成小说专属 `CLAUDE.md`，让 AI 更稳定地保持文风和叙事约束
- 用自然语言自由输入行动，而不是死板菜单指令
- 以“一个回合推进一个关键场景”为主，避免一口气跑完整段剧情
- 每轮续写后自动给出局面总结、后续方向和自由输入入口
- 支持多存档，方便分支路线和不同玩法
- 支持回滚到更早回合，换一个选择重新游玩
- 通过轻量工具按需读取 lore，而不是一次性塞入全部设定
- 控制叙事节奏，尽量避免跳结局式推进和失控升级
- 游戏界面支持中文或英文

<a id="quick-start"></a>
## 快速开始

```bash
git clone https://github.com/YouHuang67/novel-game.git
cd novel-game
```

本仓库已经在 `.claude/skills/novel-game` 下配置了项目级 skill 链接，所以直接在这个仓库里使用 Claude Code 即可。

在仓库根目录创建一个目录，并把小说放进去：

```text
my-novel/
└── novel.txt
```

然后在仓库里启动 Claude Code：

```bash
claude
```

如果你想要更丝滑、更自动化一些的体验，也可以使用：

```bash
claude --dangerously-skip-permissions
```

然后在 Claude Code 中运行：

```text
/novel-game my-novel              # 启动或继续默认存档
/novel-game my-novel evil-run     # 启动或继续命名存档
/novel-game list my-novel         # 查看已有存档
```

<a id="current-skill-design"></a>
## 当前 skill 设计

具体运行流程还在持续完善，但当前版本主要围绕这几个稳定思路：

- **小说专属写作规则**：每本小说都会有自己的 `CLAUDE.md`
- **按场景推进节奏**：强调一轮一个关键节拍，而不是流水账式快进
- **带引导的回合输出**：续写正文后会跟上简短总结和下一步方向
- **渐进式 lore 读取**：只在需要时读取设定，减少上下文压力
- **持续状态管理**：存档、时间线、回滚、语言记忆都属于核心体验

<a id="generated-files"></a>
## 游玩过程中会生成的文件

第一次正式游玩后，小说目录通常会变成这样：

```text
my-novel/
├── novel.txt
├── CLAUDE.md          # 小说专属写作规则
├── lore/              # 人物、势力、世界规则等资料
├── gamestate.json     # 默认存档
├── saves/             # 命名存档
└── turns/             # 每回合正文，按存档分组
```

<a id="repo-layout"></a>
## 仓库结构

```text
skills/novel-game/
├── SKILL.md              # Claude Code skill 主定义
└── scripts/
    ├── lore.py           # lore 索引 / 读取 / 搜索
    ├── state.py          # 存档状态、时间线、回滚辅助
    └── reference.md      # 分阶段运行说明
```

## 许可证

MIT
