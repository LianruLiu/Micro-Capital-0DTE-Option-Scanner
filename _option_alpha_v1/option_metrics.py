from __future__ import annotations

from dataclasses import dataclass

import config
from data_loader import OptionContract, StockSnapshot


@dataclass(frozen=True)
class ScoredOption:
    contract: OptionContract
    score: int
    roi_potential: float
    probability: float
    gamma_explosion: float
    liquidity: float
    iv_fairness: float
    expected_move_distance: float
    reasons: list[str]

    @property
    def cost(self) -> float:
        return self.contract.cost


def relative_volume(stock: StockSnapshot) -> float:
    if stock.avg_volume <= 0:
        return 0.0
    return stock.volume / stock.avg_volume


def expected_move(stock: StockSnapshot, iv: float, days_to_expiry: int = 1) -> float:
    iv_decimal = iv / 100
    iv_move = stock.price * iv_decimal * (days_to_expiry / 365) ** 0.5
    return max(stock.atr * 0.75, iv_move)


def infer_bias(stock: StockSnapshot, market_direction: str) -> str:
    above_vwap = stock.price > stock.vwap
    strong_volume = relative_volume(stock) >= 1.05
    if stock.change_pct > 0.5 and above_vwap and market_direction == "risk-on" and strong_volume:
        return "bullish"
    if stock.change_pct < -0.5 and not above_vwap and market_direction == "risk-off" and strong_volume:
        return "bearish"
    if stock.change_pct > 1.5 and above_vwap:
        return "bullish"
    if stock.change_pct < -1.5 and not above_vwap:
        return "bearish"
    return "neutral"


def score_option(contract: OptionContract, stock: StockSnapshot, bias: str, days_to_expiry: int = 1) -> ScoredOption:
    em = expected_move(stock, contract.iv, days_to_expiry)
    distance_to_em = abs(abs(contract.strike - stock.price) - em)
    em_quality = 1 - clamp(distance_to_em / max(em, 0.01), 0, 1)
    delta_quality = 1 if config.TARGET_DELTA_MIN <= abs(contract.delta) <= config.TARGET_DELTA_MAX else 0.45
    roi_potential = clamp((em / max(contract.ask, 0.01)) / 8, 0, 1)
    probability = clamp((delta_quality * 0.55) + (em_quality * 0.35) + trend_alignment(contract, bias) * 0.1, 0, 1)
    gamma_explosion = clamp(contract.gamma / 0.32, 0, 1)
    liquidity = clamp((contract.volume / 800) * 0.55 + (contract.open_interest / 2500) * 0.45, 0, 1)
    iv_fairness = clamp(1 - max(contract.iv - 75, 0) / 55 - contract.spread_pct * 0.55, 0, 1)

    raw_score = (
        roi_potential * 0.30
        + probability * 0.25
        + gamma_explosion * 0.20
        + liquidity * 0.15
        + iv_fairness * 0.10
    )
    reasons = build_reasons(contract, em_quality, delta_quality, liquidity, iv_fairness)

    return ScoredOption(
        contract=contract,
        score=round(raw_score * 100),
        roi_potential=roi_potential,
        probability=probability,
        gamma_explosion=gamma_explosion,
        liquidity=liquidity,
        iv_fairness=iv_fairness,
        expected_move_distance=distance_to_em,
        reasons=reasons,
    )


def trend_alignment(contract: OptionContract, bias: str) -> float:
    if bias == "bullish" and contract.option_type == "call":
        return 1.0
    if bias == "bearish" and contract.option_type == "put":
        return 1.0
    return 0.0


def build_reasons(contract: OptionContract, em_quality: float, delta_quality: float, liquidity: float, iv_fairness: float) -> list[str]:
    reasons = []
    if em_quality >= 0.72:
        reasons.append("strike 靠近 Expected Move")
    if delta_quality >= 1:
        reasons.append("Delta 位于 0.15-0.30 爆发区")
    if contract.gamma >= 0.18:
        reasons.append("Gamma 弹性高")
    if liquidity >= 0.65:
        reasons.append("Volume/OI 合格")
    if iv_fairness < 0.45:
        reasons.append("IV 或 spread 偏贵")
    return reasons


def clamp(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))
