# Guía Django — BeatPay Virtual
> Estado: Fase 3 en curso. El ambiente ya está creado en este PC.
> Este documento explica cómo usarlo cada día y cómo llevar el trabajo a otro PC.

## 1. Qué es cada cosa (en simple)
- **Python:** el lenguaje. Todo corre sobre él. Revisa que exista con `python --version`.
- **Ambiente virtual (`venv/`):** cajita aislada con las librerías solo de este proyecto. Ya está creada. No se borra, no se comparte, no se mete a zip.
- **Django:** el backend que pide tu caso (rutas, vistas, login, base de datos, panel admin).
- **`requirements.txt`:** la receta: lista exacta de librerías y versiones. Sirve para instalar todo igual en otro PC.
- **`manage.py`:** el control remoto del proyecto (prender servidor, migrar, crear cosas).
- **Flask:** NO se usa en este proyecto. No lo instales.

## 2. Uso diario (en este PC, cada vez que trabajes)
En la terminal de VS Code, parado en la carpeta `BeatPay Virtual`:
```powershell
# 1. Activar el ambiente (siempre primero)
.\venv\Scripts\Activate.ps1

# 2. Prender la página
python manage.py runserver
# Abrir http://127.0.0.1:8000/  (apagar con Ctrl+C)
```
Si `Activate.ps1` da error de permisos, una sola vez:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 3. Compartir el trabajo (qué pasar y qué NO)
Para enviarlo (pendrive, Drive, zip, GitHub) incluye:
- `BeatPay_Virtual/`, `core/` (con `core/templates/` y `core/static/` dentro), `docs/`
- `manage.py`, `requirements.txt`
- (`db.sqlite3` se regenera con `migrate`, no se comparte)

**NO incluyas `venv/`** (pesa mucho y no funciona en otro PC; se recrea allá).

## 4. Abrir el trabajo en otro PC (para que funcione)
Requisitos allá: Python 3.12+ y VS Code con extensión Python.
```powershell
# 1. Entrar a la carpeta copiada
# 2. Crear el ambiente nuevo (una sola vez por PC)
python -m venv venv

# 3. Activarlo
.\venv\Scripts\Activate.ps1

# 4. Instalar todo igual que acá (usa la receta)
pip install -r requirements.txt

# 5. Preparar la base de datos
python manage.py migrate

# 6. Prender
python manage.py runserver
# Abrir http://127.0.0.1:8000/
```
En VS Code además: `Ctrl+Shift+P` → `Python: Select Interpreter` → elegir `.\venv\Scripts\python.exe`.

## 5. Si algo falla
| Problema | Qué hacer |
|---|---|
| `django-admin` / `python` no se reconoce | Python no está instalado o no está en el PATH (reinstala marcando "Add to PATH") |
| `Activate.ps1` no se puede cargar | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `pip` instala pero Django no aparece | Hay 2 Python: usa `python -m pip install -r requirements.txt` |
| Página 404 en `dashboard` u otra | Faltan rutas: revisa `core/urls.py` (ya están las 10 creadas) |
| `db.sqlite3` no existe allá | Corre `python manage.py migrate` (paso 5 de arriba) |
| Los cambios no se ven en el navegador | `Ctrl+F5` (caché). Al HTML/CSS/JS no hay que reiniciar nada |
