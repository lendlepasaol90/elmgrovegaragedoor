/* Elm Grove Garage Door — motion + interactions */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;

  // year
  $$('[data-year]').forEach(n => n.textContent = new Date().getFullYear());

  // split headings into words
  $$('[data-split]').forEach(el => {
    let i = 0;
    const walk = node => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            const w = document.createElement('span'); w.className = 'w';
            const s = document.createElement('span'); s.textContent = part; s.style.setProperty('--i', i++);
            w.appendChild(s); frag.appendChild(w);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
  });

  // reveal on scroll
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
  }), { rootMargin: '0px 0px -8% 0px', threshold: .12 });
  $$('[data-reveal],[data-split],[data-wipe]').forEach(el => reduce ? el.classList.add('is-in') : io.observe(el));

  // header + mobile nav + mega
  const header = $('.header'), burger = $('.burger'), nav = $('.header nav');
  burger && burger.addEventListener('click', () => {
    const open = burger.getAttribute('aria-expanded') !== 'true';
    burger.setAttribute('aria-expanded', open); nav.classList.toggle('is-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  $$('.has-mega > button').forEach(b => b.addEventListener('click', () => {
    const li = b.parentElement, open = !li.classList.contains('is-open');
    li.classList.toggle('is-open', open); b.setAttribute('aria-expanded', open);
  }));
  $$('.header nav a').forEach(a => a.addEventListener('click', () => {
    if (nav.classList.contains('is-open')) { burger.click(); }
  }));

  // service filter chips
  $$('.chip').forEach(c => c.addEventListener('click', () => {
    $$('.chip').forEach(x => x.classList.toggle('is-on', x === c));
    const f = c.dataset.filter;
    $$('.scards .scard[data-cat]').forEach(card => card.classList.toggle('is-hidden', f !== 'all' && card.dataset.cat !== f));
  }));

  // seasons tabs
  $$('[data-seasons]').forEach(box => {
    const tabs = $$('.season__tab', box), panes = $$('.season__pane', box), ink = $('.season__ink', box);
    const set = i => {
      tabs.forEach((t, k) => { t.classList.toggle('is-on', k === i); t.setAttribute('aria-selected', k === i); });
      panes.forEach((p, k) => p.classList.toggle('is-on', k === i));
      if (ink) { ink.style.width = tabs[i].offsetWidth + 'px'; ink.style.transform = `translateX(${tabs[i].offsetLeft}px)`; }
    };
    tabs.forEach((t, i) => t.addEventListener('click', () => set(i)));
    set(0); addEventListener('resize', () => set(tabs.findIndex(t => t.classList.contains('is-on'))));
  });

  // quote form
  $$('[data-quote]').forEach(f => f.addEventListener('submit', async ev => {
    ev.preventDefault();
    let ok = true;
    $$('[required]', f).forEach(i => { const bad = !i.value.trim(); i.closest('.fld').classList.toggle('is-bad', bad); if (bad) ok = false; });
    if (!ok) return;
    if (f.querySelector('.hp').value) return;
    const btn = $('button[type=submit]', f); btn.disabled = true;
    if (f.action && f.getAttribute('action')) {
      try { await fetch(f.action, { method: 'POST', body: new FormData(f), headers: { Accept: 'application/json' } }); } catch (e) {}
    }
    $('.qform__ok', f).hidden = false; btn.disabled = false; f.reset();
  }));

  // magnetic buttons + tilt + glow
  if (fine && !reduce) {
    $$('[data-magnetic]').forEach(b => {
      b.addEventListener('mousemove', ev => { const r = b.getBoundingClientRect(); b.style.transform = `translate(${(ev.clientX - r.left - r.width / 2) * .18}px,${(ev.clientY - r.top - r.height / 2) * .28}px)`; });
      b.addEventListener('mouseleave', () => b.style.transform = '');
    });
    $$('[data-tilt]').forEach(c => {
      c.addEventListener('mousemove', ev => { const r = c.getBoundingClientRect(); const x = (ev.clientX - r.left) / r.width - .5, y = (ev.clientY - r.top) / r.height - .5; c.style.transform = `perspective(900px) rotateY(${x * 7}deg) rotateX(${-y * 7}deg) translateY(-4px)`; });
      c.addEventListener('mouseleave', () => c.style.transform = '');
    });
    $$('[data-glow]').forEach(c => c.addEventListener('mousemove', ev => { const r = c.getBoundingClientRect(); c.style.setProperty('--mx', ev.clientX - r.left + 'px'); c.style.setProperty('--my', ev.clientY - r.top + 'px'); }));
  }

  // scroll-linked effects
  const progress = $('.progress'), totop = $('.totop');
  const par = $$('[data-parallax]'), iris = $$('[data-iris]'), drift = $$('[data-drift]'), branches = $$('[data-branch]'), reels = $$('[data-reel]'), stackCards = $$('.stack__card');
  const vh = () => innerHeight;
  let ticking = false;
  const onScroll = () => {
    const y = scrollY, max = document.documentElement.scrollHeight - vh(), p = max > 0 ? y / max : 0;
    if (progress) progress.style.transform = `scaleX(${p})`;
    if (totop) { totop.classList.toggle('is-on', y > 700); totop.style.setProperty('--p', p); }
    header && header.classList.toggle('is-stuck', y > 10);
    if (reduce) return;
    par.forEach(img => {
      const r = img.parentElement.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh()) return;
      img.style.transform = `translate3d(0,${(r.top - vh() / 2) * -parseFloat(img.dataset.parallax)}px,0)`;
    });
    iris.forEach(m => {
      const r = m.parentElement.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh()) return;
      const t = Math.min(1, Math.max(0, (vh() - r.top) / (vh() * .9)));
      m.style.setProperty('--iris', (18 + t * 70) + '%');
      const im = m.querySelector('img'); if (im) im.style.transform = `translate3d(0,${(r.top) * -.15}px,0) scale(${1.15 - t * .15})`;
    });
    drift.forEach(d => { const r = d.parentElement.getBoundingClientRect(); d.style.transform = `translateX(${(r.top) * .25}px)`; });
    branches.forEach(b => { const r = b.getBoundingClientRect(); const t = Math.min(1, Math.max(0, (vh() * .75 - r.top) / r.height)); b.style.setProperty('--p', t); });
    reels.forEach(rl => {
      if (innerWidth <= 720) return;
      const r = rl.getBoundingClientRect(), track = rl.querySelector('.reel__track');
      const total = rl.offsetHeight - vh(), t = Math.min(1, Math.max(0, -r.top / total));
      const dist = track.scrollWidth - innerWidth + 40;
      track.style.transform = `translate3d(${-t * dist}px,0,0)`;
    });
    stackCards.forEach((c, i) => {
      const next = stackCards[i + 1]; if (!next) return;
      const r = next.getBoundingClientRect(), top = parseFloat(getComputedStyle(next).top);
      const t = Math.min(1, Math.max(0, 1 - (r.top - top) / vh()));
      c.style.transform = `scale(${1 - t * .05})`; c.style.filter = `brightness(${1 - t * .12})`;
    });
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { onScroll(); ticking = false; }); } }, { passive: true });
  addEventListener('resize', onScroll); onScroll();
  totop && totop.addEventListener('click', () => scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }));

  // drifting leaves in the hero
  if (!reduce) $$('.leaves').forEach(cv => {
    const ctx = cv.getContext('2d'); let W, H, dpr = Math.min(2, devicePixelRatio || 1), leaves = [], running = true;
    const colors = ['#8db59a', '#557f66', '#d9a35e', '#c98f4a', '#b7cdb9'];
    const size = () => { W = cv.offsetWidth; H = cv.offsetHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); };
    size(); addEventListener('resize', size);
    const n = innerWidth < 720 ? 8 : 16;
    for (let i = 0; i < n; i++) leaves.push({ x: Math.random() * W, y: Math.random() * H, s: 6 + Math.random() * 9, vy: .25 + Math.random() * .5, vx: -.2 + Math.random() * .4, r: Math.random() * 6, vr: -.02 + Math.random() * .04, ph: Math.random() * 6, c: colors[i % colors.length], a: .35 + Math.random() * .35 });
    const draw = l => {
      ctx.save(); ctx.translate(l.x, l.y); ctx.rotate(l.r); ctx.globalAlpha = l.a; ctx.fillStyle = l.c;
      ctx.beginPath(); ctx.moveTo(0, -l.s); ctx.quadraticCurveTo(l.s * .9, 0, 0, l.s); ctx.quadraticCurveTo(-l.s * .9, 0, 0, -l.s); ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,.5)'; ctx.lineWidth = .6; ctx.beginPath(); ctx.moveTo(0, -l.s); ctx.lineTo(0, l.s); ctx.stroke(); ctx.restore();
    };
    const visIO = new IntersectionObserver(es => { running = es[0].isIntersecting; if (running) requestAnimationFrame(loop); });
    visIO.observe(cv);
    let t = 0;
    function loop() {
      if (!running) return;
      t += .01; ctx.clearRect(0, 0, W, H);
      leaves.forEach(l => {
        l.y += l.vy; l.x += l.vx + Math.sin(t * 2 + l.ph) * .5; l.r += l.vr;
        if (l.y > H + 20) { l.y = -20; l.x = Math.random() * W; }
        if (l.x > W + 20) l.x = -20; if (l.x < -20) l.x = W + 20;
        draw(l);
      });
      requestAnimationFrame(loop);
    }
  });

  // gentle float on cards
  if (!reduce) $$('[data-float]').forEach((el, i) => el.animate([{ transform: 'translateY(0)' }, { transform: 'translateY(-10px)' }, { transform: 'translateY(0)' }], { duration: 5000 + i * 700, iterations: Infinity, easing: 'ease-in-out' }));
})();
