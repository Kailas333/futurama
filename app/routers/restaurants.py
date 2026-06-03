from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Restaurant, User, UserRole
from app.schemas import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[RestaurantResponse])
async def get_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Получение списка ресторанов"""
    restaurants = db.query(Restaurant).filter(
        Restaurant.is_active == is_active
    ).offset(skip).limit(limit).all()
    return restaurants

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    """Получение информации о ресторане"""
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.is_active == True
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    return restaurant

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание нового ресторана (только для админов и ресторанных админов)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания ресторана"
        )
    
    db_restaurant = Restaurant(**restaurant_data.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    
    return db_restaurant

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о ресторане"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    # Проверка прав доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления ресторана"
        )
    
    # Обновление полей
    update_data = restaurant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)
    
    db.commit()
    db.refresh(restaurant)
    
    return restaurant

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удаление ресторана (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления ресторана"
        )
    
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    # Логическое удаление (деактивация)
    restaurant.is_active = False
    db.commit()
    
    return None

@router.get("/search/", response_model=List[RestaurantResponse])
async def search_restaurants(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Поиск ресторанов по названию и описанию"""
    restaurants = db.query(Restaurant).filter(
        Restaurant.is_active == True,
        (Restaurant.name.ilike(f"%{q}%") | Restaurant.description.ilike(f"%{q}%"))
    ).offset(skip).limit(limit).all()
    
    return restaurants

@router.get("/nearby/", response_model=List[RestaurantResponse])
async def get_nearby_restaurants(
    latitude: float = Query(..., description="Широта"),
    longitude: float = Query(..., description="Долгота"),
    radius: float = Query(5.0, ge=0.1, le=50.0, description="Радиус поиска в км"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получение ресторанов поблизости (заглушка для геолокации)"""
    # В реальном приложении здесь была бы логика расчета расстояний
    # Пока возвращаем все активные рестораны
    restaurants = db.query(Restaurant).filter(
        Restaurant.is_active == True
    ).offset(skip).limit(limit).all()
    
    return restaurants




