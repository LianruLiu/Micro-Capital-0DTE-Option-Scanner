"""
自动市场策略系统配置文件
"""

# 市场状态识别参数
MARKET_REGIME_CONFIG = {
    # 动量阈值
    'bull_threshold': {
        'momentum_200': 0.05,    # 200日动量 > 5%
        'momentum_50': 0.02,     # 50日动量 > 2%
        'volatility_max': 0.25   # 波动率 < 25%
    },
    'bear_threshold': {
        'momentum_200': -0.05,   # 200日动量 < -5%
        'momentum_50': -0.02,    # 50日动量 < -2%
    },
    'high_volatility_threshold': {
        'volatility_min': 0.35   # 波动率 > 35%
    }
}

# 策略参数配置
STRATEGY_CONFIG = {
    'bull_market': {
        'fast_ma': 20,
        'slow_ma': 100,
        'stop_loss': 0.05,       # 5%
        'take_profit': 0.15,     # 15%
        'position_size': 1.0     # 100%
    },
    'bear_market': {
        'fast_ma': 10,
        'slow_ma': 50,
        'stop_loss': 0.03,       # 3%
        'take_profit': 0.08,     # 8%
        'position_size': 0.5     # 50%
    },
    'high_volatility': {
        'fast_ma': 30,
        'slow_ma': 150,
        'stop_loss': 0.08,       # 8%
        'take_profit': 0.12,     # 12%
        'position_size': 0.3     # 30%
    },
    'sideways': {
        'fast_ma': 25,
        'slow_ma': 125,
        'stop_loss': 0.06,       # 6%
        'take_profit': 0.10,     # 10%
        'position_size': 0.7     # 70%
    }
}

# 数据更新配置
DATA_CONFIG = {
    'update_interval': 3600,     # 1小时更新一次
    'max_retry': 3,             # 最大重试次数
    'timeout': 30,              # 请求超时时间(秒)
    'cache_validity': 300       # 缓存有效期(秒)
}

# 期权定价配置
OPTION_CONFIG = {
    'risk_free_rate': 0.03,     # 无风险利率
    'confidence_levels': [0.68, 0.95, 0.99],  # 置信区间
    'time_horizon': 30,         # 预测天数
    'default_volatility': 0.25  # 默认波动率
}

# 绩效评估配置
PERFORMANCE_CONFIG = {
    'annual_trading_days': 252,
    'risk_free_rate': 0.03,
    'benchmark_ticker': 'SPY'
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'auto_strategy.log'
}

# 默认监控股票列表
DEFAULT_TICKERS = ['SPY', 'QQQ', 'IWM', 'VTI', 'BND']

# 技术指标参数
TECHNICAL_CONFIG = {
    'momentum_periods': [20, 50, 200],
    'volatility_period': 20,
    'volume_period': 20
}