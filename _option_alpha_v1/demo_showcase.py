"""
系统演示脚本 - 快速展示核心功能
Demo Script - Quick Showcase of Core Features
"""

def demo_portfolio_optimization():
    """演示投资组合优化"""
    print("\n" + "="*70)
    print("📊 演示1: 投资组合优化")
    print("="*70 + "\n")
    
    from portfolio_optimizer import PortfolioOptimizer
    
    # 创建优化器
    optimizer = PortfolioOptimizer(risk_free_rate=0.03)
    
    # 定义资产
    assets = [
        {
            'name': 'SPY (标普500)',
            'ticker': 'SPY',
            'type': 'stock',
            'price': 450,
            'expected_return': 0.10,
            'volatility': 0.18
        },
        {
            'name': 'QQQ (纳斯达克)',
            'ticker': 'QQQ',
            'type': 'stock',
            'price': 350,
            'expected_return': 0.12,
            'volatility': 0.22
        },
        {
            'name': 'Call Spread SPY',
            'ticker': 'SPY',
            'type': 'option',
            'price': 450,
            'expected_return': 0.15,
            'volatility': 0.20,
            'strategy': 'call_spread'
        }
    ]
    
    # 优化组合
    portfolio = optimizer.optimize_portfolio(assets, [], total_capital=100000)
    
    print(f"💰 总资本: ${portfolio['total_capital']:,.0f}")
    print(f"\n📈 投资组合指标:")
    print(f"   期望收益率: {portfolio['expected_return']*100:.2f}%")
    print(f"   波动率:    {portfolio['volatility']*100:.2f}%")
    print(f"   夏普比率:  {portfolio['sharpe_ratio']:.2f}")
    
    print(f"\n📋 持仓分配:")
    for i, pos in enumerate(portfolio['positions'], 1):
        print(f"\n   {i}. {pos['asset']}")
        print(f"      权重:     {pos['weight']*100:>5.1f}%")
        print(f"      金额:     ${pos['amount']:>10,.0f}")
        print(f"      数量:     {pos['quantity']:>10.2f}")
        print(f"      期望收益: {pos['expected_return']*100:>5.1f}%")

def demo_greeks_analysis():
    """演示Greeks分析"""
    print("\n" + "="*70)
    print("🎲 演示2: Greeks敏感性分析")
    print("="*70 + "\n")
    
    from portfolio_optimizer import GreeksAnalyzer
    
    # 模拟期权推荐
    option_rec = {
        'strategy': 'call_spread',
        'strike': 450,
        'expiry_date': '2024-06-15',
        'greeks': {
            'delta': 0.65,
            'gamma': 0.018,
            'theta': -0.0015,
            'vega': 0.045,
            'rho': 0.012
        }
    }
    
    analysis = GreeksAnalyzer.analyze_greeks(option_rec)
    
    print(f"策略: {option_rec['strategy'].upper()}")
    print(f"行权价: ${option_rec['strike']}")
    print(f"到期日: {option_rec['expiry_date']}\n")
    
    print("📊 Greeks 值:")
    print(f"   Δ (Delta)  = {analysis['delta']:>7.3f}  →  价格敏感性 (方向风险)")
    print(f"   Γ (Gamma)  = {analysis['gamma']:>7.4f}  →  加速度 (伽玛风险)")
    print(f"   Θ (Theta)  = {analysis['theta']:>7.4f}  →  时间衰减 (时间成本)")
    print(f"   Ν (Vega)   = {analysis['vega']:>7.4f}  →  波动率敏感性")
    print(f"   Ρ (Rho)    = {analysis['rho']:>7.4f}  →  利率敏感性")
    
    print(f"\n⚠️  风险因素:")
    if analysis['risk_factors']:
        for i, factor in enumerate(analysis['risk_factors'], 1):
            print(f"   {i}. {factor}")
    else:
        print(f"   ✓ 无明显风险因素")
    
    print(f"\n📈 风险评分: {analysis['risk_score']}/5")
    if analysis['risk_score'] <= 2:
        print("   风险等级: 🟢 低")
    elif analysis['risk_score'] <= 3:
        print("   风险等级: 🟡 中")
    else:
        print("   风险等级: 🔴 高")

def demo_market_detection():
    """演示市场状态检测"""
    print("\n" + "="*70)
    print("📈 演示3: 实时市场状态检测")
    print("="*70 + "\n")
    
    from auto_market_strategy import MarketRegimeDetector
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # 创建示例数据
    detector = MarketRegimeDetector()
    
    # 生成模拟价格数据
    dates = pd.date_range(end=datetime.now(), periods=250)
    
    # 牛市场景：上升趋势
    prices_bull = 450 + np.cumsum(np.random.randn(250) * 1.5 + 0.5)
    df_bull = pd.DataFrame({'Close': prices_bull}, index=dates)
    result_bull = detector.detect_regime(df_bull)
    
    # 熊市场景：下降趋势
    prices_bear = 450 + np.cumsum(np.random.randn(250) * 1.5 - 0.5)
    df_bear = pd.DataFrame({'Close': prices_bear}, index=dates)
    result_bear = detector.detect_regime(df_bear)
    
    # 高波动率场景
    prices_high_vol = 450 + np.cumsum(np.random.randn(250) * 3)
    df_high_vol = pd.DataFrame({'Close': prices_high_vol}, index=dates)
    result_high_vol = detector.detect_regime(df_high_vol)
    
    scenarios = [
        ("牛市场景", result_bull, prices_bull[-1]),
        ("熊市场景", result_bear, prices_bear[-1]),
        ("高波动场景", result_high_vol, prices_high_vol[-1])
    ]
    
    for scenario_name, result, price in scenarios:
        print(f"\n{scenario_name}:")
        print(f"   当前价格: ${price:,.2f}")
        print(f"   市场状态: {result['regime']}")
        
        # 状态翻译
        regime_map = {
            'bull_market': '🟢 牛市',
            'bear_market': '🔴 熊市',
            'high_volatility': '🟠 高波动',
            'sideways': '🟡 震荡'
        }
        print(f"   状态图标: {regime_map.get(result['regime'], '❓')}")
        print(f"   信心度:   {result['confidence']:.2%}")
        print(f"   波动率:   {result['volatility']:.2%}")
        print(f"   动量20日: {result['momentum_20']:+.3f}")
        print(f"   动量200日: {result['momentum_200']:+.3f}")

def demo_database_operations():
    """演示数据库操作"""
    print("\n" + "="*70)
    print("🗄️  演示4: 数据库操作")
    print("="*70 + "\n")
    
    from db_manager import AnalysisDatabase
    import os
    
    # 创建测试数据库
    db = AnalysisDatabase("demo_test.db")
    
    # 保存市场分析
    analysis = {
        'regime': 'bull_market',
        'confidence': 0.85,
        'momentum_20': 0.05,
        'momentum_50': 0.02,
        'momentum_200': 0.03,
        'volatility': 0.18,
        'current_price': 450.5
    }
    
    db.save_market_analysis('SPY', analysis)
    print("✓ 保存市场分析: SPY")
    
    # 保存期权推荐
    recommendation = {
        'strategy': 'call_spread',
        'type': 'call',
        'strike': 450,
        'expiry_date': '2024-06-15',
        'expiry_days': 45,
        'position_size': 0.05,
        'risk_level': 'medium',
        'target_price': 460,
        'support': 445,
        'resistance': 455,
        'rationale': '看涨信号明显，建议买入看涨期权',
        'greeks': {'delta': 0.65, 'gamma': 0.018, 'theta': -0.0015, 'vega': 0.045, 'rho': 0.012},
        'iv': 0.18,
        'expected_return': 0.15,
        'sharpe_ratio': 1.2
    }
    
    db.save_option_recommendation('SPY', recommendation)
    print("✓ 保存期权推荐: SPY - call_spread")
    
    # 查询数据
    results = db.get_latest_analysis('SPY', limit=1)
    print(f"\n✓ 查询市场分析: {len(results)} 条记录")
    
    recs = db.get_top_recommendations(limit=5)
    print(f"✓ 查询推荐排行: {len(recs)} 条记录")
    
    tickers = db.get_all_tickers()
    print(f"✓ 查询股票列表: {len(tickers)} 支股票")
    print(f"  股票: {', '.join(tickers)}")
    
    # 清理
    if os.path.exists("demo_test.db"):
        os.remove("demo_test.db")
    print("\n✓ 演示数据库已清理")

def print_system_overview():
    """打印系统概览"""
    overview = """
╔══════════════════════════════════════════════════════════════════════════╗
║               量化交易仪表板 - 系统演示                                  ║
║        Quantitative Trading Dashboard - System Demonstration            ║
╚══════════════════════════════════════════════════════════════════════════╝

【系统架构】

┌─────────────────────────────────────────────────────────────────────┐
│                        浏览器仪表板                                  │
│            http://localhost:8000                                    │
│  • 推荐排行  • 投资组合  • Greeks分析  • 策略热力图                │
└─────────────────────────────────────────────────────────────────────┘
                            ↑    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       FastAPI Web API                               │
│          /api/analyze  /api/recommendations  /api/optimize           │
│          /api/greeks  /api/heat-map  /api/health                    │
└─────────────────────────────────────────────────────────────────────┘
                            ↑    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       分析引擎核心                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ MarketDetector   │  │  OptionPricing   │  │   Portfolio      │ │
│  │ (市场识别)       │  │  (期权定价)      │  │   Optimizer      │ │
│  │                  │  │                  │  │   (组合优化)     │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                            ↑    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      后台任务调度                                   │
│  • 每30分钟自动分析                                                │
│  • 更新推荐列表                                                    │
│  • 计算投资组合                                                    │
└─────────────────────────────────────────────────────────────────────┘
                            ↑    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    数据存储 (SQLite)                               │
│  • 市场分析结果                                                    │
│  • 期权推荐数据                                                    │
│  • 投资组合配置                                                    │
│  • 价格缓存                                                        │
└─────────────────────────────────────────────────────────────────────┘

【核心功能】

1️⃣  自动市场识别
   ├─ 识别市场状态: 牛市 / 熊市 / 高波动 / 震荡
   ├─ 计算信心度和指标
   ├─ 动态调整策略参数
   └─ 实时更新推荐

2️⃣  期权策略推荐
   ├─ Black-Scholes定价
   ├─ Greeks计算 (Delta, Gamma, Theta, Vega, Rho)
   ├─ 自动策略选择 (Call/Put/Spread/...)
   ├─ 风险等级评估
   └─ 头寸规模优化

3️⃣  投资组合优化
   ├─ 多资产配置
   ├─ 最大化夏普比率
   ├─ 风险指标计算 (VaR, Max Drawdown)
   ├─ 权重分配建议
   └─ 性能分析

4️⃣  可视化仪表板
   ├─ 实时数据展示
   ├─ 策略热力图
   ├─ Greeks风险分析
   ├─ 排名推荐列表
   └─ 性能指标图表

【使用流程】

快速开始 (3步):
  1. python run_dashboard.py          # 启动服务
  2. 浏览器打开 http://localhost:8000  # 访问仪表板
  3. 查看推荐和进行优化               # 开始分析

API调用示例:
  import requests
  
  # 获取推荐
  r = requests.get('http://localhost:8000/api/recommendations')
  recs = r.json()['recommendations']
  
  # 分析股票
  r = requests.post('http://localhost:8000/api/analyze/SPY')
  analysis = r.json()
  
  # 优化组合
  r = requests.post(
      'http://localhost:8000/api/optimize-portfolio',
      json={'tickers': ['SPY', 'QQQ'], 'total_capital': 100000}
  )
  portfolio = r.json()

【技术栈】

后端:
  ✓ Python 3.11+
  ✓ FastAPI (异步Web框架)
  ✓ Uvicorn (ASGI服务器)
  ✓ SQLite (数据库)
  ✓ Pandas/NumPy (数据处理)
  ✓ SciPy (数学计算)
  ✓ APScheduler (任务调度)

前端:
  ✓ HTML5
  ✓ CSS3 (Bootstrap 5)
  ✓ JavaScript (原生)
  ✓ Chart.js (图表)
  ✓ Axios (HTTP客户端)

【数据来源】

  • Yahoo Finance (股票数据)
  • 历史波动率计算 (20天标准差 * √252)
  • Black-Scholes模型 (期权定价)
  • 投资组合理论 (组合优化)

【特色优势】

  ✨ 完全自动化 - 无需手工干预
  ✨ 实时更新   - 后台持续分析
  ✨ Greeks优化 - 基于风险敏感性
  ✨ 组合推荐   - 最大化风险调整收益
  ✨ 可视化展现 - 友好的Web界面
  ✨ 开放API    - 支持集成和扩展

【注意事项】

⚠️  本系统仅供学习和研究使用
⚠️  市场数据可能有延迟
⚠️  模型预测不代表实际收益
⚠️  使用前请充分理解相关风险

"""
    print(overview)

def main():
    import sys
    
    print_system_overview()
    
    # 运行演示
    demos = [
        ("市场检测", demo_market_detection),
        ("Greeks分析", demo_greeks_analysis),
        ("投资组合优化", demo_portfolio_optimization),
        ("数据库操作", demo_database_operations),
    ]
    
    for i, (name, func) in enumerate(demos, 1):
        try:
            func()
        except Exception as e:
            print(f"\n❌ 演示 {i} 失败: {e}")
    
    print("\n" + "="*70)
    print("✅ 演示完成！")
    print("="*70)
    print("""
【后续步骤】

1. 启动Web服务:
   python run_dashboard.py

2. 在浏览器打开:
   http://localhost:8000

3. 查看API文档:
   http://localhost:8000/docs

4. 开始使用系统进行分析和优化!

有问题? 查看 README_DASHBOARD.md
""")

if __name__ == "__main__":
    main()
