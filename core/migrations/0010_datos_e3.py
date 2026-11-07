from django.db import migrations


def crear_datos(apps, schema_editor):
    """Migra Cuenta.saldo -> Tarjeta.saldo y crea clientes, banco e instrumentos."""
    Banco = apps.get_model('core', 'Banco')
    Cliente = apps.get_model('core', 'Cliente')
    Cuenta = apps.get_model('core', 'Cuenta')
    Tarjeta = apps.get_model('core', 'Tarjeta')
    InstrumentoFinanciero = apps.get_model('core', 'InstrumentoFinanciero')

    beatpay, _ = Banco.objects.get_or_create(
        codigo='BEATPAY',
        defaults={'nombre': 'BeatPay', 'es_interno': True, 'activo': True},
    )

    def cliente_de(user):
        cliente, _ = Cliente.objects.get_or_create(
            user_id=user.id,
            defaults={
                'nombre': user.first_name or user.username,
                'apellido': user.last_name,
                'email': user.email,
                'activo': True,
            },
        )
        return cliente

    def instrumento_de(tarjeta, cliente):
        InstrumentoFinanciero.objects.get_or_create(
            tarjeta_id=tarjeta.id,
            defaults={
                'tipo': 'INTERNO',
                'banco_id': beatpay.id,
                'titular': str(cliente)[:120],
                'alias': f'Tarjeta {tarjeta.numero[-4:]}',
                'activo': True,
            },
        )

    # 1) Tarjetas existentes: dueño (cliente), banco emisor y saldo desde la cuenta.
    for tarjeta in Tarjeta.objects.select_related('cuenta__user').all():
        cuenta = tarjeta.cuenta
        cliente = cliente_de(cuenta.user)
        tarjeta.cliente_id = cliente.id
        tarjeta.banco_id = beatpay.id
        tarjeta.saldo = cuenta.saldo
        tarjeta.save(update_fields=['cliente', 'banco', 'saldo'])
        instrumento_de(tarjeta, cliente)

    # 2) Cuentas sin tarjeta: crear la tarjeta que antes se generaba al vuelo.
    for cuenta in Cuenta.objects.select_related('user').all():
        if Tarjeta.objects.filter(cuenta_id=cuenta.id).exists():
            continue
        cliente = cliente_de(cuenta.user)
        tarjeta = Tarjeta.objects.create(
            cuenta_id=cuenta.id,
            cliente_id=cliente.id,
            banco_id=beatpay.id,
            saldo=cuenta.saldo,
        )
        instrumento_de(tarjeta, cliente)


def borrar_datos(apps, schema_editor):
    """Reverso conservador: solo elimina el banco interno si quedó sin uso."""
    Banco = apps.get_model('core', 'Banco')
    Banco.objects.filter(codigo='BEATPAY', tarjetas__isnull=True, instrumentos__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_banco_alter_tarjeta_options_tarjeta_fecha_emision_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_datos, borrar_datos),
    ]
