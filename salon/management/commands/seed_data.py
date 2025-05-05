# salon/management/commands/seed_data.py

import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from salon.models import Customer, Car, Sale, Service

User = get_user_model()

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для демонстрации'

    def handle(self, *args, **options):
        # Очищаем старые данные (по желанию)
        Service.objects.all().delete()
        Sale.objects.all().delete()
        Car.objects.all().delete()
        Customer.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # 1) Сотрудники
        self.stdout.write('Создаём сотрудников...')
        seller = User.objects.create_user(
            username='seller',
            password='password123',
            position='Продавец',
            first_name='Иван',
            last_name='Петров',
            email='seller@autosalon.test'
        )
        manager = User.objects.create_user(
            username='manager',
            password='password123',
            position='Менеджер',
            first_name='Ольга',
            last_name='Сидорова',
            email='manager@autosalon.test'
        )
        # Дадим менеджеру право видеть все продажи:
        perm = 'salon.view_all_sales'
        if not manager.has_perm(perm):
            manager.user_permissions.add(
                *[p for p in manager._meta.permissions if p[0] == perm]
            )

        # 2) Клиенты
        self.stdout.write('Создаём клиентов...')
        customers = []
        for name, email in [
            ('Алексей Смирнов', 'alexei@client.test'),
            ('Мария Иванова', 'maria@client.test'),
            ('Дмитрий Кузнецов', 'dmitry@client.test'),
        ]:
            customers.append(
                Customer.objects.create(
                    full_name=name,
                    email=email,
                    phone=f'+7{random.randrange(9000000000,9999999999)}'
                )
            )

        # 3) Автомобили
        self.stdout.write('Создаём автомобили...')
        cars = []
        car_data = [
            ('1HGCM82633A004352', 'Honda', 'Accord', 2020, 22000),
            ('2T1BURHE5GC504321', 'Toyota', 'Corolla', 2019, 18000),
            ('WVWZZZ3BZWE689154', 'Volkswagen', 'Passat', 2021, 25000),
        ]
        for vin, make, model, year, price in car_data:
            cars.append(
                Car.objects.create(
                    vin=vin, make=make, model=model,
                    year=year, price=price, is_available=True
                )
            )

        # 4) Продажи
        self.stdout.write('Создаём записи о продажах...')
        for cust, car in zip(customers, cars):
            Sale.objects.create(
                customer=cust,
                car=car,
                employee=random.choice([seller, manager]),
                amount=car.price,
                sale_date=timezone.now()
            )
            # отмечаем автомобиль как проданный
            car.is_available = False
            car.save()

        # 5) Сервисные заказы
        self.stdout.write('Создаём сервисные заказы...')
        for cust, car in zip(customers, cars):
            Service.objects.create(
                customer=cust,
                car=car,
                description='Плановое техническое обслуживание',
                cost=round(random.uniform(200, 800), 2),
                service_date=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS('База успешно заполнена тестовыми данными.'))
