"""
Vercel 部署入口文件 - 簡化版本
"""
from flask import Flask, send_from_directory
import os

# 創建 Flask 應用
app = Flask(__name__, static_folder='../static', static_url_path='/static')

@app.route('/')
def index():
    """主頁面"""
    try:
        return send_from_directory('../static', 'index.html')
    except:
        return """
        <html>
        <head>
            <title>零差錯 AI 語音點餐系統</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gradient-to-br from-blue-900 to-purple-900 min-h-screen flex items-center justify-center">
            <div class="text-center text-white p-8 max-w-2xl">
                <h1 class="text-4xl font-bold mb-6">🎤 零差錯 AI 語音點餐系統</h1>
                <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 mb-6">
                    <h2 class="text-2xl font-semibold mb-4">演示系統已成功部署！</h2>
                    <p class="text-lg mb-4">這是一個專為香港餐廳設計的智能語音點餐解決方案</p>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                        <div class="bg-green-500/20 p-4 rounded-lg">
                            <h3 class="font-bold mb-2">✅ 核心功能</h3>
                            <ul class="text-sm space-y-1">
                                <li>• 粵語語音識別</li>
                                <li>• 智能訂單解析</li>
                                <li>• 追加銷售建議</li>
                                <li>• 響應式界面</li>
                            </ul>
                        </div>
                        <div class="bg-blue-500/20 p-4 rounded-lg">
                            <h3 class="font-bold mb-2">🛠 技術棧</h3>
                            <ul class="text-sm space-y-1">
                                <li>• Python Flask 後端</li>
                                <li>• Azure Speech Services</li>
                                <li>• OpenRouter AI API</li>
                                <li>• Tailwind CSS 前端</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="space-y-4">
                    <p class="text-yellow-300">⚠️ 完整功能需要配置 API 密鑰</p>
                    <div class="flex flex-wrap gap-4 justify-center">
                        <a href="/admin" class="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-semibold transition-colors">管理員面板</a>
                        <a href="/health" class="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-semibold transition-colors">系統健康檢查</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/admin')
def admin():
    """管理員頁面"""
    try:
        return send_from_directory('../static', 'admin.html')
    except:
        return '<h1>管理員界面</h1><p>靜態文件載入中...</p>'

@app.route('/health')
def health():
    """健康檢查"""
    return {
        'status': 'healthy',
        'service': '零差錯 AI 語音點餐系統',
        'version': '1.0.0',
        'deployment': 'vercel',
        'message': 'API 功能需要環境變量配置'
    }

@app.route('/api/test')
def test():
    """測試端點"""
    return {
        'message': '系統運行正常',
        'environment': 'production',
        'platform': 'vercel'
    }

# 靜態文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    """靜態文件路由"""
    try:
        return send_from_directory('../static', filename)
    except:
        return f'文件未找到: {filename}', 404

if __name__ == "__main__":
    app.run(debug=False)
