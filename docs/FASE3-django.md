# FASE 3 — Django prototipo funcional (en curso)
> Sin base de datos propia todavía: los datos son mock en JSON.

## 1. Estructura
```text
manage.py            control remoto (runserver, migrate)
config/settings.py   apps (pagos, rest_framework), templates/, static/, es-cl, America/Santiago
config/urls.py       /admin/ + delega a pagos/
pagos/views.py       8 vistas (leen demo.json y pasan contexto)
pagos/urls.py        9 rutas (las  de Fase 1, sin tocar links)
pagos/data/demo.json cuenta demo + 4 eventos + 3 transacciones con folio
pagos/models.py      vacío (llega con la DB)
```

## 2. Rutas (todas 200, verificado con pruebas automatizadas)
`/` `index` `register` `login` `dashboard` `cargar`
`pagar` `transacciones` `tarjeta` (+ `admin/`)

## 3. Datos mock → vistas → DTL
- `demo.json`: cuenta (demo@beatpay.cl, $80.000, pto $100.000, Activa), eventos y transacciones.
- `dashboard`: contexto `usuario, saldo, pto, tarjeta, ultimas, tx_json`. Pinta `${{ saldo }}`, badge con `{% if tarjeta == 'Activa' %}` y últimas con `{% for u in ultimas %}{% empty %}`.
- `transacciones`: contexto `transacciones, total_pagos, total_cargas, tx_json`. Tabla con `{% for t %}{% if t.tipo %}{% empty %}` y resumen con filtro `{{ total_pagos|add:total_cargas }}`.
- `index`: mensaje flash (`messages.info` + `{% if messages %}{% for m %}`), contador y lista de eventos (`{{ n_eventos }}`, `{% for e in eventos %}` con `forloop.last`).
- `register`/`login`: `{{ min_pass }}`, `{{ presupuesto_default }}`, `{{ demo_email }}`.
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
