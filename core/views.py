from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import localdate
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import ClientForm, OrderForm
from .models import Client, Order


class OrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "core/orders_list.html"
    context_object_name = "orders"
    ordering = ["-date", "-time"]

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.request.user.is_superuser:
            qs = qs.filter(assigned_to=self.request.user)

        status = self.request.GET.get("status")
        if status and status != "all":
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_status"] = self.request.GET.get("status", "all")
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(assigned_to=self.request.user)


class ClientsListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "core/clients_list.html"
    context_object_name = "clients"
    paginate_by = 20

    # mapowanie dozwolonych pól sortowania (bezpieczne)
    SORT_MAP = {
        "first_name": "first_name",
        "last_name": "last_name",
        "phone": "phone",
        "city": "city",
        "address": "address",
        "created": "-created_at",
    }

    def get_queryset(self):
        qs = super().get_queryset()

        # --- WYSZUKIWANIE ---
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(phone__icontains=q)
                | Q(city__icontains=q)
                | Q(address__icontains=q)
            )

        # --- SORTOWANIE ---
        sort = self.request.GET.get("sort", "last_name")
        direction = self.request.GET.get("dir", "asc")

        order_field = self.SORT_MAP.get(sort, "last_name")
        if direction == "desc" and not order_field.startswith("-"):
            order_field = "-" + order_field
        if direction == "asc" and order_field.startswith("-"):
            order_field = order_field.lstrip("-")

        return qs.order_by(order_field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["sort"] = self.request.GET.get("sort", "last_name")
        context["dir"] = self.request.GET.get("dir", "asc")
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "core/client_detail.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context["orders"] = Order.objects.filter(client=client)
        return context


def color_for_user(user_id: int) -> str:
    colors = [
        "#3b82f6",  # blue
        "#a855f7",  # purple
        "#06b6d4",  # cyan
        "#ec4899",  # pink
        "#22c55e",  # green
        "#ef4444",  # red
        "#f59e0b",  # amber
    ]
    return colors[user_id % len(colors)]


@login_required
def dashboard(request):
    today = localdate()
    tomorrow = today + timedelta(days=1)

    orders_today = Order.objects.filter(date=today)
    orders_tomorrow = Order.objects.filter(date=tomorrow)
    orders_week = Order.objects.filter(
        date__gte=today, date__lte=today + timedelta(days=7)
    )

    if not request.user.is_superuser:
        orders_today = orders_today.filter(assigned_to=request.user)
        orders_tomorrow = orders_tomorrow.filter(assigned_to=request.user)
        orders_week = orders_week.filter(assigned_to=request.user)

    calendar_events = [
        {
            "title": f"{order.client.first_name} {order.client.last_name}"
            + (
                f" ({order.assigned_to.username})"
                if request.user.is_superuser and order.assigned_to
                else ""
            ),
            "start": f"{order.date}T{order.time}" if order.time else str(order.date),
            "backgroundColor": color_for_user(order.assigned_to_id)
            if order.assigned_to
            else "#64748b",
            "borderColor": "transparent",
        }
        for order in orders_week
    ]

    markers = [
        {
            "id": order.id,
            "client": f"{order.client.first_name} {order.client.last_name}",
            "lat": order.client.lat,
            "lng": order.client.lng,
        }
        for order in orders_today
        if order.client.lat and order.client.lng
    ]

    markers_tomorrow = [
        {
            "id": o.id,
            "client": f"{o.client.first_name} {o.client.last_name}",
            "lat": o.client.lat,
            "lng": o.client.lng,
        }
        for o in orders_tomorrow
        if o.client.lat and o.client.lng
    ]

    context = {
        "orders_today": orders_today,
        "orders_tomorrow": orders_tomorrow,
        "calendar_events": calendar_events,
        "markers": markers,
        "markers_tomorrow": markers_tomorrow,
    }

    return render(request, "core/dashboard.html", context)


@login_required
def order_add(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("orders_list")
    else:
        form = OrderForm()

    return render(
        request, "core/order_form.html", {"form": form, "title": "Dodaj zlecenie"}
    )


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("order_detail", pk=pk)
    else:
        form = OrderForm(instance=order)

    return render(
        request, "core/order_form.html", {"form": form, "title": "Edytuj zlecenie"}
    )


@login_required
@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect("orders_list")


@login_required
def client_add(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clients_list")
    else:
        form = ClientForm()

    return render(
        request, "core/client_form.html", {"form": form, "title": "Dodaj klienta"}
    )


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("client_detail", pk=pk)
    else:
        form = ClientForm(instance=client)

    return render(
        request, "core/client_form.html", {"form": form, "title": "Edytuj klienta"}
    )


@login_required
@require_POST
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect("clients_list")


@login_required
def calendar_view(request):
    today = localdate()
    mode = request.GET.get("mode", "week")
    date_str = request.GET.get("date")

    base_date = date.fromisoformat(date_str) if date_str else today

    if mode == "week":
        start = today
        end = today + timedelta(days=7)

    elif mode == "next_week":
        start = today + timedelta(days=7)
        end = start + timedelta(days=7)

    elif mode == "month":
        start = today.replace(day=1)
        year = start.year + (1 if start.month == 12 else 0)
        month = 1 if start.month == 12 else (start.month + 1)
        end = date(year, month, 1)

    elif mode == "custom_week":
        start = base_date
        end = base_date + timedelta(days=7)

    elif mode == "custom_month":
        start = base_date.replace(day=1)
        year = start.year + (1 if start.month == 12 else 0)
        month = 1 if start.month == 12 else (start.month + 1)
        end = date(year, month, 1)

    else:
        start = today
        end = today + timedelta(days=7)

    orders = Order.objects.filter(date__gte=start, date__lt=end)

    if not request.user.is_superuser:
        orders = orders.filter(assigned_to=request.user)

    calendar_events = [
        {
            "title": f"{o.client.first_name} {o.client.last_name}"
            + (
                f" ({o.assigned_to.username})"
                if request.user.is_superuser and o.assigned_to
                else ""
            ),
            "start": f"{o.date}T{o.time}" if o.time else str(o.date),
            "url": reverse("order_detail", args=[o.pk]),
            "backgroundColor": color_for_user(o.assigned_to_id)
            if o.assigned_to
            else "#64748b",
            "borderColor": "transparent",
        }
        for o in orders
    ]

    context = {
        "calendar_events": calendar_events,
        "mode": mode,
        "selected_date": date_str or "",
        "start": start,
        "end": end,
    }

    return render(request, "core/calendar_view.html", context)
