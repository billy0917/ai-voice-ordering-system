"""
訂單管理服務
"""
import logging
from typing import List, Optional, Dict, Any
from models.order import Order, OrderStatus, OrderItem
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderService:
    """訂單管理服務類"""
    
    def __init__(self):
        """初始化訂單服務"""
        # 使用內存存儲作為佔位符，實際實現將使用數據庫
        self.orders: Dict[str, Order] = {}
        logger.info("訂單服務初始化完成")
    
    def create_order(self, order_data: Dict[str, Any]) -> Order:
        """
        創建新訂單
        
        Args:
            order_data: 訂單數據字典
            
        Returns:
            Order: 創建的訂單對象
        """
        try:
            # 創建訂單項目
            items = []
            for item_data in order_data.get('items', []):
                item = OrderItem(
                    name=item_data.get('name', ''),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0.0),
                    customizations=item_data.get('customizations', {})
                )
                items.append(item)
            
            # 創建訂單
            order = Order(
                customer_id=order_data.get('customer_id'),
                items=items,
                special_requests=order_data.get('special_requests', []),
                transcription=order_data.get('transcription', ''),
                confidence_score=order_data.get('confidence_score', 0.0)
            )
            
            # 存儲訂單
            self.orders[order.id] = order
            
            logger.info(f"訂單創建成功: {order.id}")
            return order
            
        except Exception as e:
            logger.error(f"創建訂單失敗: {e}")
            raise
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        根據ID獲取訂單
        
        Args:
            order_id: 訂單ID
            
        Returns:
            Optional[Order]: 訂單對象或None
        """
        return self.orders.get(order_id)
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        """
        更新訂單狀態
        
        Args:
            order_id: 訂單ID
            status: 新狀態
            
        Returns:
            bool: 更新是否成功
        """
        try:
            order = self.orders.get(order_id)
            if order:
                order.status = status
                order.updated_at = datetime.now()
                logger.info(f"訂單 {order_id} 狀態更新為 {status.value}")
                return True
            else:
                logger.warning(f"訂單 {order_id} 不存在")
                return False
        except Exception as e:
            logger.error(f"更新訂單狀態失敗: {e}")
            return False
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """
        根據狀態獲取訂單列表
        
        Args:
            status: 訂單狀態
            
        Returns:
            List[Order]: 符合條件的訂單列表
        """
        return [order for order in self.orders.values() if order.status == status]
    
    def get_active_orders(self) -> List[Order]:
        """
        獲取活躍訂單（非已送達和已取消）
        
        Returns:
            List[Order]: 活躍訂單列表
        """
        active_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.READY
        ]
        return [
            order for order in self.orders.values()
            if order.status in active_statuses
        ]