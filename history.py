# -*- coding: utf-8 -*-
"""
价格历史快照：维护 price_history.json，供「历史价格波动」看板使用。

- 首次运行（无 price_history.json）：生成 6 个周度回溯点（含今日），
  早期点按当前价做确定性小幅上浮（示意价格下行趋势）。明确为「示例回溯」，
  真实逐时/逐日数据将在此后自动累积。
- 后续运行：把今日快照追加 / 更新到最后一格（同日则覆盖）。

结构：
{
  "dates": ["2026-09-18", ... "2026-10-23"],
  "models": {
     "vendor/model": {"ai":[after_in_CNY...], "ao":[after_out_CNY...]}
  },
  "seeded": true
}
"""
import json, os, datetime, math

RATE = 7.2  # 1 $ ≈ 7.2 ¥
HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(HERE, "price_history.json")
PRICES = os.path.join(HERE, "prices.json")
WEEKS = 6  # 回溯周数（含本周）


def cny_val(m, field):
    v = m.get(field)
    if v is None:
        return None
    return v * RATE if m.get("cur") == "$" else v


def today_iso():
    return datetime.date.today().isoformat()


def load_prices():
    with open(PRICES, encoding="utf-8") as f:
        return json.load(f)


def build_today(data):
    snap = {}
    for v in data["vendors"]:
        for m in v["models"]:
            ai = cny_val(m, "after_in_v")
            ao = cny_val(m, "after_out_v")
            if ai is None or ao is None:
                continue
            snap[v["vendor"] + "/" + m["model"]] = {
                "ai": round(ai, 4), "ao": round(ao, 4)
            }
    return snap


def seed_history(snap, today):
    """生成含今日的 WEEKS 个周度回溯点（示例）。"""
    base = datetime.date.today()
    dates = [(base - datetime.timedelta(days=7 * i)).isoformat()
             for i in range(WEEKS - 1, -1, -1)]
    models = {}
    for key, val in snap.items():
        ai0, ao0 = val["ai"], val["ao"]
        # 用 key 派生稳定抖动，保证同一模型每次 seed 一致
        h = abs(hash(key)) % 1000 / 1000.0
        s_ai, s_ao = [], []
        for i in range(WEEKS):
            age = (WEEKS - 1) - i          # 0=今日, 越大越久远
            trend = 1 + 0.03 * age          # 越久远略贵（整体下行）
            jitter = 1 + 0.05 * math.sin(i * 1.7 + h * 6.28)
            f = trend * jitter
            s_ai.append(round(ai0 * f, 4))
            s_ao.append(round(ao0 * f, 4))
        models[key] = {"ai": s_ai, "ao": s_ao}
    return {"dates": dates, "models": models, "seeded": True}


def main():
    data = load_prices()
    snap = build_today(data)
    today = today_iso()

    if os.path.exists(HIST):
        with open(HIST, encoding="utf-8") as f:
            hist = json.load(f)
    else:
        hist = None

    if not hist or not hist.get("dates"):
        hist = seed_history(snap, today)
        print("seeded", len(hist["dates"]), "dates,", len(hist["models"]), "models")
    else:
        # 对齐日期
        if hist["dates"][-1] == today:
            pass
        else:
            hist["dates"].append(today)
        # 更新 / 追加每个模型
        for key, val in snap.items():
            if key not in hist["models"]:
                pad = len(hist["dates"]) - 1
                hist["models"][key] = {
                    "ai": [None] * pad + [val["ai"]],
                    "ao": [None] * pad + [val["ao"]],
                }
            else:
                ml = hist["models"][key]
                if hist["dates"][-1] == today:
                    ml["ai"][-1] = val["ai"]
                    ml["ao"][-1] = val["ao"]
                else:
                    ml["ai"].append(val["ai"])
                    ml["ao"].append(val["ao"])
        # 长度对齐保护
        n = len(hist["dates"])
        for key, ml in hist["models"].items():
            for kk in ("ai", "ao"):
                if len(ml[kk]) < n:
                    ml[kk] = [None] * (n - len(ml[kk])) + ml[kk]
                elif len(ml[kk]) > n:
                    ml[kk] = ml[kk][-n:]
        print("updated today", today, "models:", len(hist["models"]))

    with open(HIST, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
