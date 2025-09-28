"""
Vercel 部署入口文件
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 設置工作目錄
os.chdir(project_root)

try:
    from app import create_app
    
    # 創建應用實例
    app = create_app('production')
    
except Exception as e:
    # 如果導入失敗，創建一個簡單的響應
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return f'<h1>部署成功但配置需要調整</h1><p>錯誤信息: {str(e)}</p>'
    
    @app.route('/health')
    def health():
        return {'status': 'error', 'message': str(e)}

# Vercel 入口點
if __name__ == "__main__":
    app.run()
