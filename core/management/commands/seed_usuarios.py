import random
import unicodedata

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Banco, Cliente, Cuenta, InstrumentoFinanciero, Tarjeta


def base_username(nombre, apellido):
    base = f'{nombre}.{apellido}'.lower()
    base = ''.join(c for c in unicodedata.normalize('NFKD', base)
                   if not unicodedata.combining(c))
    return base.replace('ñ', 'n').replace(' ', '')


class Command(BaseCommand):
    help = 'Genera clientes de prueba con cuenta, tarjeta e instrumento interno'

    def add_arguments(self, parser):
        parser.add_argument('cantidad', nargs='?', type=int, default=100)

    def handle(self, *args, **kwargs):
        fake = Faker('es_CL')
        beatpay, _ = Banco.objects.get_or_create(
            codigo='BEATPAY',
            defaults={'nombre': 'BeatPay', 'es_interno': True},
        )
        creados = 0
        for _ in range(kwargs['cantidad']):
            nombre = fake.first_name()
            apellido = fake.last_name()
            username = base_username(nombre, apellido)[:28]
            n = 1
            while User.objects.filter(username=username).exists():
                n += 1
                username = base_username(nombre, apellido)[:26] + str(n)
            u = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='beatpay123',
                first_name=nombre,
                last_name=apellido,
            )
            cliente = Cliente.objects.create(
                user=u,
                nombre=nombre,
                apellido=apellido,
                email=u.email,
                telefono=fake.phone_number()[:20],
                direccion=fake.address()[:200],
            )
            Cuenta.objects.create(
                user=u,
                presupuesto=random.choice([100000, 200000]),
            )
            tarjeta = Tarjeta.objects.create(
                cliente=cliente,
                banco=beatpay,
                saldo=random.choice([20000, 50000, 80000, 120000]),
                estado=random.choice(['Activa', 'Activa', 'Bloqueada']),
            )
            InstrumentoFinanciero.objects.create(
                tipo='INTERNO',
                banco=beatpay,
                tarjeta=tarjeta,
                titular=str(cliente),
                alias=f'Tarjeta {tarjeta.numero[-4:]}',
            )
            creados += 1
        self.stdout.write(self.style.SUCCESS(
            f'Creados: {creados} | Usuarios: {User.objects.count()} | '
            f'Clientes: {Cliente.objects.count()} | Tarjetas: {Tarjeta.objects.count()}'
        ))
