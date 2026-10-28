# -*- coding: utf-8 -*-
"""
读取 llm_pricing.csv，逐行套用用户给定的折扣政策，
生成带「折扣 / 折后输入 / 折后输出」列的新版 CSV 与统一 schema 的 HTML。
"""
import csv, re, html, os, json as _js

SRC = os.path.join(os.path.dirname(__file__), "llm_pricing.csv")
OUT_CSV = os.path.join(os.path.dirname(__file__), "llm_pricing.csv")  # 覆盖写入
OUT_HTML = os.path.join(os.path.dirname(__file__), "llm_pricing.html")

# ---------------------------------------------------------------------------
# 折扣映射：返回 (折扣说明文本, 用于折后价计算的基准系数)
# 阶梯类（GLM / Kimi）基准系数取最低档（≥5万 / 3万-50万）作为"起"价。
# ---------------------------------------------------------------------------
def discount_info(vendor, model):
    v = (vendor or "").strip()
    m = (model or "").lower()
    if v == "智谱 GLM":
        return ("阶梯：≥5万9折 / ≥30万85折 / ≥60万8折", 0.9)
    if v == "DeepSeek":
        return ("5折", 0.5)
    if v == "Kimi":
        return ("阶梯：月消≥50万8.5折 / 3万≤月消<50万9折", 0.9)
    if v == "稀宇科技 MiniMax":
        return ("5折（官方现时；清单价曾为8.5折）", 0.5)
    if v == "阿里通义 Qwen":
        if "preview" in m:
            return ("preview 无折扣", 1.0)
        if m in ("qwen3.7-max", "qwen3.8-max"):
            return ("6折", 0.6)
        return ("4.5折", 0.45)
    if v == "腾讯混元 Hunyuan":
        return ("6.5折", 0.65)
    if v == "百度文心 ERNIE":
        return ("9折", 0.9)
    if v == "字节豆包 Doubao":
        return ("9.5折", 0.95)
    if v == "小米 MiMo":
        return ("8.8折", 0.88)
    if v == "Anthropic Claude":
        return ("7.5折", 0.75)
    if v == "Google Gemini":
        return ("7折", 0.70)
    if v == "OpenAI":
        return ("7.5折", 0.75)
    if v == "xAI Grok":
        return ("6.5折", 0.65)
    return ("—", 1.0)

# ---------------------------------------------------------------------------
# 价格字符串套用折扣系数：保留原格式（范围"/"、币种符号、单位文字等）
# ---------------------------------------------------------------------------
def fmtnum(v):
    s = "%.4f" % v
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"

def apply_discount(price, factor, cur):
    if price is None:
        return "—"
    s = str(price).strip()
    if s == "" or s == "—" or s == "-":
        return "—"
    if "免费" in s:
        return "免费"
    # 提取币种符号（去掉已有的 ¥/$ 以便统一重新前缀）
    cur = "¥" if "¥" in s else ("$" if "$" in s else cur)
    tmp = s.replace("¥", "").replace("$", "")
    suffix = ""
    if tmp.endswith("起"):
        suffix = "起"
        tmp = tmp[:-1]
    # 无数字的特殊标记原样返回（如"命中折扣"）
    if not re.search(r"\d", tmp):
        return s
    def repl(mm):
        val = float(mm.group())
        return cur + fmtnum(round(val * factor, 6))
    out = re.sub(r"\d+\.\d+|\d+", repl, tmp)
    out += suffix
    return out

# ---------------------------------------------------------------------------
# 数值提取：供前端成本计算器 / 排序使用
# ---------------------------------------------------------------------------
def parse_price_num(s):
    s = "" if s is None else str(s)
    if "免费" in s or s.strip() in ("", "—", "-"):
        return None
    mm = re.search(r"-?\d+\.?\d*", s.replace(",", ""))
    return float(mm.group()) if mm else None

def parse_ctx_num(s):
    s = "" if s is None else str(s).strip().lower()
    if s in ("", "—", "-", "∞", "inf"):
        return None
    mm = re.search(r"(\d+(?:\.\d+)?)\s*([km])?", s)
    if not mm:
        return None
    val = float(mm.group(1)); unit = mm.group(2)
    if unit == "m":
        val *= 1_000_000
    elif unit == "k":
        val *= 1_000
    return int(val)

