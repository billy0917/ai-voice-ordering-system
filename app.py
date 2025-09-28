"""
零差錯 AI 語音點餐系統 - 主應用程序
"""
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from config import config
from utils.logger import get_app_logger

# 載入環境變量
load_dotenv()

# 設置日誌
logger = get_app_logger()

def create_app(config_name=None):
    """創建 Flask 應用程序實例"""
    # 明確指定靜態文件夾和 URL 路徑
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    
    # 載入配置
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 驗證配置
    try:
        config[config_name].validate_config()
        logger.info("配置驗證成功")
    except ValueError as e:
        logger.error(f"配置驗證失敗: {e}")
        # 在測試環境下不要拋出異常
        if config_name != 'testing':
            raise
    
    # 啟用 CORS
    CORS(app)
    
    # 註冊路由
    from routes.speech_routes import speech_bp
    from routes.order_routes import order_bp
    from routes.main_routes import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(speech_bp, url_prefix='/api/speech')
    app.register_blueprint(order_bp, url_prefix='/api/order')
    
    logger.info("Flask 應用程序創建完成")
    return app

if __name__ == '__main__':
    try:
        # 獲取配置環境
        config_name = os.getenv('FLASK_ENV', 'development')
        app = create_app(config_name)
        
        # 獲取端口配置（支持雲端部署）
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"啟動零差錯 AI 語音點餐系統 - {config_name} 模式")
        logger.info(f"服務器地址: {host}:{port}")
        
        app.run(debug=app.config['DEBUG'], host=host, port=port)
    except Exception as e:
        logger.error(f"應用程序啟動失敗: {e}")
        raise