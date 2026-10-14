# BeatPay Virtual — Music Pro S.A. / Music Pro Tour 2026
Plataforma de pago digital: cuenta + tarjeta virtual Visa para conciertos y eventos.

## Qué hace cada archivo/carpeta
```text
manage.py              control: runserver, migrate, shell
requirements.txt       receta de librerías (pip install -r ...)
db.sqlite3            base de datos local (NO se sube, ver .gitignore)
venv/                 ambiente aislado (NO se sube)
BeatPay_Virtual/     ajustes Django: settings.py, urls.py principal
core/                 app núcleo: models.py (Cuenta, Tarjeta, Auditoria),
                      views.py, urls.py, admin.py, forms.py,
                      management/commands/seed_usuarios.py (Faker), migrations/
core/data/demo.json   seed: eventos y transacciones de ejemplo
core/templates/       10 páginas HTML (index, login, register, dashboard,
                      cargar, pagar, transacciones, tarjeta, admin, usuario)
core/static/core/     style.css + app.js únicos (tema minimalista + oscuro)
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
9. `/panel` (como admin) → resumen, solicitudes de cupo, emitir,
   buscar/filtrar usuarios, tarjeta, acceso y detalle por usuario.

## Comandos importantes
```powershell
# --- Ambiente (una vez por PC) ---
python --version                  # revisa que Python exista (3.12+)
python -m venv venv               # crea el ambiente aislado
.\venv\Scripts\Activate.ps1       # lo activa (siempre primero)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned  # solo si Activate da error
pip install -r requirements.txt   # instala todo igual en cualquier PC
pip install Faker                 # suma Faker (luego anótalo en requirements)
pip show Faker                    # ver la versión instalada
deactivate                        # salir del venv

# --- Base de datos ---
python manage.py makemigrations core  # crea migración desde models.py
python manage.py migrate              # la aplica (crea/actualiza tablas)
python manage.py showmigrations       # historial: [X] = aplicada
python manage.py showmigrations core  # solo las de nuestra app
python manage.py createsuperuser      # crea tu admin (usuario, email, clave)
python manage.py dbshell              # consola SQL (.tables, .quit; pide sqlite3 CLI)
python manage.py findstatic core/css/style.css  # dónde encuentra un estático
python manage.py check                 # revisa que el proyecto esté sano

# --- Datos y uso diario ---
python manage.py seed_usuarios 100  # 100 usuarios falsos con Faker (N a gusto)
python manage.py runserver       # prende en http://127.0.0.1:8000/ (Ctrl+C apaga)
python manage.py shell           # consola Django (consultas y arreglos)
```

### Consola Django (`shell`) — lo que más usamos
```python
from django.db import connection
connection.settings_dict["ENGINE"]   # motor usado (sqlite3)
connection.settings_dict["NAME"]     # archivo real (db.sqlite3)
sorted(connection.introspection.table_names())  # tablas reales

from django.contrib.auth.models import User
from core.models import Cuenta, Tarjeta
User.objects.count()                 # cuántos usuarios hay
sorted(User.objects.values_list('username', flat=True))  # listarlos
u = User.objects.get(username='juan')
u.cuenta.saldo                       # saldo por la relación 1-1
u.cuenta.tarjeta.estado              # estado por la doble relación
User.objects.exclude(username__in=['admin', 'juan']).delete()  # borra demos con CASCADE
```

### Base de datos directa (sin dbshell)
```powershell
.\venv\Scripts\python.exe -c 'import sqlite3; print([r[0] for r in sqlite3.connect("db.sqlite3").execute("SELECT name FROM sqlite_master WHERE type = ""table"" ORDER BY name")])'
```

### Git (historial para la evaluación)
```powershell
git status                       # qué cambió
git add -A                        # prepara todo
git commit -m "tipo: qué hiciste" # guarda el cambio con mensaje
git log --oneline                # historial corto
git show --stat HEAD             # qué trajo el último commit
git mv viejo nuevo               # renombrar manteniendo historial
git push                         # sube a GitHub
# Solo la primera vez contra GitHub:
git remote add origin https://github.com/TU-USUARIO/beatpay-virtual.git
git branch -M main
git push -u origin main
```

## Documentos
- `docs/FASE1-diseno.md` — pantallas, reglas UI y cumplimiento del caso.
- `docs/FASE2-modelo-datos.md` — ER, tablas y modelo de datos.
- `docs/FLUJO-sistema-pago.md` — flujos + tabla de errores.
- `docs/DJANGO-instalacion.md` — uso diario y otro PC.
- `docs/FASE3-django.md` — rutas, mock JSON, DTL y GitHub.
