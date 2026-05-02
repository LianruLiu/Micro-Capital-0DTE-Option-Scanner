"""
快速启动指南 - 量化交易仪表板
Quick Start Guide - Quantitative Trading Dashboard
"""

def print_logo():
    logo = """
╔════════════════════════════════════════════════════════════════╗
║                  量化交易仪表板 v1.0                           ║
║         Quantitative Trading Dashboard v1.0                   ║
║                                                                ║
║  自动期权策略推荐系统                                          ║
║  Automated Option Strategy Recommendation System              ║
╚════════════════════════════════════════════════════════════════╝
    """
    print(logo)

def print_setup_guide():
    guide = """
【快速安装指南】

1️⃣  环境检查
   ✓ Python 3.11+
   ✓ Windows / Linux / macOS

2️⃣  安装依赖
   命令: pip install -r requirements_web.txt
   
   或手动安装:
   pip install fastapi uvicorn pydantic apscheduler \\
               yfinance pandas numpy scipy matplotlib

3️⃣  验证安装
   python -c "from app import app; print('✓ 应用可以启动')"

4️⃣  启动应用
   python run_dashboard.py
   
   或使用Uvicorn:
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload

5️⃣  访问仪表板
   浏览器打开: http://localhost:8000
   API文档: http://localhost:8000/docs

【文件结构】

核心模块:
  📄 auto_market_strategy.py    - 市场分析和策略推荐引擎
  📄 config.py                  - 配置参数
  📄 db_manager.py              - 数据库管理（SQLite）
  📄 portfolio_optimizer.py      - 投资组合优化算法

Web应用:
  📄 app.py                     - FastAPI应用主程序
  📄 run_dashboard.py           - 启动脚本
  📁 templates/
    └── dashboard.html         - 前端仪表板（HTML/CSS/JS）

文档:
  📄 README_DASHBOARD.md        - 详细使用指南
  📄 requirements_web.txt       - 依赖列表
  📄 QUICKSTART.py              - 本文件

数据:
  📊 analysis_results.db        - SQLite数据库（自动生成）

【系统架构】

┌─────────────────────────────────────────────────────┐
│           浏览器 (HTML/CSS/JavaScript)              │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/WebSocket
                     ↓
┌─────────────────────────────────────────────────────┐
│        FastAPI (uvicorn) - RESTful API               │
│  http://localhost:8000                              │
├─────────────────────────────────────────────────────┤
│  • /api/tickers           - 股票列表                │
│  • /api/analyze/{ticker}  - 分析股票                │
│  • /api/recommendations   - 推荐排行                │
│  • /api/optimize-portfolio- 组合优化                │
│  • /api/greeks/{ticker}   - Greeks分析              │
│  • /api/health            - 系统状态                │
└────┬───────────────────────────┬───────────────────┘
     │                           │
     ↓                           ↓
┌──────────────────────┐  ┌──────────────────────┐
│  分析引擎             │  │  后台任务调度器      │
│ (MarketDetector)    │  │  (APScheduler)      │
│ (StrategyAdjuster)  │  │                    │
│ (OptionPricingEngine)│ │  • 定期更新数据     │
│ (PortfolioOptimizer)│ │  • 计算推荐策略      │
└──────────────────────┘  └──────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────┐
│        数据存储 (SQLite Database)                    │
│  analysis_results.db                                │
├─────────────────────────────────────────────────────┤
│  • market_analysis        - 市场分析结果            │
│  • option_recommendations - 期权推荐                │
│  • portfolio_recommendations - 投资组合推荐          │
│  • price_cache            - 价格缓存                │
└─────────────────────────────────────────────────────┘

【核心功能模块】

1. 市场识别模块 (MarketRegimeDetector)
   ├─ detect_regime()         → 识别市场状态
   └─ 输出: regime, confidence, volatility, momentum

2. 策略调整模块 (DynamicStrategyAdjuster)
   ├─ adjust_strategy()       → 根据市场状态调整策略
   ├─ generate_signals()      → 生成交易信号
   └─ 输出: 持仓、止损、止盈

3. 期权定价模块 (OptionPricingEngine)
   ├─ black_scholes_greeks()  → 计算Greeks
   ├─ generate_option_chain() → 生成期权链
   ├─ recommend_option_strategy() → 推荐策略
   └─ 输出: 期权价格、Greeks、推荐

4. 投资组合优化 (PortfolioOptimizer)
   ├─ optimize_portfolio()    → 最大化夏普比率
   ├─ calculate_portfolio_metrics() → 计算风险指标
   └─ 输出: 权重、收益、波动率

5. 数据管理 (AnalysisDatabase)
   ├─ save_market_analysis()  → 保存分析结果
   ├─ save_option_recommendation() → 保存推荐
   ├─ get_top_recommendations() → 获取排名推荐
   └─ 输出: SQLite查询结果

【API 端点速查表】

获取数据:
  GET  /api/tickers                    → 股票列表
  GET  /api/analysis/{ticker}          → 最新分析
  GET  /api/recommendations            → 推荐排行
  GET  /api/heat-map                   → 热力图数据
  GET  /api/greeks/{ticker}            → Greeks分析
  GET  /api/portfolio                  → 投资组合
  GET  /api/health                     → 系统状态

执行操作:
  POST /api/analyze/{ticker}           → 分析股票
  POST /api/optimize-portfolio         → 优化组合

【关键配置参数】(config.py)

市场状态阈值:
  • bull_threshold.momentum_200 = 0.05 (看涨动量)
  • bear_threshold.momentum_200 = -0.05 (看跌动量)
  • high_volatility_threshold = 0.35 (高波动)

策略参数:
  • bull_market.position_size = 1.0 (满仓)
  • bear_market.position_size = 0.5 (半仓)
  • high_volatility.position_size = 0.3 (轻仓)

期权配置:
  • risk_free_rate = 0.03 (3%无风险利率)
  • time_horizon = 30 (30天分析周期)

【常见任务示例】

任务1: 分析SPY并获取推荐
────────────────────────────
import requests
response = requests.post('http://localhost:8000/api/analyze/SPY')
print(response.json())

任务2: 获取按收益排名的前10个推荐
────────────────────────────────────
import requests
response = requests.get(
    'http://localhost:8000/api/recommendations?limit=10&order_by=expected_return'
)
recs = response.json()['recommendations']
for i, rec in enumerate(recs, 1):
    print(f"{i}. {rec['ticker']} - {rec['strategy']}: "
          f"{rec['expected_return']*100:.1f}% "
          f"(Sharpe: {rec['sharpe_ratio']:.2f})")

任务3: 优化SPY/QQQ的投资组合
──────────────────────────────
import requests
response = requests.post(
    'http://localhost:8000/api/optimize-portfolio',
    json={
        'tickers': ['SPY', 'QQQ'],
        'total_capital': 100000
    }
)
portfolio = response.json()
print(f"期望收益: {portfolio['expected_return']*100:.2f}%")
print(f"波动率: {portfolio['volatility']*100:.2f}%")
print(f"夏普比率: {portfolio['sharpe_ratio']:.2f}")

【故障排除】

问题: 无法导入fastapi
──────────────────────
解决: pip install fastapi uvicorn

问题: 数据库为空
────────────────
解决: 
  1. 等待后台任务完成（初次需要1-2分钟）
  2. 手动调用 POST /api/analyze/SPY
  3. 刷新页面 F5

问题: 仪表板加载缓慢
──────────────────
解决:
  1. 检查网络连接
  2. 查看浏览器开发者工具 (F12)
  3. 检查API响应时间

问题: 优化报错
──────────────
解决:
  1. 确保选择了至少一支股票
  2. 检查资本金额是否有效
  3. 查看后台日志输出

【性能优化建议】

1. 调整后台更新频率
   # app.py 中修改间隔
   scheduler.add_job(background_analysis, 'interval', minutes=30)

2. 限制分析股票数
   # app.py 中修改列表
   tickers = ['SPY', 'QQQ', 'IWM']  # 减少数量

3. 清理旧数据
   # 定期删除超过N天的数据
   DELETE FROM market_analysis WHERE timestamp < datetime('now', '-30 days')

【监控仪表板】

系统状态: http://localhost:8000/api/health
API文档: http://localhost:8000/docs
Swagger UI: http://localhost:8000/redoc

【数据安全】

⚠️  注意事项:
  • 该系统仅供学习和研究使用
  • 不提供实盘交易接口
  • 市场数据来自Yahoo Finance，可能延迟
  • 模型预测不代表实际收益
  • 使用前请充分理解相关风险

【进阶用法】

1. 自定义策略
   编辑 DynamicStrategyAdjuster 中的 adjust_strategy()

2. 修改优化算法
   编辑 PortfolioOptimizer 中的 optimize_portfolio()

3. 扩展数据库
   编辑 AnalysisDatabase 中的 _init_db()

4. 添加新指标
   编辑 MarketRegimeDetector 中的 detect_regime()

【技术栈概览】

后端:
  • Python 3.11+
  • FastAPI (Web框架)
  • Uvicorn (异步服务器)
  • SQLite (数据库)
  • Pandas/NumPy (数据处理)
  • SciPy (数学计算)

前端:
  • HTML5
  • CSS3 (Bootstrap 5)
  • JavaScript (Vanilla)
  • Chart.js (图表库)
  • Axios (HTTP客户端)

【联系与支持】

如有问题，请检查:
  1. 日志输出信息
  2. README_DASHBOARD.md
  3. API文档: /docs
  4. 浏览器控制台 (F12)

【版本信息】

版本: 1.0.0
更新日期: 2024年4月
许可证: 学习使用许可

┌────────────────────────────────────────────────────────┐
│                   祝您使用愉快！                        │
│              Enjoy using Quant Dashboard!             │
└────────────────────────────────────────────────────────┘
"""
    print(guide)

if __name__ == "__main__":
    print_logo()
    print_setup_guide()
    
    # 显示启动命令
    print("\n【立即启动应用】\n")
    print("方式1 - 运行启动脚本:")
    print("  python run_dashboard.py\n")
    print("方式2 - 直接用Uvicorn:")
    print("  uvicorn app:app --host 0.0.0.0 --port 8000 --reload\n")
    print("方式3 - 使用Python:")
    print("  python -c \"from app import app; import uvicorn; "
          "uvicorn.run(app, host='0.0.0.0', port=8000)\"\n")
    
    print("✨ 访问: http://localhost:8000")
    print("📚 文档: http://localhost:8000/docs\n")
