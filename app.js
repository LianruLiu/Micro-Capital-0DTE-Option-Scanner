const WATCHLIST = ["TSLA", "NVDA", "AMD", "META", "SPY", "QQQ", "AAPL", "COIN", "MSTR", "PLTR", "SOFI"];

const marketProfiles = {
  trend: {
    spy: "上行趋势",
    qqq: "强于 SPY",
    vix: 16.8,
    yield10y: 4.52,
    direction: "risk-on",
    volumeBoost: 1.05,
  },
  chop: {
    spy: "VWAP 附近震荡",
    qqq: "无清晰方向",
    vix: 18.9,
    yield10y: 4.61,
    direction: "mixed",
    volumeBoost: 0.86,
  },
  riskoff: {
    spy: "跌破开盘低点",
    qqq: "弱势下行",
    vix: 23.7,
    yield10y: 4.74,
    direction: "risk-off",
    volumeBoost: 1.18,
  },
};

const universe = [
  makeTicker("TSLA", 251.4, 3.2, 65, 1.58, "bullish", 5.8, 248, 3.9, "突破 VWAP 后回踩不破"),
  makeTicker("NVDA", 893.2, 1.7, 48, 1.42, "bullish", 18.5, 884, 3.1, "高位趋势延续，期权成交集中"),
  makeTicker("AMD", 156.8, 0.9, 44, 1.23, "bullish", 4.1, 154, 2.2, "半导体同步走强"),
  makeTicker("META", 486.3, -0.2, 33, 0.92, "neutral", 8.6, 488, 1.4, "方向不够清晰"),
  makeTicker("SPY", 512.5, 0.7, 19, 1.08, "bullish", 4.7, 510, 1.1, "指数稳在 VWAP 上方"),
  makeTicker("QQQ", 438.6, 1.1, 24, 1.16, "bullish", 5.2, 435, 1.4, "科技权重领涨"),
  makeTicker("AAPL", 189.4, 0.3, 27, 0.88, "neutral", 3.4, 190, 1.2, "IV 不足且走势偏慢"),
  makeTicker("COIN", 226.7, 4.6, 72, 1.92, "bullish", 9.8, 219, 5.3, "高波动突破日"),
  makeTicker("MSTR", 1275, 5.4, 89, 1.76, "bullish", 58, 1230, 7.8, "盘口活跃但价差偏宽"),
  makeTicker("PLTR", 24.9, -2.8, 58, 1.61, "bearish", 0.86, 25.2, 0.8, "跌破开盘低点"),
  makeTicker("SOFI", 7.4, 1.8, 51, 1.33, "bullish", 0.28, 7.2, 0.4, "低价票弹性好但 OI 分散"),
];

const form = document.querySelector("#scanner-form");
const topWatchlist = document.querySelector("#top-watchlist");
const optionTable = document.querySelector("#option-table");
const signalFeed = document.querySelector("#signal-feed");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  runScan();
});

function makeTicker(ticker, price, changePct, iv, relativeVolume, bias, atr, vwap, expectedMove, note) {
  return {
    ticker,
    price,
    changePct,
    iv,
    relativeVolume,
    bias,
    atr,
    vwap,
    expectedMove,
    note,
    optionVolume: Math.round((relativeVolume * iv * 950) / Math.max(1, price / 100)),
    optionOpenInterest: Math.round((relativeVolume * iv * 3800) / Math.max(1, price / 120)),
  };
}

function runScan() {
  const params = getParams();
  const market = marketProfiles[params.marketMode];
  const scanUniverse = universe.filter((item) => WATCHLIST.includes(item.ticker));
  const enriched = scanUniverse.map((item) => evaluateTicker(item, market, params));
  const tradable = enriched.filter((item) => item.isTradable);
  const top = tradable.sort((a, b) => b.totalScore - a.totalScore).slice(0, 3);

  renderMarket(market, top.length);
  renderSummary(enriched, top, params);
  renderTopCards(top, enriched);
  renderOptionTable(top.flatMap((item) => item.recommendations));
  renderSignals(top, enriched, market);
}

function getParams() {
  const data = new FormData(form);
  const accountSize = Number(data.get("accountSize"));
  const maxRisk = Number(data.get("maxRisk"));
  return {
    accountSize,
    maxRisk,
    riskLevel: String(data.get("riskLevel")),
    marketMode: String(data.get("marketMode")),
    minRisk: Math.max(10, Math.min(20, maxRisk * 0.35)),
  };
}

function evaluateTicker(item, market, params) {
  const options = buildOptionCandidates(item, params);
