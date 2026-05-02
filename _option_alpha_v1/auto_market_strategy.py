import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import logging
import warnings
import requests
from requests.exceptions import RequestException
import json
import os
from pathlib import Path

warnings.filterwarnings('ignore')

# 导入配置
try:
    from config import *
except ImportError:
    print("警告: 找不到配置文件，使用默认参数")
    # 默认配置
    MARKET_REGIME_CONFIG = {
        'bull_threshold': {'momentum_200': 0.05, 'momentum_50': 0.02, 'volatility_max': 0.25},
        'bear_threshold': {'momentum_200': -0.05, 'momentum_50': -0.02},
        'high_volatility_threshold': {'volatility_min': 0.35}
    }
    STRATEGY_CONFIG = {
        'bull_market': {'fast_ma': 20, 'slow_ma': 100, 'stop_loss': 0.05, 'take_profit': 0.15, 'position_size': 1.0},
        'bear_market': {'fast_ma': 10, 'slow_ma': 50, 'stop_loss': 0.03, 'take_profit': 0.08, 'position_size': 0.5},
        'high_volatility': {'fast_ma': 30, 'slow_ma': 150, 'stop_loss': 0.08, 'take_profit': 0.12, 'position_size': 0.3},
        'sideways': {'fast_ma': 25, 'slow_ma': 125, 'stop_loss': 0.06, 'take_profit': 0.10, 'position_size': 0.7}
    }
    DATA_CONFIG = {'update_interval': 3600, 'max_retry': 3, 'timeout': 30}
    OPTION_CONFIG = {'risk_free_rate': 0.03, 'confidence_levels': [0.68, 0.95, 0.99], 'time_horizon': 30}
    LOGGING_CONFIG = {'level': 'INFO', 'format': '%(asctime)s - %(levelname)s - %(message)s'}

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

class MarketRegimeDetector:
    """市场状态识别器"""

    def __init__(self, lookback_periods=[20, 50, 200]):
        self.lookback_periods = lookback_periods

    def detect_regime(self, df):
        """识别市场状态"""
        try:
            current_price = df['Close'].iloc[-1]
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            ma200 = df['Close'].rolling(200).mean().iloc[-1]

            # 计算动量指标
            momentum_20 = (current_price - ma20) / ma20 if ma20 > 0 else 0
            momentum_50 = (current_price - ma50) / ma50 if ma50 > 0 else 0
            momentum_200 = (current_price - ma200) / ma200 if ma200 > 0 else 0

            # 计算波动率
            returns = df['Close'].pct_change().dropna()
            volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252) if len(returns) >= 20 else 0.25

            # 使用配置文件中的阈值判断市场状态
            bull_config = MARKET_REGIME_CONFIG['bull_threshold']
            bear_config = MARKET_REGIME_CONFIG['bear_threshold']
            vol_config = MARKET_REGIME_CONFIG['high_volatility_threshold']

            if (momentum_200 > bull_config['momentum_200'] and
                momentum_50 > bull_config['momentum_50'] and
                volatility < bull_config['volatility_max']):
                regime = "bull_market"  # 牛市
                confidence = min(1.0, (momentum_200 + momentum_50) / 0.1)
            elif (momentum_200 < bear_config['momentum_200'] and
                  momentum_50 < bear_config['momentum_50']):
                regime = "bear_market"  # 熊市
                confidence = min(1.0, abs(momentum_200 + momentum_50) / 0.1)
            elif volatility > vol_config['volatility_min']:
                regime = "high_volatility"  # 高波动
                confidence = min(1.0, volatility / 0.5)
            else:
                regime = "sideways"  # 震荡市
                confidence = 0.5

            return {
                'regime': regime,
                'confidence': confidence,
                'momentum_20': momentum_20,
                'momentum_50': momentum_50,
                'momentum_200': momentum_200,
                'volatility': volatility,
                'current_price': current_price
            }
        except Exception as e:
            logger.error(f"市场状态识别失败: {e}")
            return {
                'regime': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }

