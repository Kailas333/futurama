from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Restaurant, Category, MenuItem, Address
from app.auth import get_password_hash
from app.models import UserRole

def init_db():
    """Инициализация базы данных с тестовыми данными"""
    db = SessionLocal()
    
    try:
        # Создание таблиц
        Base.metadata.create_all(bind=engine)
        
        # Проверка, есть ли уже данные
        if db.query(User).first():
            print("База данных уже содержит данные. Пропускаем инициализацию.")
            return
        
        print("Создание тестовых данных...")
        
        # Создание администратора
        admin_user = User(
            email="admin@futurama.com",
            phone="+7-999-000-00-00",
            hashed_password=get_password_hash("admin123"),
            first_name="Администратор",
            last_name="Системы",
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        
        # Создание тестового пользователя
        test_user = User(
            email="user@example.com",
            phone="+7-999-111-11-11",
            hashed_password=get_password_hash("user123"),
            first_name="Иван",
            last_name="Иванов",
            role=UserRole.CUSTOMER
        )
        db.add(test_user)
        
        # Создание курьера
        courier = User(
            email="courier@futurama.com",
            phone="+7-999-222-22-22",
            hashed_password=get_password_hash("courier123"),
            first_name="Петр",
            last_name="Курьер",
            role=UserRole.DELIVERY_PERSON
        )
        db.add(courier)
        
        # Создание ресторанного админа
        restaurant_admin = User(
            email="restaurant@futurama.com",
            phone="+7-999-333-33-33",
            hashed_password=get_password_hash("restaurant123"),
            first_name="Анна",
            last_name="Ресторанная",
            role=UserRole.RESTAURANT_ADMIN
        )
        db.add(restaurant_admin)
        
        db.commit()
        
        # Создание ресторанов
        restaurant1 = Restaurant(
            name="Пиццерия Футурама",
            description="Лучшая пицца в городе с доставкой до двери",
            address="ул. Пушкина, д. 10",
            phone="+7-495-123-45-67",
            email="pizza@futurama.com",
            working_hours='{"monday": "10:00-23:00", "tuesday": "10:00-23:00", "wednesday": "10:00-23:00", "thursday": "10:00-23:00", "friday": "10:00-00:00", "saturday": "10:00-00:00", "sunday": "10:00-22:00"}',
            delivery_time=30,
            min_order_amount=500.0,
            rating=4.8
        )
        db.add(restaurant1)
        
        restaurant2 = Restaurant(
            name="Суши-бар Футурама",
            description="Свежие суши и роллы с доставкой",
            address="пр. Ленина, д. 25",
            phone="+7-495-234-56-78",
            email="sushi@futurama.com",
            working_hours='{"monday": "11:00-22:00", "tuesday": "11:00-22:00", "wednesday": "11:00-22:00", "thursday": "11:00-22:00", "friday": "11:00-23:00", "saturday": "11:00-23:00", "sunday": "11:00-21:00"}',
            delivery_time=25,
            min_order_amount=800.0,
            rating=4.6
        )
        db.add(restaurant2)
        
        db.commit()
        
        # Создание категорий для пиццерии
        pizza_category = Category(
            restaurant_id=restaurant1.id,
            name="Пицца",
            description="Классические и авторские пиццы",
            sort_order=1
        )
        db.add(pizza_category)
        
        drinks_category = Category(
            restaurant_id=restaurant1.id,
            name="Напитки",
            description="Холодные и горячие напитки",
            sort_order=2
        )
        db.add(drinks_category)
        
        # Создание категорий для суши-бара
        sushi_category = Category(
            restaurant_id=restaurant2.id,
            name="Суши и роллы",
            description="Классические суши и авторские роллы",
            sort_order=1
        )
        db.add(sushi_category)
        
        soup_category = Category(
            restaurant_id=restaurant2.id,
            name="Супы",
            description="Традиционные японские супы",
            sort_order=2
        )
        db.add(soup_category)
        
        db.commit()
        
        # Создание блюд для пиццерии
        pizza_margherita = MenuItem(
            restaurant_id=restaurant1.id,
            category_id=pizza_category.id,
            name="Пицца Маргарита",
            description="Классическая пицца с томатным соусом, моцареллой и базиликом",
            price=650.0,
            image_url="https://example.com/pizza-margherita.jpg",
            preparation_time=15,
            calories=266,
            weight="350г",
            allergens='["глютен", "лактоза"]'
        )
        db.add(pizza_margherita)
        
        pizza_pepperoni = MenuItem(
            restaurant_id=restaurant1.id,
            category_id=pizza_category.id,
            name="Пицца Пепперони",
            description="Пицца с пепперони, моцареллой и томатным соусом",
            price=750.0,
            image_url="https://example.com/pizza-pepperoni.jpg",
            preparation_time=18,
            calories=312,
            weight="380г",
            allergens='["глютен", "лактоза"]'
        )
        db.add(pizza_pepperoni)
        
        cola = MenuItem(
            restaurant_id=restaurant1.id,
            category_id=drinks_category.id,
            name="Кока-Кола",
            description="Классическая газировка",
            price=150.0,
            image_url="https://example.com/cola.jpg",
            preparation_time=2,
            calories=42,
            weight="330мл",
            allergens='[]'
        )
        db.add(cola)
        
        # Создание блюд для суши-бара
        california_roll = MenuItem(
            restaurant_id=restaurant2.id,
            category_id=sushi_category.id,
            name="Ролл Калифорния",
            description="Ролл с крабом, авокадо и огурцом",
            price=450.0,
            image_url="https://example.com/california-roll.jpg",
            preparation_time=12,
            calories=180,
            weight="200г",
            allergens='["рыба", "глютен"]'
        )
        db.add(california_roll)
        
        salmon_nigiri = MenuItem(
            restaurant_id=restaurant2.id,
            category_id=sushi_category.id,
            name="Нигири с лососем",
            description="Классические нигири с лососем",
            price=280.0,
            image_url="https://example.com/salmon-nigiri.jpg",
            preparation_time=8,
            calories=120,
            weight="80г",
            allergens='["рыба"]'
        )
        db.add(salmon_nigiri)
        
        miso_soup = MenuItem(
            restaurant_id=restaurant2.id,
            category_id=soup_category.id,
            name="Мисо суп",
            description="Традиционный японский суп с тофу и водорослями",
            price=200.0,
            image_url="https://example.com/miso-soup.jpg",
            preparation_time=10,
            calories=85,
            weight="250мл",
            allergens='["соя"]'
        )
        db.add(miso_soup)
        
        db.commit()
        
        # Создание адреса для тестового пользователя
        user_address = Address(
            user_id=test_user.id,
            street="ул. Примерная",
            house="15",
            apartment="42",
            entrance="2",
            floor="4",
            intercom="42",
            is_default=True
        )
        db.add(user_address)
        
        db.commit()
        
        print("Тестовые данные успешно созданы!")
        print("\nДоступные пользователи:")
        print("Админ: admin@futurama.com / admin123")
        print("Пользователь: user@example.com / user123")
        print("Курьер: courier@futurama.com / courier123")
        print("Ресторан: restaurant@futurama.com / restaurant123")
        
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()




