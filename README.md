# 国内外主流大模型 API 定价对比

采集时间：2026-10-13
数据来源：各厂商官方定价页 + 第三方汇总

## 文件清单

- `llm_pricing.html` — 主交付物。在浏览器中打开即可看到分国内/海外两块的完整对比表。
- `llm_pricing.csv` — 同一份数据的 CSV 形式，方便导入 Excel / Pandas / 数据库做二次分析。
- `llm_pricing.xlsx` — 可下载的 Excel 版：含「说明与折扣政策」页 + 「总表」+ 13 个厂商分表，折扣列高亮。

## 字段说明

每行一条记录，字段为：

1. **厂商**
2. **模型**
3. **计费方式**（按量计费 / 阶梯计费 / Batch 折扣 / 缓存命中折扣等）
4. **上下文长度**
5. **最大输出 Token**
6. **输入单价**（每百万 tokens，官方标牌价）
7. **输出单价**（每百万 tokens，官方标牌价）
8. **缓存命中单价**（每百万 tokens）
9. **折扣**（用户提供的代理 / 渠道折扣政策；阶梯类列全档位）
10. **折后输入单价**（输入标牌价 × 折扣系数）
11. **折后输出单价**（输出标牌价 × 折扣系数）
12. **币种**（¥ 人民币 / $ 美元）
13. **数据来源**

## 折扣政策（用户提供，2026-10-13）

| 厂商系列 | 折扣 | 系数 |
|---|---|---|
| OpenAI | 7.5折 | 0.75 |
| Anthropic / Claude | 7.5折 | 0.75 |
| Gemini | 7折 | 0.70 |
| Grok | 6.5折 | 0.65 |
| DouBao | 9.5折 | 0.95 |
| Qwen | 4.5折（qwen3.7-max 6折 / preview 无折扣） | 0.45 |
| Kimi | 阶梯：≥50万8.5折 / 3万≤月消<50万9折 | 0.90 |
| MiniMax | 5折（官方现时；清单曾8.5折） | 0.50 |
| DeepSeek / V4 | 5折 | 0.50 |
| 智谱 GLM | 阶梯：≥5万9折 / ≥30万85折 / ≥60万8折 | 0.90 |
| 小米 MiMo | 8.8折 | 0.88 |
| 腾讯混元 Hunyuan | 6.5折 | 0.65 |
| 百度文心 ERNIE | 9折 | 0.90 |

**冲突处理说明**
- MiniMax：原始清单写 8.5折，但注明"官方现时5折"，采用 **5折**。
- Kimi：清单"9折"与"月之暗面阶梯（≥50万8.5折 / 3万-50万9折）"一致，采用阶梯。
- 混元（6.5折）、文心（9折，全系列统一记者/直接折扣）已补入折扣清单。
- 阶梯类（GLM / Kimi）的「折后价」按最低档示例（GLM≥5万 9折、Kimi 3万-50万 9折）。

## 重要使用提示

1. 所有价格均为**按量计费（Pay-as-you-go）**的标牌价，不含限时优惠、商务合约价、订阅套餐（Token Plan / Coding Plan 等）。
2. 阶梯计费的模型，输入 / 输出 token 都会按"请求输入长度"对应的整档单价结算。
3. 缓存功能：
   - Anthropic / Google / OpenAI 区分"读取"与"写入"
   - 国内大部分厂商目前以"读取"为主，写入多限时免费
4. 海外币种为美元，国内为人民币。当前参考汇率约 1 $ ≈ 7.2 ¥。
5. 建议下单前到厂商官方定价页二次确认。

## 厂商速览

**国内**：智谱 GLM、DeepSeek、月之暗面 Kimi、稀宇科技 MiniMax、阿里通义千问、腾讯混元、百度文心 ERNIE、字节豆包 Doubao、小米 MiMo

**海外**：Anthropic Claude、Google Gemini、OpenAI GPT / o-series、xAI Grok

## 选型建议

- **极致成本**：豆包 Lite（¥0.10/0.10）、智谱 Flash / 文心 Speed / Lite / Tiny（免费）、Gemini 2.5 Flash-Lite
- **均衡型主力**：Qwen-Plus（¥0.8/2.0）、DeepSeek V3.x、Hunyuan TurboS（¥0.8/2.0）、豆包 1.5-pro、GPT-4.1-mini、Claude Sonnet 4.6
- **旗舰能力**：Claude Opus 5.5、GPT-5.5、Qwen3.7-Max、GLM-5.3、Hunyuan T1、MiniMax M3、Gemini 3.1 Pro
- **代码 / Agent 专化**：Claude Sonnet 5.5、GPT-5.1、Kimi K2.7 Code、Doubao-seed-2.0-code
- **超长上下文**：MiniMax-01（1M）、Qwen-Long（1M）、Gemini 全系（1M）、MiMo-V2.6-Pro（1M）
