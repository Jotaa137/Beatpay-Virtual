# FASE 2 — Modelo de datos BeatPay Virtual
> Refleja `core/models.py` tal como está implementado (ver diagrama en `docs/db-diagrama.png`).

## 1. Diagrama entidad-relación
```text
┌──────────────┐1──────1┌──────────────┐1──────1┌──────────────┐
│   auth_user  │ tiene  │  core_cuenta │ posee  │ core_tarjeta │
│  (Django)    │        │              │        │              │
│ id (PK)      │        │ id (PK)      │        │ id (PK)      │
│ username(UQ) │        │ user_id(FK,U)│        │ cuenta_id(FK,U)
│ first/last  │        │ saldo        │        │ numero       │
│ email        │        │ presupuesto  │        │ estado       │
│ password*    │        │ solicitud    │        │ tipo=Visa    │
│ is_staff     │        └──────────────┘        └──────────────┘
│ is_active    │
└──────────────┘
* password con hash (Django lo hace solo)

┌──────────────────┐
│ core_auditoria   │  suelta: usuario, accion, detalle, fecha
│ id (PK)          │  (sin FK, es solo registro)
└──────────────────┘

┌──────────────────┐
│core_transaccion  │  historial real por cuenta
│ id (PK)          │  cuenta(FK)→core_cuenta, evento texto,
│                  │  monto, tipo, estado, folio(UQ),
│                  │  saldo_antes, saldo_nuevo, fecha
└──────────────────┘
PK = primaria | UQ = única
```

## 2. Tablas y campos
### auth_user (Django, no se define en `models.py`)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| username | Char único | mín 3, sin espacios ni @, login con este campo |
| first_name / last_name | Char | nombre y apellido |
| email | EmailField | con @ |
| password | Hash | mín 6 (`set_password`) |
| is_staff | Boolean | True = ve `/panel` |
| is_active | Boolean | False = bloqueado, no entra |

### core_cuenta (1 por usuario)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| user | OneToOne → User | un usuario = una cuenta |
| saldo | Integer ≥ 0 | default 80000, jamás negativo |
| presupuesto | Integer ≥ 0 | default 100000 (tope de gasto) |
| solicitud_cupo | Integer nulo | pedido pendiente de aumento |

### core_tarjeta (1 por cuenta)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| cuenta | OneToOne → Cuenta | — |
| numero | Char(19) único | se genera al crear, se muestra completo al dueño |
| estado | Char(10) | Activa \| Bloqueada (default Activa) |
| tipo | Char(10) | default "Visa" |

### core_transaccion (historial real, solo crece)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| cuenta | FK → Cuenta | dueña del movimiento |
| evento | Char(120) | nombre del evento o transferencia |
| tipo | Char(5) | CARGA \| PAGO |
| monto | Integer ≥ 1000 | validado antes de guardar |
| saldo_antes / saldo_nuevo | Integer | para la boleta |
| estado | Char(10) | default Aprobado |
| folio | Char(10) único | BP-XXXXXX de la boleta |
| fecha | DateTime auto | — |

### core_auditoria (registro, solo crece)
| Campo | Tipo | Reglas |
|---|---|---|
| id | AutoField PK | — |
| usuario / accion / detalle | Char | quién hizo qué |
| fecha | DateTime auto | ordenada descendente |

## 3. Reglas que el modelo garantiza (vienen de la app)
1. `monto >= 1000` en CARGA, PAGO y transferencias.
2. PAGO exige tarjeta `Activa` (validado en el servidor).
3. PAGO exige `saldo >= monto` (el saldo jamás queda negativo).
4. Aviso (no bloqueo): si `monto > presupuesto` → "Te pasaste del presupuesto".
5. `username` único; `folio` único; TRANSACCION y AUDITORIA inmutables.
6. Normal ve solo su CUENTA; staff (`is_staff`) ve `/panel`.
7. Borrar usuario arrastra cuenta + tarjeta (CASCADE); la auditoría queda.

## 4. Migraciones (historial real)
0001 crea `Cuenta` → 0002 agrega `solicitud_cupo` → 0003 crea `Auditoria` → 0004 crea `Tarjeta` (saca el campo viejo) → 0005/0006 crean `Transaccion` (+ saldos).
