# BeatPay Virtual — Music Pro S.A. / Music Pro Tour 2026
Plataforma de pago digital: cuenta + tarjeta virtual Visa para conciertos y eventos.

## Estado por fase
| Fase | Estado |
|---|---|
| 1 Diseño e interfaz | ✅ cerrada (ver `docs/FASE1-diseno.md`) |
| 2 Modelo de datos | ✅ diseñada, falta dibujar ER en Draw.io (`docs/FASE2-modelo-datos.md`) |
| 3 Django funcional | 🟡 rutas + JSON mock + DTL listos; faltan modelos, login real y admin |
| 5 API REST + JWT | ⏳ DRF instalado, sin implementar |

## Qué hace cada archivo/carpeta
```text
manage.py              control remoto: runserver, migrate
requirements.txt       receta de librerías (pip install -r ...)
db.sqlite3            base de datos (hoy solo tablas internas Django)
venv/                 ambiente aislado (NO se comparte ni se sube)
.gitignore            excluye venv/ y db.sqlite3 del repo
config/               ajustes Django: settings.py, urls.py principal
pagos/                app BeatPay: views.py, urls.py, models.py (vacío), data/demo.json
templates/            8 páginas HTML (index, login, register, dashboard,
                      cargar, pagar, transacciones, tarjeta) + base.html
static/css/           style.css (tema gamer RGB + modo claro)
static/js/            app.js (núcleo) · auth.js (login/registro) ·
                      pagos.js (cuenta/carga/pago/historial) ·
                      efectos.js (fondos 3D, gato, tema)
docs/                 documentación por fase (índice abajo)
```

## Cómo correr
```powershell
# Solo la primera vez en cada PC (crea el ambiente e instala todo)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate

# Uso diario
.\venv\Scripts\Activate.ps1
python manage.py runserver
# http://127.0.0.1:8000/
```

## Demo en 2 minutos (para la revisión)
1. `/register.html` → regístrate (presupuesto vacío = $100.000).
2. `dashboard.html` → ve saldo $80.000 y tarjeta Activa.
3. `cargar.html` → carga $50.000, confirma, descarga la boleta txt.
4. `pagar.html` → paga $120.000 y mira el aviso "Te pasaste del presupuesto".
5. `transacciones.html` → filtra, busca y revisa el resumen.
6. `tarjeta.html` → bloquea, intenta pagar (error), reactiva.
7. Cambia a modo claro ☀️ y repite 3-4.

## Documentos
- `docs/FASE1-diseno.md` — pantallas, reglas UI y cumplimiento Fase 1.
- `docs/FASE2-modelo-datos.md` — ER, tablas y `models.py` de referencia.
- `docs/FLUJO-sistema-pago.md` — flujos + tabla de errores (para dibujar el diagrama).
- `docs/DJANGO-instalacion.md` — uso diario, compartir y otro PC.
- `docs/FASE3-django.md` — rutas, mock JSON, DTL y GitHub.
