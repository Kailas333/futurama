from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, restaurants, menu, orders, delivery, reports
from app.database import engine
from app.models import Base

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Футурама - Доставка еды ",
    description="API для системы доставки еды Футурама",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["Авторизация"])
app.include_router(users.router, prefix="/api/users", tags=["Клиенты"])
app.include_router(restaurants.router, prefix="/api/restaurants", tags=["Рестораны"])
app.include_router(menu.router, prefix="/api/menu", tags=["Меню"])
app.include_router(orders.router, prefix="/api/orders", tags=["Заказы"])
app.include_router(delivery.router, prefix="/api/delivery", tags=["Доставка"])
app.include_router(reports.router, prefix="/api/reports", tags=["Отчетность"])

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в API Футурама!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Футурама API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