# ---------------------------------------------------------------------------
# 读取 CSV
# ---------------------------------------------------------------------------
with open(SRC, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# 厂商官方定价页 URL（外链数据源）
try:
    _src = _js.load(open(os.path.join(os.path.dirname(__file__), "vendor_sources.json"), encoding="utf-8"))
    SOURCES = {x["vendor"]: x["url"] for x in _src}
except Exception:
    SOURCES = {}

# 计算折扣 / 折后价，并写出新版 CSV
out_rows = []
for r in rows:
    vendor = r["厂商"]
    model = r["模型"]
    cur = "¥" if r["币种"].startswith("¥") else "$"
    disc_text, factor = discount_info(vendor, model)
    r["折扣"] = disc_text
    r["折后输入单价"] = apply_discount(r["输入单价"], factor, cur)
    r["折后输出单价"] = apply_discount(r["输出单价"], factor, cur)
    out_rows.append(r)

CSV_COLS = ["厂商", "模型", "偏向能力", "计费方式", "上下文长度", "最大输出Token",
            "输入单价", "输出单价", "缓存命中单价", "折扣", "折后输入单价",
            "折后输出单价", "币种", "数据来源"]

with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CSV_COLS)
    w.writeheader()
    for r in out_rows:
        w.writerow({k: r.get(k, "") for k in CSV_COLS})

