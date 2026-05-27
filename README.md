# UC Trading — SGX USD/CNH 日频宏观因子策略

基于宏观因子模型的 SGX UC（美元/离岸人民币）期货日频交易策略。
使用免费数据源（Yahoo Finance + FRED + AKShare），模块化架构，
支持 **static 加权 + walk-forward Ridge + 单因子归因** 三种回测视角。

## 当前回测结果（2017-01 ~ 2026-05，6 因子 + 0.20 soft deadband）

| 指标 | Static (config 权重) | Walk-forward Ridge |
|---|---|---|
| **Sharpe** | **1.89** | 1.31 |
| 年化收益 | +6.88% | +4.99% |
| 年化波动 | 3.54% | 3.77% |
| **最大回撤** | **-2.36%** | -2.86% |
| Calmar | **2.92** | 1.74 |
| 在场时间 | 79% | 75% |
| 年化换手 | 48x | 76x |
| 最终净值 | 1.91 | 1.58 |

> 注：static 权重在样本内挑选过，**真实 OOS 预期更接近 WF 的 1.0–1.4 区间**；
> 详见末尾的"诚实评估"。

## 快速开始

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/run_backtest.py -v
```

```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/run_backtest.py -v
```

控制台打印 static + WF + 单因子归因表格；`output/` 生成 6 个 CSV + 5 张 PNG。

## 策略逻辑

**6 个核心宏观因子** → 每日做 252 天滚动 z-score（裁剪 ±3）→ 按 config
权重加权合成 composite signal → **deadband 阈值过滤**弱信号 → 波动率
目标 + VIX 过滤 → 向量化回测。

### 当前激活的因子

| 因子 | 经济逻辑 | 权重 | 单因子 Sharpe |
|---|---|---|---|
| `dxy_momentum` | DXY 20 日动量；美元强 → UC ↑ | +1.0 | **1.21** |
| `copper_momentum` | 铜 20 日动量；铜强 → 中国景气 → CNH 强 → UC ↓ | **-0.5** | **1.21** |
| `rate_diff_level` | UST10Y − CGB10Y 水平；高利差 → carry favorable | +1.0 | **1.01** |
| `gold_momentum` | 黄金 20 日动量；金强 → USD 弱 → UC ↓ | **-0.5** | **1.00** |
| `vix_change` | VIX 5 日变化；避险 → CNH 走弱 → UC ↑ | +0.5 | 0.77 |
| `bitcoin_momentum` | BTC 20 日动量；风险偏好代理 | **-0.5** | 0.33 |

`bitcoin_momentum` 单独看 Sharpe 弱，但贡献 MDD 削减 ~1pp，
作为**回撤抑制器**保留。详见 `git log` 中的 ablation 记录。

### 归档因子（disabled，保留代码以便消融）

| 因子 | 关闭原因 |
|---|---|
| `rate_diff_momentum` | 利差**动量**信号 Sharpe 仅 0.43，水平信号 (`rate_diff_level`) 完全替代 |
| `cnh_mean_revert` | UC 主要走势是趋势而非均值回归，Sharpe -0.31 |
| `us_curve_slope` | 2s10s 斜率动量在 bull/bear-steepening 间方向反复，Sharpe -0.44 |

### Deadband（信号阈值）

`signal.threshold = 0.20`，`deadband_mode = "soft"`：
- 当 `|composite| < 0.20`，仓位 = 0（"中间信号不强时空仓"）
- 当 `|composite| > 0.20`，仓位 = `sign(s) × (|s|-0.20)/(1-0.20)`，线性放大到 ±1

`soft` 模式让中等信号给较小仓位，强信号给较大仓位——避免硬阈值附近的
跳变。`sweep_threshold.py` 的扫描显示这个组合是全网格最优。

## 项目结构

```
uc-trading/
├── config/config.yaml             所有参数：数据源、因子、信号、回测、风控
├── data/{raw,processed}/          CSV 数据缓存（默认 TTL 1 天）
├── output/                        回测产物：CSV + PNG
├── src/
│   ├── config.py                  配置加载
│   ├── data/
│   │   ├── loaders.py             Yahoo / FRED / AKShare 抓取 + 重试 + 缓存
│   │   └── preprocess.py          日期对齐、^TNX×10 归一化、ffill
│   ├── features/factors.py        9 个因子计算（含归档）
│   ├── signals/
│   │   ├── model.py               滚动 z-score
│   │   ├── combine.py             加权合成 + signal_to_position(deadband)
│   │   ├── walk_forward.py        滚动 Ridge 回归
│   │   └── attribution.py         单因子回测
│   ├── backtest/
│   │   ├── engine.py              向量化回测引擎
│   │   └── metrics.py             Sharpe / MDD / Calmar / 换手率
│   ├── risk/sizing.py             波动率目标 + VIX 过滤
│   └── viz/plots.py               净值/回撤/仓位/因子/归因/WF 权重
├── scripts/
│   ├── run_backtest.py            主入口：static + WF + attribution
│   ├── sweep_walk_forward.py      WF 超参数网格 (window × refit × alpha)
│   └── sweep_threshold.py         Deadband 阈值 × {hard, soft} 扫描
├── tests/                         37 个 pytest 单测（不依赖网络）
└── requirements.txt
```

## 数据源

| 来源 | 用途 | 认证 | 备注 |
|---|---|---|---|
| Yahoo Finance | `CNY=X`、DXY、`^TNX`、VIX、`^GSPC`、`HG=F`、`000300.SS`、`GC=F`、`BTC-USD` | 无 | `CNH=X` 历史空，用 `CNY=X` 作为 UC 代理 |
| FRED（`pandas-datareader`） | `SOFR`、`DGS2` | 无 | 2Y 国债曲线斜率信号 |
| AKShare | 中债 10 年期国债收益率、SHIBOR | 无 | CGB 端点有 ~500 天分页限制，loader 自动分块 |

数据缓存为 CSV 在 `data/raw/`。`--no-cache` 强制全量重抓。

> ⚠️ **UC 代理数据局限**：`CNY=X` 是在岸 USD/CNY，PBoC 管理浮动；
> 与 SGX UC（离岸 USD/CNH）日内 basis 通常 < 100 pips，对**日频方向**
> 策略影响有限，但极端事件（如 811 汇改、HIBOR squeeze）会发散。
> 替换真实 UC 数据只需改 `loaders.fetch_yahoo` 一处。

## 三种执行模式

`scripts/run_backtest.py` 一次跑出所有视角：

### 1. Static（基线）— 总是运行
用 `config.yaml` 里写死的权重做加权合成。优点：可解释、稳定、低换手。
缺点：权重是人挑的，有 in-sample 偏见。

### 2. Walk-forward Ridge — 可选
滚动窗口 Ridge 回归，目标变量是次日 UC log return。
对 regime 变化有适应能力，但**真正可信的 OOS 估计**。

`signal.walk_forward` 块：
- `window_days: 504` — 训练窗口（~24 个月）
- `refit_every: 21` — 重训频率（~月）
- `alpha: 1.0` — L2 正则

### 3. Attribution — 可选
每个因子单独回测，给出每个因子的 Sharpe / MDD / 换手。
判断"哪些因子赚钱、哪些拖后腿"的核心工具。

## 超参数扫描

```powershell
# Walk-forward 三维网格（5×4×5 = 100 配置）
python scripts/sweep_walk_forward.py -v

