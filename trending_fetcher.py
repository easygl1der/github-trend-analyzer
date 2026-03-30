"""
GitHub Trending API Fetcher
使用 GitHub API 直接获取 Trending 仓库
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import API_BASE_URL, GITHUB_TOKEN

# GitHub API 配置
GITHUB_API_URL = "https://api.github.com"


def fetch_trending(
    language: str = "all",
    since: str = "daily",
    limit: int = 10
) -> List[Dict]:
    """
    获取 GitHub Trending 仓库列表

    Args:
        language: 编程语言 (e.g., "python", "javascript", "all")
        since: 时间范围 ("daily", "weekly", "monthly")
        limit: 返回数量限制

    Returns:
        仓库信息列表
    """
    # 计算时间范围
    date_range = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30
    }.get(since, 1)

    created_date = (datetime.now() - timedelta(days=date_range)).strftime("%Y-%m-%d")

    # 构建查询
    language_query = f"language:{language}" if language != "all" else ""
    query = f"created:>{created_date} {language_query}".strip()

    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": min(limit, 100)
    }

    try:
        response = requests.get(
            f"{GITHUB_API_URL}/search/repositories",
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        repos = []
        for item in data.get("items", [])[:limit]:
            repos.append({
                "owner": item.get("owner", {}).get("login", ""),
                "name": item.get("name", ""),
                "full_name": item.get("full_name", ""),
                "description": item.get("description", ""),
                "language": item.get("language", ""),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "today_stars": 0,  # GitHub API 不提供当日星星数
                "url": item.get("html_url", ""),
            })
        return repos
    except requests.RequestException as e:
        print(f"Error fetching trending: {e}")
        return []


def parse_trending_repo(repo_data: Dict) -> Dict:
    """解析仓库数据，提取关键信息"""
    return {
        "owner": repo_data.get("owner", ""),
        "repo": repo_data.get("name", ""),
        "full_name": repo_data.get("full_name", ""),
        "description": repo_data.get("description", ""),
        "language": repo_data.get("language", ""),
        "stars": repo_data.get("stars", 0),
        "forks": repo_data.get("forks", 0),
        "today_stars": repo_data.get("today_stars", 0),
        "url": repo_data.get("url", ""),
    }