import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import FastAPIUser, FastAPIRestaurant, FastAPIOrder, FastAPIDelivery, SystemLog


class FastAPISyncService:
    """Сервис для синхронизации данных с FastAPI"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'FASTAPI_URL', 'http://localhost:8000')
        self.session = requests.Session()
    
    def log_action(self, level, message, user=None, ip_address=None, user_agent=None):
        """Логирование действий"""
        SystemLog.objects.create(
            level=level,
            message=message,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def sync_users(self):
        """Синхронизация пользователей"""
        try:
            response = self.session.get(f"{self.base_url}/api/users/")
            if response.status_code == 200:
                users_data = response.json()
                for user_data in users_data:
                    FastAPIUser.objects.update_or_create(
                        fastapi_id=user_data['id'],
                        defaults={
                            'email': user_data['email'],
                            'phone': user_data['phone'],
                            'first_name': user_data['first_name'],
                            'last_name': user_data['last_name'],
                            'role': user_data['role'],
                            'is_active': user_data['is_active'],
                            'updated_at': timezone.now()
                        }
                    )
                self.log_action('info', f'Синхронизировано {len(users_data)} пользователей')
                return True
        except Exception as e:
            self.log_action('error', f'Ошибка синхронизации пользователей: {str(e)}')
            return False
    
    def sync_restaurants(self):
        """Синхронизация ресторанов"""
        try:
            response = self.session.get(f"{self.base_url}/api/restaurants/")
            if response.status_code == 200:
                restaurants_data = response.json()
                for restaurant_data in restaurants_data:
                    FastAPIRestaurant.objects.update_or_create(
                        fastapi_id=restaurant_data['id'],
                        defaults={
                            'name': restaurant_data['name'],
                            'description': restaurant_data.get('description', ''),
                            'address': restaurant_data['address'],
                            'phone': restaurant_data['phone'],
                            'email': restaurant_data.get('email', ''),
                            'working_hours': restaurant_data.get('working_hours', ''),
                            'is_active': restaurant_data['is_active'],
                            'rating': restaurant_data.get('rating', 0.0),
                            'delivery_time': restaurant_data.get('delivery_time', 30),
                            'min_order_amount': restaurant_data.get('min_order_amount', 500.0),
                            'updated_at': timezone.now()
                        }
                    )
                self.log_action('info', f'Синхронизировано {len(restaurants_data)} ресторанов')
                return True
        except Exception as e:
            self.log_action('error', f'Ошибка синхронизации ресторанов: {str(e)}')
            return False
    
    def sync_orders(self):
        """Синхронизация заказов"""
        try:
            response = self.session.get(f"{self.base_url}/api/orders/admin/all")
            if response.status_code == 200:
                orders_data = response.json()
                for order_data in orders_data:
                    # Получаем пользователя и ресторан
                    try:
                        user = FastAPIUser.objects.get(fastapi_id=order_data['user_id'])
                        restaurant = FastAPIRestaurant.objects.get(fastapi_id=order_data['restaurant_id'])
                        
                        FastAPIOrder.objects.update_or_create(
                            fastapi_id=order_data['id'],
                            defaults={
                                'user': user,
                                'restaurant': restaurant,
                                'status': order_data['status'],
                                'payment_status': order_data['payment_status'],
                                'subtotal': order_data['subtotal'],
                                'delivery_fee': order_data.get('delivery_fee', 200.0),
                                'total': order_data['total'],
                                'notes': order_data.get('notes', ''),
                                'updated_at': timezone.now()
                            }
                        )
                    except (FastAPIUser.DoesNotExist, FastAPIRestaurant.DoesNotExist):
                        continue
                
                self.log_action('info', f'Синхронизировано {len(orders_data)} заказов')
                return True
        except Exception as e:
            self.log_action('error', f'Ошибка синхронизации заказов: {str(e)}')
            return False
    
    def sync_deliveries(self):
        """Синхронизация доставок"""
        try:
            response = self.session.get(f"{self.base_url}/api/delivery/admin/all")
            if response.status_code == 200:
                deliveries_data = response.json()
                for delivery_data in deliveries_data:
                    # Получаем заказ и курьера
                    try:
                        order = FastAPIOrder.objects.get(fastapi_id=delivery_data['order_id'])
                        delivery_person = FastAPIUser.objects.get(fastapi_id=delivery_data['delivery_person_id'])
                        
                        FastAPIDelivery.objects.update_or_create(
                            fastapi_id=delivery_data['id'],
                            defaults={
                                'order': order,
                                'delivery_person': delivery_person,
                                'status': delivery_data['status'],
                                'pickup_time': delivery_data.get('pickup_time'),
                                'delivery_time': delivery_data.get('delivery_time'),
                                'notes': delivery_data.get('notes', ''),
                                'updated_at': timezone.now()
                            }
                        )
                    except (FastAPIOrder.DoesNotExist, FastAPIUser.DoesNotExist):
                        continue
                
                self.log_action('info', f'Синхронизировано {len(deliveries_data)} доставок')
                return True
        except Exception as e:
            self.log_action('error', f'Ошибка синхронизации доставок: {str(e)}')
            return False
    
    def sync_all(self):
        """Полная синхронизация всех данных"""
        self.log_action('info', 'Начало полной синхронизации')
        
        success = True
        success &= self.sync_users()
        success &= self.sync_restaurants()
        success &= self.sync_orders()
        success &= self.sync_deliveries()
        
        if success:
            self.log_action('info', 'Полная синхронизация завершена успешно')
        else:
            self.log_action('warning', 'Полная синхронизация завершена с ошибками')
        
        return success
    
    def get_system_stats(self):
        """Получение статистики системы"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None




