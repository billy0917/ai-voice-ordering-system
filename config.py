"""
應用程序配置文件
"""
import os
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

class Config:
    """基礎配置類"""
    
    # Flask 基本配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Azure Speech Services 配置
    AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
    AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')
    
    # OpenRouter API 配置
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'x-ai/grok-4-fast:free')
    
    # 網站信息
    SITE_URL = os.getenv('SITE_URL', 'http://localhost:5000')
    SITE_NAME = os.getenv('SITE_NAME', '零差錯 AI 語音點餐系統')
    
    # 數據庫配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///voice_ordering.db')
    
    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # 音頻處理配置
    MAX_AUDIO_SIZE = int(os.getenv('MAX_AUDIO_SIZE', '10485760'))  # 10MB
    SUPPORTED_AUDIO_FORMATS = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/ogg']
    
    # API 配置
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # 30秒
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    @staticmethod
    def validate_config():
        """驗證必要的配置項"""
        required_configs = [
            'AZURE_SPEECH_KEY',
            'AZURE_SPEECH_REGION',
            'OPENROUTER_API_KEY'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not os.getenv(config):
                missing_configs.append(config)
        
        if missing_configs:
            raise ValueError(f"缺少必要的環境變量: {', '.join(missing_configs)}")
        
        return True

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}