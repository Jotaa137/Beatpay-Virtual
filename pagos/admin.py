from django.contrib import admin

from .models import Cuenta


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('user', 'saldo', 'presupuesto', 'tarjeta')
    list_filter = ('tarjeta',)
    search_fields = ('user__username',)
