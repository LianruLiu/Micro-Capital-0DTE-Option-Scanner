import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 参数
ticker = "SPY"
start = "2018-01-01"
end = "2025-01-01"

# 下载数据
df = yf.download(ticker, start=start, end=end, auto_adjust=True)

# 只保留收盘价
df = df[['Close']].copy()

# 均线
df["MA50"] = df["Close"].rolling(50).mean()
df["MA200"] = df["Close"].rolling(200).mean()

# 信号：短均线大于长均线则持仓
df["Signal"] = np.where(df["MA50"] > df["MA200"], 1, 0)

# 策略收益
df["Return"] = df["Close"].pct_change()
df["Strategy_Return"] = df["Signal"].shift(1) * df["Return"]

# 累计净值
df["Equity"] = (1 + df["Strategy_Return"]).cumprod()
df["BuyHold"] = (1 + df["Return"]).cumprod()

# 最大回撤
rolling_max = df["Equity"].cummax()
drawdown = df["Equity"] / rolling_max - 1
max_dd = drawdown.min()

# 年化收益率
years = len(df) / 252
cagr = df["Equity"].iloc[-1] ** (1 / years) - 1

# Sharpe
sharpe = df["Strategy_Return"].mean() / df["Strategy_Return"].std() * np.sqrt(252)

print("Ticker:", ticker)
print("CAGR:", round(cagr * 100, 2), "%")
print("Sharpe:", round(sharpe, 2))
print("Max Drawdown:", round(max_dd * 100, 2), "%")

# 绘图
plt.figure(figsize=(12,6))
plt.plot(df.index, df["Equity"], label="Momentum Strategy")
plt.plot(df.index, df["BuyHold"], label="Buy & Hold")
plt.title(f"{ticker} Backtest")
plt.legend()
plt.grid(True)
plt.show()