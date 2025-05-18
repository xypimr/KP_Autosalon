from django.urls import path
from . import views
from .views import home, PartListView, PartCreateView, PartUpdateView, PartDetailView, PartDeleteView, backup_db_view, \
    download_latest_backup

urlpatterns = [
    path('', home, name='home'),
    # Клиенты
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer_add'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),

    # Автомобили
    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/add/', views.CarCreateView.as_view(), name='car_add'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),

    # Продажи
    path('sales/', views.SaleListView.as_view(), name='sale_list'),
    path('sales/add/', views.SaleCreateView.as_view(), name='sale_add'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sales/<int:pk>/edit/', views.SaleUpdateView.as_view(), name='sale_edit'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),

    # Сервисные заказы
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),

    path('parts/', PartListView.as_view(), name='part_list'),
    path('parts/add/', PartCreateView.as_view(), name='part_add'),
    path('parts/<int:pk>/', PartDetailView.as_view(), name='part_detail'),
    path('parts/<int:pk>/edit/', PartUpdateView.as_view(), name='part_edit'),
    path('parts/<int:pk>/delete/', PartDeleteView.as_view(), name='part_delete'),

    path('backup-db/', backup_db_view, name='backup_db'),
    path('backup-db/download/', download_latest_backup, name='download_latest_backup'),

]
