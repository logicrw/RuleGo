# Clash / Mihomo 智能分流配置与规则集

基于 RuleGo 维护的 Clash / Clash Verge Rev / Mihomo 配置文件与分流规则集。

---

## 📁 目录结构

```
Clash/
├── Sample.yaml          # Clash Verge Rev / Mihomo 完整配置模板
├── Ruleset/             # 预转换的 YAML 规则集 (domain / ipcidr / classical)
│   ├── ai-extra.yaml    # OpenAI, Claude, Grok, Cursor 等海外 AI 服务
│   ├── gemini.yaml      # Google Gemini 规则
│   ├── crypto.yaml      # 币安, OKX, Bybit 等加密货币及 Web3 资讯
│   ├── proxy-extra.yaml # 自定义代理扩展
│   ├── direct-extra.yaml# 自定义直连扩展
│   └── ...              # blackmatrix7 常用流媒体与常用服务规则
├── Script/
│   └── convert.py       # 将 Surge list 及 blackmatrix7 规则转为 YAML
└── README.md
```

---

## 🚀 快速上手

1. 复制 `Clash/Sample.yaml`。
2. 将 `proxy-providers` 下的 `YOUR_SUBSCRIPTION_URL_1` 替换为你的机场订阅链接。
3. 导入 Clash Verge Rev 或 Mihomo 内核客户端即可开箱即用。

---

## 🔄 规则维护与更新

RuleGo 是统一的规则源头（SSOT）：
- **AI 规则**：`Surge/Ruleset/Extra/AI.list`
- **Gemini 规则**：`Surge/Ruleset/Extra/GenAI/Google.list`
- **Crypto 规则**：`Surge/Ruleset/Extra/Crypto.list`

### 现代 Clash Meta / Mihomo 用户：
可以直接使用 `behavior: classical` + `format: text` 原生引用 `Surge/Ruleset/` 下的 `.list` 文件，无需任何转换。

### 传统 Clash / 本地 YAML 用户：
在仓库根目录下运行：
```bash
python3 Clash/Script/convert.py
```
脚本会自动读取 `Surge/Ruleset/` 的规则及上游源，并在 `Clash/Ruleset/` 中生成/更新对应的 YAML 规则。
