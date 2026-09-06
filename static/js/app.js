/* BeatPay Virtual - app.js (núcleo) */
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
    // Usa alert Bootstrap si existe contenedor, si no alert nativo
    let c = document.getElementById('bp-toast');
    if (!c) { alert(msg); return; }
    c.textContent = msg;
    c.className = 'alert ' + (ok ? 'alert-success' : 'alert-danger');
    c.classList.remove('d-none');
    setTimeout(() => c.classList.add('d-none'), 3500);
  }
  return { K, init, fmt, getSaldo, setSaldo, getTarjeta, setTarjeta, getTx, addTx, show, hide, toast };
})();
document.addEventListener('DOMContentLoaded', () => BeatPay.init());
function fmt(n){ return BeatPay.fmt(n); }
// Auto-carga efectos gamer RGB en todas las páginas sin editar HTML
(() => { try { const s = document.createElement('script'); s.src = '../static/js/efectos.js?v=3'; document.body.appendChild(s); } catch {} })();
