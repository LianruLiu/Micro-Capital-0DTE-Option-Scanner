from __future__ import annotations

import argparse
import json

from data_loader import build_provider
from risk import RiskProfile, default_risk_profile
from scanner import scan_market


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Small account options scanner")
    parser.add_argument("--account", type=float, default=None, help="Account size, e.g. 500")
    parser.add_argument("--max-risk", type=float, default=None, help="Max loss per trade, e.g. 80")
    parser.add_argument("--risk-level", choices=["defensive", "balanced", "aggressive"], default=None)
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = default_risk_profile()
    profile = RiskProfile(
        account_size=args.account or base.account_size,
        max_risk_per_trade=args.max_risk or base.max_risk_per_trade,
        min_contract_cost=base.min_contract_cost,
        risk_level=args.risk_level or base.risk_level,
    )
    provider = build_provider()
    result = scan_market(provider, profile)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
