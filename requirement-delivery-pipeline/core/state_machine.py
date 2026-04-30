"""订单状态机模型：用于示例中的状态流转推演"""
from enum import Enum
from typing import List, Dict


class OrderState(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDING = "refunding"
    REFUNDED = "refunded"
    COMPLETED = "completed"


VALID_TRANSITIONS: Dict[OrderState, List[OrderState]] = {
    OrderState.PENDING: [OrderState.CONFIRMED, OrderState.CANCELLED],
    OrderState.CONFIRMED: [OrderState.PAID, OrderState.CANCELLED],
    OrderState.PAID: [OrderState.SHIPPING, OrderState.REFUNDING, OrderState.CANCELLED],
    OrderState.SHIPPING: [OrderState.DELIVERED],
    OrderState.DELIVERED: [OrderState.COMPLETED, OrderState.REFUNDING],
    OrderState.REFUNDING: [OrderState.REFUNDED],
    OrderState.REFUNDED: [],
    OrderState.CANCELLED: [],
    OrderState.COMPLETED: [],
}


def validate_transition(from_state: OrderState, to_state: OrderState) -> bool:
    """验证状态流转是否合法"""
    return to_state in VALID_TRANSITIONS.get(from_state, [])


def get_possible_next_states(current_state: OrderState) -> List[OrderState]:
    """获取当前状态的所有合法下一状态"""
    return VALID_TRANSITIONS.get(current_state, [])