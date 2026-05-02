"""启动Web仪表板"""
import os
import sys
from pathlib import Path

# 确保路径正确
project_root = Path(__file__).resolve().parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    from app import app
    
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║  量化交易仪表板 - 自动期权策略推荐系统              ║
    ║  Quantitative Trading Dashboard                     ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    print("🚀 启动Web服务...")
    print("📊 访问地址: http://localhost:8000")
    print("📈 API文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root)],
        log_level="info"
    )