class DynamicStrategyAdjuster:
    """动态策略调整器"""

    def __init__(self):
        self.regime_detector = MarketRegimeDetector()

    def get_optimal_parameters(self, df, regime_info):
        """根据市场状态获取最优参数"""
        regime = regime_info['regime']

        try:
            if regime in STRATEGY_CONFIG:
                return STRATEGY_CONFIG[regime].copy()
            else:
                # 默认使用震荡市参数
                logger.warning(f"未知市场状态: {regime}, 使用默认参数")
                return STRATEGY_CONFIG['sideways'].copy()
        except Exception as e:
            logger.error(f"获取策略参数失败: {e}")
            return STRATEGY_CONFIG['sideways'].copy()

    def generate_signals(self, df, params):
        """生成交易信号"""
        fast_ma = df['Close'].rolling(params['fast_ma']).mean()
        slow_ma = df['Close'].rolling(params['slow_ma']).mean()

        # 动量交叉信号
        df = df.copy()
        df['Fast_MA'] = fast_ma
        df['Slow_MA'] = slow_ma
        df['Signal'] = np.where(fast_ma > slow_ma, 1, -1)

        # 添加止损止盈逻辑
        df['Position'] = 0
        df['Entry_Price'] = np.nan
        df['Stop_Loss'] = np.nan
        df['Take_Profit'] = np.nan

        position = 0
        entry_price = np.nan

        for i in range(len(df)):
            current_signal = df['Signal'].iloc[i]
            current_price = df['Close'].iloc[i]

            if position == 0 and current_signal == 1:
                # 开多仓
                position = 1
                entry_price = current_price
                df.loc[df.index[i], 'Position'] = 1
                df.loc[df.index[i], 'Entry_Price'] = entry_price
                df.loc[df.index[i], 'Stop_Loss'] = entry_price * (1 - params['stop_loss'])
                df.loc[df.index[i], 'Take_Profit'] = entry_price * (1 + params['take_profit'])

            elif position == 1:
                # 检查止损止盈
                if current_price <= df['Stop_Loss'].iloc[i-1] or current_price >= df['Take_Profit'].iloc[i-1]:
                    position = 0
                    df.loc[df.index[i], 'Position'] = 0
                else:
                    df.loc[df.index[i], 'Position'] = 1
                    df.loc[df.index[i], 'Entry_Price'] = entry_price
                    df.loc[df.index[i], 'Stop_Loss'] = entry_price * (1 - params['stop_loss'])
                    df.loc[df.index[i], 'Take_Profit'] = entry_price * (1 + params['take_profit'])

        return df

