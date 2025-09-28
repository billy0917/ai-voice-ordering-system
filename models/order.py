"""
訂單相關數據模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid

class OrderStatus(Enum):
    """訂單狀態枚舉"""
    PENDING = "pending"          # 待確認
    CONFIRMED = "confirmed"      # 已確認
    PREPARING = "preparing"      # 準備中
    READY = "ready"             # 完成
    DELIVERED = "delivered"      # 已送達
    CANCELLED = "cancelled"      # 已取消

@dataclass
class OrderItem:
    """訂單項目模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    quantity: int = 1
    unit_price: float = 0.0
    customizations: Dict[str, str] = field(default_factory=dict)
    
    @property
    def total_price(self) -> float:
        """計算項目總價"""
        return self.unit_price * self.quantity

@dataclass
class Order:
    """訂單模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: Optional[str] = None
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    special_requests: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    transcription: str = ""
    confidence_score: float = 0.0
    
    @property
    def total_amount(self) -> float:
        """計算訂單總金額"""
        return sum(item.total_price for item in self.items)
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'items': [
                {
                    'id': item.id,
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price,
                    'customizations': item.customizations
                }
                for item in self.items
            ],
            'total_amount': self.total_amount,
            'status': self.status.value,
            'special_requests': self.special_requests,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'transcription': self.transcription,
            'confidence_score': self.confidence_score
        }