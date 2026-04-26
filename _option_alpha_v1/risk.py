from __future__ import annotations

from dataclasses import dataclass

import config
from option_metrics import ScoredOption


@dataclass(frozen=True)
class RiskProfile:
    account_size: float
    max_risk_per_trade: float
    min_contract_cost: float
    risk_level: str

    @property
    def max_daily_loss(self) -> float:
        return min(self.account_size * 0.18, self.max_risk_per_trade * 2)


def default_risk_profile() -> RiskProfile:
    return RiskProfile(
        account_size=config.ACCOUNT_SIZE,
        max_risk_per_trade=config.MAX_RISK_PER_TRADE,
        min_contract_cost=config.MIN_CONTRACT_COST,
        risk_level=config.RISK_LEVEL,
    )


def contract_allowed(option: ScoredOption, profile: RiskProfile) -> tuple[bool, list[str]]:
    reasons = []
    contract = option.contract
    if option.cost > profile.max_risk_per_trade:
        reasons.append(f"成本 ${option.cost:.0f} 超过单笔上限 ${profile.max_risk_per_trade:.0f}")
    if option.cost < profile.min_contract_cost:
        reasons.append(f"合约太便宜，容易是低质量彩票单")
    if contract.spread_pct > config.MAX_SPREAD_PCT:
        reasons.append(f"bid/ask spread 过宽：{contract.spread_pct:.0%}")
    if contract.iv < config.MIN_IV:
        reasons.append(f"IV {contract.iv:.0f} 低于 {config.MIN_IV:.0f}")
    if contract.volume < config.MIN_OPTION_VOLUME:
        reasons.append("期权 Volume 不足")
    if contract.open_interest < config.MIN_OPEN_INTEREST:
        reasons.append("Open Interest 不足")
    if abs(contract.delta) < 0.10:
        reasons.append("Delta 太低，爆发概率不足")
    return len(reasons) == 0, reasons


def position_size(option: ScoredOption, profile: RiskProfile) -> int:
    if option.cost <= 0:
        return 0
    return max(0, int(profile.max_risk_per_trade // option.cost))
