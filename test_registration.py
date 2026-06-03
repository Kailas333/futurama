#!/usr/bin/env python3
"""
Скрипт для тестирования регистрации клиентов в FastAPI
"""

import requests
import json
import time

# URL FastAPI сервера
BASE_URL = "http://localhost:8000"

def test_registration():
    """Тестирование регистрации нового пользователя"""
    print("🧪 Тестирование регистрации клиентов...")
    print("=" * 50)
    
    # Данные для регистрации с уникальным email и телефоном
    timestamp = int(time.time())
    user_data = {
        "email": f"test{timestamp}@example.com",
        "phone": f"+7-999-{timestamp % 1000:03d}-{timestamp % 100:02d}-{timestamp % 10:02d}",
        "password": "test123",
        "first_name": "Тест",
        "last_name": "Пользователь"
    }
    
    try:
        # Регистрация нового пользователя
        print("📝 Регистрация нового пользователя...")
        print(f"Email: {user_data['email']}")
        print(f"Телефон: {user_data['phone']}")
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 201:
            user = response.json()
            print("✅ Регистрация успешна!")
            print(f"ID пользователя: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Имя: {user['first_name']} {user['last_name']}")
            print(f"Роль: {user['role']}")
            return user
        else:
            print("❌ Ошибка регистрации:")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что FastAPI сервер запущен.")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_login(email, password):
    """Тестирование входа в систему"""
    print("\n🔐 Тестирование входа в систему...")
    print("=" * 50)
    
    try:
        # Вход через JSON
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login-json",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Вход успешен!")
            print(f"Тип токена: {token_data['token_type']}")
            print(f"Токен: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print("❌ Ошибка входа:")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_get_user_info(token):
    """Тестирование получения информации о пользователе"""
    print("\n👤 Тестирование получения информации о пользователе...")
    print("=" * 50)
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=headers
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ Информация о пользователе получена!")
            print(f"ID: {user_info['id']}")
            print(f"Email: {user_info['email']}")
            print(f"Имя: {user_info['first_name']} {user_info['last_name']}")
            print(f"Телефон: {user_info['phone']}")
            print(f"Роль: {user_info['role']}")
            print(f"Активен: {user_info['is_active']}")
            return user_info
        else:
            print("❌ Ошибка получения информации:")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_duplicate_registration():
    """Тестирование регистрации с существующим email"""
    print("\n🔄 Тестирование дублирования регистрации...")
    print("=" * 50)
    
    user_data = {
        "email": "test@example.com",  # Тот же email
        "phone": "+7-999-999-99-98",  # Другой телефон
        "password": "test123",
        "first_name": "Дубликат",
        "last_name": "Пользователь"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Правильно отклонена дублирующая регистрация!")
            print(response.text)
        else:
            print("❌ Ошибка: дублирующая регистрация должна быть отклонена")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_existing_user_login():
    """Тестирование входа существующего пользователя"""
    print("\n🔐 Тестирование входа существующего пользователя...")
    print("=" * 50)
    
    try:
        login_data = {
            "email": "user@example.com",
            "password": "user123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login-json",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Вход успешен!")
            print(f"Тип токена: {token_data['token_type']}")
            print(f"Токен: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print("❌ Ошибка входа:")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов регистрации клиентов")
    print("=" * 60)
    
    # Тест 1: Регистрация нового пользователя
    user = test_registration()
    
    if user:
        # Тест 2: Вход в систему
        token = test_login(user['email'], "test123")
        
        if token:
            # Тест 3: Получение информации о пользователе
            test_get_user_info(token)
    
    # Тест 4: Попытка дублирования регистрации
    test_duplicate_registration()
    
    # Тест 5: Вход существующего пользователя
    test_existing_user_login()
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено!")

if __name__ == "__main__":
    main()
