from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Customer, Car, Sale, Service

# 1.1. Клиенты
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'salon/customer_list.html'
    context_object_name = 'customers'

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'salon/customer_detail.html'
    context_object_name = 'customer'

class CustomerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Customer
    fields = ['full_name', 'email', 'phone', 'passport_number']
    template_name = 'salon/customer_form.html'
    success_url = reverse_lazy('customer_list')
    permission_required = 'salon.add_customer'

class CustomerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Customer
    fields = ['full_name', 'email', 'phone', 'passport_number']
    template_name = 'salon/customer_form.html'
    success_url = reverse_lazy('customer_list')
    permission_required = 'salon.change_customer'

class CustomerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Customer
    template_name = 'salon/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')
    permission_required = 'salon.delete_customer'


# 1.2. Автомобили
class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'salon/car_list.html'
    context_object_name = 'cars'

class CarDetailView(LoginRequiredMixin, DetailView):
    model = Car
    template_name = 'salon/car_detail.html'
    context_object_name = 'car'

class CarCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Car
    fields = ['vin', 'make', 'model', 'year', 'price', 'is_available']
    template_name = 'salon/car_form.html'
    success_url = reverse_lazy('car_list')
    permission_required = 'salon.add_car'

class CarUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Car
    fields = ['vin', 'make', 'model', 'year', 'price', 'is_available']
    template_name = 'salon/car_form.html'
    success_url = reverse_lazy('car_list')
    permission_required = 'salon.change_car'

class CarDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Car
    template_name = 'salon/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
    permission_required = 'salon.delete_car'


# 1.3. Продажи
class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'salon/sale_list.html'
    context_object_name = 'sales'

    def get_queryset(self):
        qs = super().get_queryset()
        # если нет права просмотра всех продаж — показываем только свои
        if not self.request.user.has_perm('salon.view_all_sales'):
            return qs.filter(employee=self.request.user)
        return qs

class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'salon/sale_detail.html'
    context_object_name = 'sale'

class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Sale
    fields = ['customer', 'car', 'amount']
    template_name = 'salon/sale_form.html'
    success_url = reverse_lazy('sale_list')
    permission_required = 'salon.add_sale'

    def form_valid(self, form):
        form.instance.employee = self.request.user
        return super().form_valid(form)

class SaleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Sale
    fields = ['customer', 'car', 'amount']
    template_name = 'salon/sale_form.html'
    success_url = reverse_lazy('sale_list')
    permission_required = 'salon.change_sale'

class SaleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Sale
    template_name = 'salon/sale_confirm_delete.html'
    success_url = reverse_lazy('sale_list')
    permission_required = 'salon.delete_sale'


# 1.4. Сервисные заказы
class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'salon/service_list.html'
    context_object_name = 'services'

class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'salon/service_detail.html'
    context_object_name = 'service'

class ServiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Service
    fields = ['car', 'customer', 'description', 'cost']
    template_name = 'salon/service_form.html'
    success_url = reverse_lazy('service_list')
    permission_required = 'salon.add_service'

class ServiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Service
    fields = ['car', 'customer', 'description', 'cost']
    template_name = 'salon/service_form.html'
    success_url = reverse_lazy('service_list')
    permission_required = 'salon.change_service'

class ServiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Service
    template_name = 'salon/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')
    permission_required = 'salon.delete_service'


from django.shortcuts import render

def home(request):
    return render(request, 'salon/home.html')

