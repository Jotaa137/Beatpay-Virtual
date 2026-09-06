/* BeatPay Virtual - auth.js */
function doLogin(e) {
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  const msg = document.getElementById('msg');
  if (!email || !email.includes('@')) { BeatPay.show(msg, 'Ingresa un email válido'); return false; }
  localStorage.setItem(BeatPay.K.user, email);
  location.href = 'dashboard.html';
  return false;
}
function doReg(e) {
  e.preventDefault();
  const nombre = document.getElementById('nombre').value.trim();
  const email = document.getElementById('email').value.trim();
  const ptoRaw = document.getElementById('pto').value.trim();
  const pto = ptoRaw === '' ? '100000' : ptoRaw; // vacío = ejemplo por defecto
  if (nombre.length < 2) { BeatPay.toast('Ingresa tu nombre', false); return false; }
  if (!email.includes('@')) { BeatPay.toast('Email inválido', false); return false; }
  if (!(Number(pto) >= 0)) { BeatPay.toast('Presupuesto inválido', false); return false; }
  localStorage.setItem(BeatPay.K.user, email);
  localStorage.setItem(BeatPay.K.nombre, nombre);
  localStorage.setItem(BeatPay.K.pto, pto);
  location.href = 'dashboard.html';
  return false;
}
function doLogout() {
  // Fase 1: no borramos saldo/tx para demo, solo sesión visual
  location.href = 'index.html';
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
  // Demo permisivo: si no hay usuario, usa demo pero avisa
  if (!localStorage.getItem(BeatPay.K.user)) {
    localStorage.setItem(BeatPay.K.user, 'demo@beatpay.cl');
  }
  const u = localStorage.getItem(BeatPay.K.user);
  document.querySelectorAll('#user').forEach(el => el.textContent = u);
}
