from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, MenuItem, Restaurant, User, UserRole, OrderStatus, PaymentStatus
from app.schemas import OrderCreate, OrderResponse, OrderUpdate, OrderItemResponse
from app.auth import get_current_active_user
from app.config import settings

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание нового заказа"""
    # Проверка существования ресторана
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == order_data.restaurant_id,
        Restaurant.is_active == True
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    # Проверка минимальной суммы заказа
    subtotal = 0
    order_items = []
    
    for item in order_data.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item.menu_item_id,
            MenuItem.restaurant_id == order_data.restaurant_id,
            MenuItem.is_available == True
        ).first()
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блюдо с ID {item.menu_item_id} не найдено или недоступно"
            )
        
        item_total = menu_item.price * item.quantity
        subtotal += item_total
        order_items.append((menu_item, item))
    
    if subtotal < restaurant.min_order_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Минимальная сумма заказа: {restaurant.min_order_amount} руб."
        )
    
    # Расчет стоимости доставки
    delivery_fee = 0 if subtotal >= settings.FREE_DELIVERY_THRESHOLD else settings.DELIVERY_FEE
    total = subtotal + delivery_fee
    
    # Создание заказа
    db_order = Order(
        user_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        delivery_address_id=order_data.delivery_address_id,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        notes=order_data.notes,
        estimated_delivery_time=datetime.utcnow() + timedelta(minutes=restaurant.delivery_time)
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Создание элементов заказа
    for menu_item, item_data in order_items:
        db_order_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=menu_item.id,
            quantity=item_data.quantity,
            price=menu_item.price,
            notes=item_data.notes
        )
        db.add(db_order_item)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: OrderStatus = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение заказов пользователя"""
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение информации о заказе"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление заказа (только для ресторанов и админов)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверка прав доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления заказа"
        )
    
    # Проверка, что пользователь связан с рестораном заказа
    if current_user.role == UserRole.RESTAURANT_ADMIN and order.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления этого заказа"
        )
    
    # Обновление полей
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Отмена заказа"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверка возможности отмены
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ нельзя отменить в текущем статусе"
        )
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    
    return None

# Административные эндпоинты
@router.get("/admin/all", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: OrderStatus = Query(None),
    restaurant_id: int = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение всех заказов (только для админов и ресторанных админов)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    if restaurant_id:
        query = query.filter(Order.restaurant_id == restaurant_id)
    elif current_user.role == UserRole.RESTAURANT_ADMIN:
        # Ресторанные админы видят только заказы своего ресторана
        query = query.filter(Order.restaurant_id == current_user.restaurant_id)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/admin/{order_id}", response_model=OrderResponse)
async def get_order_admin(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение заказа администратором"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверка прав доступа для ресторанных админов
    if current_user.role == UserRole.RESTAURANT_ADMIN and order.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра этого заказа"
        )
    
    return order




