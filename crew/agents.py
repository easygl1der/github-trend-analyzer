"""
CrewAI Agents 定义
"""
import os
from crewai import Agent
from crewai.llm import LLM

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"


def get_minimax_llm(model: str = "MiniMax-Text-01"):
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
            verbose=True,
            allow_delegation=False,
            llm=get_minimax_llm(),
        )


class AnalystAgent:
    """Analyst Agent: 评估技术栈和代码质量"""

    @staticmethod
    def create():
        return Agent(
            role="技术深度分析师",
            goal="评估仓库的技术栈、代码质量、依赖复杂度和可运行性",
            verbose=True,
            allow_delegation=False,
            llm=get_minimax_llm(),
        )


class WriterAgent:
    """Writer Agent: 生成中文技术报告"""

    @staticmethod
    def create():
        return Agent(
            role="技术报告撰写专家",
            goal="生成结构清晰、内容详实的中文技术调研报告",
            verbose=True,
            allow_delegation=False,
            llm=get_minimax_llm(),
        )
