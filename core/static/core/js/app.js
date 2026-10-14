/* BeatPay Virtual - app.js unico (minimalista) */
/* Todo lo funcional lo pinta el servidor; aquí solo ayudas visuales. */

/* SECCION 1: mostrar/ocultar clave */
function verPass(id, btn) {
  const i = document.getElementById(id);
  if (!i) return false;
  const show = i.type === 'password';
  i.type = show ? 'text' : 'password';
  if (btn) btn.textContent = show ? '🙈' : '👁';
  return false;
}

/* SECCION 2: tema oscuro / claro (con memoria) */
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

/* SECCION 3: descargar boleta (lee la boleta que pintó el servidor) */
function descargarBoleta() {
  const txt = (id) => { const e = document.getElementById(id); return e ? e.textContent : ''; };
  if (!txt('b-folio')) return false;
  const L = ['BEATPAY VIRTUAL - BOLETA', 'Music Pro S.A. - Music Pro Tour 2026', '--------------------------------',
    'Folio: ' + txt('b-folio'), 'Fecha: ' + txt('b-fecha'),
    'Operacion: ' + txt('b-tipo'), 'Evento: ' + txt('b-evento'), 'Monto: ' + txt('b-monto'),
    'Saldo anterior: ' + txt('b-antes'), 'Saldo nuevo: ' + txt('b-nuevo'),
    '--------------------------------', 'Gracias por preferir BeatPay Virtual'].join('\n');
  const blob = new Blob([L], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = txt('b-folio') + '.txt';
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  return false;
}

/* SECCION 4: inicio automatico */
document.addEventListener('DOMContentLoaded', () => {
  initTema();
});
