import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import EmisionForm, LoginForm, RegistroForm
from .models import Auditoria, Cuenta, Tarjeta

# Datos mock en JSON (eventos y transacciones de ejemplo).
DEMO_PATH = Path(__file__).resolve().parent / 'data' / 'demo.json'


def _demo():
    with open(DEMO_PATH, encoding='utf-8') as f:
        return json.load(f)


def _cuenta(user):
    cuenta, _ = Cuenta.objects.get_or_create(user=user)
    return cuenta


def _tarjeta(user):
    return Tarjeta.objects.get_or_create(cuenta=_cuenta(user))[0]


def _log(usuario, accion, detalle=''):
    Auditoria.objects.create(usuario=usuario, accion=accion, detalle=detalle[:255])


def index(request):
    d = _demo()
    return render(request, 'index.html', {
        'n_eventos': len(d['eventos']),
        'eventos': d['eventos'],
    })


def register(request):
    if request.method == 'POST':
        form = RegistroForm({
            'nombre': request.POST.get('nombre', '').strip(),
            'username': request.POST.get('username', '').strip().lower(),
            'email': request.POST.get('email', '').strip().lower(),
            'password': request.POST.get('pass', ''),
            'presupuesto': request.POST.get('pto', '').strip() or None,
        })
        if not form.is_valid():
            for errs in form.errors.values():
                for e in errs:
                    messages.error(request, e)
        elif User.objects.filter(username=form.cleaned_data['username']).exists():
            messages.error(request, 'Ese usuario ya está registrado. Inicia sesión.')
        else:
            d = form.cleaned_data
            pto = d['presupuesto'] if d['presupuesto'] is not None else 100000
            user = User.objects.create_user(username=d['username'], email=d['email'], password=d['password'], first_name=d['nombre'])
            cuenta = Cuenta.objects.create(user=user, presupuesto=pto)
            Tarjeta.objects.create(cuenta=cuenta)
            _log(d['username'], 'registro', f'pto ${pto}')
            auth_login(request, user)
            return redirect('dashboard')
    return render(request, 'register.html', {
        'presupuesto_default': 100000,
        'min_pass': 6,
    })


def login(request):
    if request.method == 'POST':
        form = LoginForm({
            'username': request.POST.get('username', '').strip().lower(),
            'password': request.POST.get('pass', ''),
        })
        if form.is_valid():
            d = form.cleaned_data
            user = authenticate(request, username=d['username'], password=d['password'])
        else:
            d, user = None, None
        if user is None:
            messages.error(request, 'Usuario o contraseña inválidos.')
        else:
            auth_login(request, user)
            _log(d['username'], 'login')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('panel' if user.is_staff else 'dashboard')
    return render(request, 'login.html')