# Deadband 阈值 × hard/soft
python scripts/sweep_threshold.py -v
```

输出 CSV + 热图 PNG 到 `output/sweep_*`。
扫描评估期默认 **2020+**（前 3 年作为暖启动 + 早期数据被剔除）。

## 配置要点

| 块 | 关键字段 | 说明 |
|---|---|---|
| `data` | `start_date`、`cache_ttl_days` | 数据起点 + 缓存策略 |
| `data.tickers` / `data.fred` / `data.akshare` | 各源开关 | 关掉某源后下游因子会自动 skip |
| `factors.<name>` | `enabled`、`weight`、`lookback` | 每因子独立开关 |
| `factors.zscore_window` | 252 | 滚动标准化窗口 |
| `signal.threshold` | 0.20 | Deadband 阈值，0 = 始终持仓 |
| `signal.deadband_mode` | `"soft"` | soft / hard |
| `signal.walk_forward.*` | 见上 | WF Ridge 超参 |
| `attribution.enabled` | true | 单因子回测开关 |
| `backtest` | `signal_lag_days: 1`、`cost_bps: 1.0` | 信号 lag + 单边成本 |
| `risk` | `vol_target_annual: 0.10`、`vix_filter_threshold: 30` | 风控参数 |

## 测试

```powershell
pytest tests/ -q
```

37 个测试，**完全不依赖网络**——使用合成数据验证因子、信号合成、
回测引擎、风控逻辑。新增因子/回测改动后必跑。

## 实盘信号自动化（GitHub Actions）

仓库内置了一个每日跑的 workflow：`.github/workflows/daily-signal.yml`

**调度**：每周一到周五 UTC 22:00（北京 06:00，美股收盘 ~1 小时后）

**每次运行做的事**：
1. `scripts/daily_signal.py` — 抓最新数据，算今日信号，追加到 `signals/history.csv`
2. `scripts/update_paper_pnl.py` — 用 `history.csv` × 实际 UC 价格回放 paper PnL，更新 `signals/REPORT.md`
3. 自动 commit + push 回主分支

**产物文件**（都在 `signals/` 目录，自动追踪）：

| 文件 | 内容 |
|---|---|
| `latest.json` | 最新一条信号（人类可读） |
| `history.csv` | 历史所有信号的 append-only log |
| `paper_pnl.csv` | 每个交易日的 paper PnL 序列 |
| `stats.json` | 累计 Sharpe / MDD / 胜率等指标 |
| `REPORT.md` | Markdown 摘要，GitHub 上直接可看 |

**手动触发**：在 Actions tab 点 `Run workflow`，或在本地跑：

```powershell
python scripts/daily_signal.py
python scripts/update_paper_pnl.py
```

**注意**：paper trading 用的是 `CNY=X` 在岸现货代理，跟真实 SGX UC 期货
存在 basis 差异——这套追踪是用来**验证因子模型在真实数据上是否还 work**，
而不是模拟真实期货盈亏。

## 诚实评估 / 已知局限

**关于 Sharpe 1.89 的解读**：

- 全期（2017-2026）Sharpe 1.89 是**乐观估计**。Static 权重在样本内挑过。
- 2020+ 评估窗口 Sharpe 降到 ~1.67（更接近真实近期 OOS）。
- 走 walk-forward 路径 Sharpe ~1.10–1.36，**这才是更接近实盘的预期**。
- 实盘扣滑点 + CNH-CNY basis 后预期 **Sharpe 0.7–1.0**。

**策略衰减信号**：

- WF Top 配置在 2020-2022 半段 Sharpe ~1.86，2023-2026 半段降到 ~0.67。
- 真实 regime 已变化（PBoC 加强汇率管理 + 中美利率周期错配）。
- 当前因子集对 2024+ 区间盘整环境敏感度不足。

**数据局限**：

- UC 代理是 `CNY=X` 在岸现货，非真实 SGX UC 期货。
- AKShare CGB 数据只到 ~2025-01 后偶尔失效，loader 用分块兜底。
- BTC 是 24/7 数据，对齐到工作日时取周末前最后报价。

**结构局限**：

- 节假日未做中美港新四市场交叉校准（用 `pd.bdate_range` 简化）。
- 纯向量化回测：未模拟滑点、部分成交、隔夜资金、换月成本。
- Walk-forward Ridge 用 OLS 目标（次日 log return），未做信号 Sharpe 优化。

## 路线图（可选）

| 方向 | 预期收益 | 成本 |
|---|---|---|
| 接 Tushare/SGX 真实 UC 期货数据 | 消除 basis 偏差 | 需 token，1 个新 fetcher |
| Regime detection（高波 vs 区间） | 分段权重，可能恢复 1.5+ Sharpe | 1 周开发 |
| 因子衰减监控 dashboard | 早期识别失效因子 | 1 个脚本 |
| 加 PBoC 中间价偏离因子 | 接入 SAFE/中行公开 daily fix | 1 个数据源 |
| 实盘对接 / paper trading | 验证执行成本假设 | 需期货账户 |

---

数据 / 因子 / 信号 / 回测 / 风控**完全解耦**，新增任意一块都不需要改其他模块。
策略本身不是终点——这套架构是为了让你**快速试错**新想法。