class OptionPricingEngine:
    """期权定价引擎"""

    def __init__(self):
        pass

    def black_scholes(self, S, K, T, r, sigma, option_type='call'):
        """Black-Scholes期权定价"""
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)

        if option_type == 'call':
            price = S * norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        else:
            price = K*np.exp(-r*T)*norm.cdf(-d2) - S * norm.cdf(-d1)

        return price

    def black_scholes_greeks(self, S, K, T, r, sigma, option_type='call'):
        """Black-Scholes期权价格和Greeks"""
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)

        if option_type == 'call':
            price = S * norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
            delta = norm.cdf(d1)
            rho = K * T * np.exp(-r*T) * norm.cdf(d2)
        else:
            price = K*np.exp(-r*T)*norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = -norm.cdf(-d1)
            rho = -K * T * np.exp(-r*T) * norm.cdf(-d2)

        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T)) if S > 0 and sigma > 0 and T > 0 else 0
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100 if T > 0 else 0
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                 - r * K * np.exp(-r*T) * (norm.cdf(d2) if option_type == 'call' else -norm.cdf(-d2))) / 365 if T > 0 else 0

        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta,
            'rho': rho
        }

    def generate_option_chain(self, S, volatility, expiries=[30, 60, 90], moneyness_range=(0.8, 1.2), strike_step=0.02):
        """生成期权链和Greeks数据表"""
        strikes = np.arange(S * moneyness_range[0], S * moneyness_range[1] + S * strike_step / 2, S * strike_step)
        rows = []

        for days in expiries:
            T = days / 365
            for strike in strikes:
                for option_type in ['call', 'put']:
                    g = self.black_scholes_greeks(S, strike, T, OPTION_CONFIG['risk_free_rate'], volatility, option_type)
                    rows.append({
                        'expiry_days': days,
                        'strike': float(strike),
                        'type': option_type,
                        'price': float(g['price']),
                        'delta': float(g['delta']),
                        'gamma': float(g['gamma']),
                        'vega': float(g['vega']),
                        'theta': float(g['theta']),
                        'rho': float(g['rho']),
                        'moneyness': float(strike / S)
                    })

        return pd.DataFrame(rows)

    def recommend_option_strategy(self, S, volatility, regime_info, df=None, option_chain=None):
        """基于Greeks和市场状态推荐期权策略"""
        if option_chain is None:
            option_chain = self.generate_option_chain(S, volatility)

        regime = regime_info.get('regime', 'sideways')
        recommendation = {
            'strategy': None,
            'type': None,
            'strike': None,
            'expiry_days': None,
            'expiry_date': None,
            'position_size': None,
            'risk_level': None,
            'target_price': None,
            'rationale': None,
            'support': None,
            'resistance': None,
            'price_mid': None
        }

        if df is not None and len(df) >= 30:
            recent = df['Close'].iloc[-60:]
            support = float(recent[-20:].min())
            resistance = float(recent[-20:].max())
            price_mid = float(recent.mean())
            recommendation.update({
                'support': support,
                'resistance': resistance,
                'price_mid': price_mid
            })

        def choose_candidate(filter_df, sort_cols):
            if filter_df.empty:
                return None
            return filter_df.sort_values(sort_cols).iloc[0]

        if regime == 'bull_market':
            candidates = option_chain[(option_chain['type'] == 'call') &
                                      (option_chain['delta'] >= 0.45) &
                                      (option_chain['delta'] <= 0.65)]
            best = choose_candidate(candidates, ['expiry_days', 'vega', 'gamma'])
            recommendation.update({
                'strategy': 'Long Call',
                'type': 'call',
                'risk_level': 'Medium',
                'position_size': 0.35,
                'rationale': '趋势向上，优选Delta 0.45-0.65的看涨期权',
            })
        elif regime == 'bear_market':
            candidates = option_chain[(option_chain['type'] == 'put') &
                                      (option_chain['delta'] <= -0.45) &
                                      (option_chain['delta'] >= -0.65)]
            best = choose_candidate(candidates, ['expiry_days', 'vega', 'gamma'])
            recommendation.update({
                'strategy': 'Long Put',
                'type': 'put',
                'risk_level': 'Medium',
                'position_size': 0.35,
                'rationale': '趋势向下，优选Delta -0.45~-0.65的看跌期权',
            })
        elif regime == 'high_volatility':
            short_call = option_chain[(option_chain['type'] == 'call') &
                                      (option_chain['delta'] >= 0.18) &
                                      (option_chain['delta'] <= 0.25) &
                                      (option_chain['expiry_days'] == 30)]
            short_put = option_chain[(option_chain['type'] == 'put') &
                                     (option_chain['delta'] <= -0.18) &
                                     (option_chain['delta'] >= -0.25) &
                                     (option_chain['expiry_days'] == 30)]
            if not short_call.empty and not short_put.empty:
                call_leg = choose_candidate(short_call, ['vega', 'theta'])
                put_leg = choose_candidate(short_put, ['vega', 'theta'])
                recommendation.update({
                    'strategy': 'Iron Condor',
                    'type': 'multi-leg',
                    'risk_level': 'High',
                    'position_size': 0.25,
                    'rationale': '高波动时优先卖出时间价值，获取Theta收益',
                    'call_leg': call_leg.to_dict() if call_leg is not None else None,
                    'put_leg': put_leg.to_dict() if put_leg is not None else None
                })
                best = call_leg if call_leg is not None else put_leg
            else:
                best = choose_candidate(option_chain[(option_chain['type'] == 'call') &
                                                     (option_chain['delta'] >= 0.25) &
                                                     (option_chain['expiry_days'] == 30)], ['vega'])
                recommendation.update({
                    'strategy': 'Long Strangle',
                    'type': 'call+put',
                    'risk_level': 'High',
                    'position_size': 0.25,
                    'rationale': '高波动下优选价外跨式结构，捕捉大幅波动',
                })
        else:
            short_call = option_chain[(option_chain['type'] == 'call') &
                                      (option_chain['delta'] >= 0.22) &
                                      (option_chain['delta'] <= 0.3) &
                                      (option_chain['expiry_days'] == 30)]
            short_put = option_chain[(option_chain['type'] == 'put') &
                                     (option_chain['delta'] <= -0.22) &
                                     (option_chain['delta'] >= -0.3) &
                                     (option_chain['expiry_days'] == 30)]
            recommendation.update({
                'strategy': 'Short Iron Condor',
                'type': 'multi-leg',
                'risk_level': 'Medium',
                'position_size': 0.3,
                'rationale': '震荡市时优先卖出时间价值，收益来源于Theta衰减',
                'call_leg': choose_candidate(short_call, ['vega', 'theta']).to_dict() if choose_candidate(short_call, ['vega', 'theta']) is not None else None,
                'put_leg': choose_candidate(short_put, ['vega', 'theta']).to_dict() if choose_candidate(short_put, ['vega', 'theta']) is not None else None
            })
            best = recommendation['call_leg'] if recommendation['call_leg'] else (recommendation['put_leg'] if recommendation['put_leg'] else None)
            best = pd.Series(best) if isinstance(best, dict) else best

        if best is not None:
            recommendation.update({
                'strike': float(best['strike']),
                'expiry_days': int(best['expiry_days']),
                'expiry_date': (datetime.now() + timedelta(days=int(best['expiry_days']))).strftime('%Y-%m-%d'),
                'target_price': float(best['strike']),
                'delta': float(best.get('delta', 0)),
                'gamma': float(best.get('gamma', 0)),
                'vega': float(best.get('vega', 0)),
                'theta': float(best.get('theta', 0)),
                'rho': float(best.get('rho', 0))
            })

        return recommendation

    def calculate_price_ranges(self, S, volatility, time_horizon=None):
        """计算价格区间"""
        if time_horizon is None:
            time_horizon = OPTION_CONFIG['time_horizon']

        T = time_horizon / 365
        r = OPTION_CONFIG['risk_free_rate']

        # 不同行权价的期权价格
        strikes = np.linspace(S * 0.8, S * 1.2, 21)

        call_prices = []
        put_prices = []

        for K in strikes:
            call = self.black_scholes(S, K, T, r, volatility, 'call')
            put = self.black_scholes(S, K, T, r, volatility, 'put')
            call_prices.append(call)
            put_prices.append(put)

        # 计算置信区间
        confidence_levels = OPTION_CONFIG['confidence_levels']
        price_ranges = {}

        for conf in confidence_levels:
            z_score = norm.ppf((1 + conf) / 2)
            range_up = S * np.exp((r - 0.5*volatility**2)*T + volatility*np.sqrt(T)*z_score)
            range_down = S * np.exp((r - 0.5*volatility**2)*T - volatility*np.sqrt(T)*z_score)

            price_ranges[f'{int(conf*100)}_confidence'] = {
                'upper': range_up,
                'lower': range_down,
                'range': range_up - range_down
            }

        return {
            'strikes': strikes,
            'call_prices': call_prices,
            'put_prices': put_prices,
            'price_ranges': price_ranges
        }

