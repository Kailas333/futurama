from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserResponse, UserUpdate, AddressCreate, AddressResponse, AddressUpdate
from app.auth import get_current_active_user, get_password_hash

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Получение профиля пользователя"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля пользователя"""
    # Проверка уникальности email
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    
    # Проверка уникальности телефона
    if user_update.phone and user_update.phone != current_user.phone:
        existing_phone = db.query(User).filter(User.phone == user_update.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким телефоном уже существует"
            )
    
    # Обновление полей
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/addresses", response_model=List[AddressResponse])
async def get_user_addresses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение адресов пользователя"""
    addresses = db.query(current_user.addresses).all()
    return addresses

@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_user_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание нового адреса пользователя"""
    from app.models import Address
    
    # Если это первый адрес, делаем его адресом по умолчанию
    if not current_user.addresses:
        address_data.is_default = True
    
    # Если новый адрес должен быть по умолчанию, сбрасываем флаг у других адресов
    if address_data.is_default:
        for addr in current_user.addresses:
            addr.is_default = False
    
    db_address = Address(**address_data.dict(), user_id=current_user.id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_user_address(
    address_id: int,
    address_update: AddressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление адреса пользователя"""
    from app.models import Address
    
    # Проверка существования адреса и принадлежности пользователю
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Адрес не найден"
        )
    
    # Если адрес становится адресом по умолчанию, сбрасываем флаг у других адресов
    if address_update.is_default:
        for addr in current_user.addresses:
            if addr.id != address_id:
                addr.is_default = False
    
    # Обновление полей
    update_data = address_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    db.commit()
    db.refresh(address)
    
    return address

@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_address(
    address_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удаление адреса пользователя"""
    from app.models import Address
    
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Адрес не найден"
        )
    
    # Если удаляется адрес по умолчанию, назначаем другой адрес по умолчанию
    if address.is_default and len(current_user.addresses) > 1:
        other_address = db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id
        ).first()
        if other_address:
            other_address.is_default = True
    
    db.delete(address)
    db.commit()
    
    return None

# Административные эндпоинты (только для админов)
@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение списка всех пользователей (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение пользователя по ID (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user




