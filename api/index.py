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

# 直接在此處定義語音服務類
class VercelSpeechService:
    """適用於 Vercel 的語音識別服務"""
    
    def __init__(self):
        self.azure_key = os.environ.get('AZURE_SPEECH_KEY')
        self.azure_region = os.environ.get('AZURE_SPEECH_REGION', 'eastasia')
        self.base_url = f"https://{self.azure_region}.stt.speech.microsoft.com"
        
    def validate_config(self):
        """驗證配置"""
        return bool(self.azure_key and self.azure_region)
    
    def transcribe_audio(self, audio_data, content_type="audio/wav"):
        """語音識別"""
        if not self.validate_config():
            return {
                'success': False,
                'error': 'Azure Speech Services 未配置'
            }
        
        try:
            import requests
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_key,
                'Content-Type': content_type,
                'Accept': 'application/json'
            }
            
            url = f"{self.base_url}/speech/recognition/conversation/cognitiveservices/v1"
            params = {
                'language': 'zh-HK',
                'format': 'detailed'
            }
            
            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('RecognitionStatus') == 'Success':
                    display_text = result.get('DisplayText', '')
                    confidence = result.get('NBest', [{}])[0].get('Confidence', 0)
                    
                    return {
                        'success': True,
                        'text': display_text,
                        'confidence': confidence,
                        'language': 'zh-HK'
                    }
                else:
                    return {
                        'success': False,
                        'error': f"識別失敗: {result.get('RecognitionStatus')}"
                    }
            else:
                return {
                    'success': False,
                    'error': f"API 請求失敗: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'語音識別錯誤: {str(e)}'
            }

# 添加語音識別 API 端點（用於 Vercel 環境）
@app.route('/api/speech/transcribe', methods=['POST'])
def transcribe_speech():
    """語音識別端點 - 適用於 Vercel"""
    try:
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
            
    except Exception as e:
        return {'success': False, 'error': f'服務器錯誤: {str(e)}'}, 500

@app.route('/api/speech/test', methods=['GET'])
def test_speech_service():
    """測試語音服務配置"""
    try:
        speech_service = VercelSpeechService()
        if speech_service.validate_config():
            return {
                'success': True,
                'message': 'Azure Speech Services 配置正確',
                'region': speech_service.azure_region,
                'key_configured': bool(speech_service.azure_key)
            }
        else:
            return {
                'success': False,
                'error': 'Azure Speech Services 未配置',
                'azure_key': bool(os.environ.get('AZURE_SPEECH_KEY')),
                'azure_region': os.environ.get('AZURE_SPEECH_REGION', 'not set')
            }
    except Exception as e:
        return {'success': False, 'error': f'測試失敗: {str(e)}'}, 500