# ---------------------------------------------------------------------------
# 厂商展示元信息（顺序 = CSV 出现顺序）
# ---------------------------------------------------------------------------
VENDOR_META = {
    "智谱 GLM": ("智谱 AI", "dom", "GLM 系列",
                 "计费：按量计费（元/百万 tokens） · 平台：BigModel · 输入/输出区分 · 缓存命中约输入价 25-30%",
                 "阶梯折扣按<b>月消费</b>档位：≥5万→9折，≥30万→85折，≥60万→8折。下表「折后价」按 9折（≥5万档）示例。Batch API 标准价5折；免费模型：GLM-4.7-Flash、GLM-4.6V-Flash。"),
    "DeepSeek": ("DeepSeek", "dom", "深度求索",
                 "计费：按量计费（$/百万 tokens，海外区） · 平台：api.deepseek.com · 缓存命中约未命中的 1/50",
                 "高峰时段（周一至周五 UTC 01:00-04:00、06:00-10:00，不含中国法定假日）价格翻倍，其余时段半价；折后价已含 5折 代理折扣。"),
    "Kimi": ("月之暗面", "dom", "Kimi K 系列",
             "计费：按量计费（元/百万 tokens） · 平台：platform.kimi.com · 缓存区分 5min / 1h TTL",
             "阶梯折扣按<b>月消费</b>：≥50万→8.5折，3万≤月消<50万→9折。下表「折后价」按 9折 示例。K2 系列已演进至 K2.6 / K2.7 Code（表中输入价为缓存未命中价）；K3 为新旗舰（1M 上下文）。"),
    "稀宇科技 MiniMax": ("稀宇科技", "dom", "MiniMax / 海螺 AI",
             "计费：按量计费（¥/百万 tokens） · 平台：platform.minimaxi.com · 双兼容 OpenAI / Anthropic 端点",
             "官方现时统一 <b>5折</b>（你清单中的 8.5折 为早期/清单价，已失效）。M3 标价为永久五折后价格。"),
    "阿里通义 Qwen": ("阿里通义", "dom", "Qwen / 千问",
             "计费：按量计费（元/百万 tokens） · 平台：阿里云百炼 · 中国内地（北京）口径 · 阶梯按输入长度",
             "基础系列 <b>4.5折</b>；qwen3.7-max / qwen3.8-max 特批 <b>6折</b>；带 preview 的预览模型 <b>无折扣</b>。Batch 半价与缓存命中折扣不可叠加。"),
    "腾讯混元 Hunyuan": ("腾讯", "dom", "混元 Hunyuan",
             "计费：按量计费（元/百万 tokens） · 平台：腾讯云大模型知识引擎 · 部分模型支持缓存命中",
             "全系列 <b>6.5折</b>。混元 Lite 等免费模型维持免费；其他模型折后价按 6.5折 折算。"),
    "百度文心 ERNIE": ("百度", "dom", "文心 ERNIE",
             "计费：按量计费（元/百万 tokens） · 平台：百度智能云千帆 · 千亿参数旗舰 + 免费轻量矩阵",
             "全系列 <b>9折</b>（记者/直接折扣，全系列统一）。Speed/Lite/Tiny 长期免费；5.1 旗舰折后 ¥3.6/¥16.2。"),
    "字节豆包 Doubao": ("字节跳动", "dom", "豆包 Doubao / Seed",
             "计费：按量计费（元/百万 tokens） · 平台：火山引擎方舟 · 缓存命中与 Batch 折扣可叠加",
             "全系列 <b>9.5折</b>。国内按「输入上下文长度区间」分档：0-32K、32K-128K、128K-256K；折后价按各档分别折算。"),
    "小米 MiMo": ("小米", "dom", "MiMo",
             "计费：按量计费（元/百万 tokens） · 平台：mimo.mi.com · SGLang + HiCache 三级存储",
             "全系列 <b>8.8折</b>。当前主力为 V2.6 系列（2026-10 起 V2.5 已下线下新 V2.6）；Batch API / Token Plan 订阅另计。"),
    "Anthropic Claude": ("Anthropic", "os", "Claude",
             "计费：按量计费（$/百万 tokens） · 平台：api.anthropic.com · 缓存分 5min / 1h TTL",
             "全系列 <b>7.5折</b>。缓存读取约输入 5-10%；Batch 5折（与代理折扣可叠加与否以商务条款为准）。"),
    "Google Gemini": ("Google", "os", "Gemini",
             "计费：按量计费（$/百万 tokens） · 平台：ai.google.dev · Pro 按 200K 上下文分档",
             "全系列 <b>7折</b>。Pro 模型按 ≤200K / >200K 分档；3.7/3.6 Flash 限时价至 2026-12-31，2027 起翻倍。"),
    "OpenAI": ("OpenAI", "os", "GPT / o-series",
             "计费：按量计费（$/百万 tokens） · 平台：platform.openai.com · 缓存读取约输入 10%",
             "全系列 <b>7.5折</b>。o 系列思维链 token 计入输出计费；Fast/Priority 模式 2x 加价另计。"),
    "xAI Grok": ("xAI", "os", "Grok",
             "计费：按量计费（$/百万 tokens） · 平台：api.x.ai · 按 200K 上下文分档",
             "全系列 <b>6.5折</b>。按 ≤200K / ≥200K 分档，超过阈值整请求按高档计费。"),
}

# 折扣政策对照表（顶部）
DISCOUNT_TABLE = [
    ("OpenAI 系列", "7.5折", "0.75"),
    ("Anthropic / Claude", "7.5折", "0.75"),
    ("Gemini 系列", "7折", "0.70"),
    ("Grok 系列", "6.5折", "0.65"),
    ("DouBao 系列", "9.5折", "0.95"),
    ("Qwen 系列", "4.5折（qwen3.7/3.8-max 6折 / preview 无折扣）", "0.45"),
    ("Kimi 系列", "阶梯：≥50万8.5折 / 3万≤月消<50万9折", "0.90"),
    ("MiniMax 系列", "5折（官方现时；清单曾8.5折）", "0.50"),
    ("DeepSeek / V4", "5折", "0.50"),
    ("智谱 GLM 系列", "阶梯：≥5万9折 / ≥30万85折 / ≥60万8折", "0.90"),
    ("小米 MiMo 系列", "8.8折", "0.88"),
    ("腾讯混元 Hunyuan", "6.5折", "0.65"),
    ("百度文心 ERNIE", "9折", "0.90"),
]

# ---------------------------------------------------------------------------
# 生成 HTML
# ---------------------------------------------------------------------------
CSS = """  :root {
    --bg: #f7f8fa; --panel: #ffffff; --border: #e5e7eb; --text: #1f2328;
    --muted: #6b7280; --accent: #2563eb; --domestic: #1d4ed8; --overseas: #047857;
    --header: #f1f5f9; --zebra: #fafbfc; --disc: #fff7ed; --disc-border: #fed7aa;
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--text);
    font-family:-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI",Arial,sans-serif;
    line-height:1.55; padding:32px 16px 80px; }
  .wrap { max-width:1440px; margin:0 auto; }
  h1 { font-size:26px; margin:0 0 4px; }
  .sub { color:var(--muted); font-size:13px; margin-bottom:24px; }
  .meta { background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:12px 16px;
    font-size:13px; color:#78350f; margin-bottom:26px; }
  .meta b { color:#92400e; }
  .meta ul { margin:6px 0 0 20px; padding:0; }
  .meta li { margin:2px 0; }
  .section { background:var(--panel); border:1px solid var(--border); border-radius:12px;
    padding:18px 22px 24px; margin-bottom:26px; box-shadow:0 1px 2px rgba(0,0,0,.03); }
  .section h2 { font-size:18px; margin:0 0 4px; display:flex; align-items:center; gap:10px; }
  .tag { font-size:11px; padding:2px 8px; border-radius:999px; color:#fff; }
  .tag.dom { background:var(--domestic); } .tag.os { background:var(--overseas); }
  .section .desc { color:var(--muted); font-size:12px; margin-bottom:14px; }
  .scroll { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; font-size:13px; min-width:1100px; }
  th, td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--border);
    vertical-align:top; white-space:nowrap; }
  th { background:var(--header); font-weight:600; color:#334155; font-size:12px;
    letter-spacing:.02em; position:sticky; top:0; }
  tbody tr:nth-child(even) { background:var(--zebra); }
  tbody tr:hover { background:#eef2ff; }
  .model { font-weight:600; color:#0f172a; }
  .price { font-variant-numeric:tabular-nums; }
  .na { color:#94a3b8; font-style:italic; }
  .disc { background:var(--disc); color:#9a3412; font-weight:600; font-size:12px; }
  .disc-col { background:#fffaf2; }
  .footnote { margin-top:14px; padding-top:12px; border-top:1px dashed var(--border);
    font-size:12px; color:var(--muted); }
  .toc { display:grid; grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:8px; margin-bottom:24px; }
  .toc a { display:block; background:#fff; border:1px solid var(--border); border-radius:6px;
    padding:8px 12px; text-decoration:none; color:var(--text); font-size:13px; }
  .toc a:hover { border-color:var(--accent); color:var(--accent); }
  .toc .grp { grid-column:1/-1; font-size:11px; color:var(--muted); margin-top:6px; padding-left:4px; }
  .dtab { width:100%; border-collapse:collapse; font-size:13px; margin-bottom:8px; }
  .dtab th, .dtab td { border:1px solid var(--border); padding:7px 12px; white-space:nowrap; }
  .dtab th { background:#fef3c7; }
  .legend { display:flex; flex-wrap:wrap; gap:14px; margin:6px 0 18px; font-size:12px; color:var(--muted); }
  code { font-family:ui-monospace,Menlo,monospace; font-size:12px; }
"""

def esc(s):
    return html.escape(str(s), quote=True)

html_parts = []
html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>国内外主流大模型定价对比（含代理折扣）· 2026-10-13</title>
<style>%s</style>
</head>
<body>
<div class="wrap">

<h1>国内外主流大模型 API 定价对比 · 含代理折扣</h1>
<div class="sub">采集时间：2026-10-13 · 数据来源：各厂商官方定价页 + 第三方汇总 · 价格单位：每百万 tokens（¥ 或 $）· 折扣为用户提供政策</div>
""" % CSS)

html_parts.append("""<div class="meta">
  <b>折扣栏说明</b>
  <ul>
    <li><b>折扣</b>列：应用你提供的代理 / 渠道折扣政策。阶梯类（GLM、Kimi）按<b>月消费</b>档位，表中列全档位，「折后价」按最低档示例。</li>
    <li><b>折后输入 / 折后输出</b>：在官方标牌价基础上乘以折扣系数所得（同币种）。免费模型仍为免费；"命中折扣"等标记原样保留。</li>
    <li><b>冲突处理</b>：MiniMax 你清单写 8.5折，但注明"官方现时5折"，采用 <b>5折</b>；Kimi 基础 9折 与"月之暗面阶梯"一致，采用阶梯；混元 <b>6.5折</b>、文心 <b>9折</b> 已按你的补充计入清单。</li>
    <li>所有价格均为按量计费标牌价；不含限时折扣、订阅套餐、Batch 半价（部分可与代理折扣叠加，以商务条款为准）。</li>
    <li>汇率参考 1 $ ≈ 7.2 ¥（2026-10）；海外 $ 价未折算为 ¥。</li>
  </ul>
