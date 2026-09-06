import json
from pathlib import Path

from django.contrib import messages
from django.shortcuts import render

# Fase 3: datos mock en JSON (sin DB todavía). Las vistas los leen
# y los pasan a los templates, que los pintan con DTL.
DEMO_PATH = Path(__file__).resolve().parent / 'data' / 'demo.json'


def _demo():
    with open(DEMO_PATH, encoding='utf-8') as f:
        return json.load(f)

# Fase 3: vistas que sirven los mockups de Fase 1 como templates Django.
# (La lógica sigue en JS/localStorage; la DB llega en el siguiente paso.)
def index(request):
    d = _demo()
    messages.info(request, 'Demo BeatPay servida por Django (datos mock, sin DB).')
    return render(request, 'index.html', {
        'n_eventos': len(d['eventos']),
        'eventos': d['eventos'],
    })


def register(request):
    return render(request, 'register.html', {
        'presupuesto_default': 100000,
        'min_pass': 6,
    })


def login(request):
    d = _demo()
    return render(request, 'login.html', {
        'demo_email': d['cuenta']['usuario'],
    })


def dashboard(request):
    d = _demo()
    tx = d['transacciones']
    ultimas = []
    for t in reversed(tx):
        if len(ultimas) < 3:
            ultimas.append(t)
    return render(request, 'dashboard.html', {
        'usuario': d['cuenta']['usuario'],
        'saldo': d['cuenta']['saldo'],
        'pto': d['cuenta']['presupuesto'],
        'tarjeta': d['cuenta']['tarjeta'],
        'ultimas': ultimas,
        'tx_json': json.dumps(tx),
    })


def cargar(request):
    return render(request, 'cargar.html', {
        'monto_min': 1000,
        'monto_default': 50000,
    })


def pagar(request):
    d = _demo()
    return render(request, 'pagar.html', {
        'monto_min': 1000,
        'monto_default': 15000,
        'eventos': d['eventos'],
    })


def transacciones(request):
    d = _demo()
    tx = d['transacciones']
    pagos = []
    cargas = []
    for t in tx:
        if t['tipo'] == 'PAGO':
            pagos.append(t)
        else:
            cargas.append(t)
    total_pagos = 0
    for t in pagos:
        total_pagos = total_pagos + t['monto']
    total_cargas = 0
    for t in cargas:
        total_cargas = total_cargas + t['monto']
    al_reves = []
    for t in reversed(tx):
        al_reves.append(t)
    return render(request, 'transacciones.html', {
        'transacciones': al_reves,
        'total_pagos': total_pagos,
        'total_cargas': total_cargas,
        'tx_json': json.dumps(tx),
    })


def tarjeta(request):
    d = _demo()
    return render(request, 'tarjeta.html', {
        'tarjeta': d['cuenta']['tarjeta'],
        'tipo': 'Visa',
    })
