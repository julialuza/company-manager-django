import requests
from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    first_name = models.CharField("Imię", max_length=100)
    last_name = models.CharField("Nazwisko", max_length=150)
    phone = models.CharField("Telefon", max_length=30, blank=True)
    address = models.CharField("Adres", max_length=255, blank=True)
    city = models.CharField("Miasto", max_length=120, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    notes = models.TextField("Notatki", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # pobierz współrzędne tylko jeśli mamy adres i miasto
        if (self.address and self.city) and (self.lat is None or self.lng is None):
            full_address = f"{self.address}, {self.city}, Poland"
            url = f"https://nominatim.openstreetmap.org/search?q={full_address}&format=json"

            try:
                response = requests.get(url, headers={"User-Agent": "Django-App"})
                data = response.json()
                if data:
                    self.lat = float(data[0]["lat"])
                    self.lng = float(data[0]["lon"])
            except Exception as e:
                print("Błąd geokodowania:", e)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    ORDER_TYPES = [
        ("montaz", "Montaż"),
        ("serwis", "Serwis"),
        ("awaria", "Awaria"),
        ("przeglad", "Przegląd"),
        ("inne", "Inne"),
    ]

    STATUS_CHOICES = [
        ("new", "Nowe"),
        ("in_progress", "W trakcie"),
        ("done", "Zakończone"),
        ("cancelled", "Anulowane"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    order_type = models.CharField(max_length=50, choices=ORDER_TYPES, default="inne")

    date = models.DateField()
    time = models.TimeField(blank=True, null=True)

    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    is_paid = models.BooleanField("Opłacone", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} – {self.get_order_type_display()} ({self.date})"
