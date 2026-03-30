"""
Crew Pipeline - 编排 Explorer -> Analyst -> Writer 的执行流程
使用 MiniMax API 直接调用实现
"""
import os
import requests
from datetime import datetime
from typing import List, Dict
from config import REPORTS_DIR

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"


def call_minimax(prompt: str, system_prompt: str = "") -> str:
    """直接调用 MiniMax API"""
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "MiniMax-Text-01",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            f"{MINIMAX_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  LLM API 调用失败: {e}")
        return ""


class RepoAnalysisPipeline:
    """仓库分析 Pipeline"""

    def __init__(self):
        pass

    def analyze_repo(self, repo_info: Dict) -> str:
        """
        分析单个仓库并生成报告
        """
        repo_full_name = repo_info.get("full_name", "unknown")
        repo_description = repo_info.get("description", "")
        repo_url = repo_info.get("url", "")
        repo_language = repo_info.get("language", "")
        repo_stars = repo_info.get("stars", 0)

        print(f"\n{'='*60}")
        print(f"开始分析仓库: {repo_full_name}")
        print(f"{'='*60}\n")

        # Step 1: Explore
        print(f"[{repo_full_name}] Step 1/3: 探索仓库结构...")
        explore_prompt = f"""分析以下 GitHub 仓库：

仓库：{repo_full_name}
描述：{repo_description}
语言：{repo_language}
Stars：{repo_stars}

请分析：
1. 项目类型和目的
2. 核心技术栈
3. 主要功能特性
4. 值得关注的地方

用中文回答，简明扼要。"""
        explore_result = call_minimax(explore_prompt)
        if not explore_result:
            explore_result = f"仓库 {repo_full_name} 是一个 {repo_language} 项目，描述为：{repo_description}"
        print(f"  ✓ 探索完成")

        # Step 2: Analyze
        print(f"[{repo_full_name}] Step 2/3: 技术深度分析...")
        analyze_prompt = f"""对以下 GitHub 仓库进行技术深度分析：

仓库：{repo_full_name}
描述：{repo_description}
语言：{repo_language}
Stars：{repo_stars}
探索结果：{explore_result}

请分析：
1. 技术架构和设计模式
2. 依赖和生态系统
3. 代码质量和可维护性
4. 性能和安全考虑
5. 优缺点总结

用中文回答，结构清晰。"""
        analyze_result = call_minimax(analyze_prompt)
        if not analyze_result:
            analyze_result = f"技术栈：{repo_language} | Stars: {repo_stars} | 这是一个值得关注的项目"
        print(f"  ✓ 分析完成")

        # Step 3: Write Report
        print(f"[{repo_full_name}] Step 3/3: 生成报告...")
        report_prompt = f"""基于以下分析，为 GitHub 仓库生成一份完整的中文技术调研报告：

# 仓库信息
- 名称：{repo_full_name}
- 描述：{repo_description}
- 语言：{repo_language}
- Stars：{repo_stars}
- URL：{repo_url}

# 探索分析
{explore_result}

# 技术分析
{analyze_result}

请生成一份完整的 Markdown 格式报告，包含：
1. 项目简介
2. 技术架构
3. 核心功能
4. 使用场景
5. 优缺点分析
6. 总结与建议

报告用中文撰写，结构清晰。"""
        report_content = call_minimax(report_prompt)
        if not report_content:
            report_content = f"""# {repo_full_name} 技术调研报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 基本信息

- **仓库名称**: {repo_full_name}
- **描述**: {repo_description}
- **语言**: {repo_language}
- **Stars**: {repo_stars}
- **URL**: {repo_url}

## 项目简介

{explore_result}

## 技术分析

{analyze_result}

---
*由 GitHub Trend Analyzer 自动生成*
"""
        print(f"  ✓ 报告生成完成")

        # 保存报告
        filename = f"{repo_full_name.replace('/', '_')}.md"
        filepath = os.path.join(REPORTS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n✓ 报告已生成: {filepath}")
        return filepath

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
