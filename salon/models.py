from django.db import models
from django.contrib.auth.models import AbstractUser
from encrypted_model_fields.fields import EncryptedCharField

# Если нужно расширить стандартного пользователя:
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from encrypted_model_fields.fields import EncryptedCharField

from autosalon_project import settings


class Employee(AbstractUser):
    position = models.CharField('Должность', max_length=100)
    phone = models.CharField('Контактный телефон', max_length=20)

    # Переопределяем, чтобы не было конфликта reverse accessor
    groups = models.ManyToManyField(
        Group,
        verbose_name='Группы',
        blank=True,
        help_text='Группы, к которым принадлежит пользователь',
        related_name='employee_set',  # уникальное имя для обратной связи
        related_query_name='employee',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='Права пользователя',
        blank=True,
        help_text='Дополнительные права для конкретного пользователя',
        related_name='employee_permission_set',
        related_query_name='employee_permission',
    )

    def __str__(self):
        return f'{self.get_full_name()} ({self.position})'


class Customer(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20)
    # Защитим паспортные данные или VIN-код специальным полем
    passport_number = EncryptedCharField('№ паспорта', max_length=50, null=True, blank=True)

    def __str__(self):
        return self.full_name

class Car(models.Model):
    vin = EncryptedCharField('VIN', max_length=17, unique=True)
    make = models.CharField('Марка', max_length=50)
    model = models.CharField('Модель', max_length=50)
    year = models.PositiveSmallIntegerField('Год выпуска')
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2)
    is_available = models.BooleanField('В наличии', default=True)

    def __str__(self):
        return f'{self.make} {self.model} ({self.vin})'

class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales')
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='sales')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='sales')
    sale_date = models.DateTimeField('Дата продажи', auto_now_add=True)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)

    class Meta:
        permissions = [
            ("view_all_sales", "Can view all sales"),
            ("edit_sale", "Can edit sale records"),
        ]

    def __str__(self):
        return f'Продажа {self.car} клиенту {self.customer}'

class Service(models.Model):
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='services')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='services')
    description = models.TextField('Описание работ')
    cost = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)
    service_date = models.DateTimeField('Дата обслуживания', auto_now_add=True)

    class Meta:
        permissions = [
            ("view_all_services", "Can view all services"),
            ("edit_service", "Can edit service records"),
        ]

    def __str__(self):
        return f'Сервис {self.car} для {self.customer}'

class AccessLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    ip_address = models.GenericIPAddressField('IP-адрес')
    path = models.CharField('URL', max_length=200)
    method = models.CharField('Метод', max_length=10)
    timestamp = models.DateTimeField('Дата и время', auto_now_add=True)
    status_code = models.PositiveSmallIntegerField('Код ответа')


    def __str__(self):
        return f'{self.timestamp}: {self.user} -> {self.path} [{self.status_code}]'
