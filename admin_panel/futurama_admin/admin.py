from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import FastAPIUser, FastAPIRestaurant, FastAPIOrder, FastAPIDelivery, SystemLog


@admin.register(FastAPIUser)
class FastAPIUserAdmin(admin.ModelAdmin):
    list_display = ['fastapi_id', 'first_name', 'last_name', 'email', 'phone', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['fastapi_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('fastapi_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Статус', {
            'fields': ('role', 'is_active')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False  # Запрещаем создание через админку, только через FastAPI


@admin.register(FastAPIRestaurant)
class FastAPIRestaurantAdmin(admin.ModelAdmin):
    list_display = ['fastapi_id', 'name', 'address', 'phone', 'rating', 'is_active', 'delivery_time']
    list_filter = ['is_active', 'rating', 'delivery_time', 'created_at']
    search_fields = ['name', 'address', 'phone', 'email']
    readonly_fields = ['fastapi_id', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('fastapi_id', 'name', 'description', 'address', 'phone', 'email')
        }),
        ('Настройки', {
            'fields': ('working_hours', 'rating', 'delivery_time', 'min_order_amount', 'is_active')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(FastAPIOrder)
class FastAPIOrderAdmin(admin.ModelAdmin):
    list_display = ['fastapi_id', 'user_info', 'restaurant', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'restaurant']
    search_fields = ['fastapi_id', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['fastapi_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('fastapi_id', 'user', 'restaurant', 'status', 'payment_status')
        }),
        ('Финансы', {
            'fields': ('subtotal', 'delivery_fee', 'total')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.email})"
    user_info.short_description = 'Пользователь'

    def has_add_permission(self, request):
        return False


@admin.register(FastAPIDelivery)
class FastAPIDeliveryAdmin(admin.ModelAdmin):
    list_display = ['fastapi_id', 'order_info', 'delivery_person_info', 'status', 'pickup_time', 'delivery_time']
    list_filter = ['status', 'created_at', 'delivery_person__role']
    search_fields = ['fastapi_id', 'delivery_person__first_name', 'delivery_person__last_name']
    readonly_fields = ['fastapi_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('fastapi_id', 'order', 'delivery_person', 'status')
        }),
        ('Время', {
            'fields': ('pickup_time', 'delivery_time')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_info(self, obj):
        return f"Заказ #{obj.order.fastapi_id} - {obj.order.user.first_name} {obj.order.user.last_name}"
    order_info.short_description = 'Заказ'

    def delivery_person_info(self, obj):
        return f"{obj.delivery_person.first_name} {obj.delivery_person.last_name} ({obj.delivery_person.phone})"
    delivery_person_info.short_description = 'Курьер'

    def has_add_permission(self, request):
        return False


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'message_short', 'user', 'ip_address']
    list_filter = ['level', 'timestamp', 'user']
    search_fields = ['message', 'user__username', 'ip_address']
    readonly_fields = ['timestamp', 'level', 'message', 'user', 'ip_address', 'user_agent']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('timestamp', 'level', 'message')
        }),
        ('Пользователь', {
            'fields': ('user', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

    def message_short(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Сообщение'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Кастомизация админ панели
admin.site.site_header = "Футурама - Админ панель"
admin.site.site_title = "Футурама Админ"
admin.site.index_title = "Управление системой доставки еды"
