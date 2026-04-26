from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

try:
    import requests
except ImportError:  # Mock mode can run without third-party packages.
    requests = None

import config


@dataclass(frozen=True)
class StockSnapshot:
    symbol: str
    price: float
    change_pct: float
    volume: int
    avg_volume: int
    day_high: float
    day_low: float
    open_price: float
    vwap: float
    atr: float
    premarket_change_pct: float = 0.0
    postmarket_change_pct: float = 0.0


@dataclass(frozen=True)
class OptionContract:
    symbol: str
    underlying: str
    expiry: str
    option_type: str
    strike: float
    bid: float
    ask: float
    iv: float
    delta: float
    gamma: float
    theta: float
    vega: float
    open_interest: int
    volume: int

    @property
    def mid(self) -> float:
        if self.bid <= 0 and self.ask <= 0:
            return 0.0
        if self.bid <= 0:
            return self.ask
        if self.ask <= 0:
            return self.bid
        return (self.bid + self.ask) / 2

    @property
    def spread_pct(self) -> float:
        if self.mid <= 0:
            return 1.0
        return (self.ask - self.bid) / self.mid

    @property
    def cost(self) -> float:
        return self.ask * 100


class TradierClient:
    def __init__(self, token: str = config.TRADIER_TOKEN, base_url: str = config.TRADIER_BASE_URL):
        self.token = token
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        if requests is None:
            raise RuntimeError("Install requirements.txt before using Tradier live data")
        if not self.token:
            raise RuntimeError("TRADIER_TOKEN is required when USE_MOCK_DATA=0")
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def get_option_expirations(self, symbol: str) -> list[str]:
        url = f"{self.base_url}/markets/options/expirations"
        response = requests.get(url, headers=self._headers(), params={"symbol": symbol}, timeout=8)
        response.raise_for_status()
        dates = response.json().get("expirations", {}).get("date", [])
        return dates if isinstance(dates, list) else [dates]

    def get_quote(self, symbol: str) -> StockSnapshot:
        url = f"{self.base_url}/markets/quotes"
        response = requests.get(url, headers=self._headers(), params={"symbols": symbol}, timeout=8)
        response.raise_for_status()
        quote = response.json().get("quotes", {}).get("quote", {})
        if isinstance(quote, list):
            quote = quote[0]

        price = float(quote.get("last") or quote.get("close") or 0)
        volume = int(quote.get("volume") or 0)
        avg_volume = int(quote.get("average_volume") or max(volume, 1))
        day_high = float(quote.get("high") or price)
        day_low = float(quote.get("low") or price)
