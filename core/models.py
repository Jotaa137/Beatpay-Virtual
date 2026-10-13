from django.contrib.auth.models import User
from django.db import models


class Cuenta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cuenta')
    saldo = models.IntegerField(default=80000)
    presupuesto = models.IntegerField(default=100000)
    solicitud_cupo = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} (${self.saldo})'


class Tarjeta(models.Model):
    ESTADOS = [('Activa', 'Activa'), ('Bloqueada', 'Bloqueada')]
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name='tarjeta')
    numero = models.CharField(max_length=19, default='**** **** **** 1234')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activa')
    tipo = models.CharField(max_length=10, default='Visa')

    def __str__(self):
        return f'{self.cuenta.user.username} {self.estado}'

class Auditoria(models.Model):
    usuario = models.CharField(max_length=150)
    accion = models.CharField(max_length=50)
    detalle = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} {self.accion}'

