# -*- coding: utf-8 -*-
"""把 llm_pricing.csv 导出为带折扣栏的 Excel（.xlsx）。"""
import csv, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(__file__)
SRC = os.path.join(BASE, "llm_pricing.csv")
OUT = os.path.join(BASE, "llm_pricing.xlsx")

with open(SRC, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# 列顺序（含折扣栏）
COLS = ["厂商", "模型", "偏向能力", "计费方式", "上下文长度", "最大输出Token",
        "输入单价", "输出单价", "缓存命中单价", "折扣",
        "折后输入单价", "折后输出单价", "币种", "数据来源"]
# 分厂商页去掉"厂商"列
COLS_SUB = [c for c in COLS if c != "厂商"]

DISCOUNT_TABLE = [
    ("OpenAI 系列", "7.5折", "0.75"),
    ("Anthropic / Claude", "7.5折", "0.75"),
    ("Gemini 系列", "7折", "0.70"),
    ("Grok 系列", "6.5折", "0.65"),
    ("DouBao 系列", "9.5折", "0.95"),
    ("Qwen 系列", "4.5折（qwen3.7-max 6折 / preview 无折扣）", "0.45"),
    ("Kimi 系列", "阶梯：≥50万8.5折 / 3万≤月消<50万9折", "0.90"),
    ("MiniMax 系列", "5折（官方现时；清单曾8.5折）", "0.50"),
    ("DeepSeek / V4", "5折", "0.50"),
    ("智谱 GLM 系列", "阶梯：≥5万9折 / ≥30万85折 / ≥60万8折", "0.90"),
    ("小米 MiMo 系列", "8.8折", "0.88"),
    ("腾讯混元 Hunyuan", "未提供（按原价）", "1.00"),
    ("百度文心 ERNIE", "未提供（按原价）", "1.00"),
]

# ---- 样式 ----
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=14, color="1F4E79")
NOTE_FONT = Font(size=10, color="555555")
DISC_FILL = PatternFill("solid", fgColor="FFF2CC")      # 折扣列浅橙
AFTER_FILL = PatternFill("solid", fgColor="FCE4D6")      # 折后列浅橙
ZEBRA_FILL = PatternFill("solid", fgColor="F5F8FC")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP_TOP = Alignment(vertical="top", wrap_text=True)
CENTER = Alignment(horizontal="center", vertical="center")

def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = BORDER

def write_table(ws, data_rows, cols, start_row=1, disc_idx=None, after_idxs=None):
    # 表头
    for j, name in enumerate(cols, start=1):
        ws.cell(row=start_row, column=j, value=name)
    style_header(ws, len(cols), row=start_row)
    # 数据
    for i, r in enumerate(data_rows):
        rr = start_row + 1 + i
        for j, name in enumerate(cols, start=1):
            val = r.get(name, "")
            cell = ws.cell(row=rr, column=j, value=val)
            cell.alignment = WRAP_TOP
            cell.border = BORDER
            cell.font = Font(size=10)
            if i % 2 == 1:
                cell.fill = ZEBRA_FILL
            if disc_idx is not None and j == disc_idx:
                cell.fill = DISC_FILL
                cell.font = Font(size=10, bold=True, color="9C5700")
            if after_idxs and j in after_idxs:
                cell.fill = AFTER_FILL
                cell.font = Font(size=10, color="843C0C")
    # 列宽
    widths = {"厂商": 16, "模型": 26, "计费方式": 16, "上下文长度": 12,
              "最大输出Token": 12, "输入单价": 16, "输出单价": 16,
              "缓存命中单价": 16, "折扣": 30, "折后输入单价": 16,
              "折后输出单价": 16, "币种": 14, "数据来源": 18}
    for j, name in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(j)].width = widths.get(name, 14)
    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)

wb = Workbook()

