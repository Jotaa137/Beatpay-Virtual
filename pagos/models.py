from django.contrib.auth.models import User
from django.db import models


class Cuenta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cuenta')
    saldo = models.IntegerField(default=80000)
    presupuesto = models.IntegerField(default=100000)
    tarjeta = models.CharField(max_length=10, default='Activa')

    def __str__(self):
        return f'{self.user.username} (${self.saldo})'
