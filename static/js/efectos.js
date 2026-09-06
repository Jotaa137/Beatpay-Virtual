/* BeatPay Virtual - efectos.js GAMER RGB */
(() => {
  // 1. Canvas partículas RGB flotantes (sin romper nada si falla)
  function particles() {
    try {
      if (document.getElementById('rgb-canvas')) return;
      const c = document.createElement('canvas');
      c.id = 'rgb-canvas';
      document.body.prepend(c);
      const ctx = c.getContext('2d');
      const COLORS = ['#ff00e5', '#00fff2', '#a3ff00', '#ffe600', '#7c3aed'];
      let W, H, dots = [];
      function resize() { W = c.width = innerWidth; H = c.height = innerHeight; }
      resize(); addEventListener('resize', resize);
      for (let i = 0; i < 60; i++) dots.push({ x: Math.random() * innerWidth, y: Math.random() * innerHeight, r: Math.random() * 2.5 + .5, s: Math.random() * .6 + .2, col: COLORS[i % COLORS.length], o: Math.random() * .7 + .2 });
      (function loop() {
        ctx.clearRect(0, 0, W, H);
        for (const d of dots) {
          d.y -= d.s; if (d.y < -10) { d.y = H + 10; d.x = Math.random() * W; }
          ctx.globalAlpha = d.o; ctx.fillStyle = d.col;
          ctx.shadowBlur = 10; ctx.shadowColor = d.col;
          ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, 7); ctx.fill();
        }
        ctx.globalAlpha = 1;
        requestAnimationFrame(loop);
      })();
    } catch {}
  }
  // 2. Tilt 3D en cards gamer
  function tilt() {
    document.querySelectorAll('.bp-card').forEach(card => {
      card.addEventListener('mousemove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5;
        const y = (e.clientY - r.top) / r.height - .5;
        card.style.transform = `perspective(800px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg) translateY(-2px)`;
      });
      card.addEventListener('mouseleave', () => card.style.transform = '');
    });
  }
  // 3. Glow que sigue el mouse en tarjeta
  function cardGlow() {
    const t = document.querySelector('.tarjeta-visual');
    if (!t) return;
    t.addEventListener('mousemove', e => {
      const r = t.getBoundingClientRect();
      t.style.filter = `brightness(1.1) drop-shadow(${(e.clientX - r.left - r.width / 2) / 10}px 0 15px #00fff288)`;
    });
    t.addEventListener('mouseleave', () => t.style.filter = '');
  }
  // Init robusto: este archivo se inyecta dinámico (async), el DOMContentLoaded
  // puede haber pasado ya. Si el documento sigue cargando se espera, si no se arranca ya.
  function initEfectos() { particles(); tilt(); cardGlow(); fondo3D(); ecualizador3D(); notasMusicales(); gato(); tema(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initEfectos);
  else initEfectos();
  // 4. FONDO 3D pseudo-3D starfield + piso synthwave
  function fondo3D() {
    try {
      if (document.getElementById('fondo-3d')) return;
      const wrap = document.createElement('div');
      wrap.id = 'fondo-3d';
      wrap.innerHTML = '<canvas class="fondo3d"></canvas><div class="piso-3d"></div><div class="orbe-3d orbe-1"></div><div class="orbe-3d orbe-2"></div><div class="orbe-3d orbe-3"></div>';
      document.body.prepend(wrap);
      const cv = wrap.querySelector('canvas');
      const ctx = cv.getContext('2d');
      let W, H, stars = [], mx = 0, my = 0;
      function resize() { W = cv.width = innerWidth; H = cv.height = innerHeight; }
      resize(); addEventListener('resize', resize);
      addEventListener('mousemove', e => { mx = (e.clientX / W - .5); my = (e.clientY / H - .5); });
      const COLORS = ['#ff00e5', '#00fff2', '#a3ff00', '#ffe600', '#7c3aed'];
      for (let i = 0; i < 160; i++) stars.push({ x: Math.random() * 2000 - 1000, y: Math.random() * 2000 - 1000, z: Math.random() * 1000 + 1, col: COLORS[i % COLORS.length] });
      (function loop() {
        ctx.clearRect(0, 0, W, H);
        const cx = W / 2 + mx * 40, cy = H / 2 + my * 40;
        for (const s of stars) {
          s.z -= 4; if (s.z <= 1) { s.z = 1000; s.x = Math.random() * 2000 - 1000; s.y = Math.random() * 2000 - 1000; }
          const px = cx + (s.x / s.z) * 500, py = cy + (s.y / s.z) * 500;
          if (px < 0 || px > W || py < 0 || py > H) continue;
          const r = (1 - s.z / 1000) * 2.5 + .3;
          ctx.globalAlpha = 1 - s.z / 1000 + .15;
          ctx.fillStyle = s.col; ctx.shadowBlur = 8; ctx.shadowColor = s.col;
          ctx.beginPath(); ctx.arc(px, py, r, 0, 7); ctx.fill();
        }
        ctx.globalAlpha = 1;
        requestAnimationFrame(loop);
      })();
    } catch {}
  }
  // 5. GATO esquina inferior izquierda: click -> "¡pibf!" y viceversa "¡miau!"
  function gato() {
    try {
      if (document.getElementById('gato-beatpay')) return;
      const g = document.createElement('div');
      g.id = 'gato-beatpay';
      g.title = 'Hazme click';
      g.innerHTML = '<div id="gato-bocadillo"></div><span class="gato-cuerpo">🐱</span>';
      document.body.appendChild(g);
      const b = g.querySelector('#gato-bocadillo');
      let turnoPibf = true, timer = null;
      g.addEventListener('click', () => {
        const texto = turnoPibf ? '¡pibf!' : '¡miau!';
        turnoPibf = !turnoPibf;
        b.textContent = texto;
        b.classList.add('ver');
        g.querySelector('.gato-cuerpo').textContent = turnoPibf ? '🐱' : '😸';
        clearTimeout(timer);
        timer = setTimeout(() => b.classList.remove('ver'), 1500);
      });
    } catch {}
  }
  // 6. MODO OSCURO / CLARO con persistencia
  function tema() {
    try {
      const saved = localStorage.getItem('beatpay_theme') || 'dark';
      document.documentElement.setAttribute('data-theme', saved);
      if (document.getElementById('btn-tema')) return;
      const btn = document.createElement('button');
      btn.id = 'btn-tema';
      btn.title = 'Modo oscuro / claro';
      const pinta = () => btn.textContent = document.documentElement.getAttribute('data-theme') === 'light' ? '☀️' : '🌙';
      pinta();
      btn.addEventListener('click', () => {
        const actual = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', actual);
        localStorage.setItem('beatpay_theme', actual);
        pinta();
      });
      document.body.appendChild(btn);
    } catch {}
  }
  // 7. ECUALIZADOR 3D estilo concierto (fondo, temática BeatPay)
  function ecualizador3D() {
    try {
      if (document.getElementById('ecualizador-3d')) return;
      const cv = document.createElement('canvas');
      cv.id = 'ecualizador-3d';
      document.body.prepend(cv);
      const ctx = cv.getContext('2d');
      const COLS_OSCURO = ['#ff00e5', '#00fff2', '#a3ff00', '#ffe600', '#7c3aed'];
      const COLS_CLARO = ['#c4009e', '#0077c8', '#4d9900', '#a38600', '#5b21b6'];
      const N = 56;
      let W, H, t = 0;
      function resize() { W = cv.width = innerWidth; H = cv.height = innerHeight; }
      resize(); addEventListener('resize', resize);
      // Simula música: graves al centro, agudos a los bordes + pulso de beat
      function nivel(i, tiempo) {
        const centro = 1 - Math.abs(i / (N - 1) * 2 - 1); // 0 bordes -> 1 centro
        const beat = Math.pow(Math.max(0, Math.sin(tiempo * 2.2)), 3) * .35;
        return .12 + centro * .45
          + Math.sin(tiempo * 1.7 + i * .55) * .14
          + Math.sin(tiempo * 3.1 + i * 1.3) * .09
          + beat * (0.5 + centro * 0.5);
      }
      (function loop() {
        t += 1 / 60;
        ctx.clearRect(0, 0, W, H);
        const claro = document.documentElement.getAttribute('data-theme') === 'light';
        const COLS = claro ? COLS_CLARO : COLS_OSCURO;
        const baseY = H * 0.98, maxH = H * 0.30, gw = W / N, bw = gw * 0.55;
        for (let fila = 0; fila < 2; fila++) {
          const lejos = fila === 0;
          const escala = lejos ? 0.45 : 1;
          const yBase = lejos ? baseY - H * 0.02 : baseY;
          for (let i = 0; i < N; i++) {
            const n = Math.min(1, Math.max(0.03, nivel(i, t - (lejos ? 0.6 : 0))));
            const h = n * maxH * escala;
            const x = i * gw + (gw - bw * escala) / 2;
            const col = COLS[(i + (lejos ? 2 : 0)) % COLS.length];
            const g = ctx.createLinearGradient(0, yBase - h, 0, yBase);
            g.addColorStop(0, col);
            g.addColorStop(1, col + '11');
            ctx.globalAlpha = claro ? (lejos ? 0.55 : 0.85) : (lejos ? 0.30 : 0.55);
            ctx.fillStyle = g;
            ctx.shadowBlur = lejos ? 6 : 14;
            ctx.shadowColor = col;
            const w = bw * escala;
            // Barra con punta redondeada (efecto 3D por capas)
            ctx.beginPath();
            if (ctx.roundRect) ctx.roundRect(x, yBase - h, w, h, w / 2);
            else ctx.rect(x, yBase - h, w, h);
            ctx.fill();
            // Reflejo en el "piso"
            ctx.globalAlpha = lejos ? 0.06 : 0.12;
            ctx.shadowBlur = 0;
            ctx.fillRect(x, yBase, w, h * 0.35);
          }
        }
        ctx.globalAlpha = 1;
        requestAnimationFrame(loop);
      })();
    } catch {}
  }
  // 8. NOTAS MUSICALES flotantes (ambiente concierto)
  function notasMusicales() {
    try {
      if (document.getElementById('notas-musicales')) return;
      const cv = document.createElement('canvas');
      cv.id = 'notas-musicales';
      document.body.prepend(cv);
      const ctx = cv.getContext('2d');
      const SIMBOLOS = ['♪', '♫', '♬', '♩'];
      const COL_OSCURO = ['#ff00e5', '#00fff2', '#a3ff00', '#ffe600', '#7c3aed'];
      const COL_CLARO = ['#c4009e', '#0077c8', '#4d9900', '#a38600', '#5b21b6'];
      let W, H, notas = [];
      function resize() { W = cv.width = innerWidth; H = cv.height = innerHeight; }
      resize(); addEventListener('resize', resize);
      for (let i = 0; i < 26; i++) notas.push({
        x: Math.random() * innerWidth, y: Math.random() * innerHeight,
        s: Math.random() * 26 + 20, v: Math.random() * .5 + .25,
        fase: Math.random() * 6.28, sim: SIMBOLOS[i % SIMBOLOS.length],
        ci: i % COL_OSCURO.length, o: Math.random() * .4 + .35
      });
      (function loop() {
        const t = performance.now() / 1000;
        ctx.clearRect(0, 0, W, H);
        const claro = document.documentElement.getAttribute('data-theme') === 'light';
        const PAL = claro ? COL_CLARO : COL_OSCURO;
        for (const n of notas) {
          n.y -= n.v; if (n.y < -30) { n.y = H + 30; n.x = Math.random() * W; }
          const x = n.x + Math.sin(t + n.fase) * 18;
          ctx.globalAlpha = claro ? Math.min(1, n.o + .2) : n.o;
          ctx.font = n.s + 'px serif';
          ctx.fillStyle = PAL[n.ci];
          ctx.shadowBlur = 10; ctx.shadowColor = PAL[n.ci];
          ctx.fillText(n.sim, x, n.y);
        }
        ctx.globalAlpha = 1;
        requestAnimationFrame(loop);
      })();
    } catch {}
  }
})();
