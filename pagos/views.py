import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import Cuenta

# Datos mock en JSON (eventos y transacciones de ejemplo).
DEMO_PATH = Path(__file__).resolve().parent / 'data' / 'demo.json'


def _demo():
    with open(DEMO_PATH, encoding='utf-8') as f:
        return json.load(f)


def _cuenta(user):
    cuenta, _ = Cuenta.objects.get_or_create(user=user)
    return cuenta


def index(request):
    d = _demo()
    return render(request, 'index.html', {
        'n_eventos': len(d['eventos']),
        'eventos': d['eventos'],
    })


def register(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('pass', '')
        pto_raw = request.POST.get('pto', '').strip()
        if len(nombre) < 2:
            messages.error(request, 'Ingresa tu nombre.')
        elif '@' not in email:
            messages.error(request, 'Ingresa un email válido.')
        elif len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
        elif User.objects.filter(username=email).exists():
            messages.error(request, 'Ese email ya está registrado. Inicia sesión.')
        else:
            try:
                pto = int(pto_raw) if pto_raw else 100000
            except ValueError:
                pto = 100000
            if pto < 0:
                pto = 0
            user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
            Cuenta.objects.create(user=user, presupuesto=pto)
            auth_login(request, user)
            return redirect('dashboard')
    return render(request, 'register.html', {
        'presupuesto_default': 100000,
        'min_pass': 6,
    })


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('pass', '')
        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, 'Credenciales inválidas.')
        else:
            auth_login(request, user)
            return redirect(request.POST.get('next') or request.GET.get('next') or 'dashboard')
    d = _demo()
    return render(request, 'login.html', {
        'demo_email': d['cuenta']['usuario'],
    })


def logout_view(request):
    auth_logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    cuenta = _cuenta(request.user)
    tx = _demo()['transacciones']
    ultimas = list(reversed(tx))[:3]
    return render(request, 'dashboard.html', {
        'usuario': request.user.first_name or request.user.username,
        'saldo': cuenta.saldo,
        'pto': cuenta.presupuesto,
        'tarjeta': cuenta.tarjeta,
        'ultimas': ultimas,
        'tx_json': json.dumps(tx),
    })


@login_required
def cargar(request):
    return render(request, 'cargar.html', {
        'monto_min': 1000,
        'monto_default': 50000,
    })


@login_required
def pagar(request):
    d = _demo()
    return render(request, 'pagar.html', {
        'monto_min': 1000,
        'monto_default': 15000,
        'eventos': d['eventos'],
    })


@login_required
def transacciones(request):
    d = _demo()
    tx = d['transacciones']
    pagos = [t for t in tx if t['tipo'] == 'PAGO']
    cargas = [t for t in tx if t['tipo'] != 'PAGO']
    total_pagos = sum(t['monto'] for t in pagos)
    total_cargas = sum(t['monto'] for t in cargas)
    return render(request, 'transacciones.html', {
        'transacciones': list(reversed(tx)),
        'total_pagos': total_pagos,
        'total_cargas': total_cargas,
        'tx_json': json.dumps(tx),
    })


@login_required
def tarjeta(request):
    cuenta = _cuenta(request.user)
    return render(request, 'tarjeta.html', {
        'tarjeta': cuenta.tarjeta,
        'tipo': 'Visa',
    })


@login_required
def panel(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver el panel.')
        return redirect('dashboard')
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            target = User.objects.get(pk=request.POST.get('user_id'))
        except (User.DoesNotExist, ValueError, TypeError):
            target = None
        if target is None:
            messages.error(request, 'Usuario no encontrado.')
        elif action == 'toggle_tarjeta':
            tcuenta = _cuenta(target)
            tcuenta.tarjeta = 'Bloqueada' if tcuenta.tarjeta == 'Activa' else 'Activa'
            tcuenta.save()
            messages.success(request, f'Tarjeta de {target.username}: {tcuenta.tarjeta}.')
        elif action == 'toggle_staff':
            if target == request.user:
                messages.error(request, 'No puedes quitarte tu propio acceso.')
            else:
                target.is_staff = not target.is_staff
                target.save()
                messages.success(request, f'{target.username} {"ahora es staff" if target.is_staff else "ya no es staff"}.')
    for u in User.objects.all():
        _cuenta(u)
    return render(request, 'admin.html', {
        'usuarios': User.objects.select_related('cuenta').order_by('username'),
    })
