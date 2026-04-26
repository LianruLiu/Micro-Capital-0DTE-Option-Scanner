Small Account Options Radar
这是一个“小仓位期权机会雷达”原型，目标不是扫全市场，而是每天只盯高流动性、高波动、盘口活跃的固定 watchlist：

TSLA, NVDA, AMD, META, SPY, QQQ, AAPL, COIN, MSTR, PLTR, SOFI
当前版本是零依赖前端原型，直接打开 index.html 即可运行。页面内置了模拟行情和期权链，用来验证筛选、评分、策略推荐、风控限制和“不做交易”逻辑。

系统目标
小账户模型：

账户资金默认 $500
单笔最大亏损 $20-$80
只寻找小成本、高弹性、亏损可控的 3x-10x 机会
系统必须能主动说“不做”，而不是每天强行给交易
重要提醒：本项目是研究和决策辅助工具，不是投资建议。真实下单前必须接入可靠实时数据、验证报价、确认流动性，并使用自己的风控。

Layer 1：自动抓取
速度优先，数据源建议分层：

股票层：

实时价格、涨跌幅、成交量、相对成交量
ATR、VWAP、盘前盘后波动
开盘高低点、突破位置、日内趋势
期权链：

Strike、Bid、Ask、Mid、Spread
IV、Delta、Gamma、Theta
OI、Volume、Expiry
市场层：

SPY / QQQ 趋势
VIX
10Y Yield
大盘方向
新闻事件、财报、宏观日历
推荐真实数据接口：

Polygon.io：股票分钟线、期权链、Greeks、成交量
Tradier：期权链、报价、订单接口
Interactive Brokers：行情和执行
Benzinga / Financial Modeling Prep：新闻和事件
CBOE 或 FRED：VIX、10Y Yield
Layer 2：机会筛选
只从固定 watchlist 里筛：

IV > 30
今日成交量放大
股票有趋势，不能在 VWAP 附近乱震
期权链活跃，OI 和 Volume 够高
Bid/Ask spread 小
合约价格必须符合账户预算
输出：

今日最值得做的 3 只票
每只票给出 bias、触发原因、推荐策略和不做理由
Layer 3：策略引擎
策略池限定为小仓位适用：

Lottery Call / Put：成本 $10-$50，目标 5x-20x，只用于趋势爆发日
Debit Spread：成本 $30-$100，目标 2x-6x，性价比最高
Broken Wing Butterfly：低成本，中高赔率，要求方向明确
Cheap Earnings Lotto：财报前小金额，不允许重仓
每笔推荐必须输出：

Ticker
Bias
资金预算
策略
Strike / Expiry
成本
最大盈利或目标赔率
风险级别
为什么选它，为什么不选其他合约
Layer 4：最优价位系统
买方逻辑：

低价 OTM
靠近 Expected Move
Delta 在 0.15-0.30
Gamma 高
Spread 小
成交量和 OI 支撑退出
卖方逻辑：

高 IV
Strike 在 Expected Move 外
信用金高
风险回报合理
小账户默认不裸卖，只允许定义风险结构
Layer 5：资金模型
输入：

账户资金
单笔最大亏损
风险等级
输出限制：

合约成本不能超过单笔最大亏损
单日最多 1-3 笔
连亏 2 笔后暂停
大盘缩量或方向混乱时暂停
Layer 6：赔率评分
当前原型使用：

Option Score =
30% ROI Potential
25% Probability
20% Gamma Explosion
15% Liquidity
10% IV Fairness
评分解释：

ROI Potential：最大盈利 / 成本
Probability：Delta、趋势、Expected Move 位置
Gamma Explosion：Gamma 是否足够高
Liquidity：期权 Volume、OI、Bid/Ask spread
IV Fairness：IV 是否贵到不值得买
Layer 7：自动排除
系统必须明确排除垃圾交易：

IV 太低，没有弹性
IV 太高但赔率被吃掉
Spread 太宽，进出成本过高
方向不清晰
与 SPY / QQQ 大方向冲突
期权链不活跃
预算内没有合格合约
Layer 8：实时信号
示例：

09:45 TSLA 突破 VWAP，推荐 255C 或 Debit Spread
10:20 NVDA 跌破开盘低点，推荐 Put Debit Spread
13:00 全市场缩量，暂停交易
生产版本建议：

每 5-15 秒刷新核心 watchlist
每 1-3 秒刷新已入选合约报价
只在信号状态变化时推送提醒
推送内容必须包含“不追价”限制和失效条件
下一步开发路线
抽象 dataProvider，把模拟数据换成真实 API。
增加后端缓存，避免前端直接暴露 API key。
加入 0DTE / 1DTE expiry 选择器。
加入新闻和财报事件惩罚项。
增加交易日志和复盘统计：命中率、平均赔率、最大回撤、连亏次数。
加入 paper trading，先验证信号质量再考虑真实下单。
