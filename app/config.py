from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "Футурама API"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # База данных
    DATABASE_URL: str = "sqlite:///./futurama.db"
    
    # JWT настройки
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки приложения
    MIN_ORDER_AMOUNT: float = 500.0  # Минимальная сумма заказа в рублях
    DELIVERY_FEE: float = 200.0  # Стоимость доставки
    FREE_DELIVERY_THRESHOLD: float = 2000.0  # Сумма для бесплатной доставки
    
    class Config:
        env_file = ".env"

settings = Settings()