# 添加 OpenRouter API 端點
@app.route('/api/order/parse', methods=['POST'])
def parse_order():
    """訂單解析端點"""
    try:
        import requests
        
        data = request.get_json()
        if not data:
            return {'success': False, 'error': '缺少請求數據'}, 400
        
        # 支持多種字段名稱
        text = data.get('text') or data.get('transcription') or data.get('content')
        if not text:
            return {'success': False, 'error': '缺少文本數據', 'received_data': list(data.keys())}, 400
        openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        
        if not openrouter_key:
            return {'success': False, 'error': 'OpenRouter API 未配置'}, 500
        
        # 調用 OpenRouter API
        headers = {
            'Authorization': f'Bearer {openrouter_key}',
            'Content-Type': 'application/json'
        }
        
        # 構建詳細的系統提示
        system_prompt = """你是一個專業的港式茶餐廳點餐助手，精通港式粵語和茶餐廳文化。請解析顧客的粵語點餐內容，並按以下格式返回JSON：

{
  "success": true,
  "order": {
    "items": [
      {
        "name": "菜品名稱",
        "quantity": 數量,
        "unit_price": 預估價格,
        "customizations": {
          "甜度": "少甜/正常/甜/無糖/走糖/半糖",
          "冰塊": "走冰/少冰/正常冰/多冰/室溫",
          "溫度": "凍/熱/室溫",
          "加料": "加檸檬/加蜂蜜/加奶/走奶等",
          "份量": "大杯/中杯/小杯/加大"
        },
        "special_requirements": ["具體特殊要求"],
        "category": "主食/飲品/小食/甜品"
      }
    ],
    "total_price": 總價格,
    "special_requests": ["整體特殊要求"],
    "confidence": 0.0-1.0,
    "clarification_needed": false
  },
  "upselling": {
    "suggestions": [
      {
        "item": "推薦商品名稱",
        "reason": "推薦原因（這會成為顯示消息）", 
        "price": 價格
      }
    ]
  },
  "original_text": "原始語音文本"
}

## 專業茶餐廳知識庫

### 常見定制選項：
- **甜度：** 少甜、正常、甜、無糖、走糖、半糖
- **冰塊：** 走冰、少冰、正常冰、多冰、室溫  
- **溫度：** 凍、熱、室溫、溫
- **加料：** 加檸檬、加蜂蜜、加薄荷、加奶、走奶
- **份量：** 大杯、中杯、小杯、加大、正常

### 港式茶餐廳菜品價格參考：
**主食類：**
- 炸豬扒飯：$48-55
- 叉燒飯：$42-48
- 咖喱雞飯：$45-52
- 豉汁排骨飯：$46-53
- 蒸蛋飯：$35-42
- 白切雞飯：$45-52

**飲品類：**
- 港式奶茶：$22-28
- 凍檸茶：$18-25
- 凍檸水：$16-22
- 凍華田：$20-26
- 熱咖啡：$18-25
- 凍可樂：$15-22

**小食類：**
- 西多士：$25-35
- 菠蘿包：$12-18
- 雞翼：$25-35

### 解析要求：
1. 精確識別所有定制要求（少甜、少冰、走冰等）
2. 正確提取數量和項目名稱
3. 根據定制調整價格（特殊要求可能+$2-5）
4. 生成合理的追加銷售建議
5. 如果有不清楚的地方，設置 clarification_needed: true

### 智能推薦加購策略：
**配餐建議**：
- 只點飲品 → 推薦：薯條($18)、牛油多士($18)、雞蛋三明治($25)
- 只點主食 → 推薦：凍檸茶($18)、奶茶($22)、例湯($12)
- 點了炸類食物 → 推薦：清爽飲品消膩
- 點了麵條/河粉 → 推薦：熱湯或例湯

**時段建議**：
- 早餐時段 → 推薦：咖啡、厚多士、煎蛋
- 下午茶 → 推薦：西多士、菠蘿包、奶茶
- 晚餐 → 推薦：例湯、飲品組合

**價位建議**：
- 消費$30-50 → 推薦加飲品($15-25)
- 消費$50+ → 推薦升級套餐或甜品
- 消費少於$30 → 推薦小食補足($12-18)

**健康搭配**：
- 油膩食物 → 推薦無糖/少糖飲品
- 乾糧食物 → 推薦湯品或多汁飲品
- 單一類型 → 推薦營養均衡的配菜

### 例子：
**輸入：** "唔該我要個炸豬扒飯加杯凍奶茶少甜走冰"
**輸出：**
```json
{
  "success": true,
  "order": {
    "items": [
      {
        "name": "炸豬扒飯",
        "quantity": 1,
        "unit_price": 48.0,
        "customizations": {},
        "special_requirements": [],
        "category": "主食"
      },
      {
        "name": "凍奶茶",
        "quantity": 1,
        "unit_price": 22.0,
        "customizations": {
          "甜度": "少甜",
          "冰塊": "走冰"
        },
        "special_requirements": ["少甜", "走冰"],
        "category": "飲品"
      }
    ],
    "total_price": 70.0,
    "special_requests": ["少甜走冰"],
    "confidence": 0.95,
    "clarification_needed": false
  },
  "upselling": {
    "suggestions": [
      {
        "item": "薯條",
        "reason": "炸豬扒飯配薯條很受歡迎，金黃香脆！",
        "price": 18.0
      },
      {
        "item": "例湯",
        "reason": "今日例湯暖胃開胃，完美搭配！",
        "price": 12.0
      }
    ]
  },
  "original_text": "唔該我要個炸豬扒飯加杯凍奶茶少甜走冰"
}
```"""

        payload = {
            'model': 'anthropic/claude-3.5-sonnet',
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': f'請解析這個港式茶餐廳點餐內容：{text}'
                }
            ],
            'max_tokens': 1000,
            'temperature': 0.3
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
            
            try:
                # 嘗試解析 AI 返回的 JSON
                import json
                parsed_response = json.loads(ai_response)
                
                # 確保返回格式正確
                if isinstance(parsed_response, dict) and 'order' in parsed_response:
                    # 確保每個訂單項目都有必要的字段
                    if 'items' in parsed_response['order']:
                        for item in parsed_response['order']['items']:
                            if 'customizations' not in item:
                                item['customizations'] = {}
                            if 'special_requirements' not in item:
                                item['special_requirements'] = []
                    
                    # 確保訂單有必要的字段
                    if 'special_requests' not in parsed_response['order']:
                        parsed_response['order']['special_requests'] = []
                    if 'confidence' not in parsed_response['order']:
                        parsed_response['order']['confidence'] = 0.8
                    if 'clarification_needed' not in parsed_response['order']:
                        parsed_response['order']['clarification_needed'] = False
                    
                    # 確保 upselling 格式正確
                    if 'upselling' in parsed_response:
                        if isinstance(parsed_response['upselling'], list):
                            # 轉換字段名以匹配前端期待
                            suggestions = []
                            for suggestion in parsed_response['upselling']:
                                converted = {
                                    'item': suggestion.get('item', '推薦商品'),
                                    'message': suggestion.get('reason', suggestion.get('item', '推薦商品')),
                                    'price': suggestion.get('price', suggestion.get('unit_price', 0))
                                }
                                suggestions.append(converted)
                            parsed_response['upselling'] = {'suggestions': suggestions}
                        elif isinstance(parsed_response['upselling'], dict) and 'suggestions' in parsed_response['upselling']:
                            # 轉換 suggestions 內的字段
                            suggestions = []
                            for suggestion in parsed_response['upselling']['suggestions']:
                                converted = {
                                    'item': suggestion.get('item', '推薦商品'),
                                    'message': suggestion.get('reason', suggestion.get('item', '推薦商品')),
                                    'price': suggestion.get('price', suggestion.get('unit_price', 0))
                                }
                                suggestions.append(converted)
                            parsed_response['upselling']['suggestions'] = suggestions
                    else:
                        # 如果沒有 upselling 字段，添加默認結構
                        parsed_response['upselling'] = {'suggestions': []}
                    return parsed_response
                else:
                    # 如果格式不正確，創建標準格式
                    return {
                        'success': True,
                        'order': {
                            'items': [
                                {
                                    'name': '解析結果',
                                    'quantity': 1,
                                    'unit_price': 0,
                                    'customizations': {},
                                    'special_requirements': [],
                                    'category': '其他'
                                }
                            ],
                            'total_price': 0,
                            'special_requests': [],
                            'confidence': 0.8,
                            'clarification_needed': False,
                            'special_notes': ai_response
                        },
                        'upselling': {'suggestions': []},
                        'original_text': text
                    }
            except json.JSONDecodeError:
                # 如果無法解析為 JSON，返回文本格式
                return {
                    'success': True,
                    'order': {
                        'items': [
                            {
                                'name': '訂單解析',
                                'quantity': 1,
                                'unit_price': 0,
                                'customizations': {},
                                'special_requirements': [],
                                'category': '解析結果'
                            }
                        ],
                        'total_price': 0,
                        'special_requests': [],
                        'confidence': 0.7,
                        'clarification_needed': False,
                        'special_notes': ai_response
                    },
                    'upselling': {'suggestions': []},
                    'original_text': text,
                    'raw_ai_response': ai_response
                }
        else:
            return {'success': False, 'error': f'AI 解析失敗: {response.status_code} - {response.text}'}, 500
            
    except Exception as e:
        return {'success': False, 'error': f'解析錯誤: {str(e)}'}, 500

