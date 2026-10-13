# FASE 3 — Django prototipo funcional (listo)
> Modelos + auth real con DB (`Cuenta`) y mock JSON (`demo.json`) para eventos y transacciones.

## 1. Estructura
```text
manage.py            control remoto (runserver, migrate)
BeatPay_Virtual/settings.py   app core, es-cl, America/Santiago, LOGIN_URL
BeatPay_Virtual/urls.py       /admin/ + delega a core/
core/views.py        10 vistas (leen demo.json + DB y pasan contexto)
core/forms.py        RegistroForm, LoginForm, EmisionForm (validación centralizada)
core/urls.py         10 rutas con name (links con {% url %})
core/templates/      9 HTML (como la corrección del profe)
core/data/demo.json  4 eventos + 3 transacciones con folio
core/models.py      Cuenta (user, saldo, presupuesto, solicitud) + Tarjeta (cuenta 1-1, numero, estado, tipo) + Auditoria
```

## 2. Rutas (todas 200, verificado con pruebas automatizadas)
`/` `index` `register` `login` `logout` `dashboard` `cargar`
`pagar` `transacciones` `tarjeta` `panel` (+ `admin/`)

## 3. Datos mock → vistas → DTL
- `demo.json`: cuenta (demo@beatpay.cl, $80.000, pto $100.000, Activa), eventos y transacciones.
- `dashboard`: contexto `usuario, saldo, pto, tarjeta, ultimas, tx_json`. Pinta `${{ saldo }}`, badge con `{% if tarjeta == 'Activa' %}` y últimas con `{% for u in ultimas %}{% empty %}`.
- `transacciones`: contexto `transacciones, total_pagos, total_cargas, tx_json`. Tabla con `{% for t %}{% if t.tipo %}{% empty %}` y resumen con filtro `{{ total_pagos|add:total_cargas }}`.
- `index`: contador y lista de eventos (`{{ n_eventos }}`, `{% for e in eventos %}` con `forloop.last`) + `{% if messages %}{% for m %}`.
- `register`: `{{ min_pass }}`, `{{ presupuesto_default }}`; crea `User` + `Cuenta` y entra solo.
- `login`: usuario + clave (`authenticate`), error con `messages`, demo visibles.
- `cargar`/`pagar`: `{{ monto_min }}`, `{{ monto_default }}`; select de eventos con `{% for e in eventos %}`.
- `tarjeta`: `{{ tipo }}` + badge con `{% if %}`.
- Bucles y sumas explícitos en Python (`for`/`if` en `transacciones` y `dashboard`).
- El JS siembra `localStorage` desde el JSON del servidor si está vacío: una sola fuente de datos para DTL y JS.

## 4. Uso diario
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
# http://127.0.0.1:8000/
```

## 5. Subir a GitHub (repositorio público, con tu cuenta)
```powershell
# 1. Parado en la carpeta del proyecto (una sola vez)
git init
git add .
git commit -m "BeatPay Virtual Fase 3"

# 2. En github.com crea el repo (vacío, sin README) y conecta:
git remote add origin https://github.com/TU-USUARIO/beatpay-virtual.git
git branch -M main
git push -u origin main
```
Ojo: `venv/` pesa miles de archivos — ideal es un `.gitignore` con `venv/` y `db.sqlite3` antes del `add`.
