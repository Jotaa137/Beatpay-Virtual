from django.contrib import admin

from .models import Auditoria, Cuenta


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('user', 'saldo', 'presupuesto', 'tarjeta')
    list_filter = ('tarjeta',)
    search_fields = ('user__username',)


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'detalle')
    list_filter = ('accion',)
    search_fields = ('usuario',)
