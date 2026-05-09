# [English](README.md) | 中文

Claude Code skill。将小说 txt 转为互动游戏：输入角色行动，AI 续写故事。

## 安装

需要 Python 3 和 Claude Code。仓库内置 `.claude/skills/novel-game` 软链接，进入目录后 Claude Code 自动加载项目级 skill，无需全局安装或配置 MCP。

## 使用

在仓库根目录下创建目录并放入小说 txt，然后调用 skill：

```
/novel-game my-novel
```

首次运行会提取小说的世界观、人物和剧情，然后引导你创建角色。再次运行会展示存档选择：继续、新存档或重置。

每轮输入你想做的事，AI 续写 500 到 1500 字，然后展示当前局面和方向选项（始终包含自由输入）。

```
/novel-game my-novel evil-run    # 命名存档
/novel-game list my-novel        # 列出存档
```

## 许可

MIT