# 訂單創建端點
@app.route('/api/order/create', methods=['POST'])
def create_order():
    """創建新訂單"""
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'error': '缺少訂單數據'}, 400
        
        # 生成訂單ID
        import time
        import random
        order_id = f"ORD{int(time.time())}{random.randint(100, 999)}"
        
        # 創建訂單記錄（簡化版本，實際應該存儲到數據庫）
        order_record = {
            'id': order_id,
            'items': data.get('items', []),
            'total_price': data.get('total_price', 0),
            'special_notes': data.get('special_notes', ''),
            'status': 'pending',
            'created_at': time.time(),
            'estimated_time': '15-20分鐘'
        }
        
        return {
            'success': True,
            'order_id': order_id,
            'status': 'pending',
            'message': '訂單已成功創建',
            'estimated_time': '15-20分鐘',
            'order': order_record
        }
        
    except Exception as e:
        return {'success': False, 'error': f'創建訂單失敗: {str(e)}'}, 500

# 獲取活躍訂單端點
@app.route('/api/order/active', methods=['GET'])
def get_active_orders():
    """獲取活躍訂單列表"""
    try:
        # 模擬訂單數據（實際應該從數據庫獲取）
        import time
        current_time = time.time()
        
        sample_orders = [
            {
                'id': f'ORD{int(current_time-3600)}001',
                'status': 'preparing',
                'items': [
                    {'name': '炸豬扒飯', 'quantity': 1, 'unit_price': 48},
                    {'name': '凍可樂', 'quantity': 1, 'unit_price': 18}
                ],
                'total_price': 66,
                'created_at': current_time - 3600,
                'estimated_time': '5分鐘'
            },
            {
                'id': f'ORD{int(current_time-1800)}002', 
                'status': 'confirmed',
                'items': [
                    {'name': '叉燒飯', 'quantity': 1, 'unit_price': 45},
                    {'name': '港式奶茶', 'quantity': 1, 'unit_price': 22}
                ],
                'total_price': 67,
                'created_at': current_time - 1800,
                'estimated_time': '10分鐘'
            }
        ]
        
        return {
            'success': True,
            'orders': sample_orders,
            'total_count': len(sample_orders)
        }
        
    except Exception as e:
        return {'success': False, 'error': f'獲取訂單失敗: {str(e)}'}, 500

