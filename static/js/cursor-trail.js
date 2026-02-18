/* ───────────────────────────────────────────────────────
   Trinetra Canvas Cursor Trail  —  glow + physics + lines
   ─────────────────────────────────────────────────────── */
(() => {
  'use strict';

  /* --- palette ------------------------------------------------ */
  const COLORS = [
    { r: 251, g: 191, b: 36  },   /* amber   */
    { r: 192, g: 132, b: 252 },   /* purple  */
    { r: 34,  g: 211, b: 238 },   /* cyan    */
    { r: 110, g: 231, b: 183 },   /* emerald */
    { r: 253, g: 164, b: 175 },   /* rose    */
  ];

  const MAX      = 55;
  const LINE_D   = 110;
  const DECAY    = 0.018;
  const FRICTION = 0.975;
  const HALO_R   = 60;

  /* --- canvas setup ------------------------------------------- */
  let canvas = document.getElementById('tri-cursor-canvas');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.id = 'tri-cursor-canvas';
    canvas.style.cssText = 'position:fixed;inset:0;z-index:9998;pointer-events:none;';
    document.body.appendChild(canvas);
  }
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  function resize() {
    canvas.width  = window.innerWidth  * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width  = window.innerWidth  + 'px';
    canvas.style.height = window.innerHeight + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  /* --- state -------------------------------------------------- */
  const particles = [];
  let mx = -200, my = -200;

  /* --- mouse tracking ----------------------------------------- */
  let lastSpawn = 0;
  window.addEventListener('mousemove', (e) => {
    mx = e.clientX;
    my = e.clientY;
    const now = performance.now();
    if (now - lastSpawn < 16) return;
    lastSpawn = now;
    spawn(mx, my);
  });

  /* --- particle factory --------------------------------------- */
  function spawn(x, y) {
    const c = COLORS[Math.floor(Math.random() * COLORS.length)];
    const angle = Math.random() * Math.PI * 2;
    const speed = 0.3 + Math.random() * 1.2;
    particles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: 2 + Math.random() * 2.5,
      life: 1,
      c
    });
    if (particles.length > MAX) particles.shift();
  }

  /* --- draw loop ---------------------------------------------- */
  function frame() {
    ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

    /* connecting lines */
    for (let i = 0; i < particles.length; i++) {
      const a = particles[i];
      for (let j = i + 1; j < particles.length; j++) {
        const b = particles[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < LINE_D) {
          const alpha = (1 - d / LINE_D) * Math.min(a.life, b.life) * 0.18;
          const mr = (a.c.r + b.c.r) >> 1;
          const mg = (a.c.g + b.c.g) >> 1;
          const mb = (a.c.b + b.c.b) >> 1;
          ctx.strokeStyle = `rgba(${mr},${mg},${mb},${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    /* particles with glow */
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= FRICTION;
      p.vy *= FRICTION;
      p.life -= DECAY;

      if (p.life <= 0) { particles.splice(i, 1); continue; }

      const alpha = p.life * 0.85;
      const size  = p.r * (0.4 + p.life * 0.6);

      /* outer glow */
      const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 5);
      grd.addColorStop(0, `rgba(${p.c.r},${p.c.g},${p.c.b},${alpha * 0.25})`);
      grd.addColorStop(1, `rgba(${p.c.r},${p.c.g},${p.c.b},0)`);
      ctx.fillStyle = grd;
      ctx.beginPath();
      ctx.arc(p.x, p.y, size * 5, 0, Math.PI * 2);
      ctx.fill();

      /* core dot */
      ctx.fillStyle = `rgba(${p.c.r},${p.c.g},${p.c.b},${alpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
      ctx.fill();
    }

    /* mouse halo */
    if (mx > 0 && my > 0) {
      const halo = ctx.createRadialGradient(mx, my, 0, mx, my, HALO_R);
      halo.addColorStop(0, 'rgba(245,158,11,0.07)');
      halo.addColorStop(0.5, 'rgba(192,132,252,0.03)');
      halo.addColorStop(1, 'rgba(34,211,238,0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(mx, my, HALO_R, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
