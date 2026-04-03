# GitHub Trend Analyzer

AI 驱动的 GitHub Trending 仓库分析工具，使用 CrewAI 多智能体生成技术调研报告，自动发布到 Quartz 数字花园。

## 架构

```
github-trend-analyzer/      # 分析引擎
  ├── crew/
  │   ├── agents.py         # 3个Agent: Explorer / Analyst / Writer
  │   ├── pipeline.py        # CrewAI Pipeline (顺序执行)
  │   └── tasks.py          # 任务定义
  ├── trending_fetcher.py    # 爬 GitHub Trending 页面
  ├── github_client.py      # GitHub API Client
  ├── cli.py               # 命令行入口
  └── auto_publish.py       # 同步到 garden

github-trend-garden/        # Quartz v4 数字花园 (GitHub Pages)
  └── content/trending/YYYY-MM-DD/
```

## 从零部署

### 1. 克隆项目

```bash
git clone https://github.com/easygl1der/github-trend-analyzer.git
cd github-trend-analyzer

# 克隆 garden (与 analyzer 同级目录)
git clone https://github.com/easygl1der/github-trend-garden.git
```

### 2. 安装依赖

```bash
pip install crewai crewai-tools requests beautifulsoup4
```

### 3. 环境变量

```bash
export MINIMAX_API_KEY="your-minimax-api-key"
export GITHUB_TOKEN="your-github-token"  # 可选，提高 API 限速
```

### 4. 运行分析

```bash
# 分析 Python 语言的 5 个热点仓库，生成报告并发布到 garden
python cli.py trending --language python --limit 5 --publish
```

### 5. GitHub Pages 部署

Garden 推送后自动触发 GitHub Actions 构建，部署到：
`https://easygl1der.github.io/github-trend-garden/`

## 关键配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| MiniMax 模型 | `minimax/MiniMax-M2.7` | via LiteLLM |
| LiteLLM 端点 | `https://api.minimax.chat/v1` | 注意不是 minimax.io |
| CrewAI 模式 | `Process.sequential` | 避免 hierarchical 的工具调用错误 |

### MiniMax API 限制

- **拒绝 `role: system`**: 必须通过 LiteLLM 路由，直接调用会返回 2013 错误
- **工具调用**: Explorer Agent 使用 GitHub 工具；Analyst/Writer 仅用 LLM 分析

## 命令行用法

```bash
# 获取并分析热点仓库
python cli.py trending --language python --limit 5 --publish

# 分析指定仓库
python cli.py analyze owner/repo --language python --publish

# 参数说明
# --language, -l   编程语言 (python, javascript, all)
# --limit, -n      分析数量 (默认 5)
# --publish, -p    分析完成后发布到 garden
```

## 报告标准

- 文件名: `仓库名.md` (不含 owner 前缀)
- 头部信息: 作者(@owner)、今日新增⭐、总⭐
- 最小大小: 10KB+ (titanwings 标准)
- 低于 5KB 的报告需重新生成

## 技术细节

### CrewAI Pipeline

```
Explorer Agent → Analyst Agent → Writer Agent
   (GitHub工具)    (纯LLM分析)    (纯LLM写作)
```

- **Explorer**: 使用 `@tool` 装饰的 GitHub API 函数 (get_repo_meta, get_file_tree, read_file)
- **Analyst**: 无工具，接收 Explorer 结果进行技术分析
- **Writer**: 无工具，生成完整 Markdown 报告

### Trending Fetcher

GitHub Search API 不返回 `today_stars`，因此改爬 GitHub Trending 页面获取真实数据。

## License

MIT
