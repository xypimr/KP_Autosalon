from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Employee, Customer, Car, Sale, Service, AccessLog,
    Part, ServicePart
)

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone')
    search_fields = ('full_name', 'email', 'phone')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('vin', 'make', 'model', 'year', 'price', 'is_available')
    search_fields = ('vin', 'make', 'model')
    list_filter = ('is_available', 'year')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'customer', 'employee', 'sale_date', 'amount')
    search_fields = ('customer__full_name', 'car__vin', 'employee__username')
    list_filter = ('sale_date',)
    autocomplete_fields = ('car', 'customer', 'employee')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'customer', 'employee', 'service_date', 'cost')
    search_fields = (
        'customer__full_name',
        'car__vin',
        'employee__username'
    )
    list_filter = ('service_date',)
    autocomplete_fields = ('car', 'customer', 'employee')

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'ip_address', 'path', 'method', 'status_code')
    search_fields = ('user__username', 'ip_address', 'path')
    list_filter = ('method', 'status_code')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'name', 'cost', 'stock')
    search_fields = ('part_number', 'name')

@admin.register(ServicePart)
class ServicePartAdmin(admin.ModelAdmin):
    list_display = ('service', 'part', 'quantity')
    search_fields = (
        'service__id',
        'part__part_number',
    )
    autocomplete_fields = ('service', 'part')
