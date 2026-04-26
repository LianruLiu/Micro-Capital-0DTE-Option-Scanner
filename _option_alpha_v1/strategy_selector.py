from __future__ import annotations

from dataclasses import dataclass

from data_loader import StockSnapshot
from option_metrics import ScoredOption, expected_move
from risk import RiskProfile


@dataclass(frozen=True)
class StrategyRecommendation:
    ticker: str
    bias: str
    strategy: str
    legs: list[str]
    cost: float
    max_profit: float | None
    odds: float | None
    score: int
    risk: str
    reason: str


def select_best_strategies(
    stock: StockSnapshot,
    bias: str,
    options: list[ScoredOption],
    profile: RiskProfile,
) -> list[StrategyRecommendation]:
    direction = "call" if bias == "bullish" else "put"
    directional = [item for item in options if item.contract.option_type == direction]
    ranked = sorted(directional, key=lambda item: item.score, reverse=True)
    if not ranked:
        return []

    recommendations = []
    debit = build_debit_spread(stock, bias, ranked, profile)
    if debit:
        recommendations.append(debit)

    lottery = build_lottery(stock, bias, ranked, profile)
    if lottery:
        recommendations.append(lottery)

    butterfly = build_broken_wing_butterfly(stock, bias, ranked, profile)
    if butterfly:
        recommendations.append(butterfly)

    return sorted(recommendations, key=lambda item: item.score, reverse=True)[:2]


def build_lottery(stock: StockSnapshot, bias: str, ranked: list[ScoredOption], profile: RiskProfile) -> StrategyRecommendation | None:
    candidate = next((item for item in ranked if item.cost <= min(55, profile.max_risk_per_trade)), None)
    if not candidate:
        return None
    multiplier = 10 if candidate.contract.gamma >= 0.18 else 6
    return StrategyRecommendation(
        ticker=stock.symbol,
        bias=bias,
        strategy="1DTE Lottery Call/Put",
        legs=[format_leg(candidate)],
        cost=round(candidate.cost, 2),
        max_profit=round(candidate.cost * multiplier, 2),
        odds=multiplier,
        score=max(0, candidate.score - 5),
        risk="high",
        reason="低成本 OTM，靠近 Expected Move，适合趋势爆发日小仓位。",
    )


def build_debit_spread(stock: StockSnapshot, bias: str, ranked: list[ScoredOption], profile: RiskProfile) -> StrategyRecommendation | None:
    if len(ranked) < 2:
        return None
    long_leg = ranked[0]
    farther = sorted(ranked[1:], key=lambda item: abs(item.contract.strike - long_leg.contract.strike), reverse=True)[0]
    width = abs(farther.contract.strike - long_leg.contract.strike) * 100
    debit = max(1, long_leg.contract.ask * 100 - farther.contract.bid * 100)
    if debit > profile.max_risk_per_trade:
        debit = min(profile.max_risk_per_trade, long_leg.cost)
    max_profit = max(width - debit, 0)
    if max_profit <= 0:
        return None
    return StrategyRecommendation(
        ticker=stock.symbol,
        bias=bias,
        strategy="0DTE/1DTE Debit Spread",
        legs=[f"BUY {format_leg(long_leg)}", f"SELL {format_leg(farther)}"],
        cost=round(debit, 2),
        max_profit=round(max_profit, 2),
        odds=round(max_profit / debit, 2),
        score=min(100, long_leg.score + 4),
        risk="medium",
        reason="定义风险，成本可控，赔率和概率比裸买 OTM 更平衡。",
    )


def build_broken_wing_butterfly(stock: StockSnapshot, bias: str, ranked: list[ScoredOption], profile: RiskProfile) -> StrategyRecommendation | None:
    if len(ranked) < 3:
        return None
    legs = ranked[:3]
