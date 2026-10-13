# BeatPay Virtual — Music Pro S.A. / Music Pro Tour 2026
Plataforma de pago digital: cuenta + tarjeta virtual Visa para conciertos y eventos.

## Qué hace cada archivo/carpeta
```text
manage.py              control: runserver, migrate, shell
requirements.txt       receta de librerías (pip install -r ...)
db.sqlite3            base de datos local (NO se sube, ver .gitignore)
venv/                 ambiente aislado (NO se sube)
config/               ajustes Django: settings.py, urls.py principal
core/                 app núcleo BeatPay: models.py (Cuenta), views.py, urls.py,
                      admin.py, migrations/
core/data/demo.json   seed: eventos y transacciones de ejemplo
core/templates/       9 páginas HTML (index, login, register, dashboard,
                      cargar, pagar, transacciones, tarjeta, admin)
static/css/           style.css único (tema minimalista Bootstrap)
static/js/            app.js único (secciones: estado, clave, pagos, boleta)
docs/                 documentación por fase (índice abajo)
```

## Cómo correr
```powershell
# Solo la primera vez en cada PC
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate

# Uso diario
.\venv\Scripts\Activate.ps1
python manage.py runserver
# http://127.0.0.1:8000/
```

## Cuentas demo (clave ambas: beatpay123)
- admin → `admin` (staff, entra a `/panel`)
- usuario → `juan` (entra a su `dashboard`)

## Demo en 2 minutos (para la revisión)
1. `/` → landing con Iniciar sesión / Crear cuenta (+ botón 🌙 modo oscuro).
2. `/register` → crea tu usuario (presupuesto vacío = $100.000).
3. `dashboard` → tu saldo, tarjeta y últimos movimientos (los pinta el servidor).
4. Operaciones → transfiere a otro usuario y pide aumento de cupo.
5. `cargar` → carga $50.000, confirma, descarga la boleta txt.
6. `pagar` → paga y mira el aviso si te pasas del presupuesto.
7. `transacciones` → filtra, busca y revisa el resumen.
8. `tarjeta` → bloquea, intenta pagar (error), reactiva.
9. `/panel` (como admin) → resumen + gráficos, solicitudes de cupo,
   buscar/filtrar usuarios, tarjeta, staff y acceso.

## Documentos
- `docs/FASE1-diseno.md` — pantallas, reglas UI y cumplimiento del caso.
- `docs/FASE2-modelo-datos.md` — ER, tablas y modelo de datos.
- `docs/FLUJO-sistema-pago.md` — flujos + tabla de errores.
- `docs/DJANGO-instalacion.md` — uso diario y otro PC.
- `docs/FASE3-django.md` — rutas, mock JSON, DTL y GitHub.
