from django.urls import path

from .views import (
    ClientDetailView,
    ClientsListView,
    OrderDetailView,
    OrdersListView,
    calendar_view,
    client_add,
    client_delete,
    client_edit,
    dashboard,
    order_add,
    order_delete,
    order_edit,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("zlecenia/", OrdersListView.as_view(), name="orders_list"),
    path("zlecenia/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("zlecenia/dodaj/", order_add, name="order_add"),
    path("zlecenia/<int:pk>/edytuj/", order_edit, name="order_edit"),
    path("zlecenia/<int:pk>/usun/", order_delete, name="order_delete"),
    path("klienci/", ClientsListView.as_view(), name="clients_list"),
    path("klienci/dodaj/", client_add, name="client_add"),
    path("klienci/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("klienci/<int:pk>/edytuj/", client_edit, name="client_edit"),
    path("klienci/<int:pk>/usun/", client_delete, name="client_delete"),
    path("kalendarz/", calendar_view, name="calendar_view"),
]
