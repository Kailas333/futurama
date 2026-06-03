from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import FastAPISyncService
from .models import SystemLog
import json


@login_required
def sync_data(request):
    """Синхронизация данных с FastAPI"""
    if request.method == 'POST':
        sync_service = FastAPISyncService()
        sync_type = request.POST.get('type', 'all')
        
        success = False
        if sync_type == 'users':
            success = sync_service.sync_users()
        elif sync_type == 'restaurants':
            success = sync_service.sync_restaurants()
        elif sync_type == 'orders':
            success = sync_service.sync_orders()
        elif sync_type == 'deliveries':
            success = sync_service.sync_deliveries()
        else:
            success = sync_service.sync_all()
        
        return JsonResponse({
            'success': success,
            'message': 'Синхронизация завершена' if success else 'Ошибка синхронизации'
        })
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


@login_required
def system_stats(request):
    """Получение статистики системы"""
    sync_service = FastAPISyncService()
    stats = sync_service.get_system_stats()
    
    # Добавляем локальную статистику
    from .models import FastAPIUser, FastAPIRestaurant, FastAPIOrder, FastAPIDelivery
    
    local_stats = {
        'users_count': FastAPIUser.objects.count(),
        'restaurants_count': FastAPIRestaurant.objects.count(),
        'orders_count': FastAPIOrder.objects.count(),
        'deliveries_count': FastAPIDelivery.objects.count(),
        'logs_count': SystemLog.objects.count(),
    }
    
    return JsonResponse({
        'fastapi_stats': stats,
        'local_stats': local_stats
    })


@login_required
def system_logs(request):
    """Получение логов системы"""
    logs = SystemLog.objects.all().order_by('-timestamp')[:100]
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'timestamp': log.timestamp.isoformat(),
            'level': log.level,
            'message': log.message,
            'user': log.user.username if log.user else None,
            'ip_address': log.ip_address
        })
    
    return JsonResponse({
        'logs': logs_data,
        'total': SystemLog.objects.count()
    })


def index(request):
    """Главная страница админ панели"""
    return render(request, 'index.html')


def test_runner(request):
    """Страница для запуска тестов"""
    return render(request, 'test-runner.html')


def reports(request):
    """Страница отчетности"""
    return render(request, 'reports.html')
