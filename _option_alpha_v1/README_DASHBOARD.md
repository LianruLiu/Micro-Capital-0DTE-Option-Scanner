# 量化交易仪表板 - 自动期权策略推荐系统

## 📊 系统概述

这是一个全面的**自动化期权策略推荐系统**，具有以下核心功能：

### 🎯 核心功能

1. **实时市场分析**
   - 自动检测市场状态（牛市/熊市/高波动/震荡）
   - 计算市场动量和波动率
   - 多周期技术指标分析

2. **自动期权策略推荐**
   - 基于Greeks（Delta/Gamma/Theta/Vega/Rho）的动态优化
   - 自动选择最优的期权类型和策略
   - 风险评级和头寸规模计算

3. **投资组合优化**
   - 多资产配置优化（股票+期权组合）
   - 最大化夏普比率
   - 风险指标计算（VaR、最大回撤）

4. **可视化仪表板**
   - 实时数据展示
   - 策略热力图
   - Greeks风险分析
   - 排名推荐列表

5. **数据库持久化**
   - SQLite存储分析结果
   - 历史数据追踪
   - 推荐结果存档

---

## 🛠️ 安装与配置

### 1. 环境要求

- Python 3.11+
- Windows / Linux / macOS

### 2. 安装依赖

```bash
# 进入项目目录
cd "d:\6_python3_11\Quant\Momentum Strategy Backtesting System"

# 使用Conda激活Python环境
conda activate base  # 或你的Python环境

# 安装Web依赖
pip install -r requirements_web.txt

# 或单独安装（如果上面的失败）
pip install fastapi uvicorn pydantic apscheduler yfinance pandas numpy scipy matplotlib
```

### 3. 项目结构

```
.
├── auto_market_strategy.py       # 核心策略分析引擎
├── config.py                      # 配置文件
├── db_manager.py                  # 数据库管理器
├── portfolio_optimizer.py          # 投资组合优化
├── app.py                          # FastAPI应用
├── run_dashboard.py               # 启动脚本
├── templates/
│   └── dashboard.html             # 前端仪表板
├── requirements_web.txt           # 依赖列表
└── analysis_results.db            # SQLite数据库（自动生成）
```

---

## 🚀 快速开始

### 方式1：启动Web仪表板

```bash
# 启动Web服务
python run_dashboard.py
```

访问地址：
- 📊 **主仪表板**: http://localhost:8000
- 📚 **API文档**: http://localhost:8000/docs
- 🔌 **API Swagger**: http://localhost:8000/redoc

### 方式2：运行演示脚本

```bash
python demo_auto_strategy.py
```

---

## 📊 使用指南

### 仪表板功能说明

#### 1️⃣ 概览 Tab

- **统计卡片**: 显示跟踪股票数、推荐策略数、平均夏普比率、最高收益
- **策略分布图**: 饼图展示不同策略的比例
- **风险分布**: 柱状图显示低/中/高风险策略数量
- **策略热力图**: 矩阵展示每个股票的每个策略评分

#### 2️⃣ 推荐排行 Tab

按期望收益率从高到低排列所有推荐：
- **排名 #**: 相对排序
- **策略**: 推荐的期权策略类型
- **风险等级**: 彩色标签（低/中/高）
- **期望收益**: 年化期望收益百分比
- **夏普比率**: 风险调整后的收益指标
- **详情按钮**: 查看完整信息

#### 3️⃣ 投资组合 Tab

自动计算最优资产配置：

1. 选择要跟踪的股票（可多选）
2. 设定总资本金额
3. 点击"优化组合"
4. 查看：
   - 期望收益率
   - 波动率
   - 夏普比率
   - 每项资产的权重、金额、数量

#### 4️⃣ Greeks分析 Tab

深入分析期权敏感性：

- **Δ (Delta)**: 价格敏感性 → 方向风险
- **Γ (Gamma)**: 加速度 → 波动率风险
- **Θ (Theta)**: 时间衰减 → 持有成本
- **Ν (Vega)**: 波动率敏感性 → 隐含波动率风险
- **Ρ (Rho)**: 利率敏感性 → 利率风险

---

## 🔌 API 接口文档

### 基础URL
```
http://localhost:8000/api
```

### 主要端点

#### 1. 获取股票列表
```
GET /api/tickers

Response:
{
  "tickers": ["SPY", "QQQ", "IWM"],
  "count": 3
}
```

#### 2. 分析单个股票
```
POST /api/analyze/{ticker}

Response:
{
  "success": true,
  "ticker": "SPY",
  "regime": {
    "regime": "bull_market",
    "confidence": 0.85,
    "momentum_20": 0.02,
    "volatility": 0.18
  },
  "option_recommendation": {
    "strategy": "call_spread",
    "strike": 450,
    "expiry_date": "2024-05-31",
    "position_size": 0.05,
    "expected_return": 0.15
  },
  "greeks_analysis": {
    "delta": 0.65,
    "gamma": 0.02,
    "theta": -0.001,
    "vega": 0.05,
    "rho": 0.02
  }
}
```

#### 3. 获取推荐排行
```
GET /api/recommendations?limit=20&order_by=expected_return

Response:
{
  "recommendations": [
    {
      "ticker": "SPY",
      "strategy": "call_spread",
      "strike": 450,
      "expected_return": 0.15,
      "sharpe_ratio": 1.2,
      "risk_level": "low",
      "greeks_delta": 0.65,
      "greeks_gamma": 0.02,
      "iv": 0.18
    }
  ],
  "count": 20
}
```

#### 4. 优化投资组合
```
POST /api/optimize-portfolio

Request:
{
  "tickers": ["SPY", "QQQ"],
  "total_capital": 100000
}

Response:
{
  "expected_return": 0.12,
  "volatility": 0.16,
  "sharpe_ratio": 0.75,
  "positions": [
    {
      "asset": "SPY Stock",
      "type": "stock",
      "weight": 0.5,
      "amount": 50000,
      "quantity": 100
    }
  ]
}
```

#### 5. Greeks分析
```
GET /api/greeks/{ticker}

Response:
{
  "ticker": "SPY",
  "greeks_analysis": [
    {
      "strategy": "call_spread",
      "strike": 450,
      "greeks": {
        "delta": 0.65,
        "gamma": 0.02,
        "theta": -0.001,
        "vega": 0.05,
        "rho": 0.02,
        "risk_factors": []
      }
    }
  ]
}
```

---

## 💡 使用场景

### 场景1：日间交易者
1. 打开仪表板，查看实时推荐排行
2. 选择高夏普比率的策略
3. 查看Greeks确保风险可控
4. 执行交易

### 场景2：投资组合管理员
1. 在"投资组合"Tab选择多支股票
2. 设定总资本
3. 获得最优配置建议
4. 导出配置用于实盘交易

### 场景3：风险分析
1. 打开"Greeks分析" Tab
2. 检查特定策略的风险因素
3. 监控Delta/Gamma/Vega敏感性
4. 调整持仓规模

---

## 🔧 配置与定制

### 修改分析参数

编辑 `config.py`：

```python
# 市场状态识别阈值
MARKET_REGIME_CONFIG = {
    'bull_threshold': {
        'momentum_200': 0.05,      # 修改为自己的阈值
        'momentum_50': 0.02,
        'volatility_max': 0.25
    }
}

# 策略参数
STRATEGY_CONFIG = {
    'bull_market': {
        'fast_ma': 20,
        'slow_ma': 100,
        'stop_loss': 0.05,         # 止损比例
        'take_profit': 0.15,       # 止盈比例
        'position_size': 1.0       # 头寸规模
    }
}

# 期权配置
OPTION_CONFIG = {
    'risk_free_rate': 0.03,        # 无风险利率
    'confidence_levels': [0.68, 0.95, 0.99],
    'time_horizon': 30             # 分析期限（天）
}
```

### 修改后台更新频率

编辑 `app.py` 的 `schedule_background_tasks()` 函数：

```python
# 修改为每10分钟运行一次
scheduler.add_job(background_analysis, 'interval', minutes=10)
```

### 修改跟踪的股票

编辑 `app.py` 的 `background_analysis()` 函数：

```python
tickers = ['SPY', 'QQQ', 'IWM', 'EEM', 'EFA']  # 修改这一行
```

---

## 📈 性能监控

### 监控系统状态
```
GET http://localhost:8000/api/health
```

### 数据库大小
```bash
# 查看数据库大小
dir analysis_results.db
```

### 日志查看
Web服务会输出详细的日志信息：
```
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:后台分析完成: SPY
INFO:保存期权推荐: SPY - call_spread
```

---

## 🐛 常见问题

### Q1: 启动时提示导入错误
**A:** 运行 `pip install -r requirements_web.txt` 安装所有依赖

### Q2: 无法连接到localhost:8000
**A:** 
- 检查防火墙设置
- 确认Python进程正在运行
- 试试 `http://127.0.0.1:8000`

### Q3: 没有显示任何推荐数据
**A:**
- 等待后台分析完成（初次可能需要1-2分钟）
- 点击"推荐排行"Tab中的"刷新"按钮
- 检查 `analysis_results.db` 文件是否存在

### Q4: 如何导出数据？
**A:** 
- 推荐数据保存在 `analysis_results.db`
- 可以使用SQLite工具打开和导出
- 或通过API获取JSON格式数据

---

## 🎯 系统特色

### ✨ 智能化
- ✅ 自动市场识别
- ✅ 动态策略调整
- ✅ Greeks-based优化
- ✅ 投资组合自动配置

### 🔐 可靠性
- ✅ 数据库持久化
- ✅ 错误处理和重试
- ✅ 后台任务调度
- ✅ 健康检查

### 📊 可视化
- ✅ 实时仪表板
- ✅ 策略热力图
- ✅ Greeks风险分析
- ✅ 性能指标显示

### 🚀 性能
- ✅ 异步API
- ✅ 数据缓存
- ✅ 批量分析
- ✅ 后台更新

---

## 📞 技术支持

如有问题或建议，请检查：
1. 日志输出内容
2. 数据库状态
3. API响应内容
4. 浏览器控制台错误

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 🚀 后续改进方向

- [ ] 实时推送通知
- [ ] 实盘交易接口（IB、盈透）
- [ ] 更复杂的投资组合优化算法
- [ ] 机器学习预测模型
- [ ] 多币种支持
- [ ] 移动端应用

---

**最后更新**: 2024年4月
**版本**: 1.0.0
