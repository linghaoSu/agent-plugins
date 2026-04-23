# Issue Evaluator 安装指南

## 前置要求

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| [Claude Code](https://claude.ai/code) | 插件运行环境 | `npm install -g @anthropic-ai/claude-code` |
| [GitHub CLI](https://cli.github.com/) (`gh`) | 获取 issue 详情 | `brew install gh` (macOS) |
| [Codex 插件](https://github.com/openai/codex-plugin-cc) | `/review-fix` 对抗式 review | 见下方安装说明 |
| Git 仓库 | 插件工作在 Git 仓库中 | — |

### 验证前置依赖

```bash
# 检查 Claude Code
claude --version

# 检查 GitHub CLI 并登录
gh auth status
# 如未登录：gh auth login

# 检查 Codex 插件是否已安装（可选，仅 /review-fix 需要）
claude plugin list 2>/dev/null || echo "在 Claude Code 中运行 /plugin 查看"
```

---

## 安装方式

### 方式一：本地 Marketplace 安装（推荐）

将本仓库注册为本地 marketplace，然后安装插件。插件会被复制到 `~/.claude/plugins/cache/` 中持久化。

**1. 在 Claude Code 中注册 marketplace：**

```bash
# 在 Claude Code 交互式会话中运行
/plugin marketplace add /path/to/agent-plugins
```

**2. 安装插件：**

```bash
/plugin install issue-evaluator@claude-skills
```

**3. 验证安装：**

```bash
/plugin
# 应显示 issue-evaluator 已启用
```

### 方式二：临时加载（开发/调试用）

使用 `--plugin-dir` 参数直接加载插件目录，不写入配置。适合开发调试阶段。

```bash
claude --plugin-dir /path/to/agent-plugins/issue-evaluator
```

> 注意：此方式仅在当前会话中生效，关闭后需重新指定。

### 方式三：手动配置

直接编辑 Claude Code 设置文件，将插件路径加入。

**1. 复制插件到缓存目录：**

```bash
mkdir -p ~/.claude/plugins/cache/claude-skills/issue-evaluator/1.0.0
cp -r /path/to/agent-plugins/issue-evaluator/* \
      ~/.claude/plugins/cache/claude-skills/issue-evaluator/1.0.0/
cp -r /path/to/agent-plugins/issue-evaluator/.claude-plugin \
      ~/.claude/plugins/cache/claude-skills/issue-evaluator/1.0.0/
```

**2. 编辑 `~/.claude/plugins/installed_plugins.json`，添加插件条目：**

```json
{
  "version": 2,
  "plugins": {
    "issue-evaluator@claude-skills": [
      {
        "scope": "user",
        "installPath": "~/.claude/plugins/cache/claude-skills/issue-evaluator/1.0.0",
        "version": "1.0.0",
        "installedAt": "2026-04-02T00:00:00.000Z",
        "lastUpdated": "2026-04-02T00:00:00.000Z"
      }
    ]
  }
}
```

**3. 编辑 `~/.claude/settings.json`，启用插件：**

```json
{
  "enabledPlugins": {
    "issue-evaluator@claude-skills": true
  }
}
```

**4. 在 Claude Code 中重新加载：**

```bash
/reload-plugins
```

---

## 安装 Codex 插件（如需 `/review-fix`）

`/review-fix` 依赖 Codex 插件提供对抗式 review。如未安装：

```bash
# 在 Claude Code 中运行
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
```

---

## 使用方法

安装完成后，在任意 Git 仓库中启动 Claude Code，即可使用以下命令：

```bash
# 1. 评估一个 GitHub issue
/evaluate-issue https://github.com/owner/repo/issues/123
/evaluate-issue 123
/evaluate-issue #123

# 2. 实施修复（手动或让 Claude 实现）

# 3. 修复后运行对抗式 review
/review-fix
/review-fix --wait
/review-fix --background
```

### 生成的文件

| 文件 | 说明 |
|------|------|
| `.issue-evaluator/code-style.md` | 仓库代码风格分析文档，首次 `/evaluate-issue` 时自动生成 |

> 删除 `.issue-evaluator/code-style.md` 后重新运行 `/evaluate-issue` 可强制重新生成代码风格分析。

建议将 `.issue-evaluator/` 加入 `.gitignore`：

```bash
echo '.issue-evaluator/' >> .gitignore
```

---

## 卸载

```bash
# 在 Claude Code 中运行
/plugin uninstall issue-evaluator@claude-skills
```

或手动删除：

```bash
rm -rf ~/.claude/plugins/cache/claude-skills/issue-evaluator
```

并从 `~/.claude/plugins/installed_plugins.json` 和 `~/.claude/settings.json` 中移除相关条目。

---

## 故障排查

### 插件未出现在 `/plugin` 列表中

- 确认 `.claude-plugin/plugin.json` 存在且格式正确
- 运行 `/reload-plugins` 重新加载
- 使用 `claude --debug` 启动查看插件加载日志

### `gh` 命令失败

- 运行 `gh auth status` 确认已登录
- 确认当前目录是 Git 仓库且有 GitHub remote

### `/review-fix` 报错找不到 Codex

- 确认 Codex 插件已安装：`/plugin` 中应显示 `codex@openai-codex`
- 如未安装，参照上方"安装 Codex 插件"章节

### 代码风格文档不准确

- 删除 `.issue-evaluator/code-style.md` 后重新运行 `/evaluate-issue` 强制重新生成
