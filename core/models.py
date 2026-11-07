import random
import uuid
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def numero_default():
    while True:
        n = ' '.join(f'{random.randint(0, 9999):04d}' for _ in range(4))
        if not Tarjeta.objects.filter(numero=n).exists():
            return n


class Cliente(models.Model):
    """Titular de las tarjetas internas. Puede tener o no un usuario de login."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cliente',
        null=True,
        blank=True,
    )
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'.strip()


class Banco(models.Model):
    """Institución financiera interna o externa (BeatPay, MACH, Tenpo, bancos)."""

    nombre = models.CharField(max_length=80, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    es_interno = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'bancos'

    def __str__(self):
        return self.nombre


class Cuenta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cuenta')
    presupuesto = models.IntegerField(default=100000)
    solicitud_cupo = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(presupuesto__gte=0),
                name='cuenta_presupuesto_no_negativo',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} (pto ${self.presupuesto})'


class Tarjeta(models.Model):
    ESTADOS = [
        ('Activa', 'Activa'),
        ('Bloqueada', 'Bloqueada'),
        ('Inactiva', 'Inactiva'),
    ]
    TIPOS = [
        ('Visa', 'Visa'),
        ('Mastercard', 'Mastercard'),
        ('Otra', 'Otra'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='tarjetas',
    )
    banco = models.ForeignKey(
        Banco,
        on_delete=models.PROTECT,
        related_name='tarjetas',
        null=True,
        blank=True,
    )
    numero = models.CharField(max_length=19, default=numero_default, unique=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activa')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='Visa')
    saldo = models.IntegerField(default=0)
    fecha_emision = models.DateField(default=date.today)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['cliente', 'numero']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(saldo__gte=0),
                name='tarjeta_saldo_no_negativo',
            ),
        ]

    def __str__(self):
        return f'{self.cliente} {self.estado}'


class InstrumentoFinanciero(models.Model):
    """Instrumento interno (tarjeta del sistema) o referencia externa (UUID)."""

    TIPOS = [
        ('INTERNO', 'Interno'),
        ('EXTERNO', 'Externo'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    tipo = models.CharField(max_length=8, choices=TIPOS, default='INTERNO')
    banco = models.ForeignKey(
        Banco,
        on_delete=models.PROTECT,
        related_name='instrumentos',
    )
    tarjeta = models.OneToOneField(
        Tarjeta,
        on_delete=models.CASCADE,
        related_name='instrumento',
        null=True,
        blank=True,
    )
    titular = models.CharField(max_length=120, blank=True)
    alias = models.CharField(max_length=60, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['banco', 'alias']

    def __str__(self):
        return self.alias or f'{self.banco} {self.uuid}'


class Movimiento(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Completado', 'Completado'),
        ('Rechazado', 'Rechazado'),
    ]

    origen = models.ForeignKey(
        InstrumentoFinanciero,
        on_delete=models.PROTECT,
        related_name='movimientos_enviados',
    )
    destino = models.ForeignKey(
        InstrumentoFinanciero,
        on_delete=models.PROTECT,
        related_name='movimientos_recibidos',
    )
    monto = models.PositiveIntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=12, choices=ESTADOS, default='Completado')
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-fecha']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(origen=models.F('destino')),
                name='movimiento_origen_distinto_destino',
            ),
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name='movimiento_monto_positivo',
            ),
        ]

    def __str__(self):
        return f'{self.origen} -> {self.destino}: ${self.monto}'


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
