"""
Auto Publish - 将报告推送到 GitHub Trend Garden
"""
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

# Mintlify 文档仓库路径 (相对于当前项目)
GARDEN_PATH = os.environ.get(
    "GARDEN_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mintlify-docs")
)
CONTENT_PATH = os.path.join(GARDEN_PATH, "trending")


def publish_reports(reports_dir: str = None) -> list:
    """
    将 reports 目录下的所有 Markdown 报告复制到 garden 并提交

    Args:
        reports_dir: 报告目录路径，默认使用 config 中的 REPORTS_DIR

    Returns:
        已发布的文件名列表
    """
    if reports_dir is None:
        from config import REPORTS_DIR
        reports_dir = REPORTS_DIR

    today = date.today().isoformat()

    # 检查 garden 目录是否存在
    if not os.path.exists(GARDEN_PATH):
        raise FileNotFoundError(
            f"Garden 仓库不存在: {GARDEN_PATH}\n"
            "请先创建 github-trend-garden 仓库并克隆到同级目录\n"
            "参考: https://github.com/jackyzha0/quartz"
        )

    # 确保 content/trending/{date} 目录存在
    date_folder = Path(CONTENT_PATH) / today
    os.makedirs(date_folder, exist_ok=True)

    # 查找所有 markdown 报告
    published = []
    for md_file in Path(reports_dir).glob("*.md"):
        # 文件名直接使用仓库名（如 sherlock.md），复制到目标目录
        dest = date_folder / md_file.name
        shutil.copy2(md_file, dest)
        published.append(str(dest.relative_to(GARDEN_PATH)))
        print(f"  复制: {md_file.name} -> {dest.relative_to(GARDEN_PATH)}")

    if not published:
        print("没有找到需要发布的报告")
        return []

    # Git 操作
    print(f"\n提交到 Mintlify...")

    # Check git status first
    result = subprocess.run(
        ["git", "-C", GARDEN_PATH, "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    if not result.stdout.strip():
        print("没有新变化，跳过提交")
        return published

    # Add changes
    subprocess.run(
        ["git", "-C", GARDEN_PATH, "add", "."],
        check=True
    )

    # Commit
    commit_msg = f"🌱 {today} 每日趋势报告"
    subprocess.run(
        ["git", "-C", GARDEN_PATH, "commit", "-m", commit_msg],
        check=True
    )
    print(f"  提交: {commit_msg}")

    # Push
    try:
        subprocess.run(
            ["git", "-C", GARDEN_PATH, "push"],
            check=True,
            timeout=60
        )
        print("  推送成功!")
    except subprocess.TimeoutExpired:
        print("  ⚠ 推送超时，请手动检查网络连接")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ 推送失败: {e}")
        print("  报告仍已提交到本地 Git，请手动推送")

    return published


if __name__ == "__main__":
    print("GitHub Trend Garden 自动发布工具\n")
    from config import REPORTS_DIR
    try:
        published = publish_reports(REPORTS_DIR)
        if published:
            print(f"\n✓ 成功发布 {len(published)} 份报告到 Garden")
        else:
            print("\n没有找到新报告")
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        print("\n操作步骤:")
        print("1. 访问 https://github.com/jackyzha0/quartz")
        print("2. 点击 'Use this template' 创建新仓库")
        print("3. 克隆到本地，与 github-trend-analyzer 同级目录")
        print("4. 确保仓库名为 github-trend-garden")
