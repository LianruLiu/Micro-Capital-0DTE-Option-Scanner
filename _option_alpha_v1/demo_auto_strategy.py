"""
自动市场策略优化系统 - 使用演示
================================

这个系统包含以下核心功能：

1. 市场状态识别器 (MarketRegimeDetector)
   - 识别牛市、熊市、高波动、震荡市等市场状态
   - 基于动量指标和波动率分析

2. 动态策略调整器 (DynamicStrategyAdjuster)
   - 根据市场状态自动调整策略参数
   - 包括均线周期、止损止盈、仓位大小等

3. 期权定价引擎 (OptionPricingEngine)
   - Black-Scholes期权定价模型
   - 计算价格预测区间

4. 自动市场策略机器人 (AutoMarketStrategyBot)
   - 集成所有组件
   - 实时数据更新和策略调整
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from auto_market_strategy import AutoMarketStrategyBot, MarketRegimeDetector, DynamicStrategyAdjuster, OptionPricingEngine
import pandas as pd
import numpy as np

def demo_market_analysis():
    """演示市场分析功能"""
    print("=" * 60)
    print("自动市场策略系统演示")
    print("=" * 60)

    # 创建机器人实例
    bot = AutoMarketStrategyBot(tickers=['SPY', 'QQQ'])

    # 运行SPY分析
    print("\n1. 分析SPY市场状态和策略...")
    result = bot.run_single_analysis('SPY')

    if result:
        print("\n2. 分析完成！以下是关键结果：")

        # 显示市场状态
        regime = result['market_regime']
        print(f"市场状态: {regime['regime']}")
        print(f"当前价格: ${result['current_price']:.2f}")
        print(f"波动率: {regime['volatility']:.2%}")

        # 显示策略参数
        params = result['optimal_parameters']
        print("\n策略参数:")
        print(f"  快均线周期: {params['fast_ma']}日")
        print(f"  慢均线周期: {params['slow_ma']}日")
        print(f"  止损: {params['stop_loss']:.1%}")
        print(f"  止盈: {params['take_profit']:.1%}")
        print(f"  仓位大小: {params['position_size']:.1%}")

        # 显示绩效指标
        perf = result['performance']
        print("\n绩效指标:")
        print(f"  累计收益率: {perf['cumulative_return']:.2%}")
        print(f"  年化波动率: {perf['volatility']:.2%}")
        print(f"  夏普比率: {perf['sharpe_ratio']:.2f}")
        print(f"  最大回撤: {perf['max_drawdown']:.2%}")

        # 显示价格区间预测
        ranges = result['option_analysis']['price_ranges']
        print("\n30天价格预测区间:")
        for conf, data in ranges.items():
            print(f"  {conf}: ${data['lower']:.2f} - ${data['upper']:.2f} (区间: ${data['range']:.2f})")
    else:
        print("分析失败，请检查网络连接和数据源")

def demo_individual_components():
    """演示各个组件的功能"""
    print("\n" + "=" * 60)
    print("组件功能演示")
    print("=" * 60)

    # 1. 市场状态识别器
    print("\n1. 市场状态识别器演示")
    detector = MarketRegimeDetector()

    # 创建模拟数据
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    # 模拟牛市数据
    bull_prices = 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 300)))
    bull_df = pd.DataFrame({'Close': bull_prices}, index=dates)

    regime = detector.detect_regime(bull_df)
    print(f"模拟牛市识别结果: {regime['regime']} (置信度: {regime['confidence']:.2%})")

    # 2. 期权定价引擎
    print("\n2. 期权定价引擎演示")
    option_engine = OptionPricingEngine()

    S, K, T, r, sigma = 450, 450, 30/365, 0.03, 0.25
    bs_result = option_engine.black_scholes(S, K, T, r, sigma, 'call')
    print(f"期权定价结果:")
    print(f"  期权价格: {bs_result['price']:.4f}")
    print(f"  Delta: {bs_result['delta']:.4f}")
    print(f"  Gamma: {bs_result['gamma']:.4f}")
    print(f"  Vega: {bs_result['vega']:.4f}")

    # 价格区间计算
    ranges = option_engine.calculate_price_ranges(S, sigma)
    print("\n价格预测区间:")
    for conf, data in ranges['price_ranges'].items():
        print(f"  {conf}: ${data['lower']:.2f} - ${data['upper']:.2f} (区间: ${data['range']:.2f})")
def demo_strategy_adjustment():
    """演示策略调整功能"""
    print("\n" + "=" * 60)
    print("策略调整演示")
    print("=" * 60)

    adjuster = DynamicStrategyAdjuster()

    # 模拟不同市场状态
    market_states = [
        {"regime": "bull_market", "confidence": 0.8},
        {"regime": "bear_market", "confidence": 0.7},
        {"regime": "high_volatility", "confidence": 0.9},
        {"regime": "sideways", "confidence": 0.5}
    ]

    for state in market_states:
        params = adjuster.get_optimal_parameters(None, state)
        print(f"\n市场状态: {state['regime']}")
        print(f"  快均线: {params['fast_ma']}日")
        print(f"  慢均线: {params['slow_ma']}日")
        print(f"  止损: {params['stop_loss']:.1%}")
        print(f"  止盈: {params['take_profit']:.1%}")
        print(f"  仓位大小: {params['position_size']:.1%}")
def show_usage_guide():
    """显示使用指南"""
    print("\n" + "=" * 60)
    print("使用指南")
    print("=" * 60)

    print("""
基本使用方法:

1. 单次市场分析:
   from auto_market_strategy import AutoMarketStrategyBot
   bot = AutoMarketStrategyBot()
   result = bot.run_single_analysis('SPY')

2. 持续监控模式:
   bot = AutoMarketStrategyBot(tickers=['SPY', 'QQQ', 'IWM'], update_interval=3600)
   bot.run_continuous_monitoring()

3. 自定义策略参数:
   detector = MarketRegimeDetector()
   adjuster = DynamicStrategyAdjuster()
   regime = detector.detect_regime(data)
   params = adjuster.get_optimal_parameters(data, regime)

4. 期权定价分析:
   engine = OptionPricingEngine()
   price = engine.black_scholes(S, K, T, r, sigma, 'call')
   ranges = engine.calculate_price_ranges(S, volatility)

系统特点:
- 自动识别市场状态（牛市/熊市/高波动/震荡市）
- 动态调整策略参数以适应市场变化
- 集成期权定价和价格区间预测
- 支持多股票同时监控
- 实时数据更新和错误处理

依赖包:
- yfinance: 股票数据下载
- pandas, numpy: 数据处理
- scipy: 统计计算
- matplotlib: 可视化（可选）

注意事项:
- 确保网络连接正常以获取实时数据
- 建议在交易日期间运行以获取最新数据
- 可以根据需要调整市场状态识别的阈值参数
    """)

if __name__ == "__main__":
    try:
        # 运行演示
        demo_market_analysis()
        demo_individual_components()
        demo_strategy_adjustment()
        show_usage_guide()

        print("\n" + "=" * 60)
        print("演示完成！系统已准备就绪。")
        print("=" * 60)

    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所需的依赖包: pip install yfinance pandas numpy scipy matplotlib")
    except Exception as e:
        print(f"演示过程中出错: {e}")
        import traceback
        traceback.print_exc()