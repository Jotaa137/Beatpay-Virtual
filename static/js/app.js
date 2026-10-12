/* BeatPay Virtual - app.js unico (minimalista) */
/* SECCION 1: datos y estado */
const BeatPay = (() => {
  const K = { saldo: 'beatpay_saldo', tarjeta: 'beatpay_tarjeta', tx: 'beatpay_tx', user: 'beatpay_user', nombre: 'beatpay_nombre', pto: 'beatpay_pto' };
  const DEFAULT_TX = [
    { fecha: '10/12/2026', evento: 'Music Pro Tour', monto: 15000, tipo: 'PAGO', estado: 'Aprobado' },
    { fecha: '11/12/2026', evento: 'Rock Festival', monto: 8000, tipo: 'PAGO', estado: 'Aprobado' },
    { fecha: '12/12/2026', evento: 'Food & Music', monto: 12000, tipo: 'PAGO', estado: 'Aprobado' },
  ];
  function init() {
    if (!localStorage.getItem(K.saldo)) localStorage.setItem(K.saldo, '80000');
    if (!localStorage.getItem(K.tarjeta)) localStorage.setItem(K.tarjeta, 'Activa');
    if (!localStorage.getItem(K.pto)) localStorage.setItem(K.pto, '100000');
    if (!localStorage.getItem(K.tx)) localStorage.setItem(K.tx, JSON.stringify(DEFAULT_TX));
  }
  function fmt(n) { return '$' + Number(n || 0).toLocaleString('es-CL'); }
  function getSaldo() { return Number(localStorage.getItem(K.saldo) || 80000); }
  function setSaldo(v) { localStorage.setItem(K.saldo, String(v)); }
  function getTarjeta() { return localStorage.getItem(K.tarjeta) || 'Activa'; }
  function setTarjeta(v) { localStorage.setItem(K.tarjeta, v); }
  function getTx() { try { return JSON.parse(localStorage.getItem(K.tx) || '[]'); } catch { return []; } }
  function addTx(t) { const a = getTx(); a.push(t); localStorage.setItem(K.tx, JSON.stringify(a)); return a; }
  function show(el, msg, ok = false) {
    if (!el) return;
    el.textContent = msg;
    el.classList.remove('d-none', 'alert-danger', 'alert-success', 'alert-info');
    el.classList.add('alert', ok ? 'alert-success' : 'alert-danger');
  }
  function hide(el) { if (el) el.classList.add('d-none'); }
  function toast(msg, ok = true) {
    let c = document.getElementById('bp-toast');
    if (!c) { alert(msg); return; }
    c.textContent = msg;
    c.className = 'alert ' + (ok ? 'alert-success' : 'alert-danger');
    c.classList.remove('d-none');
    setTimeout(() => c.classList.add('d-none'), 3500);
  }
  return { K, init, fmt, getSaldo, setSaldo, getTarjeta, setTarjeta, getTx, addTx, show, hide, toast };
})();
function fmt(n) { return BeatPay.fmt(n); }

/* SECCION 2: auth (login, registro) */
function doLogin(e) {
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  const msg = document.getElementById('msg');
  if (!email || !email.includes('@')) { BeatPay.show(msg, 'Ingresa un email válido'); return false; }
  localStorage.setItem(BeatPay.K.user, email);
  location.href = 'dashboard';
  return false;
}
function doReg(e) {
  e.preventDefault();
  const nombre = document.getElementById('nombre').value.trim();
  const email = document.getElementById('email').value.trim();
  const ptoRaw = document.getElementById('pto').value.trim();
  const pto = ptoRaw === '' ? '100000' : ptoRaw;
  if (nombre.length < 2) { BeatPay.toast('Ingresa tu nombre', false); return false; }
  if (!email.includes('@')) { BeatPay.toast('Email inválido', false); return false; }
  if (!(Number(pto) >= 0)) { BeatPay.toast('Presupuesto inválido', false); return false; }
  localStorage.setItem(BeatPay.K.user, email);
  localStorage.setItem(BeatPay.K.nombre, nombre);
  localStorage.setItem(BeatPay.K.pto, pto);
  location.href = 'dashboard';
  return false;
}
function verPass(id, btn) {
  const i = document.getElementById(id);
  if (!i) return false;
  const show = i.type === 'password';
  i.type = show ? 'text' : 'password';
  if (btn) btn.textContent = show ? '🙈' : '👁';
  return false;
}
function requireAuth() {
  if (!localStorage.getItem(BeatPay.K.user)) localStorage.setItem(BeatPay.K.user, 'demo@beatpay.cl');
  const u = localStorage.getItem(BeatPay.K.user);
  document.querySelectorAll('#user').forEach(el => el.textContent = u);
}

