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
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import redirect, render

from .models import (
    Auditoria,
    Banco,
    Cliente,
    Cuenta,
    InstrumentoFinanciero,
    Movimiento,
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


def _datos_cliente(request):
    return {
        'nombre': request.POST.get('nombre', '').strip(),
        'apellido': request.POST.get('apellido', '').strip(),
        'rut': request.POST.get('rut', '').strip().upper() or None,
        'email': request.POST.get('email', '').strip().lower(),
        'telefono': request.POST.get('telefono', '').strip(),
        'direccion': request.POST.get('direccion', '').strip(),
        'activo': request.POST.get('activo') == 'on',
    }


def _validar_cliente(datos, cliente=None):
    errores = []
    if len(datos['nombre']) < 2 or len(datos['nombre']) > 80:
        errores.append('El nombre debe tener entre 2 y 80 caracteres.')
    if len(datos['apellido']) > 80:
        errores.append('El apellido no puede superar los 80 caracteres.')
    if datos['email']:
        error = _validar_email(datos['email'])
        if error:
            errores.append(error)
    if len(datos['telefono']) > 20:
        errores.append('El teléfono no puede superar los 20 caracteres.')
    if len(datos['direccion']) > 200:
        errores.append('La dirección no puede superar los 200 caracteres.')
    if datos['rut']:
        if len(datos['rut']) > 12:
            errores.append('El RUT no puede superar los 12 caracteres.')
        else:
            qs = Cliente.objects.filter(rut=datos['rut'])
            if cliente is not None:
                qs = qs.exclude(pk=cliente.pk)
            if qs.exists():
                errores.append('Ese RUT ya está registrado.')
    return errores


def _guardar_cliente(cliente, datos):
    for campo, valor in datos.items():
        setattr(cliente, campo, valor)
    cliente.save()
    if cliente.user_id:
        user = cliente.user
        user.first_name = datos['nombre']
        user.last_name = datos['apellido']
        user.email = datos['email']
        user.save(update_fields=['first_name', 'last_name', 'email'])


def _datos_banco(request):
    return {
        'nombre': request.POST.get('nombre', '').strip(),
        'codigo': request.POST.get('codigo', '').strip().upper(),
        'es_interno': request.POST.get('es_interno') == 'on',
        'activo': request.POST.get('activo') == 'on',
    }


def _validar_banco(datos, banco=None):
    errores = []
    if len(datos['nombre']) < 2 or len(datos['nombre']) > 80:
        errores.append('El nombre debe tener entre 2 y 80 caracteres.')
    if len(datos['codigo']) < 2 or len(datos['codigo']) > 20:
        errores.append('El código debe tener entre 2 y 20 caracteres.')
    elif not all(c.isalnum() or c in '-_' for c in datos['codigo']):
        errores.append('El código solo puede tener letras, números, guion y guion bajo.')
    qs = Banco.objects.filter(nombre__iexact=datos['nombre'])
    if banco is not None:
        qs = qs.exclude(pk=banco.pk)
    if qs.exists():
        errores.append('Ya existe un banco con ese nombre.')
    qs = Banco.objects.filter(codigo__iexact=datos['codigo'])
    if banco is not None:
        qs = qs.exclude(pk=banco.pk)
    if qs.exists():
        errores.append('Ya existe un banco con ese código.')
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
            cliente_id = _entero(request.POST.get('cliente_id', '').strip(), None)
            if cliente_id is not None:
                try:
                    cliente = Cliente.objects.get(pk=cliente_id, user__isnull=True)
                    cliente.user = nuevo
                    cliente.nombre = datos['nombre']
                    cliente.email = datos['email']
                    cliente.save(update_fields=['user', 'nombre', 'email'])
                except Cliente.DoesNotExist:
                    cliente = Cliente.objects.create(
                        user=nuevo,
                        nombre=datos['nombre'],
                        email=datos['email'],
                    )
            else:
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
        'clientes_sin_user': Cliente.objects.filter(user__isnull=True).order_by('apellido', 'nombre'),
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
            datos = _datos_cliente(request)
            datos['activo'] = tcliente.activo
            errores = _validar_cliente(datos, tcliente)
            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                _guardar_cliente(tcliente, datos)
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


# =====================================================================
# CRUD de Tarjetas (panel propio)
# =====================================================================

@login_required
@user_passes_test(es_staff, login_url='dashboard')
def panel_tarjetas(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    banco_id = _entero(request.GET.get('banco', '').strip(), None)
    tarjetas = Tarjeta.objects.select_related('cliente', 'banco').prefetch_related('instrumento')
    if q:
        tarjetas = tarjetas.filter(
            Q(numero__icontains=q)
            | Q(cliente__nombre__icontains=q)
            | Q(cliente__apellido__icontains=q)
            | Q(cliente__rut__icontains=q)
            | Q(banco__nombre__icontains=q)
        )
    if estado:
        tarjetas = tarjetas.filter(estado=estado)
    if banco_id is not None:
        tarjetas = tarjetas.filter(banco_id=banco_id)
    return render(request, 'panel_tarjetas.html', {
        'tarjetas': tarjetas,
        'q': q,
        'estado': estado,
        'banco': banco_id,
        'bancos': Banco.objects.all(),
        'estados': Tarjeta.ESTADOS,
        'total': tarjetas.count(),
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def tarjeta_form(request, tarjeta_id=None):
    tarjeta = None
    if tarjeta_id is not None:
        try:
            tarjeta = Tarjeta.objects.select_related('cliente', 'banco').get(pk=tarjeta_id)
        except Tarjeta.DoesNotExist:
            messages.error(request, 'Tarjeta no encontrada.')
            return redirect('panel_tarjetas')

    if request.method == 'POST':
        cliente_id = _entero(request.POST.get('cliente', '').strip(), None)
        banco_id = _entero(request.POST.get('banco', '').strip(), None)
        tipo = request.POST.get('tipo', '').strip()
        estado = request.POST.get('estado', '').strip()
        saldo = _entero(request.POST.get('saldo', '0').strip(), 0)
        fecha_venc = request.POST.get('fecha_vencimiento', '').strip() or None

        errores = []
        if cliente_id is None:
            errores.append('Debe seleccionar un cliente.')
        else:
            try:
                Cliente.objects.get(pk=cliente_id)
            except Cliente.DoesNotExist:
                errores.append('El cliente seleccionado no existe.')
        if banco_id is None:
            errores.append('Debe seleccionar un banco.')
        else:
            try:
                Banco.objects.get(pk=banco_id)
            except Banco.DoesNotExist:
                errores.append('El banco seleccionado no existe.')
        tipos_validos = [t[0] for t in Tarjeta.TIPOS]
        if tipo not in tipos_validos:
            errores.append('Tipo de tarjeta inválido.')
        estados_validos = [e[0] for e in Tarjeta.ESTADOS]
        if estado not in estados_validos:
            errores.append('Estado inválido.')
        if saldo is None or saldo < 0:
            errores.append('El saldo debe ser un entero mayor o igual a 0.')

        if errores:
            for e in errores:
                messages.error(request, e)
            valores = {
                'cliente': cliente_id or '',
                'banco': banco_id or '',
                'tipo': tipo,
                'estado': estado,
                'saldo': saldo if saldo is not None else '',
                'fecha_vencimiento': fecha_venc or '',
            }
        else:
            if tarjeta is None:
                cliente = Cliente.objects.get(pk=cliente_id)
                banco = Banco.objects.get(pk=banco_id)
                tarjeta = Tarjeta.objects.create(
                    cliente=cliente,
                    banco=banco,
                    tipo=tipo,
                    estado=estado,
                    saldo=saldo,
                    fecha_vencimiento=fecha_venc,
                )
                _instrumento_interno(tarjeta)
                _log(request.user.username, 'tarjeta', f'creada: {tarjeta.numero}')
                messages.success(request, f'Tarjeta {tarjeta.numero} creada.')
            else:
                tarjeta.cliente_id = cliente_id
                tarjeta.banco_id = banco_id
                tarjeta.tipo = tipo
                tarjeta.estado = estado
                tarjeta.saldo = saldo
                tarjeta.fecha_vencimiento = fecha_venc
                tarjeta.save()
                _log(request.user.username, 'tarjeta', f'actualizada: {tarjeta.numero}')
                messages.success(request, f'Tarjeta {tarjeta.numero} actualizada.')
            return redirect('panel_tarjetas')
    elif tarjeta is None:
        valores = {
            'cliente': '',
            'banco': '',
            'tipo': 'Visa',
            'estado': 'Activa',
            'saldo': '',
            'fecha_vencimiento': '',
        }
    else:
        valores = {
            'cliente': tarjeta.cliente_id,
            'banco': tarjeta.banco_id,
            'tipo': tarjeta.tipo,
            'estado': tarjeta.estado,
            'saldo': tarjeta.saldo,
            'fecha_vencimiento': tarjeta.fecha_vencimiento.strftime('%Y-%m-%d') if tarjeta.fecha_vencimiento else '',
        }

    return render(request, 'tarjeta_form.html', {
        'tarjeta': tarjeta,
        'valores': valores,
        'modo': 'Editar' if tarjeta else 'Nuevo',
        'clientes': Cliente.objects.all(),
        'bancos': Banco.objects.all(),
        'tipos': Tarjeta.TIPOS,
        'estados': Tarjeta.ESTADOS,
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def tarjeta_estado(request, tarjeta_id):
    if request.method != 'POST':
        return redirect('panel_tarjetas')
    try:
        tarjeta = Tarjeta.objects.get(pk=tarjeta_id)
    except Tarjeta.DoesNotExist:
        messages.error(request, 'Tarjeta no encontrada.')
        return redirect('panel_tarjetas')
    instrumento = getattr(tarjeta, 'instrumento', None)
    if instrumento and (instrumento.movimientos_enviados.exists() or instrumento.movimientos_recibidos.exists()):
        messages.error(request, f'La tarjeta {tarjeta.numero} tiene movimientos registrados; no se puede cambiar su estado.')
    else:
        tarjeta.estado = 'Inactiva' if tarjeta.estado == 'Activa' else 'Activa'
        tarjeta.save(update_fields=['estado'])
        _log(request.user.username, 'tarjeta', f'{tarjeta.numero}: {tarjeta.estado}')
        messages.success(request, f'Tarjeta {tarjeta.numero}: {tarjeta.estado}.')
    return redirect('panel_tarjetas')


# =====================================================================
# CRUD de Instrumentos Financieros (panel propio)
# =====================================================================

@login_required
@user_passes_test(es_staff, login_url='dashboard')
def panel_instrumentos(request):
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    instrumentos = InstrumentoFinanciero.objects.select_related('banco', 'tarjeta')
    if q:
        instrumentos = instrumentos.filter(
            Q(titular__icontains=q)
            | Q(alias__icontains=q)
            | Q(banco__nombre__icontains=q)
        )
    if tipo in ('INTERNO', 'EXTERNO'):
        instrumentos = instrumentos.filter(tipo=tipo)
    return render(request, 'panel_instrumentos.html', {
        'instrumentos': instrumentos,
        'q': q,
        'tipo': tipo,
        'tipos': InstrumentoFinanciero.TIPOS,
        'total': instrumentos.count(),
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def instrumento_form(request, instrumento_id=None):
    instrumento = None
    if instrumento_id is not None:
        try:
            instrumento = InstrumentoFinanciero.objects.select_related('banco', 'tarjeta').get(pk=instrumento_id)
        except InstrumentoFinanciero.DoesNotExist:
            messages.error(request, 'Instrumento no encontrado.')
            return redirect('panel_instrumentos')

    if request.method == 'POST':
        tipo = request.POST.get('tipo', '').strip()
        banco_id = _entero(request.POST.get('banco', '').strip(), None)
        tarjeta_id = _entero(request.POST.get('tarjeta', '').strip(), None)
        titular = request.POST.get('titular', '').strip()
        alias = request.POST.get('alias', '').strip()
        activo = request.POST.get('activo') == 'on'

        errores = []
        tipos_validos = [t[0] for t in InstrumentoFinanciero.TIPOS]
        if tipo not in tipos_validos:
            errores.append('Tipo inválido.')
        if banco_id is None:
            errores.append('Debe seleccionar un banco.')
        else:
            try:
                Banco.objects.get(pk=banco_id)
            except Banco.DoesNotExist:
                errores.append('El banco seleccionado no existe.')
        if tipo == 'INTERNO':
            if tarjeta_id is None:
                errores.append('Para un instrumento interno debe seleccionar una tarjeta.')
            else:
                try:
                    t = Tarjeta.objects.get(pk=tarjeta_id)
                    if hasattr(t, 'instrumento') and t.instrumento_id != (instrumento.pk if instrumento else None):
                        errores.append('Esa tarjeta ya tiene un instrumento asignado.')
                except Tarjeta.DoesNotExist:
                    errores.append('La tarjeta seleccionada no existe.')
        if tipo == 'EXTERNO' and not titular:
            errores.append('El titular es obligatorio para instrumentos externos.')

        if errores:
            for e in errores:
                messages.error(request, e)
            valores = {
                'tipo': tipo,
                'banco': banco_id or '',
                'tarjeta': tarjeta_id or '',
                'titular': titular,
                'alias': alias,
                'activo': activo,
            }
        else:
            if instrumento is None:
                banco = Banco.objects.get(pk=banco_id)
                tarjeta = Tarjeta.objects.get(pk=tarjeta_id) if tarjeta_id else None
                defaults = {
                    'banco': banco,
                    'titular': titular or (str(tarjeta.cliente)[:120] if tarjeta else ''),
                    'alias': alias or (f'Tarjeta {tarjeta.numero[-4:]}' if tarjeta else ''),
                    'activo': activo,
                }
                if tipo == 'INTERNO':
                    defaults['tarjeta'] = tarjeta
                instrumento = InstrumentoFinanciero.objects.create(tipo=tipo, **defaults)
                _log(request.user.username, 'instrumento', f'creado: {instrumento.uuid}')
                messages.success(request, f'Instrumento {instrumento.alias or instrumento.uuid} creado.')
            else:
                instrumento.tipo = tipo
                instrumento.banco_id = banco_id
                instrumento.tarjeta_id = tarjeta_id if tipo == 'INTERNO' else None
                instrumento.titular = titular
                instrumento.alias = alias
                instrumento.activo = activo
                instrumento.save()
                _log(request.user.username, 'instrumento', f'actualizado: {instrumento.uuid}')
                messages.success(request, f'Instrumento {instrumento.alias or instrumento.uuid} actualizado.')
            return redirect('panel_instrumentos')
    elif instrumento is None:
        valores = {
            'tipo': 'INTERNO',
            'banco': '',
            'tarjeta': '',
            'titular': '',
            'alias': '',
            'activo': True,
        }
    else:
        valores = {
            'tipo': instrumento.tipo,
            'banco': instrumento.banco_id,
            'tarjeta': instrumento.tarjeta_id,
            'titular': instrumento.titular,
            'alias': instrumento.alias,
            'activo': instrumento.activo,
        }

    return render(request, 'instrumento_form.html', {
        'instrumento': instrumento,
        'valores': valores,
        'modo': 'Editar' if instrumento else 'Nuevo',
        'bancos': Banco.objects.all(),
        'tarjetas': Tarjeta.objects.all(),
        'tipos': InstrumentoFinanciero.TIPOS,
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def instrumento_estado(request, instrumento_id):
    if request.method != 'POST':
        return redirect('panel_instrumentos')
    try:
        instrumento = InstrumentoFinanciero.objects.get(pk=instrumento_id)
    except InstrumentoFinanciero.DoesNotExist:
        messages.error(request, 'Instrumento no encontrado.')
        return redirect('panel_instrumentos')
    if instrumento.movimientos_enviados.exists() or instrumento.movimientos_recibidos.exists():
        messages.error(request, f'El instrumento {instrumento.alias or instrumento.uuid} tiene movimientos registrados; no se puede desactivar.')
    else:
        instrumento.activo = not instrumento.activo
        instrumento.save(update_fields=['activo'])
        _log(request.user.username, 'instrumento', f'{instrumento.uuid}: {"activo" if instrumento.activo else "inactivo"}')
        messages.success(request, f'Instrumento {instrumento.alias or instrumento.uuid}: {"activado" if instrumento.activo else "desactivado"}.')
    return redirect('panel_instrumentos')


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def panel_clientes(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    clientes = Cliente.objects.select_related('user').prefetch_related('tarjetas')
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q)
            | Q(apellido__icontains=q)
            | Q(rut__icontains=q)
            | Q(email__icontains=q)
        )
    if estado == 'activos':
        clientes = clientes.filter(activo=True)
    elif estado == 'inactivos':
        clientes = clientes.filter(activo=False)
    return render(request, 'panel_clientes.html', {
        'clientes': clientes,
        'q': q,
        'estado': estado,
        'total': clientes.count(),
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def cliente_form(request, cliente_id=None):
    cliente = None
    if cliente_id is not None:
        try:
            cliente = Cliente.objects.select_related('user').get(pk=cliente_id)
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('panel_clientes')

    if request.method == 'POST':
        datos = _datos_cliente(request)
        errores = _validar_cliente(datos, cliente)
        if errores:
            for e in errores:
                messages.error(request, e)
            valores = datos
        else:
            if cliente is None:
                cliente = Cliente.objects.create(**datos)
                _log(request.user.username, 'cliente', f'creado: {cliente}')
                messages.success(request, f'Cliente {cliente} creado.')
            else:
                _guardar_cliente(cliente, datos)
                _log(request.user.username, 'cliente', f'actualizado: {cliente}')
                messages.success(request, f'Cliente {cliente} actualizado.')
            return redirect('panel_clientes')
    elif cliente is None:
        valores = {
            'nombre': '',
            'apellido': '',
            'rut': '',
            'email': '',
            'telefono': '',
            'direccion': '',
            'activo': True,
        }
    else:
        valores = {
            'nombre': cliente.nombre,
            'apellido': cliente.apellido,
            'rut': cliente.rut or '',
            'email': cliente.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'activo': cliente.activo,
        }

    return render(request, 'cliente_form.html', {
        'cliente': cliente,
        'valores': valores,
        'modo': 'Editar' if cliente else 'Nuevo',
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def cliente_estado(request, cliente_id):
    if request.method != 'POST':
        return redirect('panel_clientes')
    try:
        cliente = Cliente.objects.get(pk=cliente_id)
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente no encontrado.')
        return redirect('panel_clientes')
    cliente.activo = not cliente.activo
    cliente.save(update_fields=['activo'])
    _log(request.user.username, 'cliente', f'{cliente}: {"activo" if cliente.activo else "inactivo"}')
    messages.success(request, f'Cliente {cliente} {"activado" if cliente.activo else "desactivado"}.')
    return redirect('panel_clientes')


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def panel_bancos(request):
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    bancos = Banco.objects.annotate(
        n_tarjetas=Count('tarjetas', distinct=True),
        n_instrumentos=Count('instrumentos', distinct=True),
    )
    if q:
        bancos = bancos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    if tipo == 'internos':
        bancos = bancos.filter(es_interno=True)
    elif tipo == 'externos':
        bancos = bancos.filter(es_interno=False)
    return render(request, 'panel_bancos.html', {
        'bancos': bancos,
        'q': q,
        'tipo': tipo,
        'total': bancos.count(),
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def banco_form(request, banco_id=None):
    banco = None
    if banco_id is not None:
        try:
            banco = Banco.objects.get(pk=banco_id)
        except Banco.DoesNotExist:
            messages.error(request, 'Banco no encontrado.')
            return redirect('panel_bancos')

    if request.method == 'POST':
        datos = _datos_banco(request)
        if banco is not None and banco.codigo == 'BEATPAY':
            datos['nombre'] = banco.nombre
            datos['codigo'] = 'BEATPAY'
            datos['es_interno'] = True
            datos['activo'] = True
        errores = _validar_banco(datos, banco)
        if errores:
            for e in errores:
                messages.error(request, e)
            valores = datos
        else:
            if banco is None:
                banco = Banco.objects.create(**datos)
                _log(request.user.username, 'banco', f'creado: {banco.codigo}')
                messages.success(request, f'Banco {banco.nombre} creado.')
            else:
                for campo, valor in datos.items():
                    setattr(banco, campo, valor)
                banco.save()
                _log(request.user.username, 'banco', f'actualizado: {banco.codigo}')
                messages.success(request, f'Banco {banco.nombre} actualizado.')
            return redirect('panel_bancos')
    elif banco is None:
        valores = {
            'nombre': '',
            'codigo': '',
            'es_interno': False,
            'activo': True,
        }
    else:
        valores = {
            'nombre': banco.nombre,
            'codigo': banco.codigo,
            'es_interno': banco.es_interno,
            'activo': banco.activo,
        }

    return render(request, 'banco_form.html', {
        'banco': banco,
        'valores': valores,
        'modo': 'Editar' if banco else 'Nuevo',
        'es_beatpay': bool(banco and banco.codigo == 'BEATPAY'),
    })


@login_required
@user_passes_test(es_staff, login_url='dashboard')
def banco_estado(request, banco_id):
    if request.method != 'POST':
        return redirect('panel_bancos')
    try:
        banco = Banco.objects.get(pk=banco_id)
    except Banco.DoesNotExist:
        messages.error(request, 'Banco no encontrado.')
        return redirect('panel_bancos')
    if banco.es_interno or banco.codigo == 'BEATPAY':
        messages.error(request, 'El banco interno de BeatPay no se puede desactivar.')
    else:
        banco.activo = not banco.activo
        banco.save(update_fields=['activo'])
        _log(request.user.username, 'banco', f'{banco.codigo}: {"activo" if banco.activo else "inactivo"}')
        messages.success(request, f'Banco {banco.nombre} {"activado" if banco.activo else "desactivado"}.')
    return redirect('panel_bancos')
