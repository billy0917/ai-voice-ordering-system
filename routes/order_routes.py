"""
訂單處理相關路由 - 最終修復版本
"""
from flask import Blueprint, request, jsonify, current_app
from services.order_service import OrderService
from services.openrouter_service import OpenRouterService
from models.order import OrderStatus
import logging

order_bp = Blueprint('order', __name__)
logger = logging.getLogger(__name__)

# 全局服務實例
order_service = OrderService()
openrouter_service = None

def get_openrouter_service():
    """獲取 OpenRouter 服務實例"""
    global openrouter_service
    if openrouter_service is None:
        api_key = current_app.config.get('OPENROUTER_API_KEY')
        model = current_app.config.get('OPENROUTER_MODEL', 'x-ai/grok-4-fast:free')
        site_url = current_app.config.get('SITE_URL')
        site_name = current_app.config.get('SITE_NAME')
        
        openrouter_service = OpenRouterService(
            api_key=api_key,
            model=model,
            site_url=site_url,
            site_name=site_name
        )
    return openrouter_service

@order_bp.route('/parse', methods=['POST'])
def parse_order():
    """
    訂單解析端點 - 穩定版本
    """
    try:
        data = request.get_json()
        if not data or 'transcription' not in data:
            return jsonify({
                'success': False,
                'error': '缺少轉錄文字'
            }), 400
        
        transcription = data['transcription']
        logger.info(f"收到訂單解析請求: {transcription}")
        
        # 使用 OpenRouter 服務解析訂單
        openrouter = get_openrouter_service()
        order_result = openrouter.parse_order_sync(transcription)
        
        logger.info("訂單解析完成（本地模式）")
        return jsonify(order_result)
        
    except Exception as e:
        logger.error(f"訂單解析錯誤: {e}")
        return jsonify({
            'success': False,
            'error': '訂單解析失敗'
        }), 500

def parse_order_locally(transcription):
    """本地訂單解析"""
    try:
        # 簡單的關鍵詞解析
        items = []
        special_requests = []
        
        # 檢測飲品
        if '茶' in transcription:
            item_name = '凍檸茶'
            if '熱' in transcription:
                item_name = '熱檸茶'
            
            customizations = {}
            
            # 檢測特殊要求
            if '少甜' in transcription:
                special_requests.append('少甜')
                customizations['甜度'] = '少甜'
            
            if '走冰' in transcription or '無冰' in transcription:
                special_requests.append('走冰')
                customizations['冰塊'] = '走冰'
            
            items.append({
                'name': item_name,
                'quantity': 1,
                'unit_price': 18.0,
                'customizations': customizations
            })
        
        elif '咖啡' in transcription:
            items.append({
                'name': '咖啡',
                'quantity': 1,
                'unit_price': 25.0,
                'customizations': {}
            })
        
        else:
            # 默認項目
            items.append({
                'name': '凍檸茶',
                'quantity': 1,
                'unit_price': 18.0,
                'customizations': {}
            })
        
        # 構建訂單
        order = {
            'items': items,
            'special_requests': special_requests,
            'transcription': transcription,
            'confidence_score': 0.90
        }
        
        # 生成追加銷售建議
        upselling = {
            'suggestions': [
                {
                    'item': '檸檬蜂蜜',
                    'message': '加檸檬蜂蜜更健康，只需加 $5',
                    'price': 5.0
                },
                {
                    'item': '薄荷葉',
                    'message': '加薄荷葉更清香，只需加 $3',
                    'price': 3.0
                }
            ]
        }
        
        return {
            'success': True,
            'order': order,
            'upselling': upselling
        }
        
    except Exception as e:
        logger.error(f"本地解析錯誤: {e}")
        return {
            'success': False,
            'error': f'解析錯誤: {str(e)}',
            'order': {},
            'upselling': {'suggestions': []}
        }

@order_bp.route('/create', methods=['POST'])
def create_order():
    """創建新訂單"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少訂單數據'
            }), 400
        
        order = order_service.create_order(data)
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"創建訂單錯誤: {e}")
        return jsonify({
            'success': False,
            'error': '創建訂單失敗'
        }), 500

@order_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    """獲取訂單詳情"""
    try:
        order = order_service.get_order(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': '訂單不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"獲取訂單錯誤: {e}")
        return jsonify({
            'success': False,
            'error': '獲取訂單失敗'
        }), 500

@order_bp.route('/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """更新訂單狀態"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': '缺少狀態信息'
            }), 400
        
        try:
            status = OrderStatus(data['status'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': '無效的訂單狀態'
            }), 400
        
        success = order_service.update_order_status(order_id, status)
        
        if success:
            return jsonify({
                'success': True,
                'message': '訂單狀態更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '訂單不存在'
            }), 404
            
    except Exception as e:
        logger.error(f"更新訂單狀態錯誤: {e}")
        return jsonify({
            'success': False,
            'error': '更新訂單狀態失敗'
        }), 500

@order_bp.route('/active', methods=['GET'])
def get_active_orders():
    """獲取活躍訂單列表"""
    try:
        orders = order_service.get_active_orders()
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        })
        
    except Exception as e:
        logger.error(f"獲取活躍訂單錯誤: {e}")
        return jsonify({
            'success': False,
            'error': '獲取訂單列表失敗'
        }), 500
