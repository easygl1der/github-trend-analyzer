"""
Crew Pipeline - 使用 CrewAI 编排 Explorer -> Analyst -> Writer 的执行流程
"""
import os
from datetime import datetime
from typing import List, Dict

from crewai import Agent, Crew, Process

from .agents import create_explorer_agent, create_analyst_agent, create_writer_agent
from .tasks import create_explore_task, create_analyze_task, create_write_task
from config import REPORTS_DIR


class RepoAnalysisPipeline:
    """仓库分析 Pipeline - 使用 CrewAI 编排多 Agent 协作"""

    def __init__(self):
        self.explorer = create_explorer_agent()
        self.analyst = create_analyst_agent()
        self.writer = create_writer_agent()

    def analyze_repo(self, repo_info: Dict) -> str:
        """
        使用 CrewAI 分析单个仓库并生成报告

        Args:
            repo_info: 仓库信息字典，包含 full_name, description, url, language, stars 等

        Returns:
            生成的报告文件路径
        """
        repo_full_name = repo_info.get("full_name", "unknown")
        repo_owner = repo_info.get("owner", "")
        repo_name = repo_info.get("repo", "")
        repo_description = repo_info.get("description", "")
        repo_url = repo_info.get("url", "")
        repo_language = repo_info.get("language", "")
        repo_stars = repo_info.get("stars", 0)
        repo_today_stars = repo_info.get("today_stars", 0)

        print(f"\n{'='*60}")
        print(f"CrewAI 开始分析仓库: {repo_full_name} (+{repo_today_stars} stars today)")
        print(f"{'='*60}\n")

        # 创建任务
        # 注意：Explorer 任务先执行，Analyst 依赖 Explorer 结果，Writer 依赖两者结果
        explore_task = create_explore_task(
            agent=self.explorer,
            repo_info=repo_info
        )

        analyze_task = create_analyze_task(
            agent=self.analyst,
            repo_info=repo_info,
            explore_result=""  # 初始为空，CrewAI 会自动处理任务间数据传递
        )

        write_task = create_write_task(
            agent=self.writer,
            repo_info=repo_info,
            explore_result="",  # 初始为空
            analyze_result=""   # 初始为空
        )

        # 创建 Crew 并执行
        # process=Process.sequential 表示顺序执行，任务间自动传递上下文
        crew = Crew(
            agents=[self.explorer, self.analyst, self.writer],
            tasks=[explore_task, analyze_task, write_task],
            process=Process.sequential,
            verbose=True,
        )

        # 执行 Crew
        result = crew.kickoff(inputs={
            "repo_info": repo_info,
            "repo_full_name": repo_full_name,
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "repo_description": repo_description,
            "repo_url": repo_url,
            "repo_language": repo_language,
            "repo_stars": repo_stars,
            "repo_today_stars": repo_today_stars,
        })

        # 从结果中提取报告内容
        # CrewAI 的 kickoff 返回的是最终任务的结果
        report_content = self._extract_report(result, repo_info)

        # 保存报告，文件名只使用仓库名（不含 owner）
        repo_name = repo_info.get("repo", repo_full_name.split('/')[-1])
        filename = f"{repo_name}.md"
        filepath = os.path.join(REPORTS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n✓ 报告已生成: {filepath}")
        return filepath

    def _extract_report(self, crew_result, repo_info: Dict) -> str:
        """从 Crew 执行结果中提取报告内容"""
        repo_full_name = repo_info.get("full_name", "unknown")
        repo_owner = repo_info.get("owner", "")
        repo_name = repo_info.get("repo", "")
        repo_description = repo_info.get("description", "")
        repo_url = repo_info.get("url", "")
        repo_language = repo_info.get("language", "")
        repo_stars = repo_info.get("stars", 0)
        repo_today_stars = repo_info.get("today_stars", 0)

        # 如果有有效结果，尝试解析
        if crew_result:
            result_str = str(crew_result)
            # 检查是否包含报告结构
            if "# " in result_str and ("技术调研报告" in result_str or "技术分析" in result_str):
                return result_str

        # 回退到默认报告格式
        return f"""# {repo_name} 技术调研报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 作者: @{repo_owner} | 今日新增: ⭐+{repo_today_stars} | 总计: ⭐{repo_stars}
> 分析引擎: CrewAI Multi-Agent

## 基本信息

- **仓库名称**: {repo_name}
- **作者**: @{repo_owner}
- **描述**: {repo_description}
- **语言**: {repo_language}
- **总 Stars**: {repo_stars}
- **今日新增**: ⭐+{repo_today_stars}
- **URL**: {repo_url}

## 分析说明

此报告由 CrewAI 多智能体系统自动生成。
Explorer Agent 负责分析仓库结构，Analyst Agent 负责技术深度分析，Writer Agent 负责撰写报告。

---
*由 GitHub Trend Analyzer + CrewAI 自动生成*
"""

    def analyze_multiple(self, repo_list: List[Dict]) -> List[str]:
        """并行分析多个仓库"""
        results = []
        for repo in repo_list:
            try:
                report_path = self.analyze_repo(repo)
                results.append(report_path)
            except Exception as e:
                print(f"分析仓库 {repo.get('full_name', 'unknown')} 时出错: {e}")
        return results


# 便捷函数
def analyze_repo(repo_info: Dict) -> str:
    """分析单个仓库"""
    pipeline = RepoAnalysisPipeline()
    return pipeline.analyze_repo(repo_info)


def analyze_trending(trending_list: List[Dict]) -> List[str]:
    """分析 Trending 仓库列表"""
    pipeline = RepoAnalysisPipeline()
    return pipeline.analyze_multiple(trending_list)