</div>""")

# 目录
html_parts.append('<div class="toc">')
html_parts.append('<div class="grp">国内</div>')
for v in VENDOR_META:
    if VENDOR_META[v][1] == "dom":
        html_parts.append('<a href="#%s">%s</a>' % (esc(v), esc(VENDOR_META[v][0])))
html_parts.append('<div class="grp">海外</div>')
for v in VENDOR_META:
    if VENDOR_META[v][1] == "os":
        html_parts.append('<a href="#%s">%s</a>' % (esc(v), esc(VENDOR_META[v][0])))
html_parts.append('</div>')

# 各厂商分节
for vendor in VENDOR_META:
    disp, tag, series, desc, foot = VENDOR_META[vendor]
    html_parts.append('<div class="section" id="%s">' % esc(vendor))
    html_parts.append('<h2>%s <span class="tag %s">%s</span> <span style="font-weight:400;font-size:13px;color:var(--muted);">%s</span></h2>'
                      % (esc(disp), esc(tag), ("国内" if tag == "dom" else "海外"), esc(series)))
    html_parts.append('<div class="desc">%s</div>' % esc(desc))
    html_parts.append('<div class="scroll"><table>')
    html_parts.append('<thead><tr>'
                      '<th>模型</th><th>偏向能力</th><th>上下文</th><th>最大输出</th>'
                      '<th>输入单价</th><th>输出单价</th><th>缓存命中</th>'
                      '<th>折扣</th><th>折后输入</th><th>折后输出</th>'
                      '</tr></thead><tbody>')
    for r in out_rows:
        if r["厂商"] != vendor:
            continue
        inp = esc(r["输入单价"]); out = esc(r["输出单价"]); cache = esc(r["缓存命中单价"])
        cache_cls = ' class="na"' if (r["缓存命中单价"] in ("—", "-", "") or "免费" in r["缓存命中单价"]) else ""
        disc = esc(r["折扣"])
        af_in = esc(r["折后输入单价"]); af_out = esc(r["折后输出单价"])
        cap = esc(r.get("偏向能力", "") or "—")
        html_parts.append(
            '<tr>'
            '<td class="model">%s</td>'
            '<td class="caps">%s</td>'
            '<td>%s</td><td>%s</td>'
            '<td class="price">%s</td><td class="price">%s</td>'
            '<td class="price"%s>%s</td>'
            '<td class="disc">%s</td>'
            '<td class="price disc-col">%s</td>'
            '<td class="price disc-col">%s</td>'
            '</tr>' % (
                esc(r["模型"]), cap, esc(r["上下文长度"]), esc(r["最大输出Token"]),
                inp, out, cache_cls, cache, disc, af_in, af_out
            )
        )
    html_parts.append('</tbody></table></div>')
    html_parts.append('<div class="footnote">%s</div>' % foot)
    html_parts.append('</div>')

# 折扣政策对照表（置于页面底部）
html_parts.append('<div class="section" id="discount">')
html_parts.append('<h2 style="font-size:17px;margin:0 0 12px;">📋 折扣政策对照表</h2>')
html_parts.append('<div class="scroll"><table class="dtab"><thead><tr><th>厂商系列</th><th>折扣政策</th></tr></thead><tbody>')
for name, pol, _coef in DISCOUNT_TABLE:
    html_parts.append("<tr><td><b>%s</b></td><td>%s</td></tr>" % (esc(name), esc(pol)))
html_parts.append("</tbody></table></div>")
html_parts.append('</div>')

# 市场对照说明
html_parts.append("""<div class="section">
  <h2 style="font-size:16px;">市场对照 & 使用建议</h2>
  <div style="font-size:13px;color:var(--muted);line-height:1.7;">
    <ol style="padding-left:22px;">
      <li><b>国内折扣力度普遍大于海外</b>：Qwen 4.5折、DeepSeek / MiniMax 5折、GLM 阶梯最低8折、MiMo 8.8折；海外 OpenAI / Anthropic 7.5折、Gemini 7折、Grok 6.5折。</li>
      <li><b>MiniMax 5折为官方现时段促销</b>（你清单标注"官方现时5折"），比早期清单 8.5折 更优，建议确认活动有效期。</li>
      <li><b>Kimi / GLM 为阶梯折扣</b>，月消费越高折扣越大；中小用量按 9折 / 9折（Kimi）、9折（GLM≥5万）估算即可。</li>
      <li><b>混元 6.5折、文心 9折</b>已计入折扣清单（混元为补充折扣，文心为全系列统一的记者/直接折扣）；其余国内厂商折扣力度见对照表。</li>
      <li><b>免费入口</b>仍可用作引流/低峰：GLM-4.7-Flash、GLM-4.6V-Flash、混元 Lite、文心 Speed/Lite/Tiny、MiMo-V2-TTS、各厂商 preview 模型（无折扣但本身低价）。</li>
      <li>数据采集 2026-10-13，模型与折扣政策变动频繁，正式大批量采购前请回官方页与商务二次确认。</li>
    </ol>
  </div>
