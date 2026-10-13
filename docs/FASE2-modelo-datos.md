# FASE 2 — Modelo de datos BeatPay Virtual
> Diseño en papel. No se instala nada (Django llega en Fase 3).
> Cada entidad nace de lo que la app ya hace hoy con `localStorage`.

## 1. Diagrama entidad-relación
```text
┌─────────────┐        ┌──────────────┐        ┌──────────────┐
│   USUARIO   │1──────1│    CUENTA    │1──────1│   TARJETA    │
│             │ tiene  │              │ posee  │              │
│ id (PK)     │        │ id (PK)      │        │ id (PK)      │
│ nombre      │        │ usuario(FK,U)│        │ cuenta(FK,U) │
│ email (UQ)  │        │ saldo        │        │ numero       │
│ password*   │        │ creado_en    │        │ estado       │
│ presupuesto │        │              │        │ tipo=Visa    │
│ es_admin    │        └──────┬───────┘        └──────────────┘
│ creado_en   │               │1
└─────────────┘               │ tiene N
                              │
┌──────────────┐        ┌─────┴────────┐
│ EVENTO       │1──────N│ TRANSACCION  │
│              │ ocurre │              │
│ id (PK)      │        │ id (PK)      │
│ nombre       │        │ cuenta(FK)   │
│ lugar        │        │ evento(FK,#) │
│ fecha        │        │ tipo         │
└──────────────┘        │ monto        │
                        │ saldo_antes  │
                        │ saldo_nuevo  │
                        │ estado       │
                        │ folio (UQ)   │
                        │ fecha        │
                        └──────────────┘
PK = primaria | UQ = única | # = puede ser nulo (cargas sin evento)
* password siempre con hash, jamás en texto (Django lo hace solo)
```

## 2. Tablas y campos
### USUARIO
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| nombre | Char(100) | mín 2 caracteres (como `doReg`) |
| email | EmailField único | con @, login por email |
| password | Hash | mín 6 (Django `set_password`) |
| presupuesto | Integer ≥ 0 | default 100000, vacío = default |
| es_admin | Boolean | False = normal, True = ve todo |
| creado_en | DateTime auto | — |

### CUENTA (1 por usuario)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| usuario | OneToOne → Usuario | un usuario = una cuenta |
| saldo | Integer ≥ 0 | default 80000, jamás negativo |
| creado_en | DateTime auto | — |

### TARJETA (1 por cuenta)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| cuenta | OneToOne → Cuenta | — |
| numero | Char(19) | se muestra **** **** **** 1234 |
| estado | Char(10) | Activa \| Bloqueada (default Activa) |
| tipo | Char(10) | default "Visa" |

### EVENTO (comercios y conciertos)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| nombre | Char(120) | ej: Music Pro Tour |
| lugar | Char(120) | opcional |
| fecha | Date | opcional |

### TRANSACCION (historial, solo crece: no se edita ni borra)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| cuenta | FK → Cuenta | dueña del movimiento |
| evento | FK → Evento (nulo) | nulo en CARGA |
| tipo | Char(5) | CARGA \| PAGO |
| monto | Integer ≥ 1000 | validado antes de guardar |
| saldo_antes | Integer | para la boleta |
| saldo_nuevo | Integer | saldo_antes ± monto |
| estado | Char(10) | default Aprobado |
| folio | Char(10) único | BP-XXXXXX de la boleta |
| fecha | DateTime auto | — |

## 3. De `localStorage` y `demo.json` al modelo
| Hoy (navegador / JSON) | Mañana (modelo) |
|---|---|
| `beatpay_user`, `beatpay_nombre` / `cuenta.usuario`, `cuenta.nombre` | USUARIO.email, USUARIO.nombre |
| `beatpay_pto` / `cuenta.presupuesto` | USUARIO.presupuesto |
| `beatpay_saldo` / `cuenta.saldo` | CUENTA.saldo |
| `beatpay_tarjeta` / `cuenta.tarjeta` | TARJETA.estado |
| `beatpay_tx[]` / `transacciones[]` | TRANSACCION (una fila por elemento) |
| folio `BP-XXXXXX` (boleta y JSON) | TRANSACCION.folio único |
| `eventos[]` del JSON | EVENTO (una fila por nombre) |

## 4. Reglas que el modelo debe garantizar (vienen de la app)
1. `monto >= 1000` en CARGA y PAGO.
2. PAGO exige `TARJETA.estado = Activa`.
3. PAGO exige `CUENTA.saldo >= monto` (el saldo jamás queda negativo).
4. Alerta (no bloqueo): si `sum(PAGO) + monto > USUARIO.presupuesto` → "Te pasaste del presupuesto".
5. `email` único; `folio` único; TRANSACCION inmutable.
6. Normal ve solo su CUENTA; admin (`es_admin`) ve todas (flujo 7 del doc de flujo).

## 5. Referencia `models.py` (igual a `core/models.py`)
> Ojo: TARJETA es tabla propia (no campo de CUENTA) y no hay EVENTO/TRANSACCION en DB (demo en JSON hasta Eval 3).
```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    presupuesto = models.PositiveIntegerField(default=100000)
    es_admin = models.BooleanField(default=False)
    def __str__(self): return self.email

class Cuenta(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cuenta')
    saldo = models.PositiveIntegerField(default=80000)
    creado_en = models.DateTimeField(auto_now_add=True)

class Tarjeta(models.Model):
    ESTADOS = [('Activa', 'Activa'), ('Bloqueada', 'Bloqueada')]
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name='tarjeta')
    numero = models.CharField(max_length=19, default='**** **** **** 1234')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activa')
    tipo = models.CharField(max_length=10, default='Visa')

class Evento(models.Model):
    nombre = models.CharField(max_length=120)
    lugar = models.CharField(max_length=120, blank=True)
    fecha = models.DateField(null=True, blank=True)
    def __str__(self): return self.nombre

class Transaccion(models.Model):
    TIPOS = [('CARGA', 'Carga'), ('PAGO', 'Pago')]
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones')
    evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=5, choices=TIPOS)
    monto = models.PositiveIntegerField()
    saldo_antes = models.PositiveIntegerField()
    saldo_nuevo = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, default='Aprobado')
    folio = models.CharField(max_length=10, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-fecha']
```