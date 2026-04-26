import os


WATCHLIST = [
    "TSLA",
    "NVDA",
    "AMD",
    "META",
    "SPY",
    "QQQ",
    "AAPL",
    "COIN",
    "MSTR",
    "PLTR",
    "SOFI",
]

ACCOUNT_SIZE = float(os.getenv("ACCOUNT_SIZE", "500"))
MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "80"))
MIN_CONTRACT_COST = float(os.getenv("MIN_CONTRACT_COST", "10"))
RISK_LEVEL = os.getenv("RISK_LEVEL", "balanced")

MIN_IV = float(os.getenv("MIN_IV", "30"))
MAX_SPREAD_PCT = float(os.getenv("MAX_SPREAD_PCT", "0.18"))
MIN_OPTION_VOLUME = int(os.getenv("MIN_OPTION_VOLUME", "100"))
MIN_OPEN_INTEREST = int(os.getenv("MIN_OPEN_INTEREST", "300"))
TARGET_DELTA_MIN = float(os.getenv("TARGET_DELTA_MIN", "0.15"))
TARGET_DELTA_MAX = float(os.getenv("TARGET_DELTA_MAX", "0.30"))

TRADIER_BASE_URL = os.getenv("TRADIER_BASE_URL", "https://api.tradier.com/v1")
TRADIER_TOKEN = os.getenv("TRADIER_TOKEN", "")

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "1") == "1"
