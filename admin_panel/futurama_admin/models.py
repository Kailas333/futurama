from django.db import models
from django.contrib.auth.models import User


class FastAPIUser(models.Model):
    """Модель для синхронизации пользователей с FastAPI"""
    fastapi_id = models.IntegerField(unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[
        ('customer', 'Клиент'),
        ('restaurant_admin', 'Администратор ресторана'),
        ('delivery_person', 'Курьер'),
        ('admin', 'Администратор'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пользователь FastAPI'
        verbose_name_plural = 'Пользователи FastAPI'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class FastAPIRestaurant(models.Model):
    """Модель для синхронизации ресторанов с FastAPI"""
    fastapi_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    working_hours = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    delivery_time = models.IntegerField(default=30)
    min_order_amount = models.FloatField(default=500.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ресторан FastAPI'
        verbose_name_plural = 'Рестораны FastAPI'

    def __str__(self):
        return self.name


class FastAPIOrder(models.Model):
    """Модель для синхронизации заказов с FastAPI"""
    fastapi_id = models.IntegerField(unique=True)
    user = models.ForeignKey(FastAPIUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(FastAPIRestaurant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтвержден'),
        ('preparing', 'Готовится'),
        ('ready', 'Готов'),
        ('in_delivery', 'В доставке'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ])
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает'),
        ('paid', 'Оплачен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возвращен'),
    ])
    subtotal = models.FloatField()
    delivery_fee = models.FloatField(default=200.0)
    total = models.FloatField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ FastAPI'
        verbose_name_plural = 'Заказы FastAPI'

    def __str__(self):
        return f"Заказ #{self.fastapi_id} - {self.user.first_name} {self.user.last_name}"


class FastAPIDelivery(models.Model):
    """Модель для синхронизации доставок с FastAPI"""
    fastapi_id = models.IntegerField(unique=True)
    order = models.ForeignKey(FastAPIOrder, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(FastAPIUser, on_delete=models.CASCADE, related_name='deliveries')
    status = models.CharField(max_length=20, choices=[
        ('assigned', 'Назначена'),
        ('picked_up', 'Получена'),
        ('delivered', 'Доставлена'),
    ])
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Доставка FastAPI'
        verbose_name_plural = 'Доставки FastAPI'

    def __str__(self):
        return f"Доставка #{self.fastapi_id} - {self.delivery_person.first_name} {self.delivery_person.last_name}"


class SystemLog(models.Model):
    """Модель для логирования действий в системе"""
    LEVEL_CHOICES = [
        ('info', 'Информация'),
        ('warning', 'Предупреждение'),
        ('error', 'Ошибка'),
        ('debug', 'Отладка'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Лог системы'
        verbose_name_plural = 'Логи системы'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.level}: {self.message[:50]}"
