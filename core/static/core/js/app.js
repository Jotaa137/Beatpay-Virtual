function verPass(id, btn) {
  const i = document.getElementById(id);
  if (!i) return false;
  const show = i.type === 'password';
  i.type = show ? 'text' : 'password';
  if (btn) btn.textContent = show ? '🙈' : '👁';
  return false;
}

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

document.addEventListener('DOMContentLoaded', () => {
});
