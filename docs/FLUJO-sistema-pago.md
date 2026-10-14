# Flujo del sistema de pago — BeatPay Virtual
> Todo validado en el servidor. Versión oficial: **un solo diagrama en ciclo**.

## 0. Diagrama único (el que se dibuja)
```text
[INICIO] → login/registro (¿datos válidos? NO→error) → ¿rol? → DASHBOARD o PANEL
  ├─ cargar (¿monto ≥1000?) → suma → boleta → DASHBOARD
  ├─ pagar (¿Activa? ¿monto ok? ¿saldo ok?) → resta → boleta → DASHBOARD
  ├─ historial (filtrar/buscar en servidor) → DASHBOARD
  ├─ tarjeta (bloquear/activar en servidor) → DASHBOARD
  └─ panel (solo staff): resumen, solicitudes, emitir, usuarios → detalle
```

## 1. Flujo general de navegación
```text
[INICIO index]
  ├─ Crear cuenta → register (nombre, usuario, email, clave, pto) → dashboard
  ├─ Iniciar sesión → login (usuario + clave) → dashboard (normal) o panel (staff)
  └─ dashboard: Cargar, Pagar, Transacciones, Tarjeta, Operaciones (transferir, pedir cupo)
```

## 2. Registro e inicio de sesión
```text
[INICIO]
  → ingresar nombre, usuario, email, password (+ presupuesto opcional)
  → ¿datos válidos? (nombre ≥2, usuario ≥3 sin @, email con @, password ≥6) ─NO→ error
  → SÍ → crear User + Cuenta ($0) + Tarjeta Activa → ir a dashboard → cargar fondos
Login: usuario + password → ¿existe y es correcta? ─NO→ error ─SÍ→ según rol
```

## 3. Cargar fondos (servidor)
```text
→ ver saldo actual (servidor)
→ ingresar monto → ¿monto >= $1.000? ─NO→ "Monto mínimo $1.000."
→ SÍ → nuevo_saldo = saldo + monto → guardar TRANSACCION CARGA con folio
→ boleta con folio + "Carga exitosa. Nuevo saldo: $X"
```

## 4. Realizar pago (servidor)
```text
1. ¿tarjeta = Activa? ─NO→ "Tu tarjeta no está activa.", FIN
2. elegir evento + monto → ¿monto >= $1.000? ─NO→ error, FIN
3. ¿saldo >= monto? ─NO→ "Saldo insuficiente...", FIN
4. si monto > presupuesto → aviso "Te pasaste del presupuesto..." (igual se paga)
5. nuevo_saldo = saldo - monto → guardar TRANSACCION PAGO con folio
6. boleta con folio + "Pago aprobado..."
```

## 5. Administrar tarjeta virtual
```text
→ ver número real + estado
→ botón Bloquear/Activar (POST al servidor) → queda registrado
→ solo Activa permite pagar y transferir
Estados: Activa | Bloqueada
```

## 6. Historial de transacciones (servidor, por usuario)
```text
→ listar las suyas (más recientes primero, con folio)
→ filtrar por tipo + buscar por evento (GET al servidor)
→ resumen: total Pagos $X | total Cargas $Y
Cada fila: folio | fecha | evento | monto | tipo | estado
```

## 7. Flujo admin
```text
[login staff] → /panel: resumen, solicitudes de cupo, emitir tarjeta,
buscar/filtrar usuarios → [Ver] → detalle del usuario:
cuenta, tarjeta, acciones (tarjeta, acceso, presupuesto, cupo, eliminar)
+ su auditoría. Todo con mensajes y registro en auditoría.
```

## 8. Tabla de errores del sistema
| Caso | Mensaje | Efecto en saldo |
|---|---|---|
| Monto < $1.000 | "Monto mínimo $1.000." | No cambia |
| Tarjeta Bloqueada al pagar | "Tu tarjeta no está activa." | No cambia |
| Saldo insuficiente | "Saldo insuficiente. Tienes $X." | No cambia |
| Sobre presupuesto | "Te pasaste del presupuesto..." | Se paga igual |
| Carga válida | "Carga exitosa. Nuevo saldo: $X" | Suma |
| Pago válido | "Pago aprobado por $X..." | Resta |
| Transferencia válida | "Transferiste $X a..." | Mueve entre cuentas |

## 9. Cómo presentarlo en el informe
1. Dibuja: INICIO → login → rol → dashboard/panel → ramas que vuelven → FIN.
2. Rombo solo para las preguntas (datos, monto, tarjeta, saldo) con SÍ/NO.
3. Anexa la tabla de errores (punto 8).
