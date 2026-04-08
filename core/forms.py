from django import forms

from .models import Client, Order

BASE_INPUT = "w-full p-2 rounded bg-white text-black border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
BASE_SELECT = BASE_INPUT
BASE_TEXTAREA = "w-full p-2 rounded bg-white text-black border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "phone", "address", "city", "notes"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "w-full p-2 rounded bg-white text-black"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "w-full p-2 rounded bg-white text-black"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "w-full p-2 rounded bg-white text-black"}
            ),
            "address": forms.TextInput(
                attrs={"class": "w-full p-2 rounded bg-white text-black"}
            ),
            "city": forms.TextInput(
                attrs={"class": "w-full p-2 rounded bg-white text-black"}
            ),
            "notes": forms.Textarea(
                attrs={"rows": 4, "class": "w-full p-2 rounded bg-white text-black"}
            ),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "client",
            "assigned_to",
            "order_type",
            "status",
            "date",
            "time",
            "description",
            "is_paid",
        ]
        widgets = {
            "client": forms.Select(attrs={"class": BASE_SELECT}),
            "assigned_to": forms.Select(attrs={"class": BASE_SELECT}),
            "order_type": forms.Select(attrs={"class": BASE_SELECT}),
            "status": forms.Select(attrs={"class": BASE_SELECT}),
            "date": forms.DateInput(attrs={"type": "date", "class": BASE_INPUT}),
            "time": forms.TimeInput(attrs={"type": "time", "class": BASE_INPUT}),
            "description": forms.Textarea(attrs={"rows": 4, "class": BASE_TEXTAREA}),
            "is_paid": forms.CheckboxInput(attrs={"class": "h-5 w-5"}),
        }
