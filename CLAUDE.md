# GitHub Trend Analyzer - Claude Code 协作规范

## 报告质量标准

**必须向 `titanwings/colleague-skill` 看齐（19.9KB 详细报告）**。

禁止使用单次 LLM 调用生成简略报告（1-2KB 是不可接受的）。

## 正确流程

```
python cli.py trending --language python --limit N --publish
```

每个仓库必须：
1. 使用 `CrewAI` + `RepoAnalysisPipeline`（不是单次 LLM 调用）
2. Explorer Agent 调用 GitHub 工具获取真实数据
3. Analyst Agent 深度技术分析
4. Writer Agent 生成 10KB+ 的详细中文报告
5. 通过 `auto_publish` 同步到 garden

## CrewAI Pipeline

- **Model**: `minimax/MiniMax-M2.7` via LiteLLM
- **Base URL**: `https://api.minimax.chat/v1`
- **Process**: `Process.sequential`
- **Explorer tools**: `[get_repo_meta, get_file_tree, read_file]`
- **Analyst tools**: `[]`（纯分析，基于 Explorer 输出）
- **Writer tools**: `[]`（纯写作）

## 报告输出目录

- 本地：`/Users/yueyh/Projects/github-trend-analyzer/reports/`
- Garden：`/Users/yueyh/Projects/github-trend-garden/content/trending/{date}/`

## 质量检查

报告生成后检查大小：
- `< 5KB`：不合格，需要重做
- `5-10KB`：勉强合格
- `> 10KB`：合格（参考 titanwings 是 19.9KB）
