from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import (
    Banco,
    Cliente,
    Cuenta,
    InstrumentoFinanciero,
    Movimiento,
    Tarjeta,
)

settings.ALLOWED_HOSTS.append('testserver')

User = get_user_model()


class BeatPayAccesoTest(TestCase):
    """Control de acceso a las vistas del panel (etapa 5, 6A, 7)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True, is_superuser=True
        )
        self.cliente_user = User.objects.create_user(
            username='cliente', password='clave123', is_staff=False
        )
        self.cliente = Cliente.objects.create(
            user=self.cliente_user,
            nombre='Cliente Test',
            email='cliente@test.cl',
        )
        Cuenta.objects.create(user=self.cliente_user)
        Tarjeta.objects.create(cliente=self.cliente, saldo=1000)

    def test_anonimo_redirige_a_login(self):
        c = Client()
        for ruta in [
            '/panel/clientes', '/panel/bancos', '/panel/tarjetas',
            '/panel/instrumentos', '/panel/movimientos',
            '/panel/clientes/nuevo', '/panel/bancos/nuevo',
            '/panel/tarjetas/nuevo', '/panel/instrumentos/nuevo',
            '/panel/movimientos/nuevo',
        ]:
            r = c.get(ruta)
            self.assertEqual(r.status_code, 302)
            self.assertTrue(r.url.startswith('/login'))

    def test_cliente_no_staff_redirige_a_dashboard(self):
        c = Client()
        c.force_login(self.cliente_user)
        for ruta in [
            '/panel/clientes', '/panel/bancos', '/panel/tarjetas',
            '/panel/instrumentos', '/panel/movimientos',
        ]:
            r = c.get(ruta)
            self.assertEqual(r.status_code, 302)
            self.assertTrue(r.url.startswith('/dashboard'))

    def test_staff_accede_al_panel(self):
        c = Client()
        c.force_login(self.staff)
        for ruta in ['/panel/clientes', '/panel/bancos', '/panel/tarjetas',
                     '/panel/instrumentos', '/panel/movimientos']:
            r = c.get(ruta)
            self.assertEqual(r.status_code, 200)


class BeatPayClientesTest(TestCase):
    """CRUD de clientes administrativos (etapa 5)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True
        )
        self.c = Client()
        self.c.force_login(self.staff)

    def test_crear_cliente_sin_user(self):
        r = self.c.post('/panel/clientes/nuevo', {
            'nombre': 'Ana', 'apellido': 'Pérez', 'rut': '11.111.111-1',
            'email': 'ana@test.cl', 'telefono': '', 'direccion': '',
            'activo': 'on',
        })
        self.assertEqual(r.status_code, 302)
        cli = Cliente.objects.get(rut='11.111.111-1')
        self.assertEqual(cli.nombre, 'Ana')
        self.assertIsNone(cli.user_id)
        self.assertTrue(cli.activo)

    def test_rechaza_rut_duplicado(self):
        Cliente.objects.create(nombre='Existente', rut='22.222.222-2')
        r = self.c.post('/panel/clientes/nuevo', {
            'nombre': 'Duplicado', 'apellido': '', 'rut': '22.222.222-2',
            'email': 'd@test.cl', 'telefono': '', 'direccion': '', 'activo': 'on',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Cliente.objects.filter(rut='22.222.222-2').count(), 1)

    def test_rechaza_email_invalido(self):
        r = self.c.post('/panel/clientes/nuevo', {
            'nombre': 'Malo', 'apellido': '', 'rut': '',
            'email': 'no-es-email', 'telefono': '', 'direccion': '', 'activo': 'on',
        })
        self.assertFalse(Cliente.objects.filter(nombre='Malo').exists())

    def test_desactivar_y_reactivar_cliente(self):
        cli = Cliente.objects.create(nombre='Desactivable', rut='33.333.333-3')
        r = self.c.post(f'/panel/clientes/{cli.id}/estado')
        self.assertEqual(r.status_code, 302)
        cli.refresh_from_db()
        self.assertFalse(cli.activo)
        self.c.post(f'/panel/clientes/{cli.id}/estado')
        cli.refresh_from_db()
        self.assertTrue(cli.activo)

    def test_editar_cliente_actualiza_campos(self):
        cli = Cliente.objects.create(nombre='Viejo', rut='44.444.444-4')
        r = self.c.post(f'/panel/clientes/{cli.id}/editar', {
            'nombre': 'Nuevo', 'apellido': 'Apellido', 'rut': '44.444.444-4',
            'email': 'nuevo@test.cl', 'telefono': '123', 'direccion': 'Calle',
            'activo': 'on',
        })
        cli.refresh_from_db()
        self.assertEqual(r.status_code, 302)
        self.assertEqual(cli.nombre, 'Nuevo')
        self.assertEqual(cli.email, 'nuevo@test.cl')


class BeatPayBancosTest(TestCase):
    """CRUD de bancos (etapa 5)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True
        )
        self.c = Client()
        self.c.force_login(self.staff)

    def test_crear_banco_externo(self):
        r = self.c.post('/panel/bancos/nuevo', {
            'nombre': 'Banco Test', 'codigo': 'BTST', 'es_interno': '', 'activo': 'on',
        })
        self.assertEqual(r.status_code, 302)
        b = Banco.objects.get(codigo='BTST')
        self.assertEqual(b.nombre, 'Banco Test')
        self.assertFalse(b.es_interno)

    def test_rechaza_nombre_duplicado(self):
        Banco.objects.create(nombre='Dupe', codigo='DUP1', es_interno=False)
        r = self.c.post('/panel/bancos/nuevo', {
            'nombre': 'Dupe', 'codigo': 'OTRO', 'es_interno': '', 'activo': 'on',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Banco.objects.filter(codigo='OTRO').count(), 0)

    def test_rechaza_codigo_invalido(self):
        r = self.c.post('/panel/bancos/nuevo', {
            'nombre': 'Mal Código', 'codigo': 'AA A', 'es_interno': '', 'activo': 'on',
        })
        self.assertFalse(Banco.objects.filter(nombre='Mal Código').exists())

    def test_beatpay_no_se_puede_desactivar(self):
        b = Banco.objects.get(codigo='BEATPAY')
        r = self.c.post(f'/panel/bancos/{b.id}/estado')
        b.refresh_from_db()
        self.assertTrue(b.activo)


class BeatPayTarjetasTest(TestCase):
    """CRUD de tarjetas (etapa 6A)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True
        )
        self.c = Client()
        self.c.force_login(self.staff)
        self.banco = Banco.objects.create(
            nombre='Banco T', codigo='BT', es_interno=False
        )
        self.cliente = Cliente.objects.create(nombre='Cliente T', rut='55.555.555-5')

    def test_crear_tarjeta(self):
        r = self.c.post('/panel/tarjetas/nuevo', {
            'cliente': self.cliente.id, 'banco': self.banco.id,
            'tipo': 'Visa', 'estado': 'Activa', 'saldo': '10000',
            'fecha_vencimiento': '2030-12-31',
        })
        self.assertEqual(r.status_code, 302)
        t = Tarjeta.objects.get(cliente=self.cliente)
        self.assertEqual(t.saldo, 10000)
        self.assertIsNotNone(t.instrumento)

    def test_no_desactivar_tarjeta_con_movimientos(self):
        t = Tarjeta.objects.create(cliente=self.cliente, banco=self.banco, saldo=5000)
        inst = InstrumentoFinanciero.objects.create(
            tipo='INTERNO', banco=self.banco, tarjeta=t,
            titular='X', alias='Y',
        )
        otro = Tarjeta.objects.create(cliente=self.cliente, banco=self.banco, saldo=1000)
        inst2 = InstrumentoFinanciero.objects.create(
            tipo='INTERNO', banco=self.banco, tarjeta=otro,
            titular='Z', alias='W',
        )
        Movimiento.objects.create(origen=inst, destino=inst2, monto=100, estado='Completado')
        r = self.c.post(f'/panel/tarjetas/{t.id}/estado')
        t.refresh_from_db()
        self.assertEqual(t.estado, 'Activa')  # no se desactivó


