"""数据库管理器 - 存储实时分析和推荐结果"""
import sqlite3
import json
from datetime import datetime
import threading
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AnalysisDatabase:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path='analysis_results.db'):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 市场分析结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    regime TEXT,
                    confidence REAL,
                    volatility REAL,
                    momentum_20 REAL,
                    momentum_50 REAL,
                    momentum_200 REAL,
                    current_price REAL,
                    UNIQUE(ticker, timestamp)
                )
            ''')
            
            # 期权推荐表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS option_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    strategy TEXT,
                    option_type TEXT,
                    strike REAL,
                    expiry_date TEXT,
                    expiry_days INTEGER,
                    position_size REAL,
                    risk_level TEXT,
                    target_price REAL,
                    support REAL,
                    resistance REAL,
                    rationale TEXT,
                    greeks_delta REAL,
                    greeks_gamma REAL,
                    greeks_theta REAL,
                    greeks_vega REAL,
                    greeks_rho REAL,
                    iv REAL,
                    expected_return REAL,
                    sharpe_ratio REAL,
                    UNIQUE(ticker, strategy, timestamp)
                )
            ''')
            
            # 投资组合推荐表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    portfolio_data TEXT NOT NULL,
                    total_return REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    var_95 REAL,
                    recommendation_summary TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # 实时行情缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_cache (
                    ticker TEXT PRIMARY KEY,
                    last_price REAL,
                    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
                    bid REAL,
                    ask REAL,
                    volume REAL
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_timestamp ON market_analysis(ticker, timestamp DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_option_ticker ON option_recommendations(ticker, timestamp DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_timestamp ON portfolio_recommendations(timestamp DESC)')
            
            conn.commit()
            logger.info(f"数据库初始化完成: {self.db_path}")
    
    def save_market_analysis(self, ticker: str, analysis: Dict):
        """保存市场分析结果"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO market_analysis
                        (ticker, regime, confidence, volatility, momentum_20, momentum_50, momentum_200, current_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker,
                        analysis.get('regime'),
                        analysis.get('confidence'),
                        analysis.get('volatility'),
                        analysis.get('momentum_20'),
                        analysis.get('momentum_50'),
                        analysis.get('momentum_200'),
                        analysis.get('current_price')
                    ))
                    conn.commit()
                    logger.debug(f"保存市场分析: {ticker}")
            except Exception as e:
                logger.error(f"保存市场分析失败: {e}")
    
    def save_option_recommendation(self, ticker: str, recommendation: Dict):
        """保存期权推荐"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO option_recommendations
                        (ticker, strategy, option_type, strike, expiry_date, expiry_days, position_size,
                         risk_level, target_price, support, resistance, rationale,
                         greeks_delta, greeks_gamma, greeks_theta, greeks_vega, greeks_rho, iv,
                         expected_return, sharpe_ratio)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker,
                        recommendation.get('strategy'),
                        recommendation.get('type'),
                        recommendation.get('strike'),
                        recommendation.get('expiry_date'),
                        recommendation.get('expiry_days'),
                        recommendation.get('position_size'),
                        recommendation.get('risk_level'),
                        recommendation.get('target_price'),
                        recommendation.get('support'),
                        recommendation.get('resistance'),
                        recommendation.get('rationale'),
                        recommendation.get('greeks', {}).get('delta'),
                        recommendation.get('greeks', {}).get('gamma'),
                        recommendation.get('greeks', {}).get('theta'),
                        recommendation.get('greeks', {}).get('vega'),
                        recommendation.get('greeks', {}).get('rho'),
                        recommendation.get('iv'),
                        recommendation.get('expected_return'),
                        recommendation.get('sharpe_ratio')
                    ))
                    conn.commit()
                    logger.debug(f"保存期权推荐: {ticker} - {recommendation.get('strategy')}")
            except Exception as e:
                logger.error(f"保存期权推荐失败: {e}")
    
    def save_portfolio_recommendation(self, portfolio_data: List[Dict], metrics: Dict):
        """保存投资组合推荐"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO portfolio_recommendations
                        (portfolio_data, total_return, sharpe_ratio, max_drawdown, var_95, recommendation_summary)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        json.dumps(portfolio_data, ensure_ascii=False),
                        metrics.get('total_return'),
                        metrics.get('sharpe_ratio'),
                        metrics.get('max_drawdown'),
                        metrics.get('var_95'),
                        metrics.get('summary')
                    ))
                    conn.commit()
                    logger.debug("保存投资组合推荐")
            except Exception as e:
                logger.error(f"保存投资组合推荐失败: {e}")
    
    def get_latest_analysis(self, ticker: str, limit: int = 1) -> List[Dict]:
        """获取最新分析结果"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM market_analysis 
                        WHERE ticker = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (ticker, limit))
                    return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"获取分析结果失败: {e}")
                return []
    
    def get_top_recommendations(self, limit: int = 10, order_by: str = 'expected_return') -> List[Dict]:
        """获取排名靠前的推荐"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    # 去重：每个ticker+strategy只取最新的
                    cursor.execute(f'''
                        SELECT * FROM option_recommendations 
                        WHERE timestamp IN (
                            SELECT MAX(timestamp) 
                            FROM option_recommendations 
                            GROUP BY ticker, strategy
                        )
                        ORDER BY {order_by} DESC NULLS LAST
                        LIMIT ?
                    ''', (limit,))
                    return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"获取推荐列表失败: {e}")
                return []
    
    def get_all_tickers(self) -> List[str]:
        """获取所有跟踪的股票"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT DISTINCT ticker FROM market_analysis ORDER BY ticker')
                    return [row[0] for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"获取股票列表失败: {e}")
                return []
    
    def get_portfolio_recommendation(self, recommendation_id: int = None) -> Optional[Dict]:
        """获取投资组合推荐"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    if recommendation_id:
                        cursor.execute('SELECT * FROM portfolio_recommendations WHERE id = ?', (recommendation_id,))
                    else:
                        cursor.execute('''
                            SELECT * FROM portfolio_recommendations 
                            WHERE status = 'active'
                            ORDER BY timestamp DESC 
                            LIMIT 1
                        ''')
                    row = cursor.fetchone()
                    if row:
                        result = dict(row)
                        result['portfolio_data'] = json.loads(result['portfolio_data'])
                        return result
                    return None
            except Exception as e:
                logger.error(f"获取投资组合推荐失败: {e}")
                return None
    
    def update_price_cache(self, ticker: str, price_data: Dict):
        """更新价格缓存"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO price_cache 
                        (ticker, last_price, bid, ask, volume)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        ticker,
                        price_data.get('last_price'),
                        price_data.get('bid'),
                        price_data.get('ask'),
                        price_data.get('volume')
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"更新价格缓存失败: {e}")
    
    def get_price_cache(self, ticker: str) -> Optional[Dict]:
        """获取价格缓存"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM price_cache WHERE ticker = ?', (ticker,))
                    row = cursor.fetchone()
                    return dict(row) if row else None
            except Exception as e:
                logger.error(f"获取价格缓存失败: {e}")
                return None
