"""投资组合优化器 - 计算最优资产配置"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """投资组合优化引擎"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """计算历史收益率"""
        return prices.pct_change().dropna()
    
    def portfolio_stats(self, weights: np.ndarray, mean_returns: np.ndarray, 
                       cov_matrix: np.ndarray) -> Tuple[float, float, float]:
        """计算投资组合统计指标
        
        Returns:
            (年化收益率, 年化波动率, 夏普比率)
        """
        portfolio_return = np.sum(weights * mean_returns) * 252
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std if portfolio_std > 0 else 0
        return portfolio_return, portfolio_std, sharpe_ratio
    
    def negative_sharpe(self, weights: np.ndarray, mean_returns: np.ndarray, 
                        cov_matrix: np.ndarray) -> float:
        """负夏普比率（用于最小化）"""
        _, _, sharpe = self.portfolio_stats(weights, mean_returns, cov_matrix)
        return -sharpe
    
    def optimize_portfolio(self, assets: List[Dict], option_recommendations: List[Dict],
                          total_capital: float = 100000) -> Dict:
        """优化投资组合
        
        Args:
            assets: 股票/期权资产列表，每项包含 name, price, expected_return, volatility, sharpe_ratio
            option_recommendations: 期权推荐列表
            total_capital: 总资本
        
        Returns:
            {
                'allocation': {asset_name: weight},
                'expected_return': 预期收益率,
                'volatility': 波动率,
                'sharpe_ratio': 夏普比率,
                'positions': [{asset, quantity, amount, weight, ...}]
            }
        """
        try:
            n_assets = len(assets)
            if n_assets == 0:
                return self._empty_portfolio()
            
            # 构建收益率和波动率矩阵
            returns = np.array([a.get('expected_return', 0.05) for a in assets])
            stds = np.array([a.get('volatility', 0.2) for a in assets])
            
            # 简化版相关系数矩阵（可扩展）
            if n_assets == 1:
                cov_matrix = np.array([[stds[0]**2]])
            else:
                # 假设0.5相关系数
                cov_matrix = np.outer(stds, stds) * 0.5
                np.fill_diagonal(cov_matrix, stds**2)
            
            # 约束条件
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # 权重和为1
            ]
            
            # 边界条件（0到1之间）
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # 初始权重
            init_weights = np.array([1/n_assets] * n_assets)
            
            # 最大化夏普比率（最小化负夏普比率）
            result = minimize(
                self.negative_sharpe,
                init_weights,
                args=(returns, cov_matrix),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                logger.warning(f"优化未收敛: {result.message}，使用等权重配置")
                optimal_weights = init_weights
            else:
                optimal_weights = result.x
            
            # 计算优化后的投资组合指标
            opt_return, opt_vol, opt_sharpe = self.portfolio_stats(
                optimal_weights, returns, cov_matrix
            )
            
            # 生成持仓信息
            positions = []
            for i, asset in enumerate(assets):
                weight = optimal_weights[i]
                amount = weight * total_capital
                quantity = amount / asset.get('price', 1)
                
                positions.append({
                    'asset': asset.get('name', f'Asset{i}'),
                    'ticker': asset.get('ticker'),
                    'type': asset.get('type', 'stock'),  # stock 或 option
                    'weight': weight,
                    'amount': amount,
                    'quantity': quantity,
                    'price': asset.get('price'),
                    'expected_return': asset.get('expected_return'),
                    'volatility': asset.get('volatility'),
                    'strategy': asset.get('strategy'),  # 对于期权
                })
            
            # 排序按权重降序
            positions.sort(key=lambda x: x['weight'], reverse=True)
            
            return {
                'success': True,
                'expected_return': opt_return,
                'volatility': opt_vol,
                'sharpe_ratio': opt_sharpe,
                'positions': positions,
                'total_capital': total_capital,
                'summary': self._generate_summary(opt_return, opt_vol, opt_sharpe, positions)
            }
        
        except Exception as e:
            logger.error(f"投资组合优化失败: {e}")
            return self._empty_portfolio()
    
    def calculate_portfolio_metrics(self, positions: List[Dict]) -> Dict:
        """计算投资组合风险指标"""
        try:
            # 计算VaR (95%)
            returns = np.array([p.get('expected_return', 0.05) for p in positions])
            vols = np.array([p.get('volatility', 0.2) for p in positions])
            weights = np.array([p.get('weight', 0) for p in positions])
            
            portfolio_return = np.sum(returns * weights)
            portfolio_vol = np.sqrt(np.sum((weights * vols) ** 2))  # 简化
            
            # VaR 95% = -1.645 * std
            var_95 = portfolio_return - 1.645 * portfolio_vol
            
            # 最大回撤估算（保守估计）
            max_drawdown = -2 * portfolio_vol
            
            return {
                'portfolio_return': portfolio_return,
                'portfolio_volatility': portfolio_vol,
                'var_95': var_95,
                'max_drawdown': max_drawdown
            }
        except Exception as e:
            logger.error(f"计算投资组合指标失败: {e}")
            return {}
    
    def rank_opportunities(self, recommendations: List[Dict]) -> List[Dict]:
        """按期望收益率排名机会"""
        # 计算综合评分
        for rec in recommendations:
            # 夏普比率权重(40%) + 期望收益(40%) + 风险调整(20%)
            sharpe = rec.get('sharpe_ratio', 0) or 0
            expected_return = rec.get('expected_return', 0) or 0
            risk_level_score = {'low': 0.2, 'medium': 0.15, 'high': 0.1}.get(
                rec.get('risk_level', 'medium'), 0.15
            )
            
            rec['composite_score'] = (
                sharpe * 0.4 + 
                expected_return * 0.4 + 
                risk_level_score * 0.2
            )
        
        # 排序
        sorted_recs = sorted(recommendations, key=lambda x: x.get('composite_score', 0), reverse=True)
        return sorted_recs
    
    def _empty_portfolio(self) -> Dict:
        """返回空投资组合"""
        return {
            'success': False,
            'expected_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'positions': [],
            'summary': '无有效资产进行优化'
        }
    
    def _generate_summary(self, ret: float, vol: float, sharpe: float, 
                         positions: List[Dict]) -> str:
        """生成投资组合摘要"""
        summary = f"预期收益: {ret*100:.2f}% | 波动率: {vol*100:.2f}% | 夏普比率: {sharpe:.2f}\n"
        summary += "主要持仓:\n"
        for i, pos in enumerate(positions[:3], 1):
            summary += f"  {i}. {pos['asset']}: {pos['weight']*100:.1f}% (${pos['amount']:.0f})\n"
        return summary


class GreeksAnalyzer:
    """Greeks分析器"""
    
    @staticmethod
    def analyze_greeks(option_rec: Dict) -> Dict:
        """分析Greeks敏感性"""
        greeks = option_rec.get('greeks', {})
        analysis = {
            'delta': greeks.get('delta', 0),  # 价格敏感性
            'gamma': greeks.get('gamma', 0),  # delta变化率
            'theta': greeks.get('theta', 0),  # 时间衰减
            'vega': greeks.get('vega', 0),   # 波动率敏感性
            'rho': greeks.get('rho', 0),      # 利率敏感性
        }
        
        # 风险评估
        risk_factors = []
        if abs(analysis['delta']) > 0.7:
            risk_factors.append('高方向风险')
        if analysis['gamma'] > 0.05:
            risk_factors.append('高伽玛风险')
        if analysis['vega'] > 0.1:
            risk_factors.append('高波动率风险')
        if analysis['theta'] < -0.05:
            risk_factors.append('时间衰减风险')
        
        analysis['risk_factors'] = risk_factors
        analysis['risk_score'] = len(risk_factors)
        
        return analysis


def combine_stock_options(stock_price: float, stock_return: float, stock_vol: float,
                         option_recs: List[Dict]) -> List[Dict]:
    """组合股票和期权推荐"""
    combined = [
        {
            'name': f'Stock',
            'ticker': 'STOCK',
            'type': 'stock',
            'price': stock_price,
            'expected_return': stock_return,
            'volatility': stock_vol,
            'sharpe_ratio': (stock_return - 0.03) / stock_vol if stock_vol > 0 else 0
        }
    ]
    
    # 转换期权推荐为资产格式
    for opt in option_recs:
        combined.append({
            'name': f"{opt.get('type')} {opt.get('strategy')}",
            'ticker': opt.get('ticker'),
            'type': 'option',
            'price': opt.get('strike', 1),
            'expected_return': opt.get('expected_return', 0.05),
            'volatility': opt.get('greeks', {}).get('vega', 0.1) or 0.1,
            'sharpe_ratio': opt.get('sharpe_ratio', 0),
            'strategy': opt.get('strategy'),
            'greeks': opt.get('greeks', {})
        })
    
    return combined