class BeatPayInstrumentosTest(TestCase):
    """CRUD de instrumentos financieros (etapa 6A)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True
        )
        self.c = Client()
        self.c.force_login(self.staff)
        self.banco = Banco.objects.create(
            nombre='Banco I', codigo='BI', es_interno=False
        )
        self.cliente = Cliente.objects.create(nombre='Cliente I', rut='66.666.666-6')
        self.tarjeta = Tarjeta.objects.create(cliente=self.cliente, banco=self.banco)

    def test_crear_instrumento_interno(self):
        r = self.c.post('/panel/instrumentos/nuevo', {
            'tipo': 'INTERNO', 'banco': self.banco.id, 'tarjeta': self.tarjeta.id,
            'titular': '', 'alias': 'Int Test', 'activo': 'on',
        })
        self.assertEqual(r.status_code, 302)
        inst = InstrumentoFinanciero.objects.get(alias='Int Test')
        self.assertEqual(inst.tipo, 'INTERNO')
        self.assertEqual(inst.tarjeta_id, self.tarjeta.id)

    def test_crear_instrumento_externo(self):
        r = self.c.post('/panel/instrumentos/nuevo', {
            'tipo': 'EXTERNO', 'banco': self.banco.id, 'tarjeta': '',
            'titular': 'Ext Test', 'alias': 'Ext Test', 'activo': 'on',
        })
        self.assertEqual(r.status_code, 302)
        inst = InstrumentoFinanciero.objects.get(alias='Ext Test')
        self.assertEqual(inst.tipo, 'EXTERNO')
        self.assertIsNone(inst.tarjeta_id)
        self.assertEqual(inst.titular, 'Ext Test')

    def test_no_desactivar_instrumento_con_movimientos(self):
        inst = InstrumentoFinanciero.objects.create(
            tipo='EXTERNO', banco=self.banco, titular='Con M', alias='Con M',
        )
        otro = InstrumentoFinanciero.objects.create(
            tipo='EXTERNO', banco=self.banco, titular='Otro', alias='Otro',
        )
        Movimiento.objects.create(origen=inst, destino=otro, monto=100, estado='Completado')
        r = self.c.post(f'/panel/instrumentos/{inst.id}/estado')
        inst.refresh_from_db()
        self.assertTrue(inst.activo)


class BeatPayMovimientosTest(TestCase):
    """CRUD de movimientos (etapa 7)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True
        )
        self.c = Client()
        self.c.force_login(self.staff)
        self.banco = Banco.objects.create(
            nombre='Banco M', codigo='BM', es_interno=False
        )
        cli_o = Cliente.objects.create(nombre='O', rut='77.777.777-7')
        cli_d = Cliente.objects.create(nombre='D', rut='88.888.888-8')
        self.t_o = Tarjeta.objects.create(cliente=cli_o, banco=self.banco, saldo=10000)
        self.t_d = Tarjeta.objects.create(cliente=cli_d, banco=self.banco, saldo=5000)
        self.inst_o = InstrumentoFinanciero.objects.create(
            tipo='INTERNO', banco=self.banco, tarjeta=self.t_o,
            titular='Origen', alias='Origen',
        )
        self.inst_d = InstrumentoFinanciero.objects.create(
            tipo='INTERNO', banco=self.banco, tarjeta=self.t_d,
            titular='Destino', alias='Destino',
        )

    def test_crear_movimiento_completado_aplica_saldo(self):
        r = self.c.post('/panel/movimientos/nuevo', {
            'origen': self.inst_o.id, 'destino': self.inst_d.id,
            'monto': '3000', 'estado': 'Completado', 'descripcion': 'Transferencia',
        })
        self.assertEqual(r.status_code, 302)
        mov = Movimiento.objects.get(descripcion='Transferencia')
        self.t_o.refresh_from_db()
        self.t_d.refresh_from_db()
        self.assertEqual(self.t_o.saldo, 7000)
        self.assertEqual(self.t_d.saldo, 8000)
        self.assertEqual(mov.estado, 'Completado')

    def test_no_crear_movimiento_saldo_insuficiente(self):
        r = self.c.post('/panel/movimientos/nuevo', {
            'origen': self.inst_o.id, 'destino': self.inst_d.id,
            'monto': '999999', 'estado': 'Completado', 'descripcion': 'Sin saldo',
        })
        self.assertFalse(Movimiento.objects.filter(descripcion='Sin saldo').exists())

    def test_no_editar_movimiento_completado(self):
        mov = Movimiento.objects.create(
            origen=self.inst_o, destino=self.inst_d, monto=1000,
            estado='Completado', descripcion='Completado',
        )
        r = self.c.post(f'/panel/movimientos/{mov.id}/editar', {
            'origen': self.inst_o.id, 'destino': self.inst_d.id,
            'monto': '2000', 'estado': 'Completado', 'descripcion': 'Editado',
        })
        mov.refresh_from_db()
        self.assertEqual(mov.descripcion, 'Completado')
        self.assertEqual(mov.monto, 1000)

    def test_cambiar_estado_movimiento(self):
        mov = Movimiento.objects.create(
            origen=self.inst_o, destino=self.inst_d, monto=1000,
            estado='Pendiente', descripcion='Estado',
        )
        self.c.post(f'/panel/movimientos/{mov.id}/estado', {'estado': 'Completado'})
        mov.refresh_from_db()
        self.assertEqual(mov.estado, 'Completado')
        self.t_o.refresh_from_db()
        self.t_d.refresh_from_db()
        self.assertEqual(self.t_o.saldo, 9000)
        self.assertEqual(self.t_d.saldo, 6000)