</div>

</div>
</body>
</html>""")

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(html_parts))

# ---------------------------------------------------------------------------
# 导出 prices.json：数据 / 展示分离，供 index.html 动态加载（固定链接前提）
# ---------------------------------------------------------------------------
import json as _json
_vendors_json = []
for _vendor in VENDOR_META:
    _disp, _tag, _series, _desc, _foot = VENDOR_META[_vendor]
    _src_url = SOURCES.get(_vendor, "")
    _models = []
    for _r in out_rows:
        if _r["厂商"] != _vendor:
            continue
        _disc_text, _factor = discount_info(_vendor, _r["模型"])
        _models.append({
            "model": _r["模型"],
            "cap": _r.get("偏向能力", ""),
            "context": _r["上下文长度"],
            "max_output": _r["最大输出Token"],
            "input": _r["输入单价"],
            "output": _r["输出单价"],
            "cache": _r["缓存命中单价"],
            "discount": _r["折扣"],
            "after_in": _r["折后输入单价"],
            "after_out": _r["折后输出单价"],
            # 数值字段（前端计算器 / 排序用）
            "in_v": parse_price_num(_r["输入单价"]),
            "out_v": parse_price_num(_r["输出单价"]),
            "after_in_v": parse_price_num(_r["折后输入单价"]),
            "after_out_v": parse_price_num(_r["折后输出单价"]),
            "ctx_v": parse_ctx_num(_r["上下文长度"]),
            "coef": round(_factor, 4),
            "cur": "$" if ("$" in (_r["折后输入单价"] + _r["输入单价"])) else "¥",
            "free": ("免费" in _r["输入单价"] and "免费" in _r["输出单价"]),
        })
    _vendors_json.append({
        "vendor": _vendor, "display": _disp, "tag": _tag,
        "series": _series, "desc": _desc, "footnote": _foot,
        "source": _src_url,
        "models": _models,
    })
import datetime as _dt
_data = {
    "meta": {
        "generated": _dt.date.today().isoformat(),
        "updated": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "各厂商官方定价页 + 第三方汇总；折扣为用户提供政策",
        "currency_note": "¥ 人民币 / $ 美元；汇率参考 1 $ ≈ 7.2 ¥",
    },
    "discount_table": [{"name": n, "policy": p, "coef": c} for (n, p, c) in DISCOUNT_TABLE],
    "vendors": _vendors_json,
}
with open(os.path.join(os.path.dirname(__file__), "prices.json"), "w", encoding="utf-8") as f:
    _json.dump(_data, f, ensure_ascii=False, indent=2)

print("done. rows=%d vendors=%d json=%d" % (len(out_rows), len(VENDOR_META), len(_vendors_json)))
