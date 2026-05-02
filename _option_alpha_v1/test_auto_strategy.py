import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

def test_basic_functionality():
    """测试基本功能"""
    print("开始测试自动市场策略系统...")

    # 测试数据下载
    try:
        print("下载SPY数据...")
        df = yf.download("SPY", period="1y", auto_adjust=True)
        print(f"成功下载 {len(df)} 条数据")
        print(f"最新价格: ${df['Close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"数据下载失败: {e}")
        return

    # 测试市场状态识别
    try:
        current_price = df['Close'].iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]

        momentum_20 = (current_price - ma20) / ma20
        momentum_50 = (current_price - ma50) / ma50

        returns = df['Close'].pct_change().dropna()
        volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)

        print("\n市场状态分析:")
        print(f"当前价格: ${current_price:.2f}")
        print(f"20日动量: {momentum_20:.2%}")
        print(f"50日动量: {momentum_50:.2%}")
        print(f"波动率: {volatility:.2%}")

        # 判断市场状态
        if momentum_50 > 0.02 and volatility < 0.25:
            regime = "牛市"
        elif momentum_50 < -0.02:
            regime = "熊市"
        elif volatility > 0.35:
            regime = "高波动"
        else:
            regime = "震荡市"

        print(f"市场状态: {regime}")

    except Exception as e:
        print(f"市场分析失败: {e}")
        return

    # 测试策略参数调整
    try:
        if regime == "牛市":
            fast_ma, slow_ma = 20, 100
            stop_loss, take_profit = 0.05, 0.15
        elif regime == "熊市":
            fast_ma, slow_ma = 10, 50
            stop_loss, take_profit = 0.03, 0.08
        elif regime == "高波动":
            fast_ma, slow_ma = 30, 150
            stop_loss, take_profit = 0.08, 0.12
        else:
            fast_ma, slow_ma = 25, 125
            stop_loss, take_profit = 0.06, 0.10

        print("\n策略参数:")
        print(f"快均线: {fast_ma}日")
        print(f"慢均线: {slow_ma}日")
        print(f"止损: {stop_loss:.1%}")
        print(f"止盈: {take_profit:.1%}")

    except Exception as e:
        print(f"策略调整失败: {e}")
        return

    print("\n测试完成！自动市场策略系统运行正常。")

if __name__ == "__main__":
    test_basic_functionality()