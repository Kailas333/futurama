# Футурама - API доставки еды

Полноценный бэкенд для системы доставки еды "Футурама" на FastAPI.

## 🚀 Возможности

- **Аутентификация и авторизация** с JWT токенами
- **Управление пользователями** (клиенты, курьеры, рестораны, админы)
- **Управление ресторанами** и их меню
- **Система заказов** с отслеживанием статусов
- **Управление доставкой** с назначением курьеров
- **RESTful API** с полной документацией
- **База данных SQLite** (легко переключить на PostgreSQL)

## 🛠 Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - валидация данных и сериализация
- **JWT** - аутентификация пользователей
- **bcrypt** - хеширование паролей
- **SQLite** - база данных (по умолчанию)

## 📋 Требования

- Python 3.8+
- pip

## 🔧 Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd futurama
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
```

3. **Активируйте виртуальное окружение:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

5. **Инициализируйте базу данных:**
```bash
python -m app.init_db
```

6. **Запустите сервер:**
```bash
python main.py
```

Или с помощью uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Документация

После запуска сервера документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 👥 Роли пользователей

### 1. Клиент (CUSTOMER)
- Регистрация и авторизация
- Просмотр ресторанов и меню
- Создание и отслеживание заказов
- Управление адресами доставки

### 2. Курьер (DELIVERY_PERSON)
- Просмотр назначенных доставок
- Подтверждение получения заказов
- Подтверждение доставки

### 3. Ресторанный администратор (RESTAURANT_ADMIN)
- Управление меню ресторана
- Обновление статусов заказов
- Просмотр заказов своего ресторана

### 4. Системный администратор (ADMIN)
- Полный доступ ко всем функциям
- Управление пользователями
- Назначение курьеров на доставку

## 🔑 Тестовые аккаунты

После инициализации базы данных доступны следующие тестовые аккаунты:

| Роль | Email | Пароль |
|------|-------|--------|
| Администратор | admin@futurama.com | admin123 |
| Клиент | user@example.com | user123 |
| Курьер | courier@futurama.com | courier123 |
| Ресторан | restaurant@futurama.com | restaurant123 |

## 📡 Основные эндпоинты

### Аутентификация
- `POST /api/auth/register` - Регистрация пользователя
- `POST /api/auth/login` - Вход в систему
- `POST /api/auth/login-json` - Вход через JSON
- `GET /api/auth/me` - Информация о текущем пользователе

### Пользователи
- `GET /api/users/profile` - Профиль пользователя
- `PUT /api/users/profile` - Обновление профиля
- `GET /api/users/addresses` - Адреса пользователя
- `POST /api/users/addresses` - Добавление адреса

### Рестораны
- `GET /api/restaurants/` - Список ресторанов
- `GET /api/restaurants/{id}` - Информация о ресторане
- `GET /api/restaurants/search/` - Поиск ресторанов
- `GET /api/restaurants/nearby/` - Рестораны поблизости

### Меню
- `GET /api/menu/{restaurant_id}` - Меню ресторана
- `GET /api/menu/categories/{restaurant_id}` - Категории ресторана
- `GET /api/menu/item/{item_id}` - Информация о блюде
- `GET /api/menu/search/` - Поиск блюд

### Заказы
- `POST /api/orders/` - Создание заказа
- `GET /api/orders/` - Заказы пользователя
- `GET /api/orders/{id}` - Информация о заказе
- `DELETE /api/orders/{id}` - Отмена заказа

### Доставка
- `POST /api/delivery/assign` - Назначение курьера
- `GET /api/delivery/my-deliveries` - Доставки курьера
- `PUT /api/delivery/{id}/pickup` - Подтверждение получения
- `PUT /api/delivery/{id}/deliver` - Подтверждение доставки

## 🗄 Структура базы данных

### Основные таблицы:
- **users** - Пользователи системы
- **addresses** - Адреса доставки
- **restaurants** - Рестораны
- **categories** - Категории блюд
- **menu_items** - Блюда в меню
- **orders** - Заказы
- **order_items** - Элементы заказов
- **deliveries** - Доставки

## ⚙️ Конфигурация

Настройки приложения находятся в файле `app/config.py`:

```python
# Основные настройки
APP_NAME = "Футурама API"
DEBUG = True
VERSION = "1.0.0"

# База данных
DATABASE_URL = "sqlite:///./futurama.db"

# JWT настройки
SECRET_KEY = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройки приложения
MIN_ORDER_AMOUNT = 500.0  # Минимальная сумма заказа
DELIVERY_FEE = 200.0  # Стоимость доставки
FREE_DELIVERY_THRESHOLD = 2000.0  # Сумма для бесплатной доставки
```

## 🔒 Безопасность

- Пароли хешируются с помощью bcrypt
- JWT токены для аутентификации
- Ролевая система доступа
- Валидация всех входных данных
- CORS настройки для веб-приложений

## 🚀 Развертывание

### Для продакшена рекомендуется:

1. **Изменить базу данных на PostgreSQL:**
```python
DATABASE_URL = "postgresql://user:password@localhost/futurama"
```

2. **Установить секретный ключ:**
```python
SECRET_KEY = "your-super-secret-key-here"
```

3. **Отключить режим отладки:**
```python
DEBUG = False
```

4. **Настроить CORS для конкретных доменов:**
```python
allow_origins=["https://yourdomain.com"]
```

## 📝 Примеры использования

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "phone": "+7-999-999-99-99",
    "password": "password123",
    "first_name": "Новый",
    "last_name": "Пользователь"
  }'
```

### Вход в систему
```bash
curl -X POST "http://localhost:8000/api/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "user123"
  }'
```

### Создание заказа
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "delivery_address_id": 1,
    "items": [
      {
        "menu_item_id": 1,
        "quantity": 2
      }
    ],
    "notes": "Доставить к подъезду"
  }'
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 🆘 Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории.


**Футурама** - Доставка еды будущего! 🍕🚀
 
