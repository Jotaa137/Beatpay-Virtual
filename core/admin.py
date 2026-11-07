from django.contrib import admin

from .models import (
    Auditoria,
    Banco,
    Cliente,
    Cuenta,
    InstrumentoFinanciero,
    Movimiento,
    Tarjeta,
    Transaccion,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rut', 'email', 'telefono', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'apellido', 'rut', 'email')


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'es_interno', 'activo')
    list_filter = ('es_interno', 'activo')
    search_fields = ('nombre', 'codigo')


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('user', 'presupuesto', 'solicitud_cupo')
    search_fields = ('user__username',)


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'numero', 'banco', 'estado', 'tipo', 'saldo')
    list_filter = ('estado', 'tipo', 'banco')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__rut', 'numero')


@admin.register(InstrumentoFinanciero)
class InstrumentoFinancieroAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'tipo', 'banco', 'tarjeta', 'titular', 'activo')
    list_filter = ('tipo', 'banco', 'activo')
    search_fields = ('uuid', 'titular', 'alias', 'tarjeta__numero')


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'origen', 'destino', 'monto', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('origen__uuid', 'destino__uuid', 'descripcion')
    date_hierarchy = 'fecha'


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
