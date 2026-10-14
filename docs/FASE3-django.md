# FASE 3 — Django prototipo funcional (listo)
> Modelos + auth real con DB (`Cuenta`, `Tarjeta`, `Transaccion`, `Auditoria`) y mock JSON (`demo.json`) solo para eventos.

## 1. Estructura
```text
manage.py            control remoto (runserver, migrate)
BeatPay_Virtual/settings.py   app core, es-cl, America/Santiago, LOGIN_URL
BeatPay_Virtual/urls.py       /admin/ + delega a core/
core/views.py        11 vistas (DB + demo.json de eventos, contextos al HTML)
core/forms.py        RegistroForm, LoginForm, EmisionForm (validación centralizada)
core/urls.py         11 rutas con name (links con {% url %})
core/templates/      10 HTML (como la corrección del profe)
core/data/demo.json 4 eventos (las transacciones son reales en DB)
core/models.py      Cuenta (user, saldo, presupuesto, solicitud) + Tarjeta (cuenta 1-1, numero, estado, tipo) + Auditoria
```

## 2. Rutas (todas 200, verificado con pruebas automatizadas)
`/` `register` `login` `logout` `dashboard` `cargar`
`pagar` `transacciones` `tarjeta` `panel` `panel/usuario/<id>` (+ `admin/`)

## 3. DB → vistas → DTL
- `demo.json`: solo los 4 eventos (para el select de pagar y el landing).
- `dashboard`: `usuario, saldo, pto, tarjeta, ultimos4, solicitud, ultimas` (transacciones reales del usuario).
- `cargar`/`pagar`: POST al servidor, validan y crean `Transaccion` con folio único; devuelven `boleta` (folio, antes, nuevo).
- `transacciones`: solo las del usuario, filtro y búsqueda por GET en el servidor.
- `tarjeta`: `numero` real + `estado`; el botón bloquea/activa por POST.
- `panel` (staff): resumen con sumas Python, solicitudes, emitir, buscar/filtrar; `usuario_detalle`: cuenta, acciones y su auditoría.
- `register`: crea `User` + `Cuenta` + `Tarjeta` con número único y entra solo.
- Bucles y sumas explícitos en Python (`for`/`if`, `sum`, filtros ORM).
- El JS solo ayuda visualmente (clave, tema, txt de boleta); todo lo funcional es servidor.

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
