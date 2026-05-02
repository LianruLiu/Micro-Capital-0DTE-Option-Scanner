"""FastAPI Web应用 - 可视化仪表板和API"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import os
import json
from datetime import datetime, timedelta
import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

# 导入自定义模块
from auto_market_strategy import AutoMarketStrategyBot
from db_manager import AnalysisDatabase
from portfolio_optimizer import PortfolioOptimizer, GreeksAnalyzer, combine_stock_options

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent

# 初始化
app = FastAPI(title="量化交易仪表板", description="自动化期权策略推荐系统")
if (BASE_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
db = AnalysisDatabase(db_path=str(BASE_DIR / "analysis_results.db"))
optimizer = PortfolioOptimizer()
scheduler = BackgroundScheduler()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class TickerRequest(BaseModel):
    ticker: str
    lookback_days: int = 60

class PortfolioRequest(BaseModel):
    tickers: List[str]
    total_capital: float = 100000

class RecommendationResponse(BaseModel):
    ticker: str
    strategy: str
    strike: float
    expiry_date: str
    position_size: float
    expected_return: float
    greeks: Dict
    risk_level: str

# ============ API 端点 ============

@app.get("/")
async def root():
    """返回主仪表板页面"""
    return FileResponse(str(BASE_DIR / "templates" / "dashboard.html"), media_type="text/html")

@app.get("/api/tickers")
async def get_tickers():
    """获取所有跟踪的股票列表"""
    tickers = db.get_all_tickers()
    return {"tickers": tickers, "count": len(tickers)}

@app.post("/api/analyze/{ticker}")
async def analyze_ticker(ticker: str, background_tasks: BackgroundTasks):
    """分析单个股票"""
    try:
        bot = AutoMarketStrategyBot(tickers=[ticker])
        result = bot.run_single_analysis(ticker)
        
        # 保存到数据库
        if result:
            db.save_market_analysis(ticker, result.get('market_regime', {}))
            
            if 'option_recommendation' in result:
                db.save_option_recommendation(ticker, result['option_recommendation'])
                
                # 计算Greeks分析
                greeks_analysis = GreeksAnalyzer.analyze_greeks(result['option_recommendation'])
                
                return {
                    "success": True,
                    "ticker": ticker,
                    "regime": result['market_regime'],
                    "option_recommendation": result['option_recommendation'],
                    "greeks_analysis": greeks_analysis,
                    "timestamp": datetime.now().isoformat()
                }
        
        return {"success": False, "message": "分析失败"}
    
    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/{ticker}")
async def get_latest_analysis(ticker: str, limit: int = 5):
    """获取最新分析结果"""
    try:
        results = db.get_latest_analysis(ticker, limit)
        return {
            "ticker": ticker,
            "analysis": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations")
async def get_recommendations(limit: int = 20, order_by: str = "expected_return"):
    """获取排名靠前的推荐"""
    try:
        recommendations = db.get_top_recommendations(limit, order_by)
        
        # 格式化返回数据
        formatted = []
        for rec in recommendations:
            if rec.get('timestamp'):
                rec['timestamp'] = str(rec['timestamp'])
            formatted.append(rec)
        
        return {
            "recommendations": formatted,
            "count": len(formatted),
            "sort_by": order_by,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize-portfolio")
async def optimize_portfolio(request: PortfolioRequest):
    """优化投资组合"""
    try:
        # 获取每个ticker的最新推荐
        assets = []
        all_options = []
        
        for ticker in request.tickers:
            analysis = db.get_latest_analysis(ticker, 1)
            if analysis:
                rec = db.get_top_recommendations(limit=3, order_by="expected_return")
                ticker_recs = [r for r in rec if r['ticker'] == ticker]
                all_options.extend(ticker_recs)
                
                # 添加股票资产
                latest = analysis[0]
                assets.append({
                    'name': f'{ticker} Stock',
                    'ticker': ticker,
                    'type': 'stock',
                    'price': latest.get('current_price', 100),
                    'expected_return': 0.10,  # 可根据momentum调整
                    'volatility': latest.get('volatility', 0.2)
                })
        
        # 组合股票和期权
        combined_assets = combine_stock_options(
            stock_price=assets[0]['price'] if assets else 100,
            stock_return=0.10,
            stock_vol=0.2,
            option_recs=all_options
        )
        
        # 优化
        portfolio = optimizer.optimize_portfolio(
            combined_assets,
            all_options,
            request.total_capital
        )
        
        # 保存投资组合
        metrics = {
            'total_return': portfolio.get('expected_return', 0),
            'sharpe_ratio': portfolio.get('sharpe_ratio', 0),
            'max_drawdown': -0.1,
            'var_95': 0.05,
            'summary': portfolio.get('summary', '')
        }
        db.save_portfolio_recommendation(portfolio['positions'], metrics)
        
        return portfolio
    
    except Exception as e:
        logger.error(f"投资组合优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio")
async def get_portfolio(recommendation_id: Optional[int] = None):
    """获取当前投资组合"""
    try:
        portfolio = db.get_portfolio_recommendation(recommendation_id)
        if portfolio:
            return {
                "portfolio": portfolio,
                "timestamp": datetime.now().isoformat()
            }
        return {"message": "未找到投资组合推荐"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/greeks/{ticker}")
async def get_greeks_analysis(ticker: str):
    """获取Greeks分析"""
    try:
        recommendations = db.get_top_recommendations(limit=10)
        ticker_recs = [r for r in recommendations if r['ticker'] == ticker]
        
        greeks_data = []
        for rec in ticker_recs:
            greeks_analysis = GreeksAnalyzer.analyze_greeks(rec)
            greeks_data.append({
                "strategy": rec.get('strategy'),
                "greeks": greeks_analysis,
                "strike": rec.get('strike'),
                "expiry_date": rec.get('expiry_date')
            })
        
        return {
            "ticker": ticker,
            "greeks_analysis": greeks_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/heat-map")
async def get_heat_map():
    """获取策略热力图数据"""
    try:
        recommendations = db.get_top_recommendations(limit=100)
        
        # 组织为矩阵形式：ticker x strategy
        heat_map = {}
        for rec in recommendations:
            ticker = rec.get('ticker', 'N/A')
            strategy = rec.get('strategy', 'N/A')
            score = rec.get('sharpe_ratio', 0) or 0
            
            if ticker not in heat_map:
                heat_map[ticker] = {}
            
            heat_map[ticker][strategy] = {
                'score': score,
                'return': rec.get('expected_return', 0),
                'risk_level': rec.get('risk_level', 'medium'),
                'timestamp': str(rec.get('timestamp', ''))
            }
        
        return {
            "heat_map": heat_map,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ 后台任务 ============

async def background_analysis():
    """后台持续分析"""
    try:
        tickers = ['SPY', 'QQQ', 'IWM', 'EEM', 'EFA']  # 可配置
        bot = AutoMarketStrategyBot(tickers=tickers)
        
        for ticker in tickers:
            try:
                result = bot.run_single_analysis(ticker)
                if result:
                    db.save_market_analysis(ticker, result.get('market_regime', {}))
                    if 'option_recommendation' in result:
                        db.save_option_recommendation(ticker, result['option_recommendation'])
                logger.info(f"后台分析完成: {ticker}")
            except Exception as e:
                logger.error(f"后台分析失败 {ticker}: {e}")
    
    except Exception as e:
        logger.error(f"后台任务失败: {e}")

def schedule_background_tasks():
    """启动后台任务调度"""
    # 每30分钟运行一次分析
    scheduler.add_job(background_analysis, 'interval', minutes=30)
    scheduler.start()
    logger.info("后台任务调度已启动")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    schedule_background_tasks()
    logger.info("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    scheduler.shutdown()
    logger.info("应用已关闭")

# ============ 健康检查 ============

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tickers_tracked": len(db.get_all_tickers())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
