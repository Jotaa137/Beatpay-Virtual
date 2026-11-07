import json
import random
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect, render

from .models import (
    Auditoria,
    Banco,
    Cliente,
    Cuenta,
    InstrumentoFinanciero,
    Tarjeta,
    Transaccion,
)

# Datos mock en JSON (eventos y transacciones de ejemplo).
DEMO_PATH = Path(__file__).resolve().parent / 'data' / 'demo.json'


def _demo():
    with open(DEMO_PATH, encoding='utf-8') as f:
        return json.load(f)


def _cuenta(user):
    cuenta, _ = Cuenta.objects.get_or_create(user=user)
    return cuenta


def _banco_interno():
    banco, _ = Banco.objects.get_or_create(
        codigo='BEATPAY',
        defaults={'nombre': 'BeatPay', 'es_interno': True},
    )
    return banco


def _cliente(user):
    cliente = Cliente.objects.filter(user=user).first()
    if cliente is None:
        cliente = Cliente.objects.create(
            user=user,
            nombre=user.first_name or user.username,
            apellido=user.last_name,
            email=user.email,
        )
    return cliente


def _instrumento_interno(tarjeta):
    instrumento, _ = InstrumentoFinanciero.objects.get_or_create(
        tarjeta=tarjeta,
        defaults={
            'tipo': 'INTERNO',
            'banco': _banco_interno(),
            'titular': str(tarjeta.cliente)[:120],
            'alias': f'Tarjeta {tarjeta.numero[-4:]}',
        },
    )
    return instrumento


def _tarjeta(user):
    cliente = _cliente(user)
    tarjeta = cliente.tarjetas.first()
    if tarjeta is None:
        tarjeta = Tarjeta.objects.create(cliente=cliente, banco=_banco_interno())
        _instrumento_interno(tarjeta)
    return tarjeta


def _log(usuario, accion, detalle=''):
    Auditoria.objects.create(usuario=usuario, accion=accion, detalle=detalle[:255])


def _folio():
    while True:
        f = f'BP-{random.randint(0, 999999):06d}'
        if not Transaccion.objects.filter(folio=f).exists():
            return f


def _entero(valor, default=None):
    """Convierte texto a entero. Vacío usa `default`; texto inválido devuelve None."""
    if valor in (None, ''):
        return default
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _validar_username(username):
    if len(username) < 3:
        return 'Mín. 3 caracteres, sin espacios ni @.'
    if len(username) > 150:
        return 'El usuario no puede superar los 150 caracteres.'
    if ' ' in username or '@' in username:
        return 'Mín. 3 caracteres, sin espacios ni @.'
    return None


def _validar_email(email):
    if len(email) > 254:
        return 'El email es demasiado largo.'
    try:
        validate_email(email)
    except ValidationError:
        return 'Ingresa un email válido.'
    return None


def _validar_alta(datos):
    """Reglas de registro/emisión, ahora sin django.forms."""
    errores = []
    if len(datos['nombre']) < 2 or len(datos['nombre']) > 100:
        errores.append('Ingresa un nombre de al menos 2 caracteres.')

    error = _validar_username(datos['username'])
    if error:
        errores.append(error)

    error = _validar_email(datos['email'])
    if error:
        errores.append(error)

    if len(datos['password']) < 6:
        errores.append('La clave debe tener al menos 6 caracteres.')

    return errores


def index(request):
    d = _demo()
    return render(request, 'index.html', {
        'n_eventos': len(d['eventos']),
        'eventos': d['eventos'],
    })