class BeatPayEmitirCuentaTest(TestCase):
    """Emitir cuenta vinculando cliente administrativo (etapa 6A)."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='clave123', is_staff=True
        )
        self.c = Client()
        self.c.force_login(self.staff)

    def test_emitir_vincula_cliente_existente(self):
        cli = Cliente.objects.create(nombre='Admin Cli', rut='99.999.999-9')
        r = self.c.post('/panel', {
            'action': 'emitir', 'cliente_id': cli.id,
            'nombre': 'Usuario', 'username': 'usuariotest',
            'email': 'u@test.cl', 'pass': 'clave123', 'saldo': '5000', 'pto': '100000',
        })
        cli.refresh_from_db()
        u = User.objects.get(username='usuariotest')
        self.assertEqual(cli.user_id, u.id)
        self.assertEqual(cli.nombre, 'Usuario')
        self.assertIsNotNone(cli.tarjetas.first().instrumento)

    def test_usuario_emitido_puede_iniciar_sesion(self):
        cli = Cliente.objects.create(nombre='Admin Cli 2', rut='11.111.111-1')
        self.c.post('/panel', {
            'action': 'emitir', 'cliente_id': cli.id,
            'nombre': 'Usuario 2', 'username': 'usuariotest2',
            'email': 'u2@test.cl', 'pass': 'clave123', 'saldo': '0', 'pto': '100000',
        })
        c2 = Client()
        r = c2.post('/login', {'username': 'usuariotest2', 'pass': 'clave123'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.url.startswith('/dashboard'))
