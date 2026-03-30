"""
CrewAI Tasks 定义
"""
from crewai import Task


def create_explore_task(agent, repo_info: dict) -> Task:
    """创建仓库探索任务"""
    repo_full_name = repo_info.get("full_name", "")
    repo_description = repo_info.get("description", "")

    return Task(
        description=f"""分析 GitHub 仓库 {repo_full_name} 的结构。

仓库描述：{repo_description}

请完成以下任务：
1. 获取仓库根目录的文件列表
2. 读取 README.md 文件（如果存在）
3. 识别项目类型和核心配置文件（如 package.json, requirements.txt, Cargo.toml 等）
4. 分析项目的整体结构和组织方式

返回结构化的分析结果，包括：
- 项目类型（库/应用/工具等）
- 主要编程语言
- 核心文件列表
- README 摘要
- 项目结构特点""",
        agent=agent,
        expected_output="一份详细的仓库结构分析报告，包含项目类型、语言、核心文件和结构特点"
    )


def create_analyze_task(agent, repo_info: dict, explore_result: str = "") -> Task:
    """创建技术分析任务"""
    repo_full_name = repo_info.get("full_name", "")

    return Task(
        description=f"""对 GitHub 仓库 {repo_full_name} 进行技术深度分析。

探索阶段的结果：
{explore_result}

请完成以下任务：
1. 确定项目使用的技术栈（语言、框架、主要库）
2. 评估依赖复杂度（依赖数量、是否有过时依赖）
3. 判断项目可运行性（是否有明确的运行方式、构建工具）
4. 识别代码规模（主要文件的代码行数）
5. 发现技术亮点或潜在问题

返回结构化的技术分析结果。""",
        agent=agent,
        expected_output="一份技术深度分析报告，包含技术栈、依赖复杂度、可运行性评估"
    )


def create_write_task(agent, repo_info: dict, explore_result: str = "", analyze_result: str = "") -> Task:
    """创建报告撰写任务"""
    repo_full_name = repo_info.get("full_name", "")
    repo_description = repo_info.get("description", "")
    repo_url = repo_info.get("url", "")

    return Task(
        description=f"""为 GitHub 仓库 {repo_full_name} 生成中文技术调研报告。

原始仓库信息：
- 名称：{repo_full_name}
- 描述：{repo_description}
- URL：{repo_url}

探索分析：
{explore_result}

技术分析：
{analyze_result}

请生成一份完整的 Markdown 格式报告，包含：

# {repo_full_name} 技术调研报告

## 基本信息
## 项目简介
## 技术栈分析
## 代码结构
## 依赖分析
## 可运行性评估
## 技术亮点
## 潜在问题
## 总结与建议

报告应该：
- 使用中文撰写
- 结构清晰、层次分明
- 包含具体的代码或数据引用
- 提供客观的评估和实用的建议""",
        agent=agent,
        expected_output="一份完整的中文 Markdown 格式技术调研报告"
    )
