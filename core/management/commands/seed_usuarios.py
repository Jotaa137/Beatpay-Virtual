import random
import unicodedata

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Cuenta, Tarjeta


def base_username(nombre, apellido):
    base = f'{nombre}.{apellido}'.lower()
    base = ''.join(c for c in unicodedata.normalize('NFKD', base)
                   if not unicodedata.combining(c))
    return base.replace('ñ', 'n').replace(' ', '')


class Command(BaseCommand):
    help = 'Genera usuarios de prueba con Faker (cuenta + tarjeta incluidas)'

    def add_arguments(self, parser):
        parser.add_argument('cantidad', nargs='?', type=int, default=100)

    def handle(self, *args, **kwargs):
        fake = Faker('es_CL')
        creados = 0
        for _ in range(kwargs['cantidad']):
            username = base_username(fake.first_name(), fake.last_name())[:28]
            n = 1
            while User.objects.filter(username=username).exists():
                n += 1
                username = base_username(fake.first_name(), fake.last_name())[:26] + str(n)
            u = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='beatpay123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            c = Cuenta.objects.create(
                user=u,
                saldo=random.choice([20000, 50000, 80000, 120000]),
                presupuesto=random.choice([100000, 200000]),
            )
            Tarjeta.objects.create(
                cuenta=c,
                estado=random.choice(['Activa', 'Activa', 'Bloqueada']),
            )
            creados += 1
        self.stdout.write(self.style.SUCCESS(f'Creados: {creados} | Usuarios: {User.objects.count()}'))
