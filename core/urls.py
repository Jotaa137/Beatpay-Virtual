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
    path('dashboard', views.dashboard, name='dashboard'),
    path('cargar', views.cargar, name='cargar'),
    path('pagar', views.pagar, name='pagar'),
    path('transacciones', views.transacciones, name='transacciones'),
    path('tarjeta', views.tarjeta, name='tarjeta'),
]
