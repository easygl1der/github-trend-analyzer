"""
Crew Pipeline - 编排 Explorer -> Analyst -> Writer 的执行流程
"""
import os
from datetime import datetime
from typing import List, Dict
from crew import ExplorerAgent, AnalystAgent, WriterAgent
from crew.tasks import create_explore_task, create_analyze_task, create_write_task
from config import REPORTS_DIR


class RepoAnalysisPipeline:
    """仓库分析 Pipeline"""

    def __init__(self):
        self.explorer = ExplorerAgent.create()
        self.analyst = AnalystAgent.create()
        self.writer = WriterAgent.create()

    def analyze_repo(self, repo_info: Dict) -> str:
        """
        分析单个仓库并生成报告

        Args:
            repo_info: 包含 owner, repo, full_name, description, url 等字段

        Returns:
            生成的报告文件路径
        """
        repo_full_name = repo_info.get("full_name", "unknown")
        print(f"\n{'='*60}")
        print(f"开始分析仓库: {repo_full_name}")
        print(f"{'='*60}\n")

        # Step 1: Explore - 使用 LLM 分析
        print(f"[{repo_full_name}] Step 1/3: 探索仓库结构...")
        try:
            explore_result = self.explorer.execute_task(
                task=create_explore_task(self.explorer, repo_info)
            )
        except Exception as e:
            print(f"  探索失败，使用默认描述: {e}")
            explore_result = f"仓库 {repo_full_name} 是一个 GitHub 项目，主要用于 {repo_info.get('description', '未知目的')}"

        # Step 2: Analyze - 使用 LLM 分析
        print(f"[{repo_full_name}] Step 2/3: 技术深度分析...")
        try:
            analyze_result = self.analyst.execute_task(
                task=create_analyze_task(self.analyst, repo_info, explore_result)
            )
        except Exception as e:
            print(f"  分析失败，使用默认描述: {e}")
            analyze_result = f"技术栈：{repo_info.get('language', '未知')} | Stars: {repo_info.get('stars', 0)}"

        # Step 3: Write Report - 使用 LLM 生成
        print(f"[{repo_full_name}] Step 3/3: 生成报告...")
        try:
            report_content = self.writer.execute_task(
                task=create_write_task(self.writer, repo_info, explore_result, analyze_result)
            )
        except Exception as e:
            print(f"  报告生成失败，使用模板: {e}")
            report_content = None

        # 如果 LLM 生成失败，使用模板
        if not report_content:
            report_content = f"""# {repo_full_name} 技术调研报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 基本信息

- **仓库名称**: {repo_full_name}
- **描述**: {repo_info.get('description', 'N/A')}
- **语言**: {repo_info.get('language', 'N/A')}
- **Stars**: {repo_info.get('stars', 0)}
- **URL**: {repo_info.get('url', 'N/A')}

## 探索结果

{explore_result}

## 技术分析

{analyze_result}

---
*由 GitHub Trend Analyzer 自动生成*
"""

        # 保存报告
        filename = f"{repo_full_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(REPORTS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n✓ 报告已生成: {filepath}")
        return filepath

    def analyze_multiple(self, repo_list: List[Dict]) -> List[str]:
        """
        并行分析多个仓库

        Args:
            repo_list: 仓库信息列表

        Returns:
            生成的报告文件路径列表
        """
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
