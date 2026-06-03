from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.database import get_db
from app.models import Order, OrderItem, MenuItem, Restaurant, User, UserRole, Category, OrderStatus
from app.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter()

# Схемы для отчетности
class CategoryReport(BaseModel):
    category_id: int
    category_name: str
    restaurant_id: int
    restaurant_name: str
    total_orders: int
    total_quantity: int
    total_revenue: float
    average_order_value: float

class DateReport(BaseModel):
    date: str
    total_orders: int
    total_revenue: float
    average_order_value: float
    completed_orders: int
    cancelled_orders: int
    pending_orders: int

class DetailedReport(BaseModel):
    category_reports: List[CategoryReport]
    date_reports: List[DateReport]
    summary: dict

@router.get("/categories", response_model=List[CategoryReport])
async def get_category_report(
    start_date: Optional[datetime] = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    restaurant_id: Optional[int] = Query(None, description="ID ресторана для фильтрации"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение отчета по категориям"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра отчетов"
        )
    
    # Базовый запрос
    query = db.query(
        Category.id.label('category_id'),
        Category.name.label('category_name'),
        Restaurant.id.label('restaurant_id'),
        Restaurant.name.label('restaurant_name'),
        func.count(Order.id).label('total_orders'),
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue'),
        func.avg(Order.total).label('average_order_value')
    ).join(
        MenuItem, Category.id == MenuItem.category_id
    ).join(
        OrderItem, MenuItem.id == OrderItem.menu_item_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).join(
        Restaurant, Category.restaurant_id == Restaurant.id
    ).filter(
        Order.status != OrderStatus.CANCELLED
    )
    
    # Фильтрация по датам
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date + timedelta(days=1))
    
    # Фильтрация по ресторану
    if restaurant_id:
        query = query.filter(Restaurant.id == restaurant_id)
    elif current_user.role == UserRole.RESTAURANT_ADMIN:
        # Ресторанные админы видят только свой ресторан
        query = query.filter(Restaurant.id == current_user.restaurant_id)
    
    # Группировка и сортировка
    results = query.group_by(
        Category.id, Category.name, Restaurant.id, Restaurant.name
    ).order_by(desc('total_revenue')).all()
    
    return [
        CategoryReport(
            category_id=row.category_id,
            category_name=row.category_name,
            restaurant_id=row.restaurant_id,
            restaurant_name=row.restaurant_name,
            total_orders=row.total_orders or 0,
            total_quantity=row.total_quantity or 0,
            total_revenue=float(row.total_revenue or 0),
            average_order_value=float(row.average_order_value or 0)
        )
        for row in results
    ]

@router.get("/dates", response_model=List[DateReport])
async def get_date_report(
    start_date: Optional[datetime] = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    restaurant_id: Optional[int] = Query(None, description="ID ресторана для фильтрации"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение отчета по датам"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра отчетов"
        )
    
    # Базовый запрос
    query = db.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total).label('total_revenue'),
        func.avg(Order.total).label('average_order_value'),
        func.sum(func.case([(Order.status == OrderStatus.DELIVERED, 1)], else_=0)).label('completed_orders'),
        func.sum(func.case([(Order.status == OrderStatus.CANCELLED, 1)], else_=0)).label('cancelled_orders'),
        func.sum(func.case([(Order.status == OrderStatus.PENDING, 1)], else_=0)).label('pending_orders')
    ).filter(
        Order.status != OrderStatus.CANCELLED
    )
    
    # Фильтрация по датам
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date + timedelta(days=1))
    
    # Фильтрация по ресторану
    if restaurant_id:
        query = query.filter(Order.restaurant_id == restaurant_id)
    elif current_user.role == UserRole.RESTAURANT_ADMIN:
        # Ресторанные админы видят только свой ресторан
        query = query.filter(Order.restaurant_id == current_user.restaurant_id)
    
    # Группировка и сортировка
    results = query.group_by(
        func.date(Order.created_at)
    ).order_by(desc('date')).all()
    
    return [
        DateReport(
            date=str(row.date),
            total_orders=row.total_orders or 0,
            total_revenue=float(row.total_revenue or 0),
            average_order_value=float(row.average_order_value or 0),
            completed_orders=row.completed_orders or 0,
            cancelled_orders=row.cancelled_orders or 0,
            pending_orders=row.pending_orders or 0
        )
        for row in results
    ]

@router.get("/detailed", response_model=DetailedReport)
async def get_detailed_report(
    start_date: Optional[datetime] = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    restaurant_id: Optional[int] = Query(None, description="ID ресторана для фильтрации"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение детального отчета с категориями и датами"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра отчетов"
        )
    
    # Получаем отчеты по категориям и датам
    category_reports = await get_category_report(
        start_date=start_date,
        end_date=end_date,
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db
    )
    
    date_reports = await get_date_report(
        start_date=start_date,
        end_date=end_date,
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db
    )
    
    # Вычисляем общую статистику
    total_revenue = sum(report.total_revenue for report in category_reports)
    total_orders = sum(report.total_orders for report in category_reports)
    total_quantity = sum(report.total_quantity for report in category_reports)
    
    summary = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "average_order_value": total_revenue / total_orders if total_orders > 0 else 0,
        "period_start": start_date.isoformat() if start_date else None,
        "period_end": end_date.isoformat() if end_date else None,
        "restaurant_id": restaurant_id
    }
    
    return DetailedReport(
        category_reports=category_reports,
        date_reports=date_reports,
        summary=summary
    )

@router.get("/summary")
async def get_summary_report(
    period: str = Query("week", description="Период: day, week, month, year"),
    restaurant_id: Optional[int] = Query(None, description="ID ресторана для фильтрации"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение краткого отчета за период"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра отчетов"
        )
    
    # Определяем период
    now = datetime.utcnow()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=7)
    
    # Базовый запрос
    query = db.query(
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total).label('total_revenue'),
        func.avg(Order.total).label('average_order_value'),
        func.sum(func.case([(Order.status == OrderStatus.DELIVERED, 1)], else_=0)).label('completed_orders'),
        func.sum(func.case([(Order.status == OrderStatus.CANCELLED, 1)], else_=0)).label('cancelled_orders')
    ).filter(
        Order.created_at >= start_date,
        Order.status != OrderStatus.CANCELLED
    )
    
    # Фильтрация по ресторану
    if restaurant_id:
        query = query.filter(Order.restaurant_id == restaurant_id)
    elif current_user.role == UserRole.RESTAURANT_ADMIN:
        query = query.filter(Order.restaurant_id == current_user.restaurant_id)
    
    result = query.first()
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "total_orders": result.total_orders or 0,
        "total_revenue": float(result.total_revenue or 0),
        "average_order_value": float(result.average_order_value or 0),
        "completed_orders": result.completed_orders or 0,
        "cancelled_orders": result.cancelled_orders or 0,
        "completion_rate": (result.completed_orders or 0) / (result.total_orders or 1) * 100
    }
