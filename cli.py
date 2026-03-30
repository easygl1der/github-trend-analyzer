#!/usr/bin/env python3
"""
GitHub Trend Analyzer CLI
命令行入口，支持 trending 和 analyze 两个子命令
"""
import argparse
import sys
import os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trending_fetcher import fetch_trending, parse_trending_repo
from crew.pipeline import analyze_trending, analyze_repo
from auto_publish import publish_reports


def cmd_trending(args):
    """获取并分析 GitHub Trending 仓库"""
    print(f"\n{'='*60}")
    print(f"GitHub Trending 分析")
    print(f"{'='*60}")
    print(f"语言: {args.language}")
    print(f"时间范围: {args.since}")
    print(f"数量限制: {args.limit}")
    print(f"{'='*60}\n")

    # Step 1: 获取 Trending 列表
    print("[1/3] 获取 GitHub Trending 列表...")
    raw_repos = fetch_trending(
        language=args.language,
        since=args.since,
        limit=args.limit
    )

    if not raw_repos:
        print("获取 Trending 列表失败，请检查 Docker 服务是否运行")
        return 1

    repos = [parse_trending_repo(r) for r in raw_repos]
    print(f"✓ 成功获取 {len(repos)} 个热门仓库\n")

    # Step 2: 分析每个仓库
    print("[2/3] 开始分析仓库...")
    report_files = analyze_trending(repos)
    print(f"✓ 生成了 {len(report_files)} 份报告\n")

    # Step 3: 可选：发布到 Garden
    if args.publish:
        print("[3/3] 发布报告到 Digital Garden...")
        try:
            publish_reports()
            print("✓ 报告已发布到 GitHub Trend Garden")
        except Exception as e:
            print(f"⚠ 发布失败: {e}")
            print("  报告仍保存在本地 reports/ 目录")

    return 0


def cmd_analyze(args):
    """分析指定仓库"""
    owner, repo = args.repo.split("/")
    repo_info = {
        "owner": owner,
        "repo": repo,
        "full_name": args.repo,
        "description": args.description or f"GitHub 仓库 {args.repo}",
        "language": args.language or "Unknown",
        "stars": 0,
        "forks": 0,
        "today_stars": 0,
        "url": f"https://github.com/{args.repo}",
    }

    print(f"\n{'='*60}")
    print(f"分析仓库: {args.repo}")
    print(f"{'='*60}\n")

    report_file = analyze_repo(repo_info)

    if args.publish:
        print("\n发布到 Digital Garden...")
        try:
            publish_reports()
            print("✓ 报告已发布")
        except Exception as e:
            print(f"⚠ 发布失败: {e}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Trend Analyzer - AI 驱动的 GitHub Trending 分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # trending 子命令
    trending_parser = subparsers.add_parser(
        "trending",
        help="获取并分析 GitHub Trending 仓库"
    )
    trending_parser.add_argument(
        "--language", "-l",
        default="all",
        help="编程语言 (python, javascript, all 等)"
    )
    trending_parser.add_argument(
        "--since", "-s",
        default="daily",
        choices=["daily", "weekly", "monthly"],
        help="时间范围"
    )
    trending_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="分析仓库数量"
    )
    trending_parser.add_argument(
        "--publish", "-p",
        action="store_true",
        help="分析完成后自动发布到 Digital Garden"
    )
    trending_parser.set_defaults(func=cmd_trending)

    # analyze 子命令
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="分析指定 GitHub 仓库"
    )
    analyze_parser.add_argument(
        "repo",
        help="仓库名 (格式: owner/repo)"
    )
    analyze_parser.add_argument(
        "--description", "-d",
        help="仓库描述"
    )
    analyze_parser.add_argument(
        "--language",
        help="主要编程语言"
    )
    analyze_parser.add_argument(
        "--publish", "-p",
        action="store_true",
        help="分析完成后自动发布到 Digital Garden"
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
