import os
import random
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BeatPay_Virtual.settings')
django.setup()

from django.contrib.auth.models import User
from faker import Faker
from core.models import Cuenta, Tarjeta


def base_username(nombre, apellido):
    base = f'{nombre}.{apellido}'.lower()
    base = ''.join(c for c in unicodedata.normalize('NFKD', base)
                   if not unicodedata.combining(c))
    return base.replace('ñ', 'n').replace(' ', '')


fake = Faker('es_CL')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100

creados = 0
for _ in range(N):
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

print(f'Creados: {creados} | Usuarios: {User.objects.count()}')