# ===== Sheet 1: 说明 + 折扣政策对照表 =====
ws0 = wb.active
ws0.title = "说明与折扣政策"
ws0.sheet_view.showGridLines = False
ws0["A1"] = "国内外主流大模型 API 定价对比（含代理折扣）"
ws0["A1"].font = TITLE_FONT
ws0["A2"] = "采集时间：2026-10-13 · 折扣为用户提供政策 · 价格单位：每百万 tokens（¥ 或 $）"
ws0["A2"].font = NOTE_FONT
notes = [
    "1. 折扣列：应用用户提供的代理/渠道折扣政策；阶梯类（GLM、Kimi）按「月消费」档位，表内列全档位。",
    "2. 折后输入 / 折后输出：官方标牌价 × 折扣系数（同币种）；免费模型仍为免费。",
    "3. 冲突处理：MiniMax 采用 5折（官方现时，清单 8.5折 已失效）；Kimi 取阶梯；混元、文心未提供按原价。",
    "4. 阶梯类折后价按最低档示例（GLM≥5万 9折 / Kimi 3万-50万 9折）。",
    "5. 汇率参考 1 $ ≈ 7.2 ¥（2026-10）；海外 $ 价未折算 ¥。",
    "6. 本工作簿含：本页（折扣政策对照表）+ 『总表』（全部厂商合并）+ 13 个厂商分表。",
]
r = 4
for n in notes:
    ws0.cell(row=r, column=1, value=n).font = NOTE_FONT
    r += 1
r += 1
ws0.cell(row=r, column=1, value="折扣政策对照表").font = Font(bold=True, size=12, color="1F4E79")
r += 1
hdr = ["厂商系列", "折扣政策", "系数"]
for j, h in enumerate(hdr, start=1):
    c = ws0.cell(row=r, column=j, value=h)
    c.fill = HEADER_FILL; c.font = HEADER_FONT; c.border = BORDER
    c.alignment = CENTER
for name, pol, coef in DISCOUNT_TABLE:
    r += 1
    ws0.cell(row=r, column=1, value=name).border = BORDER
    ws0.cell(row=r, column=2, value=pol).border = BORDER
    ws0.cell(row=r, column=3, value=coef).border = BORDER
ws0.column_dimensions["A"].width = 22
ws0.column_dimensions["B"].width = 46
ws0.column_dimensions["C"].width = 10

# ===== Sheet 2: 总表 =====
ws_all = wb.create_sheet("总表")
disc_i = COLS.index("折扣") + 1
after_i = [COLS.index("折后输入单价") + 1, COLS.index("折后输出单价") + 1]
write_table(ws_all, rows, COLS, disc_idx=disc_i, after_idxs=after_i)

# ===== Sheet 3..: 各厂商分表 =====
from collections import OrderedDict
groups = OrderedDict()
for r in rows:
    groups.setdefault(r["厂商"], []).append(r)

VENDOR_ORDER = ["智谱 GLM", "DeepSeek", "Kimi", "稀宇科技 MiniMax", "阿里通义 Qwen",
                "腾讯混元 Hunyuan", "百度文心 ERNIE", "字节豆包 Doubao", "小米 MiMo",
                "Anthropic Claude", "Google Gemini", "OpenAI", "xAI Grok"]

SHORT = {
    "智谱 GLM": "GLM", "DeepSeek": "DeepSeek", "Kimi": "Kimi",
    "稀宇科技 MiniMax": "MiniMax", "阿里通义 Qwen": "Qwen",
    "腾讯混元 Hunyuan": "Hunyuan", "百度文心 ERNIE": "ERNIE",
    "字节豆包 Doubao": "Doubao", "小米 MiMo": "MiMo",
    "Anthropic Claude": "Claude", "Google Gemini": "Gemini",
    "OpenAI": "OpenAI", "xAI Grok": "Grok",
}

def sheet_name(v):
    return SHORT.get(v, v)[:31]

for v in VENDOR_ORDER:
    if v not in groups:
        continue
    sub = groups[v]
    ws = wb.create_sheet(sheet_name(v))
    di = COLS_SUB.index("折扣") + 1
    ai = [COLS_SUB.index("折后输入单价") + 1, COLS_SUB.index("折后输出单价") + 1]
    write_table(ws, sub, COLS_SUB, disc_idx=di, after_idxs=ai)

wb.save(OUT)
print("saved:", OUT, "sheets:", wb.sheetnames)
