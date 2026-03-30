"""
CrewAI Agents 定义
"""
import os
from crewai import Agent
from crewai.llm import LLM

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"


def get_minimax_llm(model: str = "MiniMax-Embedding"):
    """创建 MiniMax LLM 实例"""
    return LLM(
        model=model,
        base_url=MINIMAX_BASE_URL,
        api_key=MINIMAX_API_KEY,
    )


class ExplorerAgent:
    """Explorer Agent: 分析仓库结构"""

    @staticmethod
    def create():
        return Agent(
            role="仓库结构分析师",
            goal="深入分析 GitHub 仓库的文件结构、README 和核心配置文件",
            backstory="""你是一位经验丰富的技术架构师，擅长通过分析项目结构和配置文件来快速理解一个代码仓库。
            你会仔细查看 README.md、LICENSE、package.json、requirements.txt、Dockerfile 等关键文件，
            并提供对项目整体架构和目的的准确判断。""",
            verbose=True,
            allow_delegation=False,
            llm=get_minimax_llm("MiniMax-Text-01"),
        )


class AnalystAgent:
    """Analyst Agent: 评估技术栈和代码质量"""

    @staticmethod
    def create():
        return Agent(
            role="技术深度分析师",
            goal="评估仓库的技术栈、代码质量、依赖复杂度和可运行性",
            backstory="""你是一位资深的软件工程师，对各种编程语言、框架和工具链都有深入了解。
            你能够快速识别项目使用的核心技术栈，评估依赖的复杂度，并判断项目是否可以直接运行。
            你的分析客观准确，善于发现潜在的技术亮点和问题。""",
            verbose=True,
            allow_delegation=False,
            llm=get_minimax_llm("MiniMax-Text-01"),
        )


class WriterAgent:
    """Writer Agent: 生成中文技术报告"""

    @staticmethod
    def create():
        return Agent(
            role="技术报告撰写专家",
            goal="生成结构清晰、内容详实的中文技术调研报告",
            backstory="""你是一位专业的技术文档工程师，擅长将复杂的代码分析结果转化为易读的中文报告。
            你的报告不仅准确描述技术细节，还会提供独到的见解和实用的建议。
            你熟悉各种技术领域的术语，能够用简洁明了的语言解释复杂概念。""",
            verbose=True,
            allow_delegation=False,
            llm=get_minimax_llm("MiniMax-Text-01"),
        )
