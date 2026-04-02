"""
CrewAI Agents 定义
为每个 Agent 挂载 GitHub 工具，实现真正的 Agentic AI
使用 LiteLLM 接入 MiniMax，处理 system role 兼容性问题
"""
import os
from crewai import Agent
from crewai.llm import LLM
from crewai.tools import tool
from github_client import GitHubClient

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
# LiteLLM 统一入口，自动处理 provider 兼容性问题
LITELLM_BASE_URL = "https://api.minimax.chat/v1"
# 设置 Litellm 的 API base（Litellm 内部使用）
os.environ["LITELLM_API_BASE"] = LITELLM_BASE_URL
os.environ["LITELLM_API_KEY"] = MINIMAX_API_KEY

# 创建 GitHub 客户端实例
_github_client = GitHubClient()


@tool("get_repo_meta")
def get_repo_meta(repo_path: str) -> str:
    """
    获取 GitHub 仓库的元信息。

    Args:
        repo_path: 仓库路径，格式为 "owner/repo"，例如 "easygl1der/github-trend-analyzer"

    Returns:
        包含仓库基本信息的字典：full_name, description, language, stars, forks,
        open_issues, license, topics, created_at, pushed_at, homepage, url
    """
    parts = repo_path.split("/")
    if len(parts) != 2:
        return f"错误：repo_path 格式应为 'owner/repo'，实际收到: {repo_path}"
    owner, repo = parts[0], parts[1]
    result = _github_client.get_repo_meta(owner, repo)
    if "error" in result:
        return f"获取仓库元信息失败: {result['error']}"
    return str(result)


@tool("get_file_tree")
def get_file_tree(repo_path: str, ref: str = "main") -> str:
    """
    获取 GitHub 仓库根目录的文件列表。

    Args:
        repo_path: 仓库路径，格式为 "owner/repo"
        ref: 分支或标签名，默认为 "main"

    Returns:
        仓库根目录的文件列表（JSON格式字符串），每个文件包含 path, size, type 等信息
    """
    parts = repo_path.split("/")
    if len(parts) != 2:
        return f"错误：repo_path 格式应为 'owner/repo'，实际收到: {repo_path}"
    owner, repo = parts[0], parts[1]
    result = _github_client.get_file_tree(owner, repo, ref)
    if result and isinstance(result, list) and "error" in result[0]:
        return f"获取文件列表失败: {result[0]['error']}"
    return str(result)


@tool("read_file")
def read_file(repo_path: str, file_path: str, ref: str = "main") -> str:
    """
    读取 GitHub 仓库中指定文件的内容。

    Args:
        repo_path: 仓库路径，格式为 "owner/repo"
        file_path: 文件在仓库中的路径，例如 "README.md", "src/main.py"
        ref: 分支或标签名，默认为 "main"

    Returns:
        文件的文本内容。如果文件不存在或无法读取，返回错误信息。
    """
    parts = repo_path.split("/")
    if len(parts) != 2:
        return f"错误：repo_path 格式应为 'owner/repo'，实际收到: {repo_path}"
    owner, repo = parts[0], parts[1]
    result = _github_client.read_file(owner, repo, file_path, ref)
    if result is None:
        return f"文件不存在或无法读取: {file_path}"
    return result


def get_minimax_llm(model: str = "minimax/MiniMax-M2.7"):
    """创建 MiniMax LLM 实例 — 通过 Litellm 路由，自动处理 system role 兼容"""
    return LLM(
        model=model,
        base_url="https://api.minimax.chat/v1",
        api_key=MINIMAX_API_KEY,
    )


def create_explorer_agent() -> Agent:
    """创建 Explorer Agent：分析仓库结构（使用 GitHub 工具）"""
    return Agent(
        role="仓库结构分析师",
        goal="深入分析 GitHub 仓库的文件结构、README 和核心配置文件，为后续技术分析提供基础",
        backstory="""你是一位经验丰富的软件架构师，擅长快速理解开源项目的结构和组织方式。
你可以通过仓库的文件结构判断项目的类型（库/应用/工具）、主要编程语言、构建系统和依赖管理方式。
你善于发现项目中的核心文件和关键配置。""",
        verbose=True,
        allow_delegation=False,
        tools=[get_repo_meta, get_file_tree, read_file],
        llm=get_minimax_llm(),
    )


def create_analyst_agent() -> Agent:
    """创建 Analyst Agent：评估技术栈和代码质量（不使用工具，纯分析）"""
    return Agent(
        role="技术深度分析师",
        goal="评估仓库的技术栈、代码质量、依赖复杂度和可运行性",
        backstory="""你是一位资深技术专家，专注于分析开源项目的技术深度。
你能够评估一个项目的技术架构、设计模式、代码质量和可维护性。
你善于发现项目中的技术亮点和创新点，同时也能识别潜在的问题和风险。
注意：你不需要调用任何工具，基于 Explorer 提供的信息进行分析即可。""",
        verbose=True,
        allow_delegation=False,
        tools=[],  # Analyst 不需要工具，基于 Explorer 输出做分析
        llm=get_minimax_llm(),
    )


def create_writer_agent() -> Agent:
    """创建 Writer Agent：生成中文技术报告（不使用工具，纯写作）"""
    return Agent(
        role="技术报告撰写专家",
        goal="生成结构清晰、内容详实的中文技术调研报告",
        backstory="""你是一位专业的技术文档撰写专家，擅长将复杂的代码分析转化为易于理解的中文报告。
你的报告结构清晰、层次分明，包含具体的数据和代码引用。
你总是使用中文撰写报告。
注意：你不需要调用任何工具，基于 Explorer 和 Analyst 的分析结果撰写报告即可。""",
        verbose=True,
        allow_delegation=False,
        tools=[],  # Writer 不需要工具，基于前两阶段输出撰写报告
        llm=get_minimax_llm(),
    )


# 为了保持向后兼容，保留类方式的接口
class ExplorerAgent:
    @staticmethod
    def create():
        return create_explorer_agent()


class AnalystAgent:
    @staticmethod
    def create():
        return create_analyst_agent()


class WriterAgent:
    @staticmethod
    def create():
        return create_writer_agent()
