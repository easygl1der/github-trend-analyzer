"""
GitHub Trending Fetcher
爬取 GitHub Trending 页面获取真实数据（包括今日新增 star）
"""
import requests
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

GITHUB_TRENDING_URL = "https://github.com/trending"


def fetch_trending(
    language: str = "all",
    since: str = "daily",
    limit: int = 10
) -> List[Dict]:
    """
    获取 GitHub Trending 仓库列表（从 GitHub Trending 页面爬取）

    Args:
        language: 编程语言 (e.g., "python", "javascript", "all")
        since: 时间范围 ("daily", "weekly", "monthly") — 目前页面默认就是daily
        limit: 返回数量限制

    Returns:
        仓库信息列表，包含真实的 today_stars 数据
    """
    # 构建 URL
    if language and language != "all":
        url = f"{GITHUB_TRENDING_URL}/{language}"
    else:
        url = GITHUB_TRENDING_URL

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching trending: {e}")
        return []

    repos = parse_trending_page(response.text, limit)
    return repos


def parse_trending_page(html: str, limit: int = 10) -> List[Dict]:
    """
    解析 GitHub Trending 页面 HTML，提取仓库信息

    Args:
        html: 页面 HTML 内容
        limit: 返回数量限制

    Returns:
        仓库信息列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select('article.Box-row')

    repos = []
    for article in articles[:limit]:
        repo_info = parse_repo_article(article)
        if repo_info:
            repos.append(repo_info)

    return repos


def parse_repo_article(article) -> Optional[Dict]:
    """
    解析单个仓库的 article 元素

    Args:
        article: BeautifulSoup article 元素

    Returns:
        仓库信息字典
    """
    # 获取仓库全名 (owner/repo)
    h2 = article.select_one('h2 a')
    if not h2:
        return None

    # 清理仓库名，格式: " owner / repo "
    full_name = h2.text.strip()
    # 去掉空格和斜线，得到 "owner/repo"
    full_name = re.sub(r'\s+', '', full_name)

    if '/' not in full_name:
        return None

    owner, repo_name = full_name.split('/', 1)

    # 获取描述
    description_elem = article.select_one('p')
    description = description_elem.text.strip() if description_elem else ""

    # 获取编程语言
    language_elem = article.select_one('[itemprop="programmingLanguage"]')
    language = language_elem.text.strip() if language_elem else ""

    # 获取总 star 数
    stars_text = ""
    for span in article.select('span'):
        t = span.text.strip()
        if re.match(r'[\d,]+ stars', t):
            stars_text = t
            break

    # 解析总 star 数
    stars_match = re.search(r'([\d,]+)\s*stars', stars_text)
    stars = int(stars_match.group(1).replace(',', '')) if stars_match else 0

    # 获取今日新增 star
    today_stars = 0
    for span in article.select('span'):
        t = span.text.strip()
        if 'stars today' in t:
            match = re.search(r'([\d,]+)\s*stars today', t)
            if match:
                today_stars = int(match.group(1).replace(',', ''))
            break

    # 获取 fork 数
    forks = 0
    for a in article.select('a'):
        href = a.get('href', '')
        if href.endswith('/forks'):
            fork_text = a.text.strip()
            match = re.search(r'([\d,]+)', fork_text)
            if match:
                forks = int(match.group(1).replace(',', ''))
            break

    # 获取 URL
    url = f"https://github.com/{full_name}"

    return {
        "owner": owner,
        "repo": repo_name,
        "full_name": full_name,
        "description": description,
        "language": language,
        "stars": stars,
        "forks": forks,
        "today_stars": today_stars,
        "url": url,
    }


def parse_trending_repo(repo_data: Dict) -> Dict:
    """解析仓库数据，提取关键信息（兼容旧接口）"""
    return {
        "owner": repo_data.get("owner", ""),
        "repo": repo_data.get("repo", ""),
        "full_name": repo_data.get("full_name", ""),
        "description": repo_data.get("description", ""),
        "language": repo_data.get("language", ""),
        "stars": repo_data.get("stars", 0),
        "forks": repo_data.get("forks", 0),
        "today_stars": repo_data.get("today_stars", 0),
        "url": repo_data.get("url", ""),
    }


if __name__ == "__main__":
    # 测试
    repos = fetch_trending(language="python", limit=5)
    for r in repos:
        print(f"{r['full_name']} | ⭐{r['stars']} | +{r['today_stars']}/今天 | {r['language']}")