class AutoMarketStrategyBot:
    """自动市场策略机器人"""

    def __init__(self, tickers=None, update_interval=None):
        if tickers is None:
            tickers = DEFAULT_TICKERS
        if update_interval is None:
            update_interval = DATA_CONFIG['update_interval']

        self.tickers = tickers
        self.update_interval = update_interval
        self.market_detector = MarketRegimeDetector()
        self.strategy_adjuster = DynamicStrategyAdjuster()
        self.option_engine = OptionPricingEngine()
        self.data_cache = {}
        self.last_update = {}

        # 创建结果存储目录
        project_root = Path(__file__).resolve().parent
        self.results_dir = project_root / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def fetch_data(self, ticker, period="2y"):
        """获取股票数据"""
        max_retry = DATA_CONFIG['max_retry']
        timeout = DATA_CONFIG['timeout']

        for attempt in range(max_retry):
            try:
                logger.info(f"下载 {ticker} 数据 (尝试 {attempt + 1}/{max_retry})")
                df = yf.download(ticker, period=period, auto_adjust=True, timeout=timeout)

                if df.empty or len(df) < 100:
                    logger.warning(f"{ticker} 数据不足 ({len(df)} 条)")
                    time.sleep(2)
                    continue

                df = df[['Close', 'Volume']].copy()
                df = df.dropna()  # 删除NaN值

                logger.info(f"成功下载 {ticker} 数据: {len(df)} 条记录")
                self.data_cache[ticker] = df
                self.last_update[ticker] = datetime.now()
                return df

            except Exception as e:
                logger.warning(f"{ticker} 下载失败 (尝试 {attempt + 1}): {e}")
                if attempt < max_retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                continue

        logger.error(f"{ticker} 数据下载失败，已达到最大重试次数")
        return None

    def update_data(self, ticker):
        """更新数据"""
        if ticker not in self.data_cache:
            return self.fetch_data(ticker)

        # 检查是否需要更新
        if ticker in self.last_update:
            time_diff = (datetime.now() - self.last_update[ticker]).seconds
            if time_diff < self.update_interval:
                return self.data_cache[ticker]

        # 获取最新数据
        try:
            latest_data = yf.download(ticker, period="5d", auto_adjust=True)
            if not latest_data.empty:
                # 合并数据
                existing_data = self.data_cache[ticker]
                combined = pd.concat([existing_data, latest_data])
                combined = combined[~combined.index.duplicated(keep='last')]
                combined = combined.sort_index()
                self.data_cache[ticker] = combined
                self.last_update[ticker] = datetime.now()
                return combined
        except Exception as e:
            logger.error(f"Error updating data for {ticker}: {e}")

        return self.data_cache[ticker]

    def analyze_market_and_adjust_strategy(self, ticker):
        """分析市场并调整策略"""
        df = self.update_data(ticker)
        if df is None or len(df) < 200:
            logger.warning(f"Insufficient data for {ticker}")
            return None

        # 检测市场状态
        regime_info = self.market_detector.detect_regime(df)

        # 获取最优参数
        optimal_params = self.strategy_adjuster.get_optimal_parameters(df, regime_info)

        # 生成信号
        df_with_signals = self.strategy_adjuster.generate_signals(df, optimal_params)

        # 计算期权价格区间和Greeks分析
        current_price = df['Close'].iloc[-1]
        volatility = df['Close'].pct_change().rolling(20).std().iloc[-1] * np.sqrt(252)
        option_analysis = self.option_engine.calculate_price_ranges(current_price, volatility)
        option_chain = self.option_engine.generate_option_chain(current_price, volatility, expiries=[30, 60, 90])
        option_recommendation = self.option_engine.recommend_option_strategy(
            current_price,
            volatility,
            regime_info,
            df=df,
            option_chain=option_chain
        )

        # 计算策略表现
        returns = df_with_signals['Close'].pct_change()
        strategy_returns = df_with_signals['Position'].shift(1) * returns

        # 绩效指标
        cumulative_return = (1 + strategy_returns.fillna(0)).cumprod().iloc[-1] - 1
        volatility_strategy = strategy_returns.std() * np.sqrt(252)
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0

        # 最大回撤
        cumulative_equity = (1 + strategy_returns.fillna(0)).cumprod()
        rolling_max = cumulative_equity.cummax()
        drawdown = cumulative_equity / rolling_max - 1
        max_drawdown = drawdown.min()

        result = {
            'ticker': ticker,
            'timestamp': datetime.now(),
            'market_regime': regime_info,
            'optimal_parameters': optimal_params,
            'current_price': current_price,
            'option_analysis': option_analysis,
            'option_recommendation': option_recommendation,
            'performance': {
                'cumulative_return': cumulative_return,
                'volatility': volatility_strategy,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            },
            'signals': df_with_signals[['Close', 'Position', 'Signal']].tail(10).to_dict()
        }

        self.results[ticker] = result
        plot_file = self.plot_analysis(ticker, df, option_chain, result)
        result['plot_file'] = plot_file

        # 保存结果到文件
        try:
            result_file = self.results_dir / f"{ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                # 转换numpy类型为Python类型以便JSON序列化
                json_result = self._make_json_serializable(result)
                json.dump(json_result, f, indent=2, ensure_ascii=False)
            logger.info(f"结果已保存到: {result_file}")
        except Exception as e:
            logger.error(f"保存结果失败: {e}")

        return result

    def _make_json_serializable(self, obj):
        """将结果转换为JSON可序列化格式"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        else:
            return obj

    def run_continuous_monitoring(self):
        """运行持续监控"""
        logger.info("Starting continuous market monitoring...")

        while True:
            for ticker in self.tickers:
                try:
                    result = self.analyze_market_and_adjust_strategy(ticker)
                    if result:
                        self.print_summary(result)
                except Exception as e:
                    logger.error(f"Error analyzing {ticker}: {e}")

            logger.info(f"Sleeping for {self.update_interval} seconds...")
            time.sleep(self.update_interval)

    def print_summary(self, result):
        """打印分析摘要"""
        print(f"\n{'='*60}")
        print(f"市场分析报告 - {result['ticker']} ({result['timestamp'].strftime('%Y-%m-%d %H:%M')})")
        print(f"{'='*60}")

        # 市场状态
        regime = result['market_regime']
        print(f"市场状态: {regime['regime']} (置信度: {regime['confidence']:.2%})")
        print(f"当前价格: ${result['current_price']:.2f}")
        print(f"波动率: {regime['volatility']:.2%}")

        # 策略参数
        params = result['optimal_parameters']
        print(f"\n策略参数:")
        print(f"  快均线: {params['fast_ma']}日")
        print(f"  慢均线: {params['slow_ma']}日")
        print(f"  止损: {params['stop_loss']:.1%}")
        print(f"  止盈: {params['take_profit']:.1%}")
        print(f"  仓位大小: {params['position_size']:.1%}")

        # 绩效指标
        perf = result['performance']
        print(f"\n绩效指标:")
        print(f"  累计收益率: {perf['cumulative_return']:.2%}")
        print(f"  年化波动率: {perf['volatility']:.2%}")
        print(f"  夏普比率: {perf['sharpe_ratio']:.2f}")
        print(f"  最大回撤: {perf['max_drawdown']:.2%}")

        # 价格区间
        ranges = result['option_analysis']['price_ranges']
        print(f"\n价格预测区间 (30天):")
        for conf, data in ranges.items():
            print(f"  {conf}: ${data['lower']:.2f} - ${data['upper']:.2f} (区间: ${data['range']:.2f})")

        # 期权推荐
        rec = result.get('option_recommendation', {})
        if rec:
            print(f"\n推荐期权策略: {rec.get('strategy', 'N/A')}")
            print(f"  期权类型: {rec.get('type', 'N/A')}")
            if rec.get('strike') is not None:
                print(f"  行权价: ${rec['strike']:.2f}")
            if rec.get('expiry_date'):
                print(f"  到期日: {rec['expiry_date']}")
            print(f"  建议仓位: {rec.get('position_size', 0):.1%}")
            print(f"  风险等级: {rec.get('risk_level', 'N/A')}")
            print(f"  目标价位: {rec.get('target_price', 0):.2f}")
            print(f"  说明: {rec.get('rationale', 'N/A')}")
            if rec.get('support') is not None and rec.get('resistance') is not None:
                print(f"  价位参考区间: ${rec['support']:.2f} - ${rec['resistance']:.2f}")

        plot_file = result.get('plot_file')
        if plot_file:
            print(f"\n图表保存: {plot_file}")

        print(f"{'='*60}\n")

    def plot_analysis(self, ticker, df, option_chain, result):
        """生成分析图表并保存"""
        fig, axes = plt.subplots(3, 1, figsize=(14, 16), constrained_layout=True)

        axes[0].plot(df.index, df['Close'], label='Close', color='tab:blue')
        axes[0].plot(df['Close'].rolling(20).mean(), label='MA20', color='tab:orange')
        axes[0].plot(df['Close'].rolling(50).mean(), label='MA50', color='tab:green')
        axes[0].set_title(f"{ticker} 价格走势与均线")
        axes[0].legend()
        axes[0].grid(True)

        if not option_chain.empty:
            expiry_days = int(result['option_recommendation'].get('expiry_days', 30) or 30)
            subset = option_chain[option_chain['expiry_days'] == expiry_days]
            if not subset.empty:
                axes[1].plot(subset['strike'], subset['delta'], label='Delta', color='tab:blue')
                axes[1].plot(subset['strike'], subset['gamma'], label='Gamma', color='tab:orange')
                axes[1].set_title(f"{expiry_days}天到期 Option Greeks")
                axes[1].legend()
                axes[1].grid(True)

                axes[2].plot(subset['strike'], subset['vega'], label='Vega', color='tab:green')
                axes[2].plot(subset['strike'], subset['theta'], label='Theta', color='tab:red')
                axes[2].set_title(f"{expiry_days}天到期 Vega/Theta")
                axes[2].legend()
                axes[2].grid(True)
            else:
                axes[1].text(0.5, 0.5, 'No option data for selected expiry', ha='center')
                axes[2].text(0.5, 0.5, 'No option data for selected expiry', ha='center')
        else:
            axes[1].text(0.5, 0.5, 'No option chain data', ha='center')
            axes[2].text(0.5, 0.5, 'No option chain data', ha='center')

        plot_file = self.results_dir / f"{ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close(fig)
        logger.info(f"图表已保存到: {plot_file}")
        return str(plot_file)

    def run_single_analysis(self, ticker='SPY'):
        """运行单次分析"""
        result = self.analyze_market_and_adjust_strategy(ticker)
        if result:
            self.print_summary(result)
            return result
        return None

# 主程序
if __name__ == "__main__":
    print("初始化自动市场策略机器人...")
    try:
        # 创建机器人实例
        bot = AutoMarketStrategyBot(tickers=['SPY'])

        print("运行市场分析...")
        # 运行单次分析
        result = bot.run_single_analysis('SPY')

        if result:
            print("分析完成！")
        else:
            print("分析失败，请检查数据连接")

    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
