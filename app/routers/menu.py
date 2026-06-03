from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem, Category, Restaurant, User, UserRole
from app.schemas import (
    MenuItemCreate, MenuItemResponse, MenuItemUpdate,
    CategoryCreate, CategoryResponse, CategoryUpdate
)
from app.auth import get_current_active_user

router = APIRouter()

# Эндпоинты для категорий
@router.get("/categories/{restaurant_id}", response_model=List[CategoryResponse])
async def get_restaurant_categories(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    """Получение категорий ресторана"""
    # Проверка существования ресторана
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.is_active == True
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    categories = db.query(Category).filter(
        Category.restaurant_id == restaurant_id,
        Category.is_active == True
    ).order_by(Category.sort_order).all()
    
    return categories

@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание новой категории (только для админов и ресторанных админов)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания категории"
        )
    
    # Проверка существования ресторана
    restaurant = db.query(Restaurant).filter(Restaurant.id == category_data.restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    db_category = Category(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление категории"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления категории"
        )
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удаление категории"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления категории"
        )
    
    # Проверка наличия блюд в категории
    menu_items = db.query(MenuItem).filter(MenuItem.category_id == category_id).first()
    if menu_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить категорию, содержащую блюда"
        )
    
    db.delete(category)
    db.commit()
    
    return None

# Эндпоинты для блюд
@router.get("/{restaurant_id}", response_model=List[MenuItemResponse])
async def get_restaurant_menu(
    restaurant_id: int,
    category_id: int = Query(None, description="Фильтр по категории"),
    is_available: bool = Query(True, description="Фильтр по доступности"),
    db: Session = Depends(get_db)
):
    """Получение меню ресторана"""
    # Проверка существования ресторана
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.is_active == True
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    query = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.is_available == is_available
    )
    
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    
    menu_items = query.all()
    return menu_items

@router.get("/item/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Получение информации о блюде"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено"
        )
    
    return menu_item

@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item_data: MenuItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание нового блюда (только для админов и ресторанных админов)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания блюда"
        )
    
    # Проверка существования ресторана
    restaurant = db.query(Restaurant).filter(Restaurant.id == menu_item_data.restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    # Проверка существования категории
    category = db.query(Category).filter(Category.id == menu_item_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    db_menu_item = MenuItem(**menu_item_data.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    
    return db_menu_item

@router.put("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: int,
    menu_item_update: MenuItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление блюда"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено"
        )
    
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления блюда"
        )
    
    update_data = menu_item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu_item, field, value)
    
    db.commit()
    db.refresh(menu_item)
    
    return menu_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удаление блюда"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Блюдо не найдено"
        )
    
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления блюда"
        )
    
    db.delete(menu_item)
    db.commit()
    
    return None

@router.get("/search/", response_model=List[MenuItemResponse])
async def search_menu_items(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    restaurant_id: int = Query(None, description="Фильтр по ресторану"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Поиск блюд по названию и описанию"""
    query = db.query(MenuItem).filter(
        MenuItem.is_available == True,
        (MenuItem.name.ilike(f"%{q}%") | MenuItem.description.ilike(f"%{q}%"))
    )
    
    if restaurant_id:
        query = query.filter(MenuItem.restaurant_id == restaurant_id)
    
    menu_items = query.offset(skip).limit(limit).all()
    return menu_items




