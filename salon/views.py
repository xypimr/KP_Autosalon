from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .forms import ServicePartFormSet, PartForm
from .models import Customer, Car, Sale, Service, ServicePart


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

    def get_queryset(self):
        qs = super().get_queryset()
        # Если у пользователя нет права смотреть все сервисы — показываем только свои
        if not self.request.user.has_perm('salon.view_all_services'):
            return qs.filter(employee=self.request.user)
        return qs

class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'salon/service_detail.html'
    context_object_name = 'service'

# salon/views.py

class ServiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Service
    fields = ['car', 'customer', 'description', 'cost']
    template_name = 'salon/service_form.html'
    success_url = reverse_lazy('service_list')
    permission_required = 'salon.add_service'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # Для создания у нас self.object ещё не сохранён, но formset нужен пустой
        if 'formset' not in data:
            data['formset'] = ServicePartFormSet(
                instance=None,
                prefix='service_parts'
            )
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        # При POST обязательно передаём тот же prefix
        formset = ServicePartFormSet(
            request.POST,
            instance=None,
            prefix='service_parts'
        )

        if form.is_valid() and formset.is_valid():
            return self.form_valid_with_parts(form, formset)

        # Диагностика ошибок в шаблоне
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def form_valid_with_parts(self, form, formset):
        service = form.save(commit=False)
        service.employee = self.request.user
        service.save()

        # 1) Обрабатываем новые и обновлённые ServicePart
        for subform in formset:
            cd = subform.cleaned_data
            if not cd or cd.get('DELETE') or cd.get('part') is None:
                continue

            # Если подформа редактирует существующую запись — получаем старое количество
            if subform.instance.pk:
                old_sp = ServicePart.objects.get(pk=subform.instance.pk)
                old_qty = old_sp.quantity
            else:
                old_qty = 0

            # Сохраняем новую версию записи
            sp = subform.save(commit=False)
            sp.service = service
            sp.save()

            # Вычисляем изменение количества
            new_qty = sp.quantity
            delta = new_qty - old_qty

            # Если delta>0 — списываем со склада; если <0 — восстанавливаем
            Part.objects.filter(pk=sp.part_id).update(stock=F('stock') - delta)

        # 2) Удаляем те записи, которые помечены на удаление, и восстанавливаем остаток
        for del_form in formset.deleted_forms:
            old = del_form.instance
            if old.pk:
                Part.objects.filter(pk=old.part_id).update(stock=F('stock') + old.quantity)
                old.delete()

        return redirect(self.success_url)


class ServiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Service
    fields = ['car', 'customer', 'description', 'cost']
    template_name = 'salon/service_form.html'
    success_url = reverse_lazy('service_list')
    permission_required = 'salon.change_service'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # При редактировании передаём существующий instance
        if 'formset' not in data:
            data['formset'] = ServicePartFormSet(
                instance=self.object,
                prefix='service_parts'
            )
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ServicePartFormSet(
            request.POST,
            instance=self.object,
            prefix='service_parts'
        )

        if form.is_valid() and formset.is_valid():
            return self.form_valid_with_parts(form, formset)

        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def form_valid_with_parts(self, form, formset):
        service = form.save(commit=False)
        service.employee = self.request.user
        service.save()

        # 1) Обрабатываем новые и обновлённые ServicePart
        for subform in formset:
            cd = subform.cleaned_data
            if not cd or cd.get('DELETE') or cd.get('part') is None:
                continue

            # Если подформа редактирует существующую запись — получаем старое количество
            if subform.instance.pk:
                old_sp = ServicePart.objects.get(pk=subform.instance.pk)
                old_qty = old_sp.quantity
            else:
                old_qty = 0

            # Сохраняем новую версию записи
            sp = subform.save(commit=False)
            sp.service = service
            sp.save()

            # Вычисляем изменение количества
            new_qty = sp.quantity
            delta = new_qty - old_qty

            # Если delta>0 — списываем со склада; если <0 — восстанавливаем
            Part.objects.filter(pk=sp.part_id).update(stock=F('stock') - delta)

        # 2) Удаляем те записи, которые помечены на удаление, и восстанавливаем остаток
        for del_form in formset.deleted_forms:
            old = del_form.instance
            if old.pk:
                Part.objects.filter(pk=old.part_id).update(stock=F('stock') + old.quantity)
                old.delete()

        return redirect(self.success_url)


class ServiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Service
    template_name = 'salon/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')
    permission_required = 'salon.delete_service'

from .models import Part

class PartListView(LoginRequiredMixin, ListView):
    model = Part
    template_name = 'salon/part_list.html'
    context_object_name = 'parts'
    permission_required = 'salon.view_part'

class PartDetailView(LoginRequiredMixin, DetailView):
    model = Part
    template_name = 'salon/part_detail.html'
    permission_required = 'salon.view_part'

class PartCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Part
    form_class = PartForm
    template_name = 'salon/part_form.html'
    success_url = reverse_lazy('part_list')
    permission_required = 'salon.add_part'

class PartUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Part
    form_class = PartForm
    template_name = 'salon/part_form.html'
    success_url = reverse_lazy('part_list')
    permission_required = 'salon.change_part'

class PartDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Part
    template_name = 'salon/part_confirm_delete.html'
    success_url = reverse_lazy('part_list')
    permission_required = 'salon.delete_part'


from django.shortcuts import render, redirect


def home(request):
    return render(request, 'salon/home.html')

