# -*- coding: utf-8 -*-
"""
根据 2026-10-23 对各厂商官网的逐一核对，重建 llm_pricing.csv 的原始价格数据。
折扣口径（用户给定）不变，由 build_discount.py 统一重算「折扣 / 折后」列。
本脚本只保证：厂商、模型、上下文、最大输出、输入/输出/缓存原始价、币种、来源 准确。
"""
import csv, os

OUT = os.path.join(os.path.dirname(__file__), "llm_pricing.csv")
COLS = ["厂商","模型","偏向能力","计费方式","上下文长度","最大输出Token","输入单价","输出单价",
        "缓存命中单价","折扣","折后输入单价","折后输出单价","币种","数据来源"]

# 每条: (厂商, 模型, 计费方式, 上下文, 最大输出, 输入, 输出, 缓存, 币种, 来源)
# 折扣/折后列留空，交给 build_discount.py 重算
R = []  # rows
def add(vendor, model, bill, ctx, maxout, inp, out, cache, cur, src):
    R.append({
        "厂商":vendor,"模型":model,"计费方式":bill,"上下文长度":ctx,"最大输出Token":maxout,
        "输入单价":inp,"输出单价":out,"缓存命中单价":cache,
        "折扣":"","折后输入单价":"","折后输出单价":"",
        "币种":cur,"数据来源":src,
    })

CN = "¥/百万tokens"
US = "$/百万tokens"

# ---------------- 国内 ----------------
# 智谱 GLM
add("智谱 GLM","GLM-5.3","按量计费","1M","128K","8.00","28.00","2.00",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-5.3-Flash","按量计费","1M","128K","0.80","2.80","0.23",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-5.3-FlashX","按量计费","1M","128K","2.00","7.00","-",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-5.2","按量计费","1M","128K","8.00","28.00","2.00",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-5.1","按量计费","200K","128K","6.00","24.00","1.30",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-5","按量计费","200K","128K","4.00","18.00","1.00",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-4.7-Flash","按量计费","200K","128K","免费","免费","免费",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-4.6V(视觉)","按量计费(视觉)","200K","-","1.00/2.00","3.00/6.00","-",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-4.6V-Flash","按量计费(视觉)","-","-","免费","免费","免费",CN,"智谱 BigModel 官方")
add("智谱 GLM","GLM-OCR","按量计费","32K","-","0.20","0.20","-",CN,"智谱 BigModel 官方")

# DeepSeek
add("DeepSeek","deepseek-v4-flash","按量计费(峰/非峰)","1M","384K","0.14/0.44","0.28","0.0028",US,"DeepSeek 官方")
add("DeepSeek","deepseek-v4-pro","按量计费(峰/非峰)","1M","384K","0.435/1.32","0.87","0.003625",US,"DeepSeek 官方")

# Kimi
add("Kimi","kimi-k3","按量计费","1M","-","20.00","100.00","2.00",CN,"Kimi 平台官方")
add("Kimi","kimi-k2.7-code","按量计费","256K","-","6.50","27.00","1.30",CN,"Kimi 平台官方")
add("Kimi","kimi-k2.7-code-highspeed","按量计费","256K","-","13.00","54.00","2.60",CN,"Kimi 平台官方")
add("Kimi","kimi-k2.6","按量计费","256K","-","6.50","27.00","1.10",CN,"Kimi 平台官方")
add("Kimi","moonshot-v1-8k","按量计费","8K","-","2.00","10.00","-",CN,"Kimi 平台官方")
add("Kimi","moonshot-v1-32k","按量计费","32K","-","5.00","20.00","-",CN,"Kimi 平台官方")
add("Kimi","moonshot-v1-128k","按量计费","128K","-","10.00","30.00","-",CN,"Kimi 平台官方")

