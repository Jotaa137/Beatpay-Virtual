# FASE 1 — Diseño BeatPay Virtual (FINAL)

## 1. Objetivo
Interfaz navegable y responsive, hoy integrada como plantillas Django (`core/templates/`).
Flujos detallados en `FLUJO-sistema-pago.md` (este doc no los duplica).

## 2. Proceso seguido
1. Se recortó el caso a lo que toca BeatPay (sin Bodega/Transporte).
2. Se definió el flujo: landing → registro/login → rol → home usuario / panel admin → cerrar sesión.
3. Se dibujaron mockups de las pantallas.
4. Se construyeron navegables con HTML + Bootstrap 5.3 + 1 JS (`localStorage` como apoyo demo).
5. Se auditó: sin links rotos (todo con `{% url %}`), botones coherentes, responsive.

## 3. Pantallas (qué hace cada una)
| Archivo | Propósito |
|---|---|
| `index` | Landing: hero, beneficios, [Iniciar sesión][Crear cuenta] |
| `login` | Entrada con usuario + clave (ojo mostrar/ocultar), credenciales demo visibles |
| `register` | Crea cuenta: nombre, usuario, email, clave, presupuesto opcional + link a login |
| `dashboard` | La cuenta del usuario: saldo, presupuesto, tarjeta, últimas 3 + operaciones (transferir, pedir cupo) |
| `cargar` | Suma fondos (mín $1.000) con confirmación + boleta folio/imprimir/txt |
| `pagar` | Paga en eventos: valida tarjeta, saldo y presupuesto (alerta si te pasas) + boleta |
| `transacciones` | Historial con filtro, buscador y resumen Pagos/Cargas |
| `tarjeta` | Estado Activa/Bloqueada (bloqueada impide pagar) |
| `admin` | Panel staff: resumen global + buscar/filtrar usuarios + tarjeta/staff |

## 4. Archivos de soporte (qué hace cada uno)
| Archivo | Propósito |
|---|---|
| `static/css/style.css` | Tema minimalista (solo Bootstrap), responsive, impresión de boleta |
| `static/js/app.js` | Único JS por secciones: estado `localStorage`, ayuda clave, cargar/pagar, historial, tarjeta, boleta |

## 5. Reglas UI (resumen)
Navbar único (logo + botones derecha), cards blancas `bp-card`, 1 CSS + 1 JS, links con `{% url %}`, `{% static %}` para estáticos, modo oscuro/claro con memoria (botón 🌙).

## 6. Cumplimiento del caso (dónde ver cada exigencia)
| Exigencia | Dónde probarlo |
|---|---|
| Registro + ingreso seguro | `register` / `login` (validan y ojo 👁) |
| Cuenta, tarjeta Activa/Bloqueada | `dashboard` + `tarjeta` (bloqueo impide pagar) |
| Carga, saldo, presupuesto | `cargar` (mín $1.000, boleta con folio) |
| Pagos con validaciones | `pagar` (tarjeta + saldo + presupuesto + confirm) |
| Historial actualizado | `transacciones` (filtro + buscador + resumen) |
| Roles usuario/admin | login por rol: `dashboard` (transferir, pedir cupo) vs `panel` (resumen, gráficos, solicitudes, buscar/filtrar, tarjeta, staff, acceso, presupuesto, emitir, auditoría) |
| Seguridad | Auth Django + `login_required` + control `is_staff` |
| Interfaz móvil + web | Responsive, probar en celular |
