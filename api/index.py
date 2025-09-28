"""
Vercel 部署入口文件 - 完整功能版本
"""
import sys
import os
from flask import request

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 設置工作目錄
os.chdir(project_root)

# 設置環境變量（如果在 Vercel 環境中沒有 .env 文件）
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # 導入完整的應用
    from app import create_app
    
    # 創建應用實例
    app = create_app('production')
    
    print("✅ 成功載入完整的 AI 語音點餐系統")
    
except Exception as e:
    print(f"❌ 載入完整應用失敗，使用簡化版本: {e}")
    
    # 如果完整應用載入失敗，創建簡化版本
    from flask import Flask, send_from_directory
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

# 添加語音識別 API 端點（用於 Vercel 環境）
@app.route('/api/speech/transcribe', methods=['POST'])
def transcribe_speech():
    """語音識別端點 - 適用於 Vercel"""
    try:
        from speech_api import VercelSpeechService
        
        if 'audio' not in request.files:
            return {'success': False, 'error': '沒有音頻文件'}, 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return {'success': False, 'error': '沒有選擇文件'}, 400
        
        # 讀取音頻數據
        audio_data = audio_file.read()
        content_type = audio_file.content_type or 'audio/wav'
        
        # 使用語音識別服務
        speech_service = VercelSpeechService()
        result = speech_service.transcribe_audio(audio_data, content_type)
        
        if result['success']:
            return {
                'success': True,
                'transcription': result['text'],
                'confidence': result['confidence'],
                'language': result['language']
            }
        else:
            return {'success': False, 'error': result['error']}, 500
            
    except ImportError:
        return {'success': False, 'error': '語音服務未配置'}, 500
    except Exception as e:
        return {'success': False, 'error': f'服務器錯誤: {str(e)}'}, 500

@app.route('/api/speech/test', methods=['GET'])
def test_speech_service():
    """測試語音服務配置"""
    try:
        from speech_api import VercelSpeechService
        
        speech_service = VercelSpeechService()
        if speech_service.validate_config():
            token = speech_service.get_token()
            if token:
                return {
                    'success': True,
                    'message': 'Azure Speech Services 配置正確',
                    'region': speech_service.azure_region
                }
            else:
                return {
                    'success': False,
                    'error': 'API 密鑰無效或網絡問題'
                }
        else:
            return {
                'success': False,
                'error': 'Azure Speech Services 未配置'
            }
    except ImportError:
        return {'success': False, 'error': '語音服務模組未找到'}, 500
    except Exception as e:
        return {'success': False, 'error': f'測試失敗: {str(e)}'}, 500

# 添加 OpenRouter API 端點
@app.route('/api/order/parse', methods=['POST'])
def parse_order():
    """訂單解析端點"""
    try:
        import requests
        
        data = request.get_json()
        if not data or 'text' not in data:
            return {'success': False, 'error': '缺少文本數據'}, 400
        
        text = data['text']
        openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        
        if not openrouter_key:
            return {'success': False, 'error': 'OpenRouter API 未配置'}, 500
        
        # 調用 OpenRouter API
        headers = {
            'Authorization': f'Bearer {openrouter_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'x-ai/grok-2-1212',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一個專業的港式餐廳點餐助手。請解析顧客的點餐內容，提取菜品、數量、特殊要求等信息，並以JSON格式返回。'
                },
                {
                    'role': 'user',
                    'content': f'請解析這個點餐內容：{text}'
                }
            ],
            'max_tokens': 500
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            return {
                'success': True,
                'parsed_order': ai_response,
                'original_text': text
            }
        else:
            return {'success': False, 'error': f'AI 解析失敗: {response.status_code}'}, 500
            
    except Exception as e:
        return {'success': False, 'error': f'解析錯誤: {str(e)}'}, 500

if __name__ == "__main__":
    app.run(debug=False)
