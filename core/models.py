import random

from django.contrib.auth.models import User
from django.db import models


def numero_default():
    while True:
        n = ' '.join(f'{random.randint(0, 9999):04d}' for _ in range(4))
        if not Tarjeta.objects.filter(numero=n).exists():
            return n


class Cuenta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cuenta')
    saldo = models.IntegerField(default=0)
    presupuesto = models.IntegerField(default=100000)
    solicitud_cupo = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} (${self.saldo})'


class Tarjeta(models.Model):
    ESTADOS = [('Activa', 'Activa'), ('Bloqueada', 'Bloqueada')]
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name='tarjeta')
    numero = models.CharField(max_length=19, default=numero_default, unique=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activa')
    tipo = models.CharField(max_length=10, default='Visa')

    def __str__(self):
        return f'{self.cuenta.user.username} {self.estado}'

class Transaccion(models.Model):
    TIPOS = [('CARGA', 'Carga'), ('PAGO', 'Pago')]
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones')
    evento = models.CharField(max_length=120)
    monto = models.IntegerField()
    tipo = models.CharField(max_length=5, choices=TIPOS)
    estado = models.CharField(max_length=10, default='Aprobado')
    folio = models.CharField(max_length=10, unique=True)
    saldo_antes = models.IntegerField(default=0)
    saldo_nuevo = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.folio} {self.tipo} ${self.monto}'


class Auditoria(models.Model):
    usuario = models.CharField(max_length=150)
    accion = models.CharField(max_length=50)
    detalle = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} {self.accion}'

