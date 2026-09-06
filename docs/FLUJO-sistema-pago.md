# Flujo del sistema de pago — BeatPay Virtual
> Cómo debe ir el flujo de la aplicación web de pago que exige el proyecto.
> Versión oficial: **un solo diagrama en ciclo**. Abajo el detalle por rama.

## 0. Diagrama único (el que se dibuja)
```text
[INICIO] → login/registro (¿datos válidos? NO→error) → [DASHBOARD]
  ├─ cargar (¿monto ≥1000? ¿confirma?) → suma → boleta → DASHBOARD
  ├─ pagar (¿Activa? ¿monto ok? ¿saldo ok? ¿confirma?) → resta → boleta → DASHBOARD
  ├─ historial (filtrar/buscar) → DASHBOARD
  └─ tarjeta (bloquear/activar) → DASHBOARD → [FIN]
```
Símbolos: óvalo = inicio-fin, rectángulo = proceso, rombo = las 4 preguntas, flechas SÍ/NO rotuladas.

## 1. Flujo general de navegación
```text
[INICIO index]
  ├─ Crear cuenta → register → dashboard
  ├─ Iniciar sesión → login → dashboard
  └─ Ver cuenta demo → dashboard
        ├─ Cargar fondos → dashboard (saldo actualizado)
        ├─ Realizar pago → dashboard (saldo actualizado)
        ├─ Ver transacciones (filtro + buscador)
        └─ Administrar tarjeta (bloquear / activar)
```

## 2. Registro e inicio de sesión
```text
[INICIO]
  → ingresar nombre, email, password (+ presupuesto opcional)
  → ¿datos válidos? (nombre ≥2, email con @, password ≥6) ─NO→ mostrar error, volver
  → SÍ → crear cuenta + tarjeta virtual Activa + saldo inicial
  → ir a dashboard
[FIN]

Login: email + password → ¿existe y es correcta? ─NO→ error ─SÍ→ dashboard
```

## 3. Cargar fondos (modifica el saldo)
```text
[INICIO en dashboard]
  → ver saldo actual
  → ingresar monto
  → ¿monto >= $1.000? ─NO→ error "Monto mínimo $1.000", volver
  → SÍ → pedir confirmación ─NO→ FIN (sin cambios)
  → SÍ → nuevo_saldo = saldo + monto
  → guardar transacción {tipo: CARGA, estado: Aprobado, fecha, evento: "Carga BeatPay"}
  → mostrar boleta con folio + "Carga exitosa. Nuevo saldo: $X"
[FIN en dashboard]
```

## 4. Realizar pago (flujo principal exigido por el caso)
```text
[INICIO en dashboard]
  1. identificar usuario (sesión)
  2. identificar tarjeta
  3. ¿tarjeta = Activa? ─NO→ error "Tarjeta no habilitada", FIN
  4. elegir evento/comercio + ingresar monto
  5. ¿monto >= $1.000? ─NO→ error "Monto inválido", FIN
  6. ¿saldo >= monto? ─NO→ error "Saldo insuficiente", FIN
  7. SÍ → si gastado + monto > presupuesto avisar "Te pasaste del presupuesto"
  8. pedir confirmación
     → ¿confirma? ─NO→ FIN (sin cambios)
     → SÍ → nuevo_saldo = saldo - monto
  9. guardar transacción {tipo: PAGO, estado: Aprobado, fecha, evento}
  10. mostrar boleta con folio + "Pago aprobado. Nuevo saldo: $X"
[FIN en dashboard / historial]
```

## 5. Administrar tarjeta virtual
```text
[INICIO] → ver datos (**** 1234, estado)
  → ¿estado = Activa? → botón "Bloquear" → estado = Bloqueada
  → ¿estado = Bloqueada? → botón "Activar" → estado = Activa
  → solo Activa permite pagar (ver flujo 4, paso 3)
[FIN]
Estados posibles: Activa | Bloqueada
```

## 6. Historial de transacciones
```text
[INICIO] → listar todas (más recientes primero)
  → opcional filtrar por tipo (Todas / Pagos / Cargas)
  → opcional buscar por evento/comercio
  → ver resumen: total Pagos $X | total Cargas $Y | N movs
Cada fila: fecha | evento | monto | tipo | estado
[FIN]
```

## 7. Flujo admin (Fases 3-4, a futuro)
```text
[INICIO login admin]
  → ¿is_staff? ─NO→ dashboard normal (solo su cuenta)
  → SÍ → panel admin: tabla de TODAS las cuentas
        ├─ ver saldo/tarjeta/transacciones de cada usuario
        ├─ bloquear o activar tarjetas
        └─ ajustar saldos (queda registrado como transacción)
[FIN]
```

## 8. Tabla de errores del sistema
| Caso | Mensaje | Se descuenta saldo |
|---|---|---|
| Monto < $1.000 | "Monto mínimo $1.000" / "Monto inválido" | No |
| Tarjeta Bloqueada al pagar | "Tarjeta no habilitada" | No |
| Saldo insuficiente | "Saldo insuficiente. Tienes $X..." | No |
| Usuario cancela confirmación | (sin mensaje, vuelve) | No |
| Carga válida | "Carga exitosa. Nuevo saldo: $X" | Suma |
| Pago válido | "Pago aprobado por $X. Nuevo saldo: $Y" | Resta |

## 9. Cómo presentarlo en el informe
Elegido: **un solo diagrama en ciclo** (no uno por flujo).
1. Dibuja: INICIO → login → dashboard → 4 ramas (cargar, pagar, historial, tarjeta) que vuelven al dashboard → FIN. Los errores también terminan en FIN.
2. Rombo solo para las 4 preguntas (datos válidos, monto válido, tarjeta activa, saldo suficiente) con SÍ/NO rotulados.
3. Anexa la tabla de errores (punto 8).
4. El flujo admin (punto 7) se menciona como futuro con Django.
