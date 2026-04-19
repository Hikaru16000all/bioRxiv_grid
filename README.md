# bioRxiv_grid

一个可扩展的 bioRxiv 预印本扫描框架，支持三步流水线：

1. 扫描最新 bioRxiv 预印本。
2. 根据关键词或任务描述做筛选（可选接入大模型 API 提升语义匹配）。
3. 自动总结入选论文（可选，需大模型 API）。

---

## 功能概览

- **最新预印本扫描**
  - 通过 `https://api.biorxiv.org/details/...` 拉取指定时间窗口内的新论文。
  - 支持 `days_back`、`end_lag_days` 和 `max_records` 控制抓取范围。

- **筛选**
  - 关键词筛选：标题/摘要中出现关键词即命中。
  - 语义筛选（可选）：调用兼容 OpenAI Chat Completions 的 API，对“目标描述”进行 0~1 相关性打分。

- **总结（可选）**
  - 对入选论文生成中文 3~5 句摘要（研究问题、方法、结论）。

- **输出**
  - 统一输出 JSON，包含 DOI、标题、摘要、分类、匹配关键词、相关性分数、总结等字段。

---

## 快速开始

### 1) 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) 准备配置

复制并编辑示例配置：

```bash
cp configs/example.json configs/my_run.json
```

### 3) 运行

```bash
biorxiv-grid --config configs/my_run.json --out outputs/latest_results.json
```

运行后会输出：

- 处理后的论文总数
- 结果文件路径

---

## 配置说明（`configs/*.json`）

```json
{
  "days_back": 1,
  "end_lag_days": 1,
  "max_records": 200,
  "keywords": ["single-cell", "CRISPR"],
  "description": "与你关心方向相关的一段描述",
  "relevance_threshold": 0.65,
  "llm_relevance": {
    "enabled": false,
    "api_key": null,
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4.1-mini",
    "timeout_sec": 40
  },
  "llm_summary": {
    "enabled": false,
    "api_key": null,
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4.1-mini",
    "timeout_sec": 40
  }
}
```

### 关键字段

- `days_back`: 回溯天数（例如 1=最近一天）。
- `end_lag_days`: 结束日期相对今天回退天数（默认 1，即按“昨天”为结束日期，避免当日数据未整理完成）。
- `max_records`: 最大抓取条数。
- `keywords`: 关键词列表（为空则不做关键词过滤）。
- `description`: 语义筛选目标描述。
- `relevance_threshold`: LLM 相关性阈值（0~1）。
- `llm_relevance.enabled`: 是否启用 LLM 语义筛选。
- `llm_summary.enabled`: 是否启用 LLM 总结。

> 两个 LLM 模块可独立开关：只筛选不总结 / 只总结不过滤 / 都开 / 都关 都支持。

---

## API Key 传入方式

可写在配置文件，也可通过环境变量覆盖：

```bash
export BIORXIV_GRID_RELEVANCE_API_KEY="..."
export BIORXIV_GRID_SUMMARY_API_KEY="..."
```

---

## 目录结构

```text
.
├── configs/
│   └── example.json
├── src/biorxiv_grid/
│   ├── biorxiv_client.py
│   ├── cli.py
│   ├── config.py
│   ├── filter_engine.py
│   ├── llm.py
│   ├── models.py
│   ├── pipeline.py
│   └── summarizer.py
└── README.md
```

---

## 后续可扩展建议

- 增加定时任务（cron / GitHub Actions）实现每日自动扫描。
- 增加邮件/Slack/飞书通知。
- 把 JSON 输出同步到数据库或向量库。
- 支持 medRxiv、多源聚合与去重。
