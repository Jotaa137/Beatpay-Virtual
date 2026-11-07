from django.urls import path
from . import views

# Se usan las mismas rutas  de Fase 1 para no tocar los templates.
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('panel', views.panel, name='panel'),
    path('panel/usuario/<int:user_id>', views.usuario_detalle, name='usuario_detalle'),
    path('panel/clientes', views.panel_clientes, name='panel_clientes'),
    path('panel/clientes/nuevo', views.cliente_form, name='cliente_nuevo'),
    path('panel/clientes/<int:cliente_id>/editar', views.cliente_form, name='cliente_editar'),
    path('panel/clientes/<int:cliente_id>/estado', views.cliente_estado, name='cliente_estado'),
    path('panel/bancos', views.panel_bancos, name='panel_bancos'),
    path('panel/bancos/nuevo', views.banco_form, name='banco_nuevo'),
    path('panel/bancos/<int:banco_id>/editar', views.banco_form, name='banco_editar'),
    path('panel/bancos/<int:banco_id>/estado', views.banco_estado, name='banco_estado'),
    path('panel/tarjetas', views.panel_tarjetas, name='panel_tarjetas'),
    path('panel/tarjetas/nuevo', views.tarjeta_form, name='tarjeta_nuevo'),
    path('panel/tarjetas/<int:tarjeta_id>/editar', views.tarjeta_form, name='tarjeta_editar'),
    path('panel/tarjetas/<int:tarjeta_id>/estado', views.tarjeta_estado, name='tarjeta_estado'),
    path('panel/instrumentos', views.panel_instrumentos, name='panel_instrumentos'),
    path('panel/instrumentos/nuevo', views.instrumento_form, name='instrumento_nuevo'),
    path('panel/instrumentos/<int:instrumento_id>/editar', views.instrumento_form, name='instrumento_editar'),
    path('panel/instrumentos/<int:instrumento_id>/estado', views.instrumento_estado, name='instrumento_estado'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('cargar', views.cargar, name='cargar'),
    path('pagar', views.pagar, name='pagar'),
    path('transacciones', views.transacciones, name='transacciones'),
    path('tarjeta', views.tarjeta, name='tarjeta'),
]