def logout_view(request):
    if request.user.is_authenticated:
        _log(request.user.username, 'logout')
    auth_logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('panel')
    cuenta = _cuenta(request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'solicitar_cupo':
            try:
                monto = int(request.POST.get('monto', ''))
            except (ValueError, TypeError):
                monto = 0
            if monto <= cuenta.presupuesto:
                messages.error(request, 'El cupo solicitado debe ser mayor a tu presupuesto actual.')
            else:
                cuenta.solicitud_cupo = monto
                cuenta.save()
                _log(request.user.username, 'solicitar_cupo', f'${monto}')
                messages.success(request, f'Solicitud de cupo por ${monto} enviada.')
        elif action == 'transferir':
            destino_nombre = request.POST.get('destino', '').strip().lower()
            try:
                monto = int(request.POST.get('monto', ''))
            except (ValueError, TypeError):
                monto = 0
            try:
                destino = User.objects.get(username=destino_nombre)
                destino_cuenta = _cuenta(destino)
            except User.DoesNotExist:
                destino = None
            if destino is None:
                messages.error(request, 'Ese usuario no existe.')
            elif destino == request.user:
                messages.error(request, 'No puedes transferirte a ti mismo.')
            elif not destino.is_active:
                messages.error(request, 'Ese usuario está bloqueado.')
            elif _tarjeta(request.user).estado != 'Activa':
                messages.error(request, 'Tu tarjeta no está activa.')
            elif monto < 1000:
                messages.error(request, 'Monto mínimo $1.000.')
            elif monto > cuenta.saldo:
                messages.error(request, f'Saldo insuficiente. Tienes ${cuenta.saldo}.')
            else:
                cuenta.saldo -= monto
                cuenta.save()
                destino_cuenta.saldo += monto
                destino_cuenta.save()
                _log(request.user.username, 'transferir', f'${monto} a {destino.username}')
                messages.success(request, f'Transferiste ${monto} a {destino.username}. Nuevo saldo: ${cuenta.saldo}.')
        return redirect('dashboard')
    tx = _demo()['transacciones']
    ultimas = list(reversed(tx))[:3]
    return render(request, 'dashboard.html', {
        'usuario': request.user.first_name or request.user.username,
        'saldo': cuenta.saldo,
        'pto': cuenta.presupuesto,
        'tarjeta': _tarjeta(request.user).estado,
        'solicitud': cuenta.solicitud_cupo,
        'ultimas': ultimas,
        'tx_json': json.dumps(tx),
    })


@login_required
def cargar(request):
    if request.user.is_staff:
        return redirect('panel')
    return render(request, 'cargar.html', {
        'monto_min': 1000,
        'monto_default': 50000,
    })


@login_required
def pagar(request):
    if request.user.is_staff:
        return redirect('panel')
    d = _demo()
    return render(request, 'pagar.html', {
        'monto_min': 1000,
        'monto_default': 15000,
        'eventos': d['eventos'],
    })


@login_required
def transacciones(request):
    if request.user.is_staff:
        return redirect('panel')
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
    if request.user.is_staff:
        return redirect('panel')
    tobj = _tarjeta(request.user)
    if request.method == 'POST' and request.POST.get('action') == 'toggle':
        tobj.estado = 'Bloqueada' if tobj.estado == 'Activa' else 'Activa'
        tobj.save()
        _log(request.user.username, 'tarjeta', f'propia: {tobj.estado}')
        messages.success(request, f'Tarjeta {tobj.estado.lower()}.')
        return redirect('tarjeta')
    return render(request, 'tarjeta.html', {
        'tarjeta': tobj.estado,
        'tipo': tobj.tipo,
    })


@login_required
def panel(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver el panel.')
        return redirect('dashboard')
    if request.method == 'POST' and request.POST.get('action') == 'emitir':
        form = EmisionForm({
            'nombre': request.POST.get('nombre', '').strip(),
            'username': request.POST.get('username', '').strip().lower(),
            'email': request.POST.get('email', '').strip().lower(),
            'password': request.POST.get('pass', ''),
        })
        if not form.is_valid():
            for errs in form.errors.values():
                for e in errs:
                    messages.error(request, e)
        elif User.objects.filter(username=form.cleaned_data['username']).exists():
            messages.error(request, 'Ese usuario ya existe.')
        else:
            d = form.cleaned_data
            nuevo = User.objects.create_user(username=d['username'], email=d['email'], password=d['password'], first_name=d['nombre'])
            Tarjeta.objects.create(cuenta=Cuenta.objects.create(user=nuevo))
            _log(request.user.username, 'emitir', f'tarjeta para {d["username"]}')
            messages.success(request, f'Tarjeta emitida para {d["username"]}.')
    for u in User.objects.all():
        _tarjeta(u)
    clientes = list(User.objects.filter(is_staff=False).select_related('cuenta').order_by('username'))
    cuentas = [u.cuenta for u in clientes]
    tx = _demo()['transacciones']
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', '')
    usuarios = list(clientes)
    if q:
        usuarios = [u for u in usuarios if q.lower() in u.username.lower() or q.lower() in (u.first_name or '').lower()]
    if filtro == 'activas':
        usuarios = [u for u in usuarios if u.cuenta.tarjeta.estado == 'Activa']
    elif filtro == 'bloqueadas':
        usuarios = [u for u in usuarios if u.cuenta.tarjeta.estado != 'Activa']
    todos = clientes
    return render(request, 'admin.html', {
        'usuarios': usuarios,
        'solicitudes': [u for u in todos if u.cuenta.solicitud_cupo],
        'q': q,
        'filtro': filtro,
        'n_bloqueados': sum(1 for u in todos if not u.is_active),
        'saldo_total': sum(c.saldo for c in cuentas),
        'saldo_promedio': round(sum(c.saldo for c in cuentas) / max(len(cuentas), 1)),
        'tarjetas_activas': Tarjeta.objects.filter(estado='Activa').count(),
        'tarjetas_bloqueadas': Tarjeta.objects.exclude(estado='Activa').count(),
        'total_pagos': sum(t['monto'] for t in tx if t['tipo'] == 'PAGO'),
        'total_cargas': sum(t['monto'] for t in tx if t['tipo'] != 'PAGO'),
    })


@login_required
def usuario_detalle(request, user_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver el panel.')
        return redirect('dashboard')
    try:
        target = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Usuario no encontrado.')
        return redirect('panel')
    tcuenta = _cuenta(target)
    ttarjeta = _tarjeta(target)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_tarjeta':
            ttarjeta.estado = 'Bloqueada' if ttarjeta.estado == 'Activa' else 'Activa'
            ttarjeta.save()
            _log(request.user.username, 'tarjeta', f'{target.username}: {ttarjeta.estado}')
            messages.success(request, f'Tarjeta de {target.username}: {ttarjeta.estado}.')
        elif action == 'toggle_activo':
            if target == request.user:
                messages.error(request, 'No puedes bloquearte a ti mismo.')
            else:
                target.is_active = not target.is_active
                target.save()
                _log(request.user.username, 'acceso', f'{target.username}: {"sí" if target.is_active else "no"}')
                messages.success(request, f'{target.username} {"desbloqueado" if target.is_active else "bloqueado"}.')
        elif action == 'set_pto':
            try:
                pto = int(request.POST.get('pto', ''))
            except (ValueError, TypeError):
                pto = -1
            if pto < 0:
                messages.error(request, 'Presupuesto inválido.')
            else:
                tcuenta.presupuesto = pto
                tcuenta.save()
                _log(request.user.username, 'presupuesto', f'{target.username}: ${pto}')
                messages.success(request, f'Presupuesto de {target.username}: ${pto}.')
        elif action == 'aprobar_cupo':
            if tcuenta.solicitud_cupo:
                tcuenta.presupuesto = tcuenta.solicitud_cupo
                tcuenta.solicitud_cupo = None
                tcuenta.save()
                _log(request.user.username, 'cupo', f'{target.username} aprobado: ${tcuenta.presupuesto}')
                messages.success(request, f'Cupo de {target.username} aprobado: ${tcuenta.presupuesto}.')
        elif action == 'rechazar_cupo':
            tcuenta.solicitud_cupo = None
            tcuenta.save()
            _log(request.user.username, 'cupo', f'{target.username} rechazado')
            messages.success(request, f'Solicitud de {target.username} rechazada.')
        return redirect('usuario_detalle', user_id=target.id)
    historial = Auditoria.objects.filter(Q(usuario=target.username) | Q(detalle__icontains=target.username)).order_by('-fecha')[:10]
    return render(request, 'usuario.html', {
        'target': target,
        'cuenta': tcuenta,
        'tarjeta': ttarjeta,
        'historial': historial,
    })
