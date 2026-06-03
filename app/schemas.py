from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, OrderStatus, PaymentStatus

# Базовые схемы
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# Схемы пользователей
class UserBase(BaseSchema):
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# Схемы аутентификации
class Token(BaseSchema):
    access_token: str
    token_type: str

class TokenData(BaseSchema):
    email: Optional[str] = None

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str

# Схемы адресов
class AddressBase(BaseSchema):
    street: str
    house: str
    apartment: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[str] = None
    intercom: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseSchema):
    street: Optional[str] = None
    house: Optional[str] = None
    apartment: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[str] = None
    intercom: Optional[str] = None
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime

# Схемы ресторанов
class RestaurantBase(BaseSchema):
    name: str
    description: Optional[str] = None
    address: str
    phone: str
    email: Optional[EmailStr] = None
    working_hours: Optional[str] = None
    delivery_time: int = 30
    min_order_amount: float = 500.0

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    working_hours: Optional[str] = None
    is_active: Optional[bool] = None
    delivery_time: Optional[int] = None
    min_order_amount: Optional[float] = None

class RestaurantResponse(RestaurantBase):
    id: int
    is_active: bool
    rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None

# Схемы категорий
class CategoryBase(BaseSchema):
    name: str
    description: Optional[str] = None
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    restaurant_id: int

class CategoryUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    restaurant_id: int
    is_active: bool

# Схемы блюд
class MenuItemBase(BaseSchema):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    preparation_time: int = 15
    calories: Optional[int] = None
    weight: Optional[str] = None
    allergens: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    restaurant_id: int
    category_id: int

class MenuItemUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = None
    calories: Optional[int] = None
    weight: Optional[str] = None
    allergens: Optional[str] = None

class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    category_id: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# Схемы заказов
class OrderItemBase(BaseSchema):
    menu_item_id: int
    quantity: int
    notes: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price: float
    menu_item: MenuItemResponse

class OrderBase(BaseSchema):
    restaurant_id: int
    delivery_address_id: int
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseSchema):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    delivery_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    notes: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: float
    delivery_fee: float
    total: float
    delivery_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse]

# Схемы доставки
class DeliveryBase(BaseSchema):
    order_id: int
    delivery_person_id: int
    notes: Optional[str] = None

class DeliveryCreate(DeliveryBase):
    pass

class DeliveryUpdate(BaseSchema):
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class DeliveryResponse(DeliveryBase):
    id: int
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Схемы для API ответов
class MessageResponse(BaseSchema):
    message: str

class PaginatedResponse(BaseSchema):
    items: List
    total: int
    page: int
    size: int
    pages: int




