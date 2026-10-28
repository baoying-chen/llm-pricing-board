#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性初始化：把定价站点部署到 GitHub Pages（业务隔离 / 免连接器授权 / 链接固定）。

用法：
  python setup_github.py --pat <你的PAT> --repo <仓库名> [--user <登录名>] [--private]

做了什么：
  1. 用 PAT 调 GitHub API 创建仓库（若已存在则跳过）
  2. 把 PAT / owner / repo 写入本地 .deploy_env（已被 .gitignore 忽略，不会进仓库）
  3. 配置 git remote origin（含 PAT，便于推送）
  4. 推送当前 main 分支
  5. 开启 GitHub Pages（main 分支 / 根目录）
  6. 打印固定外网链接

说明：
  - PAT 需具备 repo 权限（classic token 勾 repo；fine-grained 勾 仓库的 Contents+Pages）
  - 固定链接形如 https://<owner>.github.io/<repo>/
  - 之后每周自动更新只需 deploy_site.py，凭据从 .deploy_env 读取，无需再登录
"""
import argparse
import json
import subprocess
import sys
import os
import urllib.request
import urllib.error

API = "https://api.github.com"


def api(method, path, pat, data=None):
    url = API + path
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + pat)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "pricing-deploy")
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8")
            return r.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        try:
            msg = json.loads(body).get("message", body)
        except Exception:
            msg = body
        return e.code, {"message": msg}


def run(cmd):
    print(">>", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print(out.strip())
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pat", required=True, help="GitHub Personal Access Token（需 repo 权限）")
    p.add_argument("--repo", required=True, help="仓库名，如 llm-pricing-board")
    p.add_argument("--user", default=None, help="GitHub 登录名（不填则自动获取）")
    p.add_argument("--private", action="store_true", help="创建为私有仓库（Pages 仍可用）")
    p.add_argument("--desc", default="国内外主流大模型 API 定价对比（含折扣）", help="仓库描述")
    args = p.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    # 0) 获取登录名
    owner = args.user
    if not owner:
        st, j = api("GET", "/user", args.pat)
        if st != 200:
            sys.exit("✗ 获取 GitHub 用户失败（PAT 可能无效）：" + str(j.get("message")))
        owner = j.get("login")
        if not owner:
            sys.exit("✗ 无法解析 GitHub 登录名：" + str(j))
    print("GitHub 登录名：", owner)

    # 1) 创建仓库（已存在则忽略）
    st, j = api("POST", "/user/repos", args.pat, {
        "name": args.repo,
        "private": bool(args.private),
        "description": args.desc,
        "auto_init": False,
        "has_issues": False,
        "has_wiki": False,
    })
    if st == 201:
        print("✓ 已创建仓库：", j.get("full_name"))
    elif st == 422 and "name already exists" in str(j.get("message", "")).lower():
        print("· 仓库已存在，继续。")
    elif st == 200:
        print("· 仓库已存在，继续。")
    else:
        sys.exit("✗ 创建仓库失败（%d）：%s" % (st, j.get("message")))

    # 2) 写 .deploy_env（gitignored）
    with open(".deploy_env", "w", encoding="utf-8") as f:
        f.write("OWNER=%s\n" % owner)
        f.write("REPO=%s\n" % args.repo)
        f.write("PAT=%s\n" % args.pat)
    print("✓ 凭据已写入 .deploy_env（已 gitignore，不会进入仓库）")

    # 3) 配置 remote
    remote_url = "https://%s@github.com/%s/%s.git" % (args.pat, owner, args.repo)
    run(["git", "remote", "remove", "origin"])
    run(["git", "remote", "add", "origin", remote_url])

    # 4) 推送
    pr = run(["git", "push", "-u", "origin", "main"])
    if pr.returncode != 0:
        sys.exit("✗ 推送失败，请检查 PAT 权限与网络。")

    # 5) 开启 Pages
    st, j = api("POST", "/repos/%s/%s/pages" % (owner, args.repo), args.pat,
                {"source": {"branch": "main", "path": "/"}})
    if st in (201, 200):
        print("✓ GitHub Pages 已开启")
    elif st == 409 and "already enabled" in str(j.get("message", "")).lower():
        print("· GitHub Pages 已开启")
    else:
        print("! 开启 Pages 返回 (%d)：%s —— 可稍后在仓库 Settings → Pages 手动开启" % (st, j.get("message")))

    url = "https://%s.github.io/%s/" % (owner, args.repo)
    print("\n🎉 部署完成！固定外网链接：")
    print("   " + url)
    print("   首次生效通常需 1–2 分钟；之后每周自动更新只推送 prices.json，链接不变。")


if __name__ == "__main__":
    main()
