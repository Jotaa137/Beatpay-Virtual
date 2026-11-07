from django.db import migrations


def crear_instrumentos(apps, schema_editor):
    Banco = apps.get_model('core', 'Banco')
    InstrumentoFinanciero = apps.get_model('core', 'InstrumentoFinanciero')
    Tarjeta = apps.get_model('core', 'Tarjeta')

    beatpay, _ = Banco.objects.get_or_create(
        codigo='BEATPAY',
        defaults={'nombre': 'BeatPay', 'es_interno': True, 'activo': True},
    )
    for tarjeta in Tarjeta.objects.filter(instrumento__isnull=True).select_related('cliente'):
        InstrumentoFinanciero.objects.create(
            tipo='INTERNO',
            banco_id=beatpay.id,
            tarjeta_id=tarjeta.id,
            titular=str(tarjeta.cliente)[:120],
            alias=f'Tarjeta {tarjeta.numero[-4:]}',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_cuenta_saldo_remove_tarjeta_cuenta_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_instrumentos, migrations.RunPython.noop),
    ]
