from django.urls import path
from . import views

app_name = 'futurama_admin'

urlpatterns = [
    path('sync/', views.sync_data, name='sync_data'),
    path('stats/', views.system_stats, name='system_stats'),
    path('logs/', views.system_logs, name='system_logs'),
    path('reports/', views.reports, name='reports'),
]




