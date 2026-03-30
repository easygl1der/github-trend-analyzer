"""
GitHub API Client
封装 GitHub API 调用，用于获取仓库元信息和文件内容
"""
import requests
import base64
from typing import Dict, List, Optional
from config import GITHUB_TOKEN

HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


class GitHubClient:
    def __init__(self, token: str = GITHUB_TOKEN):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = HEADERS.copy()
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_repo_meta(self, owner: str, repo: str) -> Dict:
        """获取仓库元信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "language": data.get("language"),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "license": data.get("license", {}).get("name") if data.get("license") else None,
                "topics": data.get("topics", []),
                "created_at": data.get("created_at"),
                "pushed_at": data.get("pushed_at"),
                "homepage": data.get("homepage"),
                "url": data.get("html_url"),
            }
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_file_tree(self, owner: str, repo: str, ref: str = "main") -> List[Dict]:
        """获取仓库根目录文件列表"""
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{ref}"
        params = {"recursive": "1"}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("tree"):
                # 返回根目录文件（path 不包含 /）
                return [item for item in data["tree"] if "/" not in item["path"]][:50]
            return []
        except requests.RequestException as e:
            return [{"error": str(e)}]

    def read_file(self, owner: str, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """读取文件内容（Base64 解码）"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("content"):
                content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                return content
            return None
        except requests.RequestException as e:
            return None


# 全局客户端实例
github_client = GitHubClient()