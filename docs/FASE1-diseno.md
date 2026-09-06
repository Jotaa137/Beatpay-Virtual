# FASE 1 — Diseño BeatPay Virtual (FINAL)

## 1. Objetivo
Interfaz navegable y responsive sin backend, lista para volverse templates Django.
Flujos detallados en `FLUJO-sistema-pago.md` (este doc no los duplica).

## 2. Proceso seguido
1. Se recortó el caso a lo que toca BeatPay (sin Bodega/Transporte).
2. Se definió el flujo: registro → cuenta → cargar → pagar → historial.
3. Se dibujaron mockups de 8 pantallas + base.
4. Se construyeron navegables con HTML + Bootstrap/Tailwind + JS (`localStorage` como DB simulada).
5. Se auditó: sin links rotos, mismos botones/inputs en las 9 páginas, textos legibles en ambos modos.

## 3. Pantallas (qué hace cada una)
| Archivo | Propósito |
|---|---|
| `index.html` | Landing: hero, beneficios, navbar PayPal [Iniciar sesión][Crear cuenta], CTA [Ver cuenta demo] |
| `login.html` | Entrada con email + clave (ojo mostrar/ocultar) y validación |
| `register.html` | Crea cuenta: nombre, email, clave, presupuesto opcional (`Ej: 100000`) |
| `dashboard.html` | La cuenta: saldo, presupuesto, tarjeta holográfica, últimas 3 + [Ver todo][Restablecer demo] |
| `cargar.html` | Suma fondos (mín $1.000) con confirmación + boleta folio/imprimir/txt |
| `pagar.html` | Paga en eventos: valida tarjeta, saldo y presupuesto (alerta si te pasas) + boleta |
| `transacciones.html` | Historial con filtro, buscador y resumen Pagos/Cargas |
| `tarjeta.html` | Estado Activa/Bloqueada (bloqueada impide pagar) |
| `base.html` | Plantilla de partida, no navegable |

## 4. Archivos de soporte (qué hace cada uno)
| Archivo | Propósito |
|---|---|
| `static/css/style.css` | Tema gamer RGB, modo claro/oscuro, responsive móvil, impresión de boleta |
| `static/js/app.js` | Núcleo: saldo/tarjeta/tx en `localStorage` + auto-carga efectos |
| `static/js/auth.js` | Login, registro, ojo de clave |
| `static/js/pagos.js` | Cuenta, carga, pago (con confirmaciones y alerta), historial, tarjeta, boleta, reseteo |
| `static/js/efectos.js` | Starfield 3D, piso synthwave, ecualizador, notas ♪, gato pibf/miau, botón tema |

## 5. Reglas UI (resumen)
Navbar único (logo + botones derecha, en móvil centrados), cards oscuras con borde RGB solo en el filo, Orbitron + Rajdhani, inputs legibles en ambos modos, `?v=3` anti-caché, anti-flash de tema en el `<head>`.

## 6. Cumplimiento del caso (dónde ver cada exigencia)
| Exigencia | Dónde probarlo |
|---|---|
| Registro + ingreso seguro | `register.html` / `login.html` (validan y ojo 👁) |
| Cuenta, tarjeta Activa/Bloqueada | `dashboard.html` + `tarjeta.html` (bloqueo impide pagar) |
| Carga, saldo, presupuesto | `cargar.html` (mín $1.000, boleta con folio) |
| Pagos con validaciones | `pagar.html` (tarjeta + saldo + presupuesto + confirm) |
| Historial actualizado | `transacciones.html` (filtro + buscador + resumen) |
| Integración con eventos | Base lista (eventos + API en Fase 5) |
| Seguridad | Validaciones + boletas + hash/JWT en Django |
| Interfaz móvil + web | Responsive 9/9, probar en celular |
| Bodega/Transporte/GPS | ❌ fuera de alcance |

## 7. Checklist
- [x] Flujo, mockups, navegación sin rotos, coherencia 9/9, fondos/efectos
- [ ] Screenshots + diagrama en Draw.io (tuyos)