/* SECCION 3: pagos (dashboard, cargar, pagar) */
function renderDashboard() {
  requireAuth();
  const saldo = BeatPay.getSaldo();
  const sEl = document.getElementById('saldo'); if (sEl) sEl.textContent = BeatPay.fmt(saldo);
  const pEl = document.getElementById('pto'); if (pEl) pEl.textContent = BeatPay.fmt(localStorage.getItem(BeatPay.K.pto) || 100000);
  const est = BeatPay.getTarjeta();
  const b = document.getElementById('estadoBadge');
  if (b) { b.textContent = est; b.className = 'badge ' + (est === 'Activa' ? 'text-bg-success' : 'text-bg-danger'); }
  const last = document.getElementById('last');
  if (last) {
    const tx = BeatPay.getTx().slice(-3).reverse();
    last.innerHTML = '<table class="table table-striped mb-0"><thead><tr><th>Fecha</th><th>Evento</th><th>Monto</th><th>Estado</th></tr></thead><tbody>' +
      tx.map(t => `<tr><td>${t.fecha}</td><td>${t.evento}</td><td>$${Number(t.monto).toLocaleString('es-CL')}</td><td><span class="badge text-bg-success">${t.estado}</span></td></tr>`).join('') + '</tbody></table>';
  }
}
function cargar(e) {
  e.preventDefault();
  const m = Number(document.getElementById('monto').value);
  const err = document.getElementById('err'), ok = document.getElementById('ok');
  BeatPay.hide(err); BeatPay.hide(ok);
  if (!(m >= 1000)) { BeatPay.show(err, 'Monto mínimo $1.000'); return false; }
  if (!confirm(`Confirmar carga de ${BeatPay.fmt(m)} a tu cuenta?`)) return false;
  const antes = BeatPay.getSaldo();
  const nuevo = antes + m;
  BeatPay.setSaldo(nuevo);
  BeatPay.addTx({ fecha: new Date().toLocaleDateString('es-CL'), evento: 'Carga BeatPay', monto: m, tipo: 'CARGA', estado: 'Aprobado' });
  const a = document.getElementById('actual'); if (a) a.textContent = BeatPay.fmt(nuevo);
  BeatPay.show(ok, `Carga exitosa. Nuevo saldo: ${BeatPay.fmt(nuevo)}`, true);
  mostrarBoleta({ tipo: 'CARGA', evento: 'Carga BeatPay', monto: m, antes: antes, nuevo: nuevo });
  return false;
}
function pagar(e) {
  e.preventDefault();
  const err = document.getElementById('err'), ok = document.getElementById('ok');
  BeatPay.hide(err); BeatPay.hide(ok);
  if (BeatPay.getTarjeta() !== 'Activa') { BeatPay.show(err, 'Tarjeta no habilitada (estado: ' + BeatPay.getTarjeta() + ')'); return false; }
  const m = Number(document.getElementById('monto').value);
  const s = BeatPay.getSaldo();
  if (!(m >= 1000)) { BeatPay.show(err, 'Monto mínimo $1.000'); return false; }
  if (m > s) { BeatPay.show(err, `Saldo insuficiente. Tienes ${BeatPay.fmt(s)} e intentas pagar ${BeatPay.fmt(m)}`); return false; }
  const evento = document.getElementById('evento').value;
  const pto = Number(localStorage.getItem(BeatPay.K.pto) || 100000);
  const gastado = BeatPay.getTx().filter(t => t.tipo === 'PAGO').reduce((a, t) => a + Number(t.monto), 0);
  let msg = `Confirmar pago de ${BeatPay.fmt(m)} en ${evento}?`;
  if (gastado + m > pto) msg = `Te pasaste del presupuesto (gastado ${BeatPay.fmt(gastado)} de ${BeatPay.fmt(pto)}). Confirmar igual?`;
  if (!confirm(msg)) return false;
  const nuevo = s - m;
  BeatPay.setSaldo(nuevo);
  BeatPay.addTx({ fecha: new Date().toLocaleDateString('es-CL'), evento: evento, monto: m, tipo: 'PAGO', estado: 'Aprobado' });
  document.getElementById('saldo').textContent = BeatPay.fmt(nuevo);
  BeatPay.show(ok, `Pago aprobado por ${BeatPay.fmt(m)}. Nuevo saldo: ${BeatPay.fmt(nuevo)}`, true);
  mostrarBoleta({ tipo: 'PAGO', evento: evento, monto: m, antes: s, nuevo: nuevo });
  return false;
}

