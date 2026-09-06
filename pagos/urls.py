from django.urls import path
from . import views

# Se usan las mismas rutas .html de Fase 1 para no tocar los templates.
urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    path('register.html', views.register, name='register'),
    path('login.html', views.login, name='login'),
    path('dashboard.html', views.dashboard, name='dashboard'),
    path('cargar.html', views.cargar, name='cargar'),
    path('pagar.html', views.pagar, name='pagar'),
    path('transacciones.html', views.transacciones, name='transacciones'),
    path('tarjeta.html', views.tarjeta, name='tarjeta'),
]
