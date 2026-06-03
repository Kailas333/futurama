from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Delivery, Order, User, UserRole, OrderStatus
from app.schemas import DeliveryCreate, DeliveryResponse, DeliveryUpdate
from app.auth import get_current_active_user

router = APIRouter()

@router.post("/assign", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def assign_delivery(
    delivery_data: DeliveryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Назначение курьера на доставку (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для назначения доставки"
        )
    
    # Проверка существования заказа
    order = db.query(Order).filter(Order.id == delivery_data.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверка статуса заказа
    if order.status != OrderStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ не готов к доставке"
        )
    
    # Проверка существования курьера
    delivery_person = db.query(User).filter(
        User.id == delivery_data.delivery_person_id,
        User.role == UserRole.DELIVERY_PERSON,
        User.is_active == True
    ).first()
    
    if not delivery_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курьер не найден"
        )
    
    # Проверка, что заказ еще не назначен на доставку
    existing_delivery = db.query(Delivery).filter(
        Delivery.order_id == delivery_data.order_id,
        Delivery.status.in_(["assigned", "picked_up"])
    ).first()
    
    if existing_delivery:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ уже назначен на доставку"
        )
    
    # Создание доставки
    db_delivery = Delivery(**delivery_data.dict())
    db.add(db_delivery)
    
    # Обновление статуса заказа
    order.status = OrderStatus.IN_DELIVERY
    
    db.commit()
    db.refresh(db_delivery)
    
    return db_delivery

@router.get("/my-deliveries", response_model=List[DeliveryResponse])
async def get_my_deliveries(
    status_filter: str = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение доставок курьера"""
    if current_user.role != UserRole.DELIVERY_PERSON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для курьеров"
        )
    
    query = db.query(Delivery).filter(Delivery.delivery_person_id == current_user.id)
    
    if status_filter:
        query = query.filter(Delivery.status == status_filter)
    
    deliveries = query.order_by(Delivery.created_at.desc()).all()
    return deliveries

@router.put("/{delivery_id}/pickup", response_model=DeliveryResponse)
async def pickup_order(
    delivery_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Подтверждение получения заказа курьером"""
    if current_user.role != UserRole.DELIVERY_PERSON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для курьеров"
        )
    
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id,
        Delivery.delivery_person_id == current_user.id
    ).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не найдена"
        )
    
    if delivery.status != "assigned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ уже получен или доставлен"
        )
    
    delivery.status = "picked_up"
    delivery.pickup_time = datetime.utcnow()
    
    db.commit()
    db.refresh(delivery)
    
    return delivery

@router.put("/{delivery_id}/deliver", response_model=DeliveryResponse)
async def deliver_order(
    delivery_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Подтверждение доставки заказа"""
    if current_user.role != UserRole.DELIVERY_PERSON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для курьеров"
        )
    
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id,
        Delivery.delivery_person_id == current_user.id
    ).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не найдена"
        )
    
    if delivery.status != "picked_up":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ еще не получен"
        )
    
    delivery.status = "delivered"
    delivery.delivery_time = datetime.utcnow()
    
    # Обновление статуса заказа
    order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if order:
        order.status = OrderStatus.DELIVERED
        order.delivery_time = datetime.utcnow()
    
    db.commit()
    db.refresh(delivery)
    
    return delivery

@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение информации о доставке"""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не найдена"
        )
    
    # Проверка прав доступа
    if current_user.role == UserRole.DELIVERY_PERSON and delivery.delivery_person_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра этой доставки"
        )
    
    return delivery

@router.put("/{delivery_id}", response_model=DeliveryResponse)
async def update_delivery(
    delivery_id: int,
    delivery_update: DeliveryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о доставке (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления доставки"
        )
    
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не найдена"
        )
    
    update_data = delivery_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(delivery, field, value)
    
    db.commit()
    db.refresh(delivery)
    
    return delivery

# Административные эндпоинты
@router.get("/admin/all", response_model=List[DeliveryResponse])
async def get_all_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    delivery_person_id: int = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение всех доставок (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    query = db.query(Delivery)
    
    if status_filter:
        query = query.filter(Delivery.status == status_filter)
    
    if delivery_person_id:
        query = query.filter(Delivery.delivery_person_id == delivery_person_id)
    
    deliveries = query.order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()
    return deliveries

@router.get("/admin/available-couriers", response_model=List[dict])
async def get_available_couriers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение списка доступных курьеров (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    # Получаем всех активных курьеров
    couriers = db.query(User).filter(
        User.role == UserRole.DELIVERY_PERSON,
        User.is_active == True
    ).all()
    
    # Для каждого курьера проверяем количество активных доставок
    available_couriers = []
    for courier in couriers:
        active_deliveries = db.query(Delivery).filter(
            Delivery.delivery_person_id == courier.id,
            Delivery.status.in_(["assigned", "picked_up"])
        ).count()
        
        available_couriers.append({
            "id": courier.id,
            "name": f"{courier.first_name} {courier.last_name}",
            "phone": courier.phone,
            "active_deliveries": active_deliveries,
            "available": active_deliveries < 3  # Максимум 3 активные доставки
        })
    
    return available_couriers




