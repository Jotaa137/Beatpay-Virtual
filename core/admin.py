from django.contrib import admin

from .models import Auditoria, Cuenta, Tarjeta, Transaccion


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('user', 'saldo', 'presupuesto', 'solicitud_cupo')
    search_fields = ('user__username',)


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'numero', 'estado', 'tipo')
    list_filter = ('estado', 'tipo')
    search_fields = ('cuenta__user__username', 'numero')


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('folio', 'cuenta', 'evento', 'monto', 'tipo', 'estado', 'fecha')
    list_filter = ('tipo', 'estado')
    search_fields = ('folio', 'evento', 'cuenta__user__username')
    date_hierarchy = 'fecha'


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'detalle')
    list_filter = ('accion', 'fecha')
    search_fields = ('usuario', 'accion', 'detalle')
    date_hierarchy = 'fecha'