# 更新訂單狀態端點
@app.route('/api/order/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """更新訂單狀態"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return {'success': False, 'error': '缺少狀態信息'}, 400
        
        new_status = data['status']
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered']
        
        if new_status not in valid_statuses:
            return {'success': False, 'error': '無效的訂單狀態'}, 400
        
        # 模擬更新訂單狀態（實際應該更新數據庫）
        import time
        return {
            'success': True,
            'order_id': order_id,
            'status': new_status,
            'message': f'訂單狀態已更新為: {new_status}',
            'updated_at': time.time()
        }
        
    except Exception as e:
        return {'success': False, 'error': f'更新狀態失敗: {str(e)}'}, 500

# 獲取訂單詳情端點
@app.route('/api/order/<order_id>', methods=['GET'])
def get_order_details(order_id):
    """獲取特定訂單詳情"""
    try:
        import time
        
        # 模擬訂單數據
        order_details = {
            'id': order_id,
            'status': 'confirmed',
            'items': [
                {
                    'name': '炸豬扒飯',
                    'quantity': 1,
                    'unit_price': 48,
                    'special_requirements': []
                },
                {
                    'name': '凍可樂', 
                    'quantity': 1,
                    'unit_price': 18,
                    'special_requirements': []
                }
            ],
            'total_price': 66,
            'special_notes': '',
            'created_at': time.time() - 900,
            'estimated_time': '10分鐘',
            'status_history': [
                {'status': 'pending', 'timestamp': time.time() - 900},
                {'status': 'confirmed', 'timestamp': time.time() - 600}
            ]
        }
        
        return {
            'success': True,
            'order': order_details
        }
        
    except Exception as e:
        return {'success': False, 'error': f'獲取訂單詳情失敗: {str(e)}'}, 500

if __name__ == "__main__":
    app.run(debug=False)
