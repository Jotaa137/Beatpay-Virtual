/* BeatPay Virtual - app.js unico (minimalista) */
/* SECCION 1: datos y estado */
const BeatPay = (() => {
  const K = { saldo: 'beatpay_saldo', tarjeta: 'beatpay_tarjeta', tx: 'beatpay_tx', user: 'beatpay_user', pto: 'beatpay_pto' };
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
  return { K, init, fmt, getSaldo, setSaldo, getTarjeta, setTarjeta, getTx, addTx, show, hide };
})();

/* SECCION 2: ayuda (mostrar/ocultar clave) */
function verPass(id, btn) {
  const i = document.getElementById(id);
  if (!i) return false;
  const show = i.type === 'password';
  i.type = show ? 'text' : 'password';
  if (btn) btn.textContent = show ? '🙈' : '👁';
  return false;
}
/* SECCION 3: tema oscuro / claro (con memoria) */
function initTema() {
  const t = localStorage.getItem('beatpay_theme') || 'light';
  document.documentElement.setAttribute('data-theme', t);
  let b = document.getElementById('btn-tema');
  if (!b) {
    b = document.createElement('button');
    b.id = 'btn-tema';
    b.title = 'Modo oscuro / claro';
    b.setAttribute('onclick', 'return toggleTema()');
    document.body.appendChild(b);
  }
  b.textContent = t === 'dark' ? '☀️' : '🌙';
}
function toggleTema() {
  const actual = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', actual);
  localStorage.setItem('beatpay_theme', actual);
  initTema();
  return false;
}

/* SECCION 4: pagos (cargar, pagar) */
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

/* SECCION 5: historial, tarjeta y boleta */
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

/* SECCION 6: inicio automatico */
function initPagos() {
  const a = document.getElementById('actual'); if (a) a.textContent = BeatPay.fmt(BeatPay.getSaldo());
  const s = document.getElementById('saldo'); if (s && document.getElementById('evento')) s.textContent = BeatPay.fmt(BeatPay.getSaldo());
  const t = document.getElementById('tarj'); if (t) t.textContent = BeatPay.getTarjeta();
}
document.addEventListener('DOMContentLoaded', () => {
  BeatPay.init();
  initTema();
  initPagos();
  // Dashboard, tarjeta e historial los pinta el servidor (por usuario).
  // refresh/render solo se usan al filtrar o al operar la tarjeta.
});
