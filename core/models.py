from django.contrib.auth.models import User
from django.db import models


class Cuenta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cuenta')
    saldo = models.IntegerField(default=80000)
    presupuesto = models.IntegerField(default=100000)
    tarjeta = models.CharField(max_length=10, default='Activa')
    solicitud_cupo = models.IntegerField(null=True, blank=True)


class Auditoria(models.Model):
    usuario = models.CharField(max_length=150)
    accion = models.CharField(max_length=50)
    detalle = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} {self.accion}'

    def __str__(self):
        return f'{self.user.username} (${self.saldo})'
