"""
OpenRouter API 集成服務 - 語言模型處理
"""
from openai import OpenAI
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class OpenRouterService:
    """OpenRouter API 服務類"""
    
    def __init__(self, api_key: str, model: str = "x-ai/grok-4-fast:free", site_url: Optional[str] = None, site_name: Optional[str] = None):
        """
        初始化 OpenRouter 服務
        
        Args:
            api_key: OpenRouter API 密鑰
            model: 要使用的模型名稱
            site_url: 網站 URL (可選)
            site_name: 網站名稱 (可選)
        """
        self.api_key = api_key
        self.site_url = site_url
        self.site_name = site_name
        self.model = model
        
        # 性能優化：緩存機制
        self._cache = {}
        self._cache_max_size = 100
        self._cache_ttl = 300  # 5分鐘緩存
        
        # 初始化 OpenAI 客戶端連接到 OpenRouter
        try:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                timeout=10.0  # 設置超時時間
            )
            logger.info("OpenRouter 客戶端初始化成功")
        except Exception as e:
            logger.error(f"OpenRouter 客戶端初始化失敗: {e}")
            self.client = None
        
        logger.info("OpenRouter 服務初始化完成")
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """從緩存獲取結果"""
        import time
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                del self._cache[key]
        return None
    
    def _save_to_cache(self, key: str, result: Dict[str, Any]):
        """保存結果到緩存"""
        import time
        if len(self._cache) >= self._cache_max_size:
            # 清理最舊的緩存項
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[key] = (result, time.time())
    
    def _is_simple_order(self, text: str) -> bool:
        """判斷是否為簡單訂單，可以使用本地解析"""
        simple_patterns = [
            '檸檬茶', '檸茶', '奶茶', '咖啡', '可樂', '雪碧',
            '炒河', '炒麵', '炒飯', '多士', '三明治'
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in simple_patterns)
    
    def _get_default_price(self, item_name: str) -> float:
        """根據項目名稱獲取默認價格"""
        item_name_lower = item_name.lower()
        
        # 完整的香港茶餐廳價格映射
        price_map = {
            # 茶類飲品
            '檸檬茶': 18.0,
            '凍檸茶': 18.0,
            '熱檸茶': 18.0,
            '檸茶': 18.0,
            '奶茶': 22.0,
            '凍奶茶': 22.0,
            '熱奶茶': 22.0,
            '絲襪奶茶': 25.0,
            '港式奶茶': 25.0,
            '茶餐廳奶茶': 25.0,
            '紅茶': 15.0,
            '綠茶': 15.0,
            '烏龍茶': 18.0,
            '茉莉花茶': 16.0,
            '普洱茶': 20.0,
            
            # 咖啡類
            '咖啡': 25.0,
            '黑咖啡': 22.0,
            '白咖啡': 28.0,
            '即溶咖啡': 20.0,
            '港式咖啡': 25.0,
            '鴛鴦': 28.0,  # 咖啡奶茶
            '凍鴛鴦': 28.0,
            '熱鴛鴦': 28.0,
            
            # 果汁類
            '橙汁': 20.0,
            '蘋果汁': 18.0,
            '葡萄汁': 20.0,
            '檸檬汁': 18.0,
            '西瓜汁': 22.0,
            '芒果汁': 25.0,
            '鮮橙汁': 25.0,
            '鮮榨果汁': 28.0,
            
            # 汽水類
            '可樂': 15.0,
            '雪碧': 15.0,
            '芬達': 15.0,
            '汽水': 15.0,
            '梳打水': 12.0,
            '檸檬梳打': 18.0,
            
            # 特色飲品
            '檸檬蜜': 22.0,
            '檸檬蜂蜜': 22.0,
            '蜂蜜檸檬': 22.0,
            '薄荷茶': 20.0,
            '薑茶': 18.0,
            '檸檬薑茶': 22.0,
            '凍檸賓': 25.0,
            '熱檸賓': 25.0,
            
            # 奶類飲品
            '朱古力': 25.0,
            '熱朱古力': 25.0,
            '凍朱古力': 25.0,
            '阿華田': 22.0,
            '好立克': 22.0,
            '牛奶': 18.0,
            '鮮奶': 20.0,
            '豆漿': 15.0,
            
            # 湯類
            '例湯': 12.0,
            '餐湯': 12.0,
            '湯': 12.0,
            '羅宋湯': 18.0,
            '粟米湯': 15.0,
            '蛋花湯': 15.0,
            '紫菜蛋花湯': 18.0,
            
            # 主食類
            '炒河': 35.0,
            '乾炒牛河': 38.0,
            '濕炒牛河': 38.0,
            '炒麵': 32.0,
            '撈麵': 30.0,
            '湯麵': 28.0,
            '雲吞麵': 35.0,
            '牛腩麵': 42.0,
            '叉燒麵': 38.0,
            '餐蛋麵': 25.0,
            '公仔麵': 22.0,
            
            # 飯類
            '白飯': 8.0,
            '炒飯': 32.0,
            '揚州炒飯': 35.0,
            '叉燒炒飯': 38.0,
            '蝦仁炒飯': 42.0,
            '牛肉炒飯': 40.0,
            '雞絲炒飯': 35.0,
            '鹹牛肉炒飯': 38.0,
            
            # 多士類
            '多士': 15.0,
            '牛油多士': 18.0,
            '花生醬多士': 20.0,
            '煉奶多士': 22.0,
            '法式多士': 25.0,
            '西多士': 28.0,
            '厚多士': 32.0,
            
            # 三明治類
            '三明治': 25.0,
            '火腿三明治': 28.0,
            '雞蛋三明治': 25.0,
            '吞拿魚三明治': 30.0,
            '牛肉三明治': 35.0,
            '芝士三明治': 28.0,
            '總匯三明治': 38.0,
            
            # 蛋類
            '煎蛋': 12.0,
            '炒蛋': 15.0,
            '蒸蛋': 18.0,
            '水波蛋': 15.0,
            '溏心蛋': 15.0,
            '茶葉蛋': 8.0,
            
            # 小食類
            '薯條': 18.0,
            '雞翼': 25.0,
            '雞塊': 22.0,
            '春卷': 20.0,
            '燒賣': 15.0,
            '魚蛋': 12.0,
            '牛丸': 15.0,
            '腸粉': 18.0,
            
            # 甜品類
            '布丁': 18.0,
            '雪糕': 15.0,
            '紅豆冰': 22.0,
            '芒果布丁': 25.0,
            '椰汁西米露': 20.0,
            '楊枝甘露': 28.0,
        }
        
        # 精確匹配優先
        if item_name_lower in price_map:
            return price_map[item_name_lower]
        
        # 模糊匹配
        for key, price in price_map.items():
            if key in item_name_lower:
                return price
        
        # 按類別匹配
        if any(keyword in item_name_lower for keyword in ['茶', '奶茶']):
            return 22.0
        elif any(keyword in item_name_lower for keyword in ['咖啡', '鴛鴦']):
            return 25.0
        elif any(keyword in item_name_lower for keyword in ['汁', '果汁']):
            return 20.0
        elif any(keyword in item_name_lower for keyword in ['可樂', '汽水', '雪碧']):
            return 15.0
        elif any(keyword in item_name_lower for keyword in ['炒河', '炒麵', '麵']):
            return 35.0
        elif any(keyword in item_name_lower for keyword in ['炒飯', '飯']):
            return 32.0
        elif any(keyword in item_name_lower for keyword in ['多士', '三明治']):
            return 25.0
        elif any(keyword in item_name_lower for keyword in ['湯']):
            return 15.0
        
        return 20.0  # 默認價格
    
    def _get_extra_headers(self) -> Dict[str, str]:
        """獲取額外的請求頭"""
        headers = {}
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            # 確保標題是 ASCII 兼容的
            safe_title = "AI Voice Ordering System"
            headers["X-Title"] = safe_title
        return headers
    
    def parse_order_sync(self, transcribed_text: str) -> Dict[str, Any]:
        """
        解析訂單內容（同步版本，已優化性能）
        
        Args:
            transcribed_text: 語音轉錄文字
            
        Returns:
            Dict: 結構化訂單數據
        """
        try:
            # 性能優化：檢查緩存
            cache_key = f"parse_{hash(transcribed_text)}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info("使用緩存的解析結果")
                return cached_result
            
            # 檢查客戶端是否可用
            if not self.client:
                logger.warning("OpenRouter 客戶端不可用，使用本地解析")
                return self._parse_order_locally(transcribed_text)
            
            # 檢查是否為測試模式（只有測試模式才使用本地解析）
            if self.api_key.startswith('test-'):
                logger.info("使用本地解析（測試模式）")
                result = self._parse_order_locally(transcribed_text)
                self._save_to_cache(cache_key, result)
                return result
            
            # 對於正常的API key，優先使用AI解析
            logger.info("使用AI解析（OpenRouter）")
            
            prompt = self.create_order_prompt(transcribed_text)
            
            # 調用 OpenRouter API（按照官方文檔格式）
            extra_headers = self._get_extra_headers()
            
            response = self.client.chat.completions.create(
                extra_headers=extra_headers,
                extra_body={},
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個專門處理香港茶餐廳訂單的AI助手。請以JSON格式返回結構化的訂單信息。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # 降低溫度以提高一致性和速度
                max_tokens=800    # 減少token數量
            )
            
            # 解析回應
            content = response.choices[0].message.content
            logger.info("OpenRouter 回應已收到")
            
            # 嘗試解析 JSON
            import json
            import re
            
            # 提取 JSON 部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                order_data = json.loads(json_str)
            else:
                # 如果沒有找到 JSON，創建基本結構
                order_data = {
                    "items": [
                        {
                            "name": "未識別項目",
                            "quantity": 1
                        }
                    ],
                    "special_requests": []
                }
            
            # 處理 API 回應，確保格式一致
            processed_items = []
            for item in order_data.get('items', []):
                processed_item = {
                    'name': item.get('name', '未識別項目'),
                    'quantity': item.get('quantity', 1),
                    'unit_price': item.get('unit_price', self._get_default_price(item.get('name', ''))),
                    'customizations': item.get('customizations', {})
                }
                processed_items.append(processed_item)
            
            # 從特殊要求中提取定制信息
            special_requests = order_data.get('special_requests', [])
            if processed_items and special_requests:
                customizations = {}
                for request in special_requests:
                    if '少甜' in request:
                        customizations['甜度'] = '少甜'
                    elif '走冰' in request or '無冰' in request:
                        customizations['冰塊'] = '走冰'
                
                if customizations:
                    processed_items[0]['customizations'].update(customizations)
            
            # 構建完整的訂單對象
            order = {
                'items': processed_items,
                'special_requests': special_requests,
                'transcription': transcribed_text,
                'confidence_score': 0.90
            }
            
            # 生成追加銷售建議
            upselling = self.generate_upselling_sync(order)
            
            return {
                'success': True,
                'order': order,
                'upselling': upselling
            }
            
        except Exception as e:
            logger.error(f"訂單解析錯誤: {e}")
            # 回退到本地解析
            logger.info("回退到本地解析")
            return self._parse_order_locally(transcribed_text)
    
    def _parse_order_locally(self, transcribed_text: str) -> Dict[str, Any]:
        """
        本地訂單解析（不依賴 API）- 增強版
        
        Args:
            transcribed_text: 語音轉錄文字
            
        Returns:
            Dict: 結構化訂單數據
        """
        try:
            import re
            
            items = []
            special_requests = []
            text_lower = transcribed_text.lower()
            
            # 數量識別
            def extract_quantity(text, item_keyword):
                """提取數量"""
                # 中文數字映射
                chinese_numbers = {
                    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                    '兩': 2, '半': 0.5
                }
                
                # 查找數量詞
                patterns = [
                    rf'([一二三四五六七八九十兩半])[杯份個碗碟客]*{item_keyword}',
                    rf'(\d+)[杯份個碗碟客]*{item_keyword}',
                    rf'{item_keyword}.*?([一二三四五六七八九十兩半])[杯份個碗碟客]',
                    rf'{item_keyword}.*?(\d+)[杯份個碗碟客]'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        qty_str = match.group(1)
                        if qty_str in chinese_numbers:
                            return chinese_numbers[qty_str]
                        elif qty_str.isdigit():
                            return int(qty_str)
                
                return 1  # 默認數量
            
            # 定制選項識別
            def extract_customizations(text):
                """提取定制選項"""
                customizations = {}
                
                # 甜度
                if '少甜' in text:
                    customizations['甜度'] = '少甜'
                elif '無糖' in text or '走糖' in text:
                    customizations['甜度'] = '無糖'
                elif '甜' in text and '少甜' not in text:
                    customizations['甜度'] = '甜'
                elif '半糖' in text:
                    customizations['甜度'] = '半糖'
                
                # 冰塊
                if '走冰' in text or '無冰' in text:
                    customizations['冰塊'] = '走冰'
                elif '少冰' in text:
                    customizations['冰塊'] = '少冰'
                elif '多冰' in text:
                    customizations['冰塊'] = '多冰'
                
                # 溫度
                if '熱' in text:
                    customizations['溫度'] = '熱'
                elif '凍' in text:
                    customizations['溫度'] = '凍'
                elif '室溫' in text:
                    customizations['溫度'] = '室溫'
                
                # 加料
                add_ons = []
                if '加檸檬' in text:
                    add_ons.append('檸檬')
                if '加蜂蜜' in text:
                    add_ons.append('蜂蜜')
                if '加薄荷' in text:
                    add_ons.append('薄荷')
                if '加奶' in text:
                    add_ons.append('奶')
                if add_ons:
                    customizations['加料'] = ','.join(add_ons)
                
                # 份量
                if '大杯' in text:
                    customizations['份量'] = '大杯'
                elif '小杯' in text:
                    customizations['份量'] = '小杯'
                elif '中杯' in text:
                    customizations['份量'] = '中杯'
                
                return customizations
            
            # 項目識別和解析
            detected_items = []
            
            # 飲品類識別
            drink_patterns = {
                '檸檬茶': ['檸檬茶', '檸茶', '凍檸茶', '熱檸茶'],
                '奶茶': ['奶茶', '絲襪奶茶', '港式奶茶'],
                '咖啡': ['咖啡', '黑咖啡', '白咖啡'],
                '鴛鴦': ['鴛鴦'],
                '橙汁': ['橙汁', '鮮橙汁'],
                '可樂': ['可樂', 'cola'],
                '雪碧': ['雪碧', 'sprite'],
                '檸檬蜜': ['檸檬蜜', '蜂蜜檸檬'],
                '阿華田': ['阿華田'],
                '好立克': ['好立克']
            }
            
            # 主食類識別
            food_patterns = {
                '乾炒牛河': ['乾炒牛河', '炒牛河'],
                '炒河': ['炒河'],
                '炒麵': ['炒麵'],
                '雲吞麵': ['雲吞麵'],
                '牛腩麵': ['牛腩麵'],
                '叉燒麵': ['叉燒麵'],
                '揚州炒飯': ['揚州炒飯'],
                '叉燒炒飯': ['叉燒炒飯'],
                '炒飯': ['炒飯'],
                '牛油多士': ['牛油多士'],
                '法式多士': ['法式多士'],
                '多士': ['多士'],
                '三明治': ['三明治', 'sandwich']
            }
            
            all_patterns = {**drink_patterns, **food_patterns}
            
            # 檢測所有項目
            for item_name, keywords in all_patterns.items():
                for keyword in keywords:
                    if keyword in transcribed_text:
                        quantity = extract_quantity(transcribed_text, keyword)
                        customizations = extract_customizations(transcribed_text)
                        unit_price = self._get_default_price(item_name)
                        
                        # 溫度邏輯調整
                        if '熱' in transcribed_text and item_name == '檸檬茶':
                            item_name = '熱檸茶'
                        elif '凍' in transcribed_text and item_name == '檸檬茶':
                            item_name = '凍檸茶'
                        
                        detected_items.append({
                            'name': item_name,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'customizations': customizations
                        })
                        break
            
            # 如果沒有檢測到任何項目，添加默認項目
            if not detected_items:
                detected_items.append({
                    'name': '凍檸茶',
                    'quantity': 1,
                    'unit_price': 18.0,
                    'customizations': extract_customizations(transcribed_text)
                })
            
            # 提取特殊要求
            special_requests = []
            if '少甜' in transcribed_text:
                special_requests.append('少甜')
            if '走冰' in transcribed_text or '無冰' in transcribed_text:
                special_requests.append('走冰')
            if '加檸檬' in transcribed_text:
                special_requests.append('加檸檬')
            if '加蜂蜜' in transcribed_text:
                special_requests.append('加蜂蜜')
            if '熱' in transcribed_text:
                special_requests.append('要熱的')
            if '大杯' in transcribed_text:
                special_requests.append('大杯')
            
            # 構建訂單
            order = {
                'items': detected_items,
                'special_requests': special_requests,
                'transcription': transcribed_text,
                'confidence_score': 0.85,
                'total': sum(item['unit_price'] * item['quantity'] for item in detected_items)
            }
            
            # 生成追加銷售建議
            upselling = self.generate_upselling_sync(order)
            
            return {
                'success': True,
                'order': order,
                'upselling': upselling
            }
            
        except Exception as e:
            logger.error(f"本地解析錯誤: {e}")
            return {
                'success': False,
                'error': f'本地解析錯誤: {str(e)}',
                'order': {
                    'items': [{
                        'name': '凍檸茶',
                        'quantity': 1,
                        'unit_price': 18.0,
                        'customizations': {}
                    }],
                    'special_requests': [],
                    'transcription': transcribed_text,
                    'confidence_score': 0.5,
                    'total': 18.0
                },
                'upselling': {'suggestions': []}
            }
    
    def generate_upselling_sync(self, current_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成追加銷售建議（同步版本）- 增強版
        
        Args:
            current_order: 當前訂單數據
            
        Returns:
            Dict: 追加銷售建議
        """
        try:
            suggestions = []
            items = current_order.get('items', [])
            total_amount = current_order.get('total', 0)
            
            # 分析訂單內容
            has_drinks = False
            has_food = False
            has_tea = False
            has_coffee = False
            has_cold_drinks = False
            has_hot_drinks = False
            
            for item in items:
                item_name = item.get('name', '').lower()
                customizations = item.get('customizations', {})
                
                # 分類分析
                if any(keyword in item_name for keyword in ['茶', '汁', '可樂', '咖啡', '奶茶']):
                    has_drinks = True
                    
                    if '茶' in item_name:
                        has_tea = True
                    if '咖啡' in item_name or '鴛鴦' in item_name:
                        has_coffee = True
                        
                    # 溫度分析
                    temp = customizations.get('溫度', '')
                    if temp == '凍' or '凍' in item_name:
                        has_cold_drinks = True
                    elif temp == '熱' or '熱' in item_name:
                        has_hot_drinks = True
                
                if any(keyword in item_name for keyword in ['河', '麵', '飯', '多士', '三明治']):
                    has_food = True
            
            # 基於飲品的建議
            if has_tea:
                suggestions.extend([
                    {
                        'item': '檸檬蜂蜜',
                        'message': '加檸檬蜂蜜，天然健康更好味！',
                        'price': 5.0,
                        'category': '加料'
                    },
                    {
                        'item': '薄荷葉',
                        'message': '加薄荷葉，清香怡人！',
                        'price': 3.0,
                        'category': '加料'
                    }
                ])
            
            if has_coffee:
                suggestions.extend([
                    {
                        'item': '額外濃縮',
                        'message': '加一份濃縮，更香濃提神！',
                        'price': 8.0,
                        'category': '加料'
                    },
                    {
                        'item': '鮮奶',
                        'message': '轉用鮮奶，口感更順滑！',
                        'price': 5.0,
                        'category': '升級'
                    }
                ])
            
            # 基於溫度的建議
            if has_cold_drinks:
                suggestions.append({
                    'item': '加冰',
                    'message': '夏日特飲，加冰更爽！',
                    'price': 2.0,
                    'category': '加料'
                })
            
            # 配餐建議
            if has_drinks and not has_food:
                suggestions.extend([
                    {
                        'item': '牛油多士',
                        'message': '經典茶餐廳配搭，香脆可口！',
                        'price': 18.0,
                        'category': '配餐'
                    },
                    {
                        'item': '雞蛋三明治',
                        'message': '營養豐富，飽肚之選！',
                        'price': 25.0,
                        'category': '配餐'
                    },
                    {
                        'item': '薯條',
                        'message': '金黃香脆，老少咸宜！',
                        'price': 18.0,
                        'category': '小食'
                    }
                ])
            
            if has_food and not has_drinks:
                suggestions.extend([
                    {
                        'item': '凍檸茶',
                        'message': '茶餐廳經典，解膩必備！',
                        'price': 18.0,
                        'category': '飲品'
                    },
                    {
                        'item': '例湯',
                        'message': '今日例湯，暖胃開胃！',
                        'price': 12.0,
                        'category': '湯品'
                    }
                ])
            
            # 基於消費金額的建議
            if total_amount >= 50:
                suggestions.append({
                    'item': '甜品',
                    'message': '滿$50送甜品優惠，布丁或雪糕任選！',
                    'price': 0.0,
                    'category': '優惠'
                })
            elif total_amount >= 30:
                suggestions.append({
                    'item': '升級套餐',
                    'message': '加$8升級套餐，包飲品+例湯！',
                    'price': 8.0,
                    'category': '套餐'
                })
            
            # 時段特色建議
            from datetime import datetime
            current_hour = datetime.now().hour
            
            if 6 <= current_hour <= 11:  # 早餐時段
                suggestions.extend([
                    {
                        'item': '煎蛋',
                        'message': '早餐必備，營養豐富！',
                        'price': 12.0,
                        'category': '早餐'
                    },
                    {
                        'item': '熱咖啡',
                        'message': '早晨提神，香濃醒腦！',
                        'price': 25.0,
                        'category': '飲品'
                    }
                ])
            elif 11 <= current_hour <= 14:  # 午餐時段
                suggestions.extend([
                    {
                        'item': '今日特餐',
                        'message': '午餐特價，經濟實惠！',
                        'price': 35.0,
                        'category': '特餐'
                    }
                ])
            elif 14 <= current_hour <= 17:  # 下午茶時段
                suggestions.extend([
                    {
                        'item': '下午茶套餐',
                        'message': '下午茶時光，多士+飲品！',
                        'price': 28.0,
                        'category': '套餐'
                    }
                ])
            
            # 健康選擇建議
            suggestions.extend([
                {
                    'item': '少糖選擇',
                    'message': '關注健康？可選擇少糖或無糖！',
                    'price': 0.0,
                    'category': '健康'
                },
                {
                    'item': '鮮榨果汁',
                    'message': '新鮮現榨，維他命豐富！',
                    'price': 28.0,
                    'category': '健康'
                }
            ])
            
            # 去重並限制數量
            seen = set()
            unique_suggestions = []
            for suggestion in suggestions:
                key = suggestion['item']
                if key not in seen:
                    seen.add(key)
                    unique_suggestions.append(suggestion)
            
            # 按類別和價格排序，限制數量
            unique_suggestions.sort(key=lambda x: (x['category'], x['price']))
            final_suggestions = unique_suggestions[:4]  # 最多4個建議
            
            return {
                'suggestions': final_suggestions,
                'total_suggestions': len(unique_suggestions),
                'categories': list(set(s['category'] for s in final_suggestions))
            }
            
        except Exception as e:
            logger.error(f"生成追加銷售建議錯誤: {e}")
            return {
                'suggestions': [
                    {
                        'item': '檸檬蜂蜜',
                        'message': '加檸檬蜂蜜更健康！',
                        'price': 5.0,
                        'category': '加料'
                    }
                ],
                'total_suggestions': 1,
                'categories': ['加料']
            }
    
    async def parse_order(self, transcribed_text: str) -> Dict[str, Any]:
        """
        解析訂單內容（異步版本）
        
        Args:
            transcribed_text: 語音轉錄文字
            
        Returns:
            Dict: 結構化訂單數據
        """
        # 目前使用同步版本
        return self.parse_order_sync(transcribed_text)
    
    async def generate_upselling(self, current_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成追加銷售建議
        
        Args:
            current_order: 當前訂單數據
            
        Returns:
            Dict: 追加銷售建議
        """
        # 這裡是佔位符實現，實際實現將在後續任務中完成
        logger.info("追加銷售功能將在後續任務中實現")
        return {
            "suggestions": [],
            "message": "功能尚未實現"
        }
    
    def create_order_prompt(self, text: str) -> str:
        """
        創建訂單解析的提示詞
        
        Args:
            text: 語音轉錄文字
            
        Returns:
            str: 格式化的提示詞
        """
        prompt = f"""
你是一個專業的香港茶餐廳點餐系統AI助手。請精確解析以下語音轉錄的點餐內容，並返回結構化的訂單信息。

語音轉錄內容："{text}"

## 解析要求：

### 1. 語言理解能力
- 由於語音轉文字會不准確，所以如果出現不能理解的字眼你需要猜測在粵語中（同音字）大概的意思
- 精通港式粵語表達和茶餐廳術語
- 理解中英混合語言（如"一杯coffee"、"兩個sandwich"）
- 識別數量詞（一杯、兩份、三個、半打等）
- 理解溫度表達（凍、熱、室溫、少冰、走冰、正常冰）
- 識別甜度要求（少甜、正常、甜、無糖、走糖）

### 2. 常見茶餐廳項目識別
**飲品類：**
- 茶類：檸檬茶/檸茶/凍檸茶/熱檸茶、奶茶、絲襪奶茶、紅茶、綠茶
- 咖啡類：咖啡、黑咖啡、白咖啡、鴛鴦（咖啡奶茶）
- 果汁類：橙汁、蘋果汁、鮮榨果汁、檸檬汁
- 汽水類：可樂、雪碧、芬達、梳打水
- 特色飲品：檸檬蜜、薄荷茶、阿華田、好立克

**主食類：**
- 麵類：炒河、乾炒牛河、炒麵、撈麵、湯麵、雲吞麵、牛腩麵、叉燒麵
- 飯類：白飯、炒飯、揚州炒飯、叉燒炒飯、牛肉炒飯
- 多士類：牛油多士、花生醬多士、法式多士、西多士
- 三明治類：火腿三明治、雞蛋三明治、總匯三明治

**小食類：**
- 薯條、雞翼、春卷、燒賣、魚蛋、腸粉

### 3. 定制選項識別
- **甜度：** 少甜、正常、甜、無糖、走糖、半糖
- **冰塊：** 走冰、少冰、正常冰、多冰、室溫
- **溫度：** 凍、熱、室溫、溫
- **加料：** 加檸檬、加蜂蜜、加薄荷、加奶、走奶
- **份量：** 大杯、中杯、小杯、加大、正常

### 4. 數量識別
- 中文數字：一、二、三、四、五、六、七、八、九、十
- 阿拉伯數字：1、2、3、4、5、6、7、8、9、10
- 量詞：杯、份、個、碗、碟、客、打、半打

### 5. JSON 輸出格式
請嚴格按照以下格式返回：

```json
{{
  "items": [
    {{
      "name": "項目名稱",
      "quantity": 數量,
      "unit_price": 單價,
      "customizations": {{
        "甜度": "少甜/正常/甜/無糖",
        "冰塊": "走冰/少冰/正常冰/多冰",
        "溫度": "凍/熱/室溫",
        "加料": "加檸檬/加蜂蜜等",
        "份量": "大杯/中杯/小杯"
      }}
    }}
  ],
  "special_requests": ["特殊要求1", "特殊要求2"],
  "total": 總價格,
  "confidence": 0.0-1.0,
  "clarification_needed": false,
  "unclear_items": []
}}
```

### 6. 價格參考（港幣）
- 檸檬茶類：$18
- 奶茶類：$22-25
- 咖啡類：$22-28
- 果汁類：$18-25
- 汽水類：$15
- 炒河/炒麵：$32-38
- 炒飯類：$32-40
- 多士類：$15-32
- 三明治類：$25-38
- 湯類：$12-18

### 7. 錯誤處理
- 如果無法識別某個項目，設置 "clarification_needed": true
- 將不清楚的項目列在 "unclear_items" 中
- 對於模糊的數量，默認為 1
- 對於不確定的定制，不要添加到 customizations 中

### 8. 解析例子
**輸入：** "我要兩杯凍檸茶，一杯少甜走冰，一杯正常"
**輸出：**
```json
{{
  "items": [
    {{
      "name": "凍檸茶",
      "quantity": 1,
      "unit_price": 18.0,
      "customizations": {{
        "甜度": "少甜",
        "冰塊": "走冰"
      }}
    }},
    {{
      "name": "凍檸茶", 
      "quantity": 1,
      "unit_price": 18.0,
      "customizations": {{
        "甜度": "正常"
      }}
    }}
  ],
  "special_requests": ["少甜走冰", "正常"],
  "total": 36.0,
  "confidence": 0.95,
  "clarification_needed": false,
  "unclear_items": []
}}
```

請現在解析上述語音轉錄內容，並嚴格按照JSON格式返回結果。
"""
        return prompt