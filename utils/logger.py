"""
日誌配置工具
"""
import logging
import os
from datetime import datetime
import colorlog

def setup_logger(name=None, log_level='INFO', log_file=None):
    """
    設置日誌記錄器
    
    Args:
        name: 記錄器名稱
        log_level: 日誌級別
        log_file: 日誌文件路徑
    
    Returns:
        logging.Logger: 配置好的記錄器
    """
    logger = logging.getLogger(name or __name__)
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 控制台處理器（彩色輸出）
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件處理器
    if log_file:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_app_logger():
    """獲取應用程序主日誌記錄器"""
    from config import Config
    return setup_logger(
        name='voice_ordering',
        log_level=Config.LOG_LEVEL,
        log_file=Config.LOG_FILE
    )