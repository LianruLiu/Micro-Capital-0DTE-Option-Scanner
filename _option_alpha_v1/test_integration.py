"""
系统集成测试 - 验证所有模块正常工作
Integration Test - Verify All Components
"""

import os
import sys
from pathlib import Path

def test_imports():
    """测试所有模块导入"""
    print("\n" + "="*60)
    print("🔍 测试模块导入")
    print("="*60 + "\n")
    
    tests = [
        ("config", "from config import *"),
        ("auto_market_strategy", "from auto_market_strategy import AutoMarketStrategyBot"),
        ("db_manager", "from db_manager import AnalysisDatabase"),
        ("portfolio_optimizer", "from portfolio_optimizer import PortfolioOptimizer, GreeksAnalyzer"),
        ("fastapi", "import fastapi"),
        ("uvicorn", "import uvicorn"),
        ("apscheduler", "import apscheduler"),
    ]
    
    failed = []
    for name, code in tests:
        try:
            exec(code)
            print(f"  ✓ {name:30} 正常")
        except Exception as e:
            print(f"  ✗ {name:30} 失败: {e}")
            failed.append(name)
    
    return len(failed) == 0

def test_database():
    """测试数据库功能"""
    print("\n" + "="*60)
    print("🗄️  测试数据库")
    print("="*60 + "\n")
    
    try:
        from db_manager import AnalysisDatabase
        
        db = AnalysisDatabase(db_path="test_analysis.db")
        print("  ✓ 数据库初始化成功")
        
        # 测试保存
        test_analysis = {
            'regime': 'bull_market',
            'confidence': 0.85,
            'momentum_20': 0.05,
            'momentum_50': 0.02,
            'momentum_200': 0.03,
            'volatility': 0.18,
            'current_price': 450.5
        }
        
        db.save_market_analysis('SPY', test_analysis)
        print("  ✓ 市场分析保存成功")
        
        # 测试读取
        results = db.get_latest_analysis('SPY', limit=1)
        if results:
            print(f"  ✓ 数据读取成功: {len(results)} 条记录")
        
        # 清理
        if os.path.exists("test_analysis.db"):
            os.remove("test_analysis.db")
        
        return True
    except Exception as e:
        print(f"  ✗ 数据库测试失败: {e}")
        return False

def test_optimizer():
    """测试投资组合优化器"""
    print("\n" + "="*60)
    print("📊 测试投资组合优化")
    print("="*60 + "\n")
    
    try:
        from portfolio_optimizer import PortfolioOptimizer, GreeksAnalyzer
        import numpy as np
        
        optimizer = PortfolioOptimizer()
        print("  ✓ 优化器初始化成功")
        
        # 创建测试资产
        assets = [
            {
                'name': 'SPY Stock',
                'ticker': 'SPY',
                'type': 'stock',
                'price': 450,
                'expected_return': 0.10,
                'volatility': 0.18
            },
            {
                'name': 'QQQ Stock',
                'ticker': 'QQQ',
                'type': 'stock',
                'price': 350,
                'expected_return': 0.12,
                'volatility': 0.22
            }
        ]
        
        portfolio = optimizer.optimize_portfolio(assets, [], total_capital=100000)
        
        if portfolio['success']:
            print("  ✓ 优化成功")
            print(f"    - 期望收益: {portfolio['expected_return']*100:.2f}%")
            print(f"    - 波动率: {portfolio['volatility']*100:.2f}%")
            print(f"    - 夏普比率: {portfolio['sharpe_ratio']:.2f}")
            print(f"    - 持仓数: {len(portfolio['positions'])} 个")
            return True
        else:
            print(f"  ✗ 优化失败: {portfolio['summary']}")
            return False
    
    except Exception as e:
        print(f"  ✗ 优化器测试失败: {e}")
        return False

def test_api():
    """测试API健康状态"""
    print("\n" + "="*60)
    print("🌐 测试API集成")
    print("="*60 + "\n")
    
    try:
        from app import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        print("  ✓ FastAPI应用加载成功")
        
        # 测试健康检查
        response = client.get("/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 健康检查通过")
            print(f"    - 状态: {data.get('status')}")
            print(f"    - 跟踪股票: {data.get('tickers_tracked', 0)} 支")
        else:
            print(f"  ✗ 健康检查失败: {response.status_code}")
            return False
        
        # 测试股票列表端点
        response = client.get("/api/tickers")
        if response.status_code == 200:
            print("  ✓ 股票列表端点正常")
        
        return True
    
    except Exception as e:
        print(f"  ✗ API测试失败: {e}")
        return False

def test_market_analyzer():
    """测试市场分析器"""
    print("\n" + "="*60)
    print("📈 测试市场分析器")
    print("="*60 + "\n")
    
    try:
        from auto_market_strategy import MarketRegimeDetector
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        detector = MarketRegimeDetector()
        print("  ✓ 市场检测器初始化成功")
        
        # 创建模拟数据
        dates = pd.date_range(end=datetime.now(), periods=250)
        prices = 450 + np.cumsum(np.random.randn(250) * 2)
        df = pd.DataFrame({
            'Close': prices
        }, index=dates)
        
        result = detector.detect_regime(df)
        
        if 'regime' in result:
            print("  ✓ 市场状态检测成功")
            print(f"    - 状态: {result['regime']}")
            print(f"    - 信心度: {result['confidence']:.2f}")
            print(f"    - 波动率: {result['volatility']*100:.2f}%")
            return True
        else:
            print("  ✗ 无法检测市场状态")
            return False
    
    except Exception as e:
        print(f"  ✗ 市场分析测试失败: {e}")
        return False

def print_summary(results):
    """打印测试总结"""
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60 + "\n")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"总计: {total} 个测试")
    print(f"✓ 通过: {passed} 个")
    print(f"✗ 失败: {failed} 个")
    print(f"成功率: {passed/total*100:.1f}%\n")
    
    if failed == 0:
        print("""
╔══════════════════════════════════════════════════════════╗
║  🎉 所有测试通过！系统已准备好运行                     ║
║                                                         ║
║  启动命令: python run_dashboard.py                     ║
║  访问地址: http://localhost:8000                       ║
╚══════════════════════════════════════════════════════════╝
        """)
    else:
        print("""
⚠️  某些测试失败，请检查上述错误信息
        """)
    
    return failed == 0

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║    量化交易仪表板 - 系统集成测试                        ║
║    Quantitative Trading Dashboard - Integration Test   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        '模块导入': test_imports(),
        '数据库': test_database(),
        '市场分析': test_market_analyzer(),
        '投资组合优化': test_optimizer(),
        'API集成': test_api(),
    }
    
    success = print_summary(results)
    
    # 返回状态码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
