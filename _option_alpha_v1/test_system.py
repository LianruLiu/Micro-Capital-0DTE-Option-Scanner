#!/usr/bin/env python3
"""
自动市场策略系统 - 快速测试脚本
"""

import sys
import os
import traceback

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """测试导入"""
    print("测试模块导入...")
    try:
        from auto_market_strategy import AutoMarketStrategyBot, MarketRegimeDetector
        from config import MARKET_REGIME_CONFIG, STRATEGY_CONFIG
        print("✓ 模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    try:
        from auto_market_strategy import MarketRegimeDetector
        import pandas as pd
        import numpy as np

        # 创建模拟数据
        dates = pd.date_range('2023-01-01', periods=300, freq='D')
        prices = 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 300)))
        df = pd.DataFrame({'Close': prices}, index=dates)

        # 测试市场状态识别
        detector = MarketRegimeDetector()
        regime = detector.detect_regime(df)

        print(f"✓ 市场状态识别: {regime['regime']} (置信度: {regime['confidence']:.2%})")
        return True

    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_data_download():
    """测试数据下载"""
    print("\n测试数据下载...")
    try:
        from auto_market_strategy import AutoMarketStrategyBot

        bot = AutoMarketStrategyBot(tickers=['SPY'])
        df = bot.fetch_data('SPY', period='1y')

        if df is not None and not df.empty:
            print(f"✓ 数据下载成功: {len(df)} 条记录")
            return True
        else:
            print("✗ 数据下载失败或数据为空")
            return False

    except Exception as e:
        print(f"✗ 数据下载测试失败: {e}")
        return False

def test_full_analysis():
    """测试完整分析流程"""
    print("\n测试完整分析流程...")
    try:
        from auto_market_strategy import AutoMarketStrategyBot

        bot = AutoMarketStrategyBot(tickers=['SPY'])
        result = bot.analyze_market_and_adjust_strategy('SPY')

        if result:
            print("✓ 完整分析成功")
            print(f"  市场状态: {result['market_regime']['regime']}")
            return True
        else:
            print("✗ 完整分析失败")
            return False

    except Exception as e:
        print(f"✗ 完整分析测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("自动市场策略系统 - 功能测试")
    print("=" * 50)

    tests = [
        ("模块导入", test_imports),
        ("基本功能", test_basic_functionality),
        ("数据下载", test_data_download),
        ("完整分析", test_full_analysis)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"测试 '{test_name}' 失败")
        except Exception as e:
            print(f"测试 '{test_name}' 出现异常: {e}")

    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 50)

    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
        print("\n您可以运行以下命令:")
        print("  python demo_auto_strategy.py    # 查看演示")
        print("  python auto_market_strategy.py  # 运行完整系统")
    else:
        print("⚠️  部分测试失败，请检查依赖和配置。")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)