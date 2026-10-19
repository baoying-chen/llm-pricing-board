#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署脚本：将静态站点（index.html + prices.json）推送到 GitHub Pages 独立仓库。
- 业务隔离：专属仓库，与任何云账号业务无关
- 固定链接：推送到【同一个仓库/分支】，GitHub Pages URL 永久不变
- 纯免授权：使用 git + PAT，不依赖任何连接器

用法：
  python deploy_site.py            # 提交并推送到 origin 当前分支
  python deploy_site.py --init     # 首次：git init -b main + 初始提交（remote 需自行配置）
依赖：git 在 PATH 中，且已配置 remote `origin`（含 PAT 的 URL 或凭据助手）。
"""
import subprocess
import sys
import os
import datetime


def run(cmd, check=True, allow_fail=False):
    print(">>", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print(out.strip())
    if r.returncode != 0 and (check and not allow_fail):
        sys.exit("命令失败: " + " ".join(cmd))
    return r


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    init = "--init" in sys.argv

    # 若本地存在 .deploy_env（由 setup_github.py 写入，含 PAT/owner/repo），
    # 则临时把 remote 设为带 PAT 的 URL，便于无交互推送；不写死到 git config 之外。
    envf = os.path.join(here, ".deploy_env")
    if os.path.exists(envf):
        cfg = {}
        for line in open(envf, encoding="utf-8"):
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k] = v
        if cfg.get("PAT") and cfg.get("OWNER") and cfg.get("REPO"):
            url = "https://%s@github.com/%s/%s.git" % (cfg["PAT"], cfg["OWNER"], cfg["REPO"])
            run(["git", "remote", "set-url", "origin", url], check=False, allow_fail=True)
            print(">> 已从 .deploy_env 载入部署凭据")

    if init:
        run(["git", "init", "-b", "main"], allow_fail=True)
        # 确保只跟踪站点所需文件 + 构建脚本（便于追溯），忽略临时产物
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write("__pycache__/\n*.pyc\nupdates_*.json\n.DS_Store\n")
        run(["git", "add", "index.html", "prices.json", "README.md",
             "build_discount.py", "build_excel.py", "apply_prices.py",
             "vendor_sources.json", "deploy_site.py", ".gitignore"])
        run(["git", "commit", "-m", "init pricing site"], allow_fail=True)
        print("已初始化仓库。请执行：")
        print('  git remote add origin https://<PAT>@github.com/<user>/<repo>.git')
        print("  python deploy_site.py")
        return

    # 1) 暂存所有变更（主要是 prices.json / index.html / llm_pricing.csv / .xlsx）
    run(["git", "add", "-A"])

    # 2) 有改动才提交
    st = run(["git", "status", "--porcelain"], check=False, allow_fail=True)
    if not st.stdout.strip():
        print("无变更，跳过提交。")
    else:
        today = datetime.date.today().isoformat()
        run(["git", "commit", "-m", f"auto update pricing {today}"],
            check=False, allow_fail=True)

    # 3) 推送到当前分支（原地更新 → URL 固定）
    branch = run(["git", "branch", "--show-current"], check=False, allow_fail=True)
    branch = branch.stdout.strip() or "main"
    pr = run(["git", "push", "origin", branch], check=False, allow_fail=True)
    if pr.returncode != 0:
        sys.exit(
            "✗ 推送失败：未配置 remote `origin` 或凭据无效。\n"
            "  请先执行：git remote add origin https://<PAT>@github.com/<user>/<repo>.git\n"
            "  然后重跑：python deploy_site.py"
        )
    print("✓ 部署完成：推送到 origin/%s（GitHub Pages URL 不变）" % branch)


if __name__ == "__main__":
    main()
