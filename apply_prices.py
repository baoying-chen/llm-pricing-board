# -*- coding: utf-8 -*-
"""
把自动化抓取得到的最新基础价合并进 llm_pricing.csv。
输入 JSON 结构（argv[1]，默认 updates.json）：
{
  "updates": [
    {"vendor":"...","model":"...","context":"...","max_output":"...",
     "input":"...","output":"...","cache":"...","currency":"¥|$(可选)"},
    ...
  ]
}
- 按 (厂商, 模型) 匹配：已存在则更新 上下文/最大输出/输入/输出/缓存；不存在则追加新行。
- 折扣 / 折后 列由后续 build_discount.py 统一重算，本脚本不碰。
- 输出变更摘要到 stdout，供自动化汇报。
"""
import csv, json, os, sys

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, "llm_pricing.csv")
UPDATES_PATH = os.path.join(HERE, sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "updates.json")

COLS = ["厂商", "模型", "偏向能力", "计费方式", "上下文长度", "最大输出Token",
        "输入单价", "输出单价", "缓存命中单价", "折扣", "折后输入单价",
        "折后输出单价", "币种", "数据来源"]

OVERSEAS = {"DeepSeek", "Anthropic Claude", "Google Gemini", "OpenAI", "xAI Grok"}

def main():
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    key2row = {(r["厂商"], r["模型"]): r for r in rows}

    with open(UPDATES_PATH, encoding="utf-8") as f:
        payload = json.load(f)
    updates = payload.get("updates", [])

    changed, added = [], []
    for u in updates:
        vendor = (u.get("vendor") or "").strip()
        model = (u.get("model") or "").strip()
        if not vendor or not model:
            continue
        cur = u.get("currency") or ("$" if vendor in OVERSEAS else "¥")
        rec = {
            "context": u.get("context", ""),
            "max_output": u.get("max_output", ""),
            "input": u.get("input", ""),
            "output": u.get("output", ""),
            "cache": u.get("cache", ""),
        }
        k = (vendor, model)
        if k in key2row:
            r = key2row[k]
            diffs = []
            for fld, key in [("上下文长度", "context"), ("最大输出Token", "max_output"),
                             ("输入单价", "input"), ("输出单价", "output"), ("缓存命中单价", "cache")]:
                nv = str(rec[key]).strip()
                if r.get(fld, "") != nv:
                    diffs.append("%s: %s→%s" % (fld, r.get(fld, ""), nv))
                    r[fld] = nv
            r["币种"] = cur
            if diffs:
                changed.append((vendor, model, diffs))
        else:
            new = {c: "" for c in COLS}
            new["厂商"] = vendor
            new["模型"] = model
            new["计费方式"] = "按量计费"
            new["上下文长度"] = rec["context"]
            new["最大输出Token"] = rec["max_output"]
            new["输入单价"] = rec["input"]
            new["输出单价"] = rec["output"]
            new["缓存命中单价"] = rec["cache"]
            new["币种"] = cur
            new["数据来源"] = "自动化抓取"
            rows.append(new)
            key2row[k] = new
            added.append((vendor, model))

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLS})

    print("合并完成：更新 %d 条，新增 %d 条，总计 %d 条" % (len(changed), len(added), len(rows)))
    for v, m, d in changed:
        print("  UPDATE %s / %s: %s" % (v, m, "; ".join(d)))
    for v, m in added:
        print("  ADD    %s / %s" % (v, m))

if __name__ == "__main__":
    main()