def register(request):
    if request.method == 'POST':
        datos = {
            'nombre': request.POST.get('nombre', '').strip(),
            'username': request.POST.get('username', '').strip().lower(),
            'email': request.POST.get('email', '').strip().lower(),
            'password': request.POST.get('pass', ''),
        }
        errores = _validar_alta(datos)

        pto = _entero(request.POST.get('pto', '').strip(), 100000)
        if pto is None or pto < 0:
            errores.append('El presupuesto debe ser un entero mayor o igual a 0.')

        if errores:
            for e in errores:
                messages.error(request, e)
        elif User.objects.filter(username=datos['username']).exists():
            messages.error(request, 'Ese usuario ya está registrado. Inicia sesión.')
        else:
            user = User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password=datos['password'],
                first_name=datos['nombre'],
            )
            cliente = Cliente.objects.create(
                user=user,
                nombre=datos['nombre'],
                email=datos['email'],
            )
            Cuenta.objects.create(user=user, presupuesto=pto)
            tarjeta = Tarjeta.objects.create(
                cliente=cliente,
                banco=_banco_interno(),
            )
            _instrumento_interno(tarjeta)
            _log(datos['username'], 'registro', f'pto ${pto}')
            auth_login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html', {
        'presupuesto_default': 100000,
        'min_pass': 6,
    })


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('pass', '')

        if not username or not password:
            messages.error(request, 'Ingresa usuario y contraseña.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is None:
                messages.error(request, 'Usuario o contraseña inválidos.')
            else:
                auth_login(request, user)
                _log(username, 'login')
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
    tarjeta = _tarjeta(request.user)
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
            elif tarjeta.estado != 'Activa':
                messages.error(request, 'Tu tarjeta no está activa.')
            elif monto < 1000:
                messages.error(request, 'Monto mínimo $1.000.')
            elif monto > tarjeta.saldo:
                messages.error(request, f'Saldo insuficiente. Tienes ${tarjeta.saldo}.')
            else:
                tarjeta_destino = _tarjeta(destino)
                antes, dest_antes = tarjeta.saldo, tarjeta_destino.saldo
                tarjeta.saldo -= monto
                tarjeta.save()
                tarjeta_destino.saldo += monto
                tarjeta_destino.save()
                Transaccion.objects.create(cuenta=cuenta, evento=f'Transferencia a {destino.username}', monto=monto, tipo='PAGO', folio=_folio(), saldo_antes=antes, saldo_nuevo=tarjeta.saldo)
                Transaccion.objects.create(cuenta=destino_cuenta, evento=f'Transferencia de {request.user.username}', monto=monto, tipo='CARGA', folio=_folio(), saldo_antes=dest_antes, saldo_nuevo=tarjeta_destino.saldo)
                _log(request.user.username, 'transferir', f'${monto} a {destino.username}')
                messages.success(request, f'Transferiste ${monto} a {destino.username}. Nuevo saldo: ${tarjeta.saldo}.')
        return redirect('dashboard')
    ultimas = cuenta.transacciones.all()[:3]
    numero = tarjeta.numero.replace(' ', '')
    return render(request, 'dashboard.html', {
        'usuario': request.user.first_name or request.user.username,
        'saldo': tarjeta.saldo,
        'pto': cuenta.presupuesto,
        'tarjeta': tarjeta.estado,
        'ultimos4': numero[-4:],
        'solicitud': cuenta.solicitud_cupo,
        'ultimas': ultimas,
    })


@login_required
def cargar(request):
    if request.user.is_staff:
        return redirect('panel')
    cuenta = _cuenta(request.user)
    tarjeta = _tarjeta(request.user)
    boleta = None
    if request.method == 'POST':
        try:
            monto = int(request.POST.get('monto', ''))
        except (ValueError, TypeError):
            monto = 0
        if monto < 1000:
            messages.error(request, 'Monto mínimo $1.000.')
        else:
            antes = tarjeta.saldo
            tarjeta.saldo += monto
            tarjeta.save()
            boleta = Transaccion.objects.create(cuenta=cuenta, evento='Carga BeatPay', monto=monto, tipo='CARGA', folio=_folio(), saldo_antes=antes, saldo_nuevo=tarjeta.saldo)
            _log(request.user.username, 'cargar', f'${monto}')
            messages.success(request, f'Carga exitosa. Nuevo saldo: ${tarjeta.saldo}.')
    return render(request, 'cargar.html', {
        'monto_min': 1000,
        'monto_default': 50000,
        'saldo': tarjeta.saldo,
        'boleta': boleta,
    })


@login_required
def pagar(request):
    if request.user.is_staff:
        return redirect('panel')
    cuenta = _cuenta(request.user)
    tarjeta = _tarjeta(request.user)
    boleta = None
    if request.method == 'POST':
        evento = request.POST.get('evento', '').strip()
        try:
            monto = int(request.POST.get('monto', ''))
        except (ValueError, TypeError):
            monto = 0
        if tarjeta.estado != 'Activa':
            messages.error(request, 'Tu tarjeta no está activa.')
        elif monto < 1000:
            messages.error(request, 'Monto mínimo $1.000.')
        elif monto > tarjeta.saldo:
            messages.error(request, f'Saldo insuficiente. Tienes ${tarjeta.saldo}.')
        else:
            if monto > cuenta.presupuesto:
                messages.info(request, f'Te pasaste del presupuesto (${cuenta.presupuesto}). Igual se pagó.')
            antes = tarjeta.saldo
            tarjeta.saldo -= monto
            tarjeta.save()
            boleta = Transaccion.objects.create(cuenta=cuenta, evento=evento or 'Pago', monto=monto, tipo='PAGO', folio=_folio(), saldo_antes=antes, saldo_nuevo=tarjeta.saldo)
            _log(request.user.username, 'pagar', f'${monto} en {boleta.evento}')
            messages.success(request, f'Pago aprobado por ${monto}. Nuevo saldo: ${tarjeta.saldo}.')
    return render(request, 'pagar.html', {
        'monto_min': 1000,
        'monto_default': 15000,
        'eventos': _demo()['eventos'],
        'saldo': tarjeta.saldo,
        'tarjeta': tarjeta.estado,
        'boleta': boleta,
    })


@login_required
def transacciones(request):
    if request.user.is_staff:
        return redirect('panel')
    tx = _cuenta(request.user).transacciones.all()
    f = request.GET.get('filtro', '')
    q = request.GET.get('q', '').strip().lower()
    if f in ('PAGO', 'CARGA'):
        tx = tx.filter(tipo=f)
    if q:
        tx = tx.filter(evento__icontains=q)
    return render(request, 'transacciones.html', {
        'transacciones': tx,
        'filtro': f,
        'q': request.GET.get('q', ''),
        'total_pagos': sum(t.monto for t in tx.filter(tipo='PAGO')),
        'total_cargas': sum(t.monto for t in tx.filter(tipo='CARGA')),
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
        'numero': tobj.numero,
        'tipo': tobj.tipo,
    })


def es_staff(user):
    """Permite el acceso solo a usuarios con permisos de administración."""
    return user.is_staff


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def panel(request):
    if request.method == 'POST' and request.POST.get('action') == 'emitir':
        datos = {
            'nombre': request.POST.get('nombre', '').strip(),
            'username': request.POST.get('username', '').strip().lower(),
            'email': request.POST.get('email', '').strip().lower(),
            'password': request.POST.get('pass', ''),
        }
        errores = _validar_alta(datos)

        saldo = _entero(request.POST.get('saldo', '').strip(), 0)
        pto = _entero(request.POST.get('pto', '').strip(), 100000)

        if saldo is None or saldo < 0:
            errores.append('El saldo debe ser un entero mayor o igual a 0.')
        if pto is None or pto < 0:
            errores.append('El presupuesto debe ser un entero mayor o igual a 0.')

        if errores:
            for e in errores:
                messages.error(request, e)
        elif User.objects.filter(username=datos['username']).exists():
            messages.error(request, 'Ese usuario ya existe.')
        else:
            nuevo = User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password=datos['password'],
                first_name=datos['nombre'],
            )
            cliente = Cliente.objects.create(
                user=nuevo,
                nombre=datos['nombre'],
                email=datos['email'],
            )
            Cuenta.objects.create(user=nuevo, presupuesto=pto)
            tarjeta = Tarjeta.objects.create(
                cliente=cliente,
                banco=_banco_interno(),
                saldo=saldo,
            )
            _instrumento_interno(tarjeta)
            _log(request.user.username, 'emitir', f'tarjeta para {datos["username"]} (${tarjeta.saldo})')
            messages.success(request, f'Tarjeta emitida para {datos["username"]} con ${tarjeta.saldo}.')
    for u in User.objects.filter(is_staff=False):
        _tarjeta(u)
    clientes = list(User.objects.filter(is_staff=False).order_by('username'))
    cuentas = [_cuenta(u) for u in clientes]
    for u in clientes:
        u.tarjeta_obj = _tarjeta(u)
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', '')
    usuarios = list(clientes)
    if q:
        usuarios = [u for u in usuarios if q.lower() in u.username.lower() or q.lower() in (u.first_name or '').lower()]
    if filtro == 'activas':
        usuarios = [u for u in usuarios if u.tarjeta_obj.estado == 'Activa']
    elif filtro == 'bloqueadas':
        usuarios = [u for u in usuarios if u.tarjeta_obj.estado != 'Activa']
    todos = clientes
    saldo_total = sum(u.tarjeta_obj.saldo for u in clientes)
    return render(request, 'admin.html', {
        'usuarios': usuarios,
        'solicitudes': [u for u, c in zip(clientes, cuentas) if c.solicitud_cupo],
        'q': q,
        'filtro': filtro,
        'n_usuarios': len(todos),
        'n_bloqueados': sum(1 for u in todos if not u.is_active),
        'saldo_total': saldo_total,
        'saldo_promedio': round(saldo_total / max(len(clientes), 1)),
        'tarjetas_activas': Tarjeta.objects.filter(estado='Activa').count(),
        'tarjetas_bloqueadas': Tarjeta.objects.exclude(estado='Activa').count(),
        'total_pagos': sum(t.monto for t in Transaccion.objects.filter(tipo='PAGO')),
        'total_cargas': sum(t.monto for t in Transaccion.objects.filter(tipo='CARGA')),
        'mi_historial': Auditoria.objects.filter(usuario=request.user.username).order_by('-fecha')[:8],
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def usuario_detalle(request, user_id):
    try:
        target = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Usuario no encontrado.')
        return redirect('panel')
    tcuenta = _cuenta(target)
    ttarjeta = _tarjeta(target)
    tcliente = _cliente(target)
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
        elif action == 'editar_cliente':
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            rut = request.POST.get('rut', '').strip().upper() or None
            email = request.POST.get('email', '').strip().lower()
            telefono = request.POST.get('telefono', '').strip()
            direccion = request.POST.get('direccion', '').strip()
            errores = []
            if len(nombre) < 2 or len(nombre) > 80:
                errores.append('El nombre debe tener entre 2 y 80 caracteres.')
            if len(apellido) > 80:
                errores.append('El apellido no puede superar los 80 caracteres.')
            if email:
                error = _validar_email(email)
                if error:
                    errores.append(error)
            if len(telefono) > 20:
                errores.append('El teléfono no puede superar los 20 caracteres.')
            if len(direccion) > 200:
                errores.append('La dirección no puede superar los 200 caracteres.')
            if rut:
                if len(rut) > 12:
                    errores.append('El RUT no puede superar los 12 caracteres.')
                elif Cliente.objects.filter(rut=rut).exclude(pk=tcliente.pk).exists():
                    errores.append('Ese RUT ya está registrado.')
            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                tcliente.nombre = nombre
                tcliente.apellido = apellido
                tcliente.rut = rut
                tcliente.email = email
                tcliente.telefono = telefono
                tcliente.direccion = direccion
                tcliente.save()
                target.first_name = nombre
                target.last_name = apellido
                target.email = email
                target.save(update_fields=['first_name', 'last_name', 'email'])
                _log(request.user.username, 'cliente', f'{target.username}: datos actualizados')
                messages.success(request, f'Datos de {target.username} actualizados.')
        elif action == 'eliminar':
            if target == request.user:
                messages.error(request, 'No puedes eliminarte a ti mismo.')
            else:
                _log(request.user.username, 'eliminar', f'usuario {target.username}')
                try:
                    target.delete()
                except ProtectedError:
                    target.is_active = False
                    target.save(update_fields=['is_active'])
                    messages.warning(request, f'{target.username} tiene movimientos registrados; se desactivó en vez de eliminarse.')
                    return redirect('usuario_detalle', user_id=target.id)
                messages.success(request, f'Usuario {target.username} eliminado.')
                return redirect('panel')
        return redirect('usuario_detalle', user_id=target.id)
    historial = Auditoria.objects.filter(Q(usuario=target.username) | Q(detalle__icontains=target.username)).order_by('-fecha')[:10]
    return render(request, 'usuario.html', {
        'target': target,
        'cliente': tcliente,
        'cuenta': tcuenta,
        'tarjeta': ttarjeta,
        'historial': historial,
    })
