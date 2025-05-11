#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from datetime import datetime, timedelta

# 1. Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autosalon_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from salon.models import Customer, Car, Service, Sale, Part, ServicePart

fake = Faker('ru_RU')
User = get_user_model()

def clear_demo_data():
    """Удаляет все демонстрационные данные, кроме суперпользователей."""
    ServicePart.objects.all().delete()
    Service.objects.all().delete()
    Sale.objects.all().delete()
    Customer.objects.all().delete()
    Car.objects.all().delete()
    Part.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

def create_demo_staff():
    """Создаёт 5 продавцов и 5 менеджеров с соответствующими правами."""
    staff_members = []
    # Продавцы
    for idx in range(1, 6):
        user = User.objects.create_user(
            username=f'seller_{idx}',
            password='pass1234',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            position='Продавец'
        )
        staff_members.append(user)
    # Менеджеры с правом видеть все продажи и сервисы
    perm_sales = 'salon.view_all_sales'
    perm_services = 'salon.view_all_services'
    for idx in range(1, 6):
        user = User.objects.create_user(
            username=f'manager_{idx}',
            password='pass1234',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            position='Менеджер'
        )
        # Назначаем пермишены менеджеру
        user.user_permissions.add(
            *[perm for perm in user._meta.permissions
               if perm.codename in (perm_sales, perm_services)]
        )
        staff_members.append(user)
    return staff_members

def generate_customers(count=10):
    """Создаёт указанное число клиентов."""
    customers = []
    for _ in range(count):
        customers.append(Customer.objects.create(
            full_name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number()
        ))
    return customers

# Списки для более реалистичных названий
CAR_MAKES_MODELS = {
    'Toyota': ['Corolla', 'Camry', 'RAV4', 'Prius', 'Highlander'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Fit', 'Pilot'],
    'Ford': ['Focus', 'Fusion', 'Escape', 'Mustang', 'Explorer'],
    'BMW': ['3 Series', '5 Series', 'X3', 'X5', '1 Series'],
    'Audi': ['A3', 'A4', 'Q5', 'Q7', 'A6'],
}

PART_NAMES = [
    'Масляный фильтр',
    'Воздушный фильтр',
    'Топливный фильтр',
    'Салонный фильтр',
    'Тормозные колодки',
    'Свеча зажигания',
    'Ремень ГРМ',
    'Ремень генератора',
    'Щётки стеклоочистителя',
    'Амортизатор',
    'Радиатор охлаждения',
    'Насос охлаждающей жидкости',
    'Фара передняя',
    'Фонарь задний',
    'Трос ручного тормоза',
]

def generate_vehicles(count=10):
    """Создаёт count автомобилей из реальных марок и моделей."""
    vehicles = []
    makes = list(CAR_MAKES_MODELS.keys())
    for _ in range(count):
        make = random.choice(makes)
        model = random.choice(CAR_MAKES_MODELS[make])
        year = random.randint(2010, 2025)
        vin = fake.unique.bothify(text='?1?2?-?????-??????')
        price = round(random.uniform(150000, 6000000), 10)
        car = Car.objects.create(
            vin=vin,
            make=make,
            model=model,
            year=year,
            price=price,
            is_available=True
        )
        vehicles.append(car)
    return vehicles

def generate_parts(count=10):
    """Создаёт count запчастей с реалистичными наименованиями."""
    parts = []
    used = set()
    for _ in range(count):
        # Из списка PART_NAMES выберем случайный неиспользованный
        name = random.choice([p for p in PART_NAMES if p not in used])
        used.add(name)
        part_number = fake.unique.bothify(text='PN-####-??').upper()
        cost = round(random.uniform(200, 5000), 2)
        stock = random.randint(1, 100)
        part = Part.objects.create(
            part_number=part_number,
            name=name,
            cost=cost,
            stock=stock
        )
        parts.append(part)
    return parts

def random_past_date():
    """Возвращает случайную дату в последние 365 дней."""
    return datetime.now() - timedelta(days=random.randint(0, 365))

def generate_sales(customers, vehicles, staff, count=10):
    """Создаёт указанный число продаж, обновляя доступность авто."""
    sales = []
    for _ in range(count):
        buyer = random.choice(customers)
        available_cars = [v for v in vehicles if v.is_available]
        if not available_cars:
            break
        car = random.choice(available_cars)
        salesperson = random.choice(staff)
        sale = Sale.objects.create(
            customer=buyer,
            car=car,
            employee=salesperson,
            sale_date=random_past_date(),
            amount=car.price
        )
        car.is_available = False
        car.save()
        sales.append(sale)
    return sales

def generate_service_orders(customers, vehicles, staff, count=10):
    """Создаёт указанное число сервисных заказов."""
    services = []
    for _ in range(count):
        order = Service.objects.create(
            customer=random.choice(customers),
            car=random.choice(vehicles),
            employee=random.choice(staff),
            description=fake.sentence(nb_words=6),
            cost=round(random.uniform(200, 1500), 2),
            service_date=random_past_date()
        )
        services.append(order)
    return services

def link_parts_to_services(service_orders, parts):
    """Назначает по одной запчасти к каждому сервисному заказу."""
    for order in service_orders:
        chosen_part = random.choice(parts)
        quantity = random.randint(1, 5)
        ServicePart.objects.create(
            service=order,
            part=chosen_part,
            quantity=quantity
        )

if __name__ == '__main__':
    clear_demo_data()
    staff_list = create_demo_staff()
    customer_list = generate_customers()
    vehicle_list = generate_vehicles()
    parts_list = generate_parts()
    sales_list = generate_sales(customer_list, vehicle_list, staff_list)
    service_orders = generate_service_orders(customer_list, vehicle_list, staff_list)
    link_parts_to_services(service_orders, parts_list)

    print("✅ Демонстрационные данные добавлены:")
    print(f"  • Сотрудников:       {len(staff_list)}")
    print(f"  • Клиентов:          {len(customer_list)}")
    print(f"  • Автомобилей:       {len(vehicle_list)}")
    print(f"  • Запчастей:         {len(parts_list)}")
    print(f"  • Продаж:            {len(sales_list)}")
    print(f"  • Сервисных заказов: {len(service_orders)}")
    print("  • ServicePart:       по одной запчасти на заказ")