/* SECCION 4: historial, tarjeta y boleta */
function render() {
  const f = document.getElementById('filtro') ? document.getElementById('filtro').value : '';
  const q = document.getElementById('buscador') ? document.getElementById('buscador').value.toLowerCase() : '';
  let tx = BeatPay.getTx();
  if (f) tx = tx.filter(t => t.tipo === f);
  if (q) tx = tx.filter(t => (t.evento || '').toLowerCase().includes(q));
  const totalPagos = tx.filter(t => t.tipo === 'PAGO').reduce((a, t) => a + Number(t.monto), 0);
  const totalCargas = tx.filter(t => t.tipo === 'CARGA').reduce((a, t) => a + Number(t.monto), 0);
  const box = document.getElementById('tabla');
  const resume = document.getElementById('resumen');
  if (resume) resume.innerHTML = `<span class="badge text-bg-primary">Pagos: ${BeatPay.fmt(totalPagos)}</span> <span class="badge text-bg-success">Cargas: ${BeatPay.fmt(totalCargas)}</span> <span class="badge text-bg-light text-dark">${tx.length} movs</span>`;
  if (box) box.innerHTML = '<table class="table table-striped table-hover mb-0"><thead><tr><th>Fecha</th><th>Evento</th><th>Monto</th><th>Tipo</th><th>Estado</th></tr></thead><tbody>' +
    tx.slice().reverse().map(t => `<tr><td>${t.fecha}</td><td>${t.evento}</td><td>$${Number(t.monto).toLocaleString('es-CL')}</td><td><span class="badge ${t.tipo === 'PAGO' ? 'text-bg-primary' : 'text-bg-success'}">${t.tipo}</span></td><td><span class="badge text-bg-success">${t.estado}</span></td></tr>`).join('') + '</tbody></table>';
}
function refresh() {
  const e = BeatPay.getTarjeta();
  const b = document.getElementById('badge');
  if (b) { b.textContent = e; b.className = 'badge ' + (e === 'Activa' ? 'text-bg-success' : 'text-bg-danger'); }
  const btn = document.getElementById('btnToggle');
  if (btn) btn.textContent = e === 'Activa' ? 'Bloquear tarjeta' : 'Activar tarjeta';
}
function toggle() {
  BeatPay.setTarjeta(BeatPay.getTarjeta() === 'Activa' ? 'Bloqueada' : 'Activa');
  refresh();
}
function restablecerDemo() {
  if (!confirm('¿Restablecer demo? Vuelve a $80.000.')) return false;
  localStorage.setItem(BeatPay.K.tx, '[]');
  BeatPay.setSaldo(80000);
  BeatPay.setTarjeta('Activa');
  localStorage.setItem(BeatPay.K.pto, '100000');
  location.reload();
  return false;
}
let ultimaBoleta = null;
function mostrarBoleta(d) {
  ultimaBoleta = { folio: 'BP-' + String(Date.now()).slice(-6), fecha: new Date().toLocaleString('es-CL'), usuario: localStorage.getItem(BeatPay.K.user) || 'demo@beatpay.cl', tipo: d.tipo, evento: d.evento, monto: d.monto, antes: d.antes, nuevo: d.nuevo };
  const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
  set('b-folio', ultimaBoleta.folio); set('b-fecha', ultimaBoleta.fecha); set('b-tipo', ultimaBoleta.tipo);
  set('b-evento', ultimaBoleta.evento); set('b-monto', BeatPay.fmt(ultimaBoleta.monto));
  set('b-antes', BeatPay.fmt(ultimaBoleta.antes)); set('b-nuevo', BeatPay.fmt(ultimaBoleta.nuevo));
  const b = document.getElementById('boleta'); if (b) b.classList.remove('d-none');
}
function descargarBoleta() {
  if (!ultimaBoleta) return false;
  const L = ['BEATPAY VIRTUAL - BOLETA', 'Music Pro S.A. - Music Pro Tour 2026', '--------------------------------',
    'Folio: ' + ultimaBoleta.folio, 'Fecha: ' + ultimaBoleta.fecha, 'Usuario: ' + ultimaBoleta.usuario,
    'Operacion: ' + ultimaBoleta.tipo, 'Evento: ' + ultimaBoleta.evento, 'Monto: ' + BeatPay.fmt(ultimaBoleta.monto),
    'Saldo anterior: ' + BeatPay.fmt(ultimaBoleta.antes), 'Saldo nuevo: ' + BeatPay.fmt(ultimaBoleta.nuevo),
    '--------------------------------', 'Gracias por preferir BeatPay Virtual'].join('\n');
  const blob = new Blob([L], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = ultimaBoleta.folio + '.txt';
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  return false;
}

/* SECCION 5: inicio automatico */
function initPagos() {
  const a = document.getElementById('actual'); if (a) a.textContent = BeatPay.fmt(BeatPay.getSaldo());
  const s = document.getElementById('saldo'); if (s && document.getElementById('evento')) s.textContent = BeatPay.fmt(BeatPay.getSaldo());
  const t = document.getElementById('tarj'); if (t) t.textContent = BeatPay.getTarjeta();
}
document.addEventListener('DOMContentLoaded', () => {
  BeatPay.init();
  initPagos();
  // Dashboard, tarjeta e historial los pinta el servidor (por usuario).
  // renderDashboard/refresh/render solo se usan al filtrar o al operar.
});