# MiniMax
add("稀宇科技 MiniMax","MiniMax-M3","按量计费(阶梯)","1M","-","2.10/4.20","8.40/16.80","0.42/0.84",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-M3.1-Flash","按量计费","1M","-","1.00","4.00","0.10",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-M2.7","按量计费","200K","-","2.10","8.40","0.42",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-M2.7-highspeed","按量计费","200K","-","4.20","16.80","0.42",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-M2.5","按量计费","200K","-","2.10","8.40","0.21",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-M2.5-highspeed","按量计费","200K","-","4.20","16.80","0.21",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-M2-her","按量计费","64K","-","2.10","8.40","-",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-01","按量计费","1M","-","0.20","0.20","-",CN,"MiniMax 开放平台")
add("稀宇科技 MiniMax","MiniMax-Text-01","按量计费","1M","-","0.80","0.80","-",CN,"MiniMax 开放平台")

# 阿里通义 Qwen
add("阿里通义 Qwen","qwen3.7-max","按量计费(国际)","1M","-","6.00","18.00","命中折扣",CN,"阿里云百炼官方")
add("阿里通义 Qwen","qwen3-max","按量计费(阶梯)","256K","-","2.50/10.00","10.00/40.00","命中折扣",CN,"阿里云百炼官方")
add("阿里通义 Qwen","qwen3-plus","按量计费","1M","-","0.80","2.00","命中折扣",CN,"阿里云百炼官方")
add("阿里通义 Qwen","qwen3-flash","按量计费","1M","-","0.367","2.936","命中折扣",CN,"阿里云百炼官方")
add("阿里通义 Qwen","qwen-long","按量计费","1M","-","0.50","2.00","-",CN,"阿里云百炼官方")
add("阿里通义 Qwen","qwen-turbo","按量计费","1M","-","0.30","0.60","-",CN,"阿里云百炼官方")
add("阿里通义 Qwen","qwen3-omni-flash","按量计费(多模态)","-","-","1.80文本/15.8音频","6.9/12.7/62.6","-",CN,"阿里云百炼官方")

# 腾讯混元 Hunyuan
add("腾讯混元 Hunyuan","Hy4 preview","按量计费","960K","64K","6.00","18.00","0.30",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","Hy3","按量计费","256K","-","1.00","4.00","0.25",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","Hy3 preview","按量计费","256K","-","1.20","4.00","0.40",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","hunyuan-T1-latest","按量计费","-","-","1.00","4.00","-",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","hunyuan-turbos-latest","按量计费","-","-","0.80","2.00","-",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","hunyuan-pro","按量计费","32K","4K","30.00","100.00","-",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","hunyuan-standard-256k","按量计费","256K","-","15.00","60.00","-",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","hunyuan-standard","按量计费","32K","2K","4.50","5.00","-",CN,"腾讯云官方")
add("腾讯混元 Hunyuan","hunyuan-lite","按量计费","250K","-","免费","免费","免费",CN,"腾讯云官方")

# 百度文心 ERNIE
add("百度文心 ERNIE","ERNIE 5.1","按量计费","32K~128K","-","4.00/6.00","18.00/22.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE 5.0","按量计费","32K~128K","-","6.00/10.00","24.00/40.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE X1 Turbo","按量计费","32K","-","1.00","4.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE X1","按量计费","32K","-","2.00","8.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE 4.5 Turbo VL","按量计费(多模态)","32K~128K","-","3.00","9.00","0.75",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE 4.5","按量计费","8K","-","4.00","16.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE 4.5 Turbo","按量计费","32K~128K","-","0.80","3.20","0.20",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE 4.0","按量计费","8K","-","4.00","16.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE 3.5","按量计费","8K~128K","-","0.80","2.00","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE Speed","按量计费","128K","-","免费","免费","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE Lite","按量计费","128K","-","免费","免费","-",CN,"百度千帆官方")
add("百度文心 ERNIE","ERNIE Tiny","按量计费","8K","-","免费","免费","-",CN,"百度千帆官方")

# 字节豆包 Doubao
add("字节豆包 Doubao","Doubao-seed-2.1-pro","按量计费","256K","256K","6.00","30.00","0.64",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-seed-2.1-turbo","按量计费","256K","256K","3.00","15.00","0.32",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-seed-2.0-pro","按量计费","256K","128K","3.20","16.00","0.64",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-seed-2.0-lite","按量计费(阶梯)","256K","128K","0.60/1.80","3.60/10.80","0.12",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-seed-2.0-mini","按量计费(阶梯)","256K","128K","0.20/0.80","2.00/8.00","0.04",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-1.5-pro-32k","按量计费(命中折扣)","128K","12K","0.80","2.00","0.16",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-1.5-pro-256k","按量计费","256K","16K","0.80","2.00","-",CN,"火山引擎官方")
add("字节豆包 Doubao","Doubao-1.5-lite","按量计费","32K","-","0.30","0.60","-",CN,"火山引擎官方")

# 小米 MiMo
add("小米 MiMo","MiMo-V2.6-Pro(≤256K)","按量计费","1M","128K","3.00","6.00","0.025",CN,"mimo.mi.com 官方")
add("小米 MiMo","MiMo-V2.6-Pro(256K-1M)","按量计费","1M","128K","6.00","12.00","-",CN,"mimo.mi.com 官方")
add("小米 MiMo","MiMo-V2.6-Pro-UltraSpeed","按量计费","1M","128K","30.00","60.00","0.25",CN,"mimo.mi.com 官方")
add("小米 MiMo","MiMo-V2.6-Flash","按量计费","256K","128K","1.00","2.00","0.02",CN,"mimo.mi.com 官方")
add("小米 MiMo","MiMo-V2-Omni","按量计费(多模态)","256K","128K","2.94","14.70","0.56",CN,"mimo.mi.com 官方")
add("小米 MiMo","MiMo-V2-Flash","按量计费","256K","64K","0.70","2.10","0.07",CN,"mimo.mi.com 官方")
add("小米 MiMo","MiMo-V2-TTS","按量计费","8K","8K","免费","免费","-",CN,"mimo.mi.com 官方")

# ---------------- 海外 ----------------
# Anthropic Claude
add("Anthropic Claude","Claude Opus 5","按量计费","1M","128K","5.00","25.00","0.50",US,"Anthropic 官方")
add("Anthropic Claude","Claude Sonnet 5","按量计费","1M","128K","2.00","10.00","0.20",US,"Anthropic 官方")
add("Anthropic Claude","Claude Haiku 4.5","按量计费","200K","-","1.00","5.00","0.10",US,"Anthropic 官方")
add("Anthropic Claude","Claude Fable 5","按量计费","1M","128K","10.00","50.00","0.50",US,"Anthropic 官方")
add("Anthropic Claude","Claude Mythos 5","按量计费","1M","128K","10.00","50.00","0.50",US,"Anthropic 官方")
add("Anthropic Claude","Claude Opus 4.8","按量计费","1M","-","5.00","25.00","0.50",US,"Anthropic 官方")
add("Anthropic Claude","Claude Opus 4.7","按量计费","1M","-","5.00","25.00","0.50",US,"Anthropic 官方")
add("Anthropic Claude","Claude Sonnet 4.6","按量计费","1M","-","3.00","15.00","0.30",US,"Anthropic 官方")
add("Anthropic Claude","Claude Sonnet 4.5","按量计费","1M","-","3.00","15.00","0.30",US,"Anthropic 官方")
add("Anthropic Claude","Claude Haiku 3.5","按量计费","200K","-","0.80","4.00","0.08",US,"Anthropic 官方")

# Google Gemini
add("Google Gemini","Gemini 3.1 Pro","按量计费(阶梯)","1M","-","2.00/4.00","12.00/18.00","-",US,"Google AI 官方")
add("Google Gemini","Gemini 3 Pro","按量计费(阶梯)","1M","-","2.00/4.00","12.00/18.00","-",US,"Google AI 官方")
add("Google Gemini","Gemini 3.8 Flash","按量计费(限时)","1M","-","0.75","3.75","0.075",US,"Google AI 官方")
add("Google Gemini","Gemini 3.7 Flash","按量计费(限时)","1M","-","0.75","3.75","0.075",US,"Google AI 官方")
add("Google Gemini","Gemini 3.6 Flash","按量计费(限时)","1M","-","0.75","3.75","0.075",US,"Google AI 官方")
add("Google Gemini","Gemini 3.5 Flash","按量计费","1M","-","1.50","9.00","0.15",US,"Google AI 官方")
add("Google Gemini","Gemini 3.5 Flash-Lite","按量计费","1M","-","0.30","2.50","0.03",US,"Google AI 官方")
add("Google Gemini","Gemini 2.5 Pro","按量计费(阶梯)","1M","-","1.25/2.50","10.00/15.00","0.125/0.25",US,"Google AI 官方")
add("Google Gemini","Gemini 2.5 Flash","按量计费","1M","-","0.30","2.50","0.03",US,"Google AI 官方")
add("Google Gemini","Gemini 2.5 Flash-Lite","按量计费","1M","-","0.10","0.40","-",US,"Google AI 官方")

# OpenAI
add("OpenAI","GPT-5","按量计费","400K","128K","1.25","10.00","0.125",US,"OpenAI 官方")
add("OpenAI","GPT-5 mini","按量计费","400K","128K","0.25","2.00","0.025",US,"OpenAI 官方")
add("OpenAI","GPT-5 nano","按量计费","400K","128K","0.05","0.40","0.005",US,"OpenAI 官方")
add("OpenAI","GPT-4.1","按量计费","1M","33K","2.00","8.00","0.50",US,"OpenAI 官方")
add("OpenAI","GPT-4.1 mini","按量计费","1M","33K","0.40","1.60","0.10",US,"OpenAI 官方")
add("OpenAI","GPT-4.1 nano","按量计费","1M","33K","0.10","0.40","0.025",US,"OpenAI 官方")
add("OpenAI","GPT-4o","按量计费","128K","16K","2.50","10.00","1.25",US,"OpenAI 官方")
add("OpenAI","GPT-4o mini","按量计费","128K","16K","0.15","0.60","0.075",US,"OpenAI 官方")
add("OpenAI","o3","按量计费","200K","100K","2.00","8.00","0.50",US,"OpenAI 官方")
add("OpenAI","o3-pro","按量计费","200K","-","20.00","80.00","-",US,"OpenAI 官方")
add("OpenAI","o4-mini","按量计费","200K","100K","1.10","4.40","0.275",US,"OpenAI 官方")
add("OpenAI","o1","按量计费","200K","-","15.00","60.00","7.50",US,"OpenAI 官方")

# xAI Grok
add("xAI Grok","grok-4.7","按量计费(阶梯)","500K","-","2.00/4.00","6.00/12.00","0.50/1.00",US,"xAI 官方")
add("xAI Grok","grok-4.6","按量计费(阶梯)","500K","-","2.00/4.00","6.00/12.00","0.50/1.00",US,"xAI 官方")
add("xAI Grok","grok-4.5","按量计费(阶梯)","500K","-","2.00/4.00","6.00/12.00","0.30/0.60",US,"xAI 官方")
add("xAI Grok","grok-4.3","按量计费(阶梯)","1M","-","1.25/2.50","2.50/5.00","0.20/0.40",US,"xAI 官方")
add("xAI Grok","grok-4.20-0309-reasoning","按量计费(阶梯)","1M","-","1.25/2.50","2.50/5.00","0.20/0.40",US,"xAI 官方")
add("xAI Grok","grok-4.20-0309-non-reasoning","按量计费(阶梯)","1M","-","1.25/2.50","2.50/5.00","0.20/0.40",US,"xAI 官方")
add("xAI Grok","grok-4.20-0309-multi-agent","按量计费(阶梯)","1M","-","1.25/2.50","2.50/5.00","0.20/0.40",US,"xAI 官方")
add("xAI Grok","grok-build-0.1","按量计费(阶梯)","256K","-","1.00/2.00","2.00/4.00","0.20/0.40",US,"xAI 官方")

# ---------------- 偏向能力（页面「偏向能力」列，逗号分隔） ----------------
# 依据各厂商官方对模型的定位/主打场景标注；标签词汇统一，便于前端着色与筛选
CAPS = {
    # 智谱 GLM
    ("智谱 GLM","GLM-5.3"): "代码, 推理, Agent, 长文本, 中文",
    ("智谱 GLM","GLM-5.3-Flash"): "代码, 低成本, 极速, 长文本",
    ("智谱 GLM","GLM-5.3-FlashX"): "代码, 极速, 长文本",
    ("智谱 GLM","GLM-5.2"): "代码, 推理, Agent, 长文本, 中文",
    ("智谱 GLM","GLM-5.1"): "代码, 推理, Agent, 长文本, 中文",
    ("智谱 GLM","GLM-5"): "代码, 推理, Agent, 长文本, 中文",
    ("智谱 GLM","GLM-4.7-Flash"): "低成本, 极速, 长文本",
    ("智谱 GLM","GLM-4.6V(视觉)"): "视觉, 多模态, 中文",
    ("智谱 GLM","GLM-4.6V-Flash"): "视觉, 多模态, 低成本",
    ("智谱 GLM","GLM-OCR"): "OCR, 文档理解",
    # DeepSeek
    ("DeepSeek","deepseek-v4-flash"): "推理, 代码, 低成本, 极速, 开源",
    ("DeepSeek","deepseek-v4-pro"): "推理, 代码, 数学, 开源, 长文本",
    # Kimi
    ("Kimi","kimi-k3"): "长文本, 推理, Agent, 多模态",
    ("Kimi","kimi-k2.7-code"): "代码, Agent, 长文本",
    ("Kimi","kimi-k2.7-code-highspeed"): "代码, 极速, Agent",
    ("Kimi","kimi-k2.6"): "Agent, 长文本, 多模态, 中文",
    ("Kimi","moonshot-v1-8k"): "中文, 低成本",
    ("Kimi","moonshot-v1-32k"): "中文, 长文本",
    ("Kimi","moonshot-v1-128k"): "长文本, 中文",
    # MiniMax
    ("稀宇科技 MiniMax","MiniMax-M3"): "多模态, Agent, 长文本, 中文",
    ("稀宇科技 MiniMax","MiniMax-M3.1-Flash"): "极速, 低成本, 多模态",
    ("稀宇科技 MiniMax","MiniMax-M2.7"): "Agent, 长文本, 中文",
    ("稀宇科技 MiniMax","MiniMax-M2.7-highspeed"): "极速, Agent",
    ("稀宇科技 MiniMax","MiniMax-M2.5"): "Agent, 中文, 长文本",
    ("稀宇科技 MiniMax","MiniMax-M2.5-highspeed"): "极速, Agent",
    ("稀宇科技 MiniMax","MiniMax-M2-her"): "情感陪伴, 角色扮演, 中文",
    ("稀宇科技 MiniMax","MiniMax-01"): "长文本, 开源",
    ("稀宇科技 MiniMax","MiniMax-Text-01"): "长文本, 开源",
    # 阿里通义 Qwen
    ("阿里通义 Qwen","qwen3.7-max"): "代码, 推理, 多模态, 长文本, Agent",
    ("阿里通义 Qwen","qwen3-max"): "代码, 推理, Agent, 中文",
    ("阿里通义 Qwen","qwen3-plus"): "均衡, 代码, 长文本, 低成本",
    ("阿里通义 Qwen","qwen3-flash"): "极速, 低成本, 长文本",
    ("阿里通义 Qwen","qwen-long"): "长文本, 低成本, 文档理解",
    ("阿里通义 Qwen","qwen-turbo"): "极速, 低成本, 中文",
    ("阿里通义 Qwen","qwen3-omni-flash"): "多模态, 语音",
    # 腾讯混元 Hunyuan
    ("腾讯混元 Hunyuan","Hy4 preview"): "推理, 多模态, 长文本, 中文",
    ("腾讯混元 Hunyuan","Hy3"): "中文, 均衡, 长文本",
    ("腾讯混元 Hunyuan","Hy3 preview"): "中文, 长文本",
    ("腾讯混元 Hunyuan","hunyuan-T1-latest"): "推理, 数学, 中文",
    ("腾讯混元 Hunyuan","hunyuan-turbos-latest"): "极速, 低成本, 中文",
    ("腾讯混元 Hunyuan","hunyuan-pro"): "中文, 长文本, 知识问答",
    ("腾讯混元 Hunyuan","hunyuan-standard-256k"): "长文本, 中文",
    ("腾讯混元 Hunyuan","hunyuan-standard"): "中文, 低成本",
    ("腾讯混元 Hunyuan","hunyuan-lite"): "低成本, 中文",
    # 百度文心 ERNIE
    ("百度文心 ERNIE","ERNIE 5.1"): "中文, 知识问答, 推理",
    ("百度文心 ERNIE","ERNIE 5.0"): "中文, 知识问答, 推理",
    ("百度文心 ERNIE","ERNIE X1 Turbo"): "推理, 中文, 低成本",
    ("百度文心 ERNIE","ERNIE X1"): "推理, 数学, 中文",
    ("百度文心 ERNIE","ERNIE 4.5 Turbo VL"): "多模态, 视觉, 中文",
    ("百度文心 ERNIE","ERNIE 4.5"): "中文, 知识问答",
    ("百度文心 ERNIE","ERNIE 4.5 Turbo"): "低成本, 中文, 长文本",
    ("百度文心 ERNIE","ERNIE 4.0"): "中文, 知识问答",
    ("百度文心 ERNIE","ERNIE 3.5"): "中文, 低成本",
    ("百度文心 ERNIE","ERNIE Speed"): "极速, 低成本, 中文",
    ("百度文心 ERNIE","ERNIE Lite"): "低成本, 中文",
    ("百度文心 ERNIE","ERNIE Tiny"): "极速, 低成本, 中文",
    # 字节豆包 Doubao
    ("字节豆包 Doubao","Doubao-seed-2.1-pro"): "多模态, 推理, 长文本, 中文",
    ("字节豆包 Doubao","Doubao-seed-2.1-turbo"): "均衡, 多模态, 低成本",
    ("字节豆包 Doubao","Doubao-seed-2.0-pro"): "多模态, 长文本, 中文",
    ("字节豆包 Doubao","Doubao-seed-2.0-lite"): "低成本, 极速, 多模态",
    ("字节豆包 Doubao","Doubao-seed-2.0-mini"): "极速, 低成本",
    ("字节豆包 Doubao","Doubao-1.5-pro-32k"): "中文, 知识问答, 低成本",
    ("字节豆包 Doubao","Doubao-1.5-pro-256k"): "长文本, 中文",
    ("字节豆包 Doubao","Doubao-1.5-lite"): "极速, 低成本, 中文",
    # 小米 MiMo
    ("小米 MiMo","MiMo-V2.6-Pro(≤256K)"): "推理, 代码, 开源",
    ("小米 MiMo","MiMo-V2.6-Pro(256K-1M)"): "推理, 代码, 长文本",
    ("小米 MiMo","MiMo-V2.6-Pro-UltraSpeed"): "代码, 极速",
    ("小米 MiMo","MiMo-V2.6-Flash"): "代码, 极速, 低成本",
    ("小米 MiMo","MiMo-V2-Omni"): "多模态, 视觉, 语音",
    ("小米 MiMo","MiMo-V2-Flash"): "推理, 极速, 低成本",
    ("小米 MiMo","MiMo-V2-TTS"): "语音",
    # Anthropic Claude
    ("Anthropic Claude","Claude Opus 5"): "代码, Agent, 推理, 长任务",
    ("Anthropic Claude","Claude Sonnet 5"): "均衡, 代码, Agent",
    ("Anthropic Claude","Claude Haiku 4.5"): "极速, 低成本, 代码",
    ("Anthropic Claude","Claude Fable 5"): "创意写作, 长文本",
    ("Anthropic Claude","Claude Mythos 5"): "推理, 代码, Agent",
    ("Anthropic Claude","Claude Opus 4.8"): "代码, Agent, 推理",
    ("Anthropic Claude","Claude Opus 4.7"): "代码, Agent, 推理",
    ("Anthropic Claude","Claude Sonnet 4.6"): "均衡, 代码, Agent",
    ("Anthropic Claude","Claude Sonnet 4.5"): "代码, Agent, 均衡",
    ("Anthropic Claude","Claude Haiku 3.5"): "极速, 低成本",
    # Google Gemini
    ("Google Gemini","Gemini 3.1 Pro"): "多模态, 长文本, 推理, 视频理解",
    ("Google Gemini","Gemini 3 Pro"): "多模态, 长文本, 推理, 视频理解",
    ("Google Gemini","Gemini 3.8 Flash"): "多模态, 极速, 低成本",
    ("Google Gemini","Gemini 3.7 Flash"): "多模态, 极速, 低成本",
    ("Google Gemini","Gemini 3.6 Flash"): "多模态, 极速, 低成本",
    ("Google Gemini","Gemini 3.5 Flash"): "多模态, 长文本, 均衡",
    ("Google Gemini","Gemini 3.5 Flash-Lite"): "极速, 低成本, 多模态",
    ("Google Gemini","Gemini 2.5 Pro"): "多模态, 长文本, 推理, 代码",
    ("Google Gemini","Gemini 2.5 Flash"): "多模态, 均衡, 低成本",
    ("Google Gemini","Gemini 2.5 Flash-Lite"): "极速, 低成本",
    # OpenAI
    ("OpenAI","GPT-5"): "代码, Agent, 推理, 多模态",
    ("OpenAI","GPT-5 mini"): "均衡, 低成本, 代码",
    ("OpenAI","GPT-5 nano"): "极速, 低成本",
    ("OpenAI","GPT-4.1"): "代码, 长文本, 指令遵循",
    ("OpenAI","GPT-4.1 mini"): "代码, 长文本, 低成本",
    ("OpenAI","GPT-4.1 nano"): "极速, 低成本",
    ("OpenAI","GPT-4o"): "多模态, 语音",
    ("OpenAI","GPT-4o mini"): "多模态, 低成本, 极速",
    ("OpenAI","o3"): "推理, 数学, 代码",
    ("OpenAI","o3-pro"): "推理, 数学",
    ("OpenAI","o4-mini"): "推理, 数学, 低成本",
    ("OpenAI","o1"): "推理, 数学, 代码",
    # xAI Grok
    ("xAI Grok","grok-4.7"): "推理, 代码, 实时检索",
    ("xAI Grok","grok-4.6"): "推理, 代码, 实时检索",
    ("xAI Grok","grok-4.5"): "推理, 代码, 实时检索",
    ("xAI Grok","grok-4.3"): "推理, 代码, 实时检索, 长文本",
    ("xAI Grok","grok-4.20-0309-reasoning"): "推理, 数学, 代码",
    ("xAI Grok","grok-4.20-0309-non-reasoning"): "通用, 极速",
    ("xAI Grok","grok-4.20-0309-multi-agent"): "Agent, 多模态",
    ("xAI Grok","grok-build-0.1"): "代码, Agent",
}

def caps_of(vendor, model):
    return CAPS.get((vendor, model), "")

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in R:
        r["偏向能力"] = caps_of(r["厂商"], r["模型"])
        w.writerow({k: r.get(k, "") for k in COLS})

print("written rows:", len(R), "| caps mapped:", sum(1 for r in R if r["偏向能力"]))
