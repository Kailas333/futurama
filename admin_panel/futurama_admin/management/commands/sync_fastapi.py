from django.core.management.base import BaseCommand
from futurama_admin.services import FastAPISyncService


class Command(BaseCommand):
    help = 'Синхронизация данных с FastAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['users', 'restaurants', 'orders', 'deliveries', 'all'],
            default='all',
            help='Тип данных для синхронизации'
        )

    def handle(self, *args, **options):
        sync_service = FastAPISyncService()
        sync_type = options['type']

        self.stdout.write(
            self.style.SUCCESS(f'Начинаем синхронизацию: {sync_type}')
        )

        if sync_type == 'users':
            success = sync_service.sync_users()
        elif sync_type == 'restaurants':
            success = sync_service.sync_restaurants()
        elif sync_type == 'orders':
            success = sync_service.sync_orders()
        elif sync_type == 'deliveries':
            success = sync_service.sync_deliveries()
        else:  # all
            success = sync_service.sync_all()

        if success:
            self.stdout.write(
                self.style.SUCCESS('Синхронизация завершена успешно!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Синхронизация завершена с ошибками!')
            )




