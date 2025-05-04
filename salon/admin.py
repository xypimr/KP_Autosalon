from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Customer, Car, Sale, Service, AccessLog

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    pass

admin.site.register(Customer)
admin.site.register(Car)
admin.site.register(Sale)
admin.site.register(Service)
admin.site.register(AccessLog)
