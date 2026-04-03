#!/usr/bin/env python3
"""
Parallel GitHub Repo Analysis Script
Runs 5 repo analyses in parallel using CrewAI pipeline
"""
import os
import sys
import shutil
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crew.pipeline import RepoAnalysisPipeline
from github_client import GitHubClient

# Garden paths
GARDEN_DIR = "/Users/yueyh/Projects/github-trend-garden/content/trending/2026-04-03"
REPORTS_DIR = "/Users/yueyh/Projects/github-trend-analyzer/reports"

# Repos to analyze
REPOS = [
    {"full_name": "AIFrontierLab/TorchUMM", "stars": 16},
    {"full_name": "kenrury/polymarket-market-making-bot", "stars": 15},
    {"full_name": "bartei/wiregui", "stars": 6},
    {"full_name": "ZenmoFeiShi/dm-gateway-bot", "stars": 5},
    {"full_name": "wuyan124/Rocokingdom-AutoCoin", "stars": 5},
]

MIN_SIZE_KB = 5
TARGET_SIZE_KB = 10


def get_repo_info(full_name: str, stars: int) -> dict:
    """Get repo info from GitHub"""
    client = GitHubClient()
    owner, repo = full_name.split("/")
    meta = client.get_repo_meta(owner, repo)

    return {
        "full_name": full_name,
        "description": meta.get("description", ""),
        "url": meta.get("url", f"https://github.com/{full_name}"),
        "language": meta.get("language", ""),
        "stars": stars,
    }


def analyze_single_repo(repo_info: dict, max_retries: int = 2) -> tuple:
    """Analyze a single repo and return (repo_name, report_path, success)"""
    repo_name = repo_info["full_name"]
    pipeline = RepoAnalysisPipeline()

    for attempt in range(max_retries + 1):
        try:
            print(f"\n{'='*60}")
            print(f"[{repo_name}] Starting analysis (attempt {attempt + 1})")
            print(f"{'='*60}")

            report_path = pipeline.analyze_repo(repo_info)

            # Check file size
            file_size = os.path.getsize(report_path)
            file_size_kb = file_size / 1024

            print(f"\n[{repo_name}] Report size: {file_size_kb:.1f} KB")

            if file_size_kb < MIN_SIZE_KB:
                print(f"[{repo_name}] WARNING: Report too small ({file_size_kb:.1f} KB < {MIN_SIZE_KB} KB)")
                if attempt < max_retries:
                    print(f"[{repo_name}] Regenerating...")
                    time.sleep(5)
                    continue
                else:
                    print(f"[{repo_name}] Max retries reached, keeping small report")

            return (repo_name, report_path, True, file_size_kb)

        except Exception as e:
            print(f"[{repo_name}] ERROR: {e}")
            if attempt < max_retries:
                time.sleep(5)
            else:
                return (repo_name, None, False, 0)

    return (repo_name, None, False, 0)


def copy_to_garden(report_path: str) -> bool:
    """Copy report to garden directory"""
    if not report_path or not os.path.exists(report_path):
        return False

    try:
        filename = os.path.basename(report_path)
        dest_path = os.path.join(GARDEN_DIR, filename)
        shutil.copy2(report_path, dest_path)
        print(f"Copied {filename} to garden")
        return True
    except Exception as e:
        print(f"Failed to copy to garden: {e}")
        return False


def main():
    print("="*60)
    print("GitHub Trending Repo Analysis - Parallel Execution")
    print("="*60)

    # Ensure garden directory exists
    os.makedirs(GARDEN_DIR, exist_ok=True)

    # Get repo info for all repos
    print("\nFetching repo metadata...")
    repo_infos = []
    for repo in REPOS:
        info = get_repo_info(repo["full_name"], repo["stars"])
        repo_infos.append(info)
        print(f"  {info['full_name']}: {info.get('language', 'N/A')}")

    # Analyze all repos in parallel
    print(f"\nStarting parallel analysis of {len(repo_infos)} repos...")

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(analyze_single_repo, repo_info): repo_info
            for repo_info in repo_infos
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    all_success = True
    for repo_name, report_path, success, size_kb in results:
        status = "OK" if success else "FAILED"
        size_str = f"{size_kb:.1f} KB" if success else "N/A"
        print(f"  [{status}] {repo_name}: {size_str}")

        if success and report_path:
            copy_to_garden(report_path)
        else:
            all_success = False

    # Final status
    print("\n" + "="*60)
    if all_success:
        print("All analyses completed successfully!")
    else:
        print("Some analyses failed or produced small reports.")
    print("="*60)

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
