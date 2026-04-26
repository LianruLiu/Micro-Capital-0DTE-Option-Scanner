from __future__ import annotations

from dataclasses import asdict, dataclass

import config
from data_loader import MockDataProvider, StockSnapshot
from option_metrics import ScoredOption, infer_bias, relative_volume, score_option
from risk import RiskProfile, contract_allowed, position_size
from strategy_selector import StrategyRecommendation, select_best_strategies


@dataclass(frozen=True)
class TickerResult:
    ticker: str
    bias: str
    tradable: bool
    score: int
    price: float
    change_pct: float
    iv: float
    relative_volume: float
    rejects: list[str]
    best_options: list[ScoredOption]
    strategies: list[StrategyRecommendation]


def scan_market(provider: MockDataProvider, profile: RiskProfile) -> dict:
    market = provider.get_market_context()
    results = [scan_ticker(symbol, provider, profile, market) for symbol in config.WATCHLIST]
    tradable = sorted([item for item in results if item.tradable], key=lambda item: item.score, reverse=True)
    top = tradable[:3]
    return {
        "market": market,
        "account": asdict(profile),
        "top_3": [serialize_result(item, profile) for item in top],
        "rejected": [serialize_result(item, profile) for item in results if not item.tradable],
        "signals": build_signals(top, results, market),
    }


def scan_ticker(symbol: str, provider: MockDataProvider, profile: RiskProfile, market: dict) -> TickerResult:
    stock = provider.get_stock_snapshot(symbol)
    chain = provider.get_option_chain(symbol)
    bias = infer_bias(stock, str(market["market_direction"]))
    rvol = relative_volume(stock)
    scored = [score_option(contract, stock, bias) for contract in chain]
    allowed = []
    rejects = hard_filter_reasons(stock, chain, bias, market)

    for option in scored:
        ok, reasons = contract_allowed(option, profile)
        if ok and direction_matches(option, bias):
            allowed.append(option)

    best_options = sorted(allowed, key=lambda item: item.score, reverse=True)[:5]
    strategies = select_best_strategies(stock, bias, best_options, profile) if bias != "neutral" else []
    if not best_options:
        rejects.append("预算内没有合格合约")
    if not strategies:
        rejects.append("没有形成合格策略结构")

    rejects = sorted(set(rejects))
    score = max([option.score for option in best_options], default=0)
    return TickerResult(
        ticker=symbol,
        bias=bias,
        tradable=len(rejects) == 0,
        score=score,
        price=stock.price,
        change_pct=stock.change_pct,
        iv=max([contract.iv for contract in chain], default=0),
        relative_volume=rvol,
        rejects=rejects,
        best_options=best_options,
        strategies=strategies,
    )


def hard_filter_reasons(stock: StockSnapshot, chain: list, bias: str, market: dict) -> list[str]:
    reasons = []
    avg_iv = sum(contract.iv for contract in chain) / max(len(chain), 1)
    liquid_count = sum(1 for contract in chain if contract.volume >= config.MIN_OPTION_VOLUME and contract.open_interest >= config.MIN_OPEN_INTEREST)
    if avg_iv < config.MIN_IV:
        reasons.append(f"IV {avg_iv:.0f} 低于 {config.MIN_IV:.0f}")
    if relative_volume(stock) < 1.05:
        reasons.append("今日成交量没有放大")
    if bias == "neutral":
        reasons.append("方向不清晰")
    if liquid_count < 4:
        reasons.append("期权链不够活跃")
    if market["market_direction"] == "risk-on" and bias == "bearish":
        reasons.append("与大盘 risk-on 方向冲突")
    if market["market_direction"] == "risk-off" and bias == "bullish":
        reasons.append("与大盘 risk-off 方向冲突")
    return reasons


def direction_matches(option: ScoredOption, bias: str) -> bool:
    if bias == "bullish":
        return option.contract.option_type == "call"
