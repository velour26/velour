// CSRF helper
function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

const CSRF = getCookie('csrftoken');

async function apiRequest(url, method = 'GET', data = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
    credentials: 'same-origin',
  };
  if (data) opts.body = JSON.stringify(data);
  const res = await fetch(url, opts);
  const json = await res.json();
  if (!res.ok) throw json;
  return json;
}

// Toast
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      ${type === 'success'
        ? '<polyline points="20 6 9 17 4 12"/>'
        : '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'}
    </svg>
    <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.style.opacity = '0', 3000);
  setTimeout(() => toast.remove(), 3400);
}

// Cart counter update
function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

// Add to cart
async function addToCart(productId, variantId = null, quantity = 1) {
  try {
    const data = await apiRequest('/api/cart/add/', 'POST', { product_id: productId, variant_id: variantId, quantity });
    updateCartBadge(data.count);
    showToast('Товар добавлен в корзину');
    return data;
  } catch (e) {
    showToast(e.detail || 'Ошибка при добавлении товара', 'error');
  }
}

// Mobile menu
function initMobileMenu() {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.mobile-nav');
  const overlay = document.querySelector('.overlay');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    nav.classList.toggle('open');
    overlay?.classList.toggle('active');
    document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
  });
  overlay?.addEventListener('click', () => {
    nav.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  });
}

// Hero slider
function initHeroSlider() {
  const slides = document.querySelectorAll('.hero-slide');
  const dots = document.querySelectorAll('.hero-dot');
  if (!slides.length) return;
  let current = 0;

  function goTo(n) {
    slides[current].classList.remove('active');
    dots[current]?.classList.remove('active');
    current = (n + slides.length) % slides.length;
    slides[current].classList.add('active');
    dots[current]?.classList.add('active');
  }

  dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));
  let interval = setInterval(() => goTo(current + 1), 5000);
  document.querySelector('.hero')?.addEventListener('mouseenter', () => clearInterval(interval));
  document.querySelector('.hero')?.addEventListener('mouseleave', () => { interval = setInterval(() => goTo(current + 1), 5000); });
}

// Filters sidebar (mobile)
function initFilters() {
  const mobileBtn = document.querySelector('.filters-mobile-btn');
  const sidebar = document.querySelector('.filters-sidebar');
  const overlay = document.querySelector('.overlay');

  mobileBtn?.addEventListener('click', () => {
    sidebar?.classList.add('open');
    overlay?.classList.add('active');
    document.body.style.overflow = 'hidden';
  });

  document.querySelector('.filters-close')?.addEventListener('click', closeFilters);
  overlay?.addEventListener('click', closeFilters);

  function closeFilters() {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('active');
    document.body.style.overflow = '';
  }

  // Toggle filter groups
  document.querySelectorAll('.filter-group-header').forEach(header => {
    header.addEventListener('click', () => {
      header.closest('.filter-group').classList.toggle('open');
    });
  });

  // Open first few groups
  document.querySelectorAll('.filter-group').forEach((g, i) => {
    if (i < 3) g.classList.add('open');
  });
}

// Product tabs
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = btn.dataset.tab;
      btn.closest('.product-tabs').querySelectorAll('.tab-btn, .tab-panel').forEach(el => el.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(panel)?.classList.add('active');
    });
  });
}

// Gallery
function initGallery() {
  const mainImg = document.querySelector('.gallery-main img');
  if (!mainImg) return;
  document.querySelectorAll('.gallery-thumb').forEach(thumb => {
    thumb.addEventListener('click', () => {
      mainImg.src = thumb.querySelector('img').src;
      document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
    });
  });
}

// Newsletter form
function initNewsletter() {
  document.querySelectorAll('.newsletter-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = form.querySelector('input[type="email"]')?.value;
      const name = form.querySelector('input[name="name"]')?.value || '';
      if (!email) return;
      try {
        const res = await apiRequest('/api/newsletter/subscribe/', 'POST', { email, name });
        if (res.detail) showToast(res.detail);
        form.reset();
      } catch (err) {
        showToast(err.detail || 'Ошибка подписки', 'error');
      }
    });
  });
}

// Header search
function initHeaderSearch() {
  function handleSearch(input) {
    const clearBtn = input?.parentElement?.querySelector('.search-clear');
    function updateClear() {
      if (clearBtn) clearBtn.style.display = input.value ? 'flex' : 'none';
    }
    if (clearBtn) clearBtn.addEventListener('click', () => { input.value = ''; updateClear(); input.focus(); });

    function doSearch() {
      const q = input.value.trim();
      if (!q) return;
      const onCatalog = window.location.pathname.startsWith('/catalog/') && typeof state !== 'undefined';
      if (onCatalog) {
        state.search = q;
        state.page = 1;
        if (typeof loadProducts === 'function') loadProducts();
        const catalogSearch = document.getElementById('catalog-search');
        if (catalogSearch) catalogSearch.value = q;
      } else {
        window.location.href = `/catalog/?search=${encodeURIComponent(q)}`;
      }
    }
    input.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
    if (clearBtn) { input.addEventListener('input', updateClear); updateClear(); }
  }

  handleSearch(document.getElementById('header-search-input'));
  handleSearch(document.getElementById('mobile-search-input'));

  const urlSearch = new URLSearchParams(window.location.search).get('search');
  if (urlSearch) {
    const input = document.getElementById('header-search-input');
    if (input) input.value = urlSearch;
  }
}

// Qty controls
function initQtyControls() {
  document.querySelectorAll('.qty-control').forEach(ctrl => {
    const display = ctrl.querySelector('.qty-value');
    const plusBtn  = ctrl.querySelector('.qty-plus');
    const minusBtn = ctrl.querySelector('.qty-minus');

    function getMax() {
      const raw = ctrl.dataset.max;
      return raw ? parseInt(raw) : Infinity;
    }

    function refresh() {
      const v = parseInt(display.textContent) || 1;
      const max = getMax();
      if (plusBtn)  plusBtn.disabled  = v >= max;
      if (minusBtn) minusBtn.disabled = v <= 1;
    }

    minusBtn?.addEventListener('click', () => {
      const v = parseInt(display.textContent) || 1;
      if (v > 1) { display.textContent = v - 1; refresh(); }
    });
    plusBtn?.addEventListener('click', () => {
      const v   = parseInt(display.textContent) || 1;
      const max = getMax();
      if (v < max) {
        display.textContent = v + 1;
        refresh();
      } else {
        showToast(`Доступно только ${max} шт.`, 'error');
      }
    });

    // Обновлять при изменении data-max извне (MutationObserver)
    new MutationObserver(refresh).observe(ctrl, { attributes: true, attributeFilter: ['data-max'] });
    refresh();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initHeroSlider();
  initFilters();
  initTabs();
  initGallery();
  initNewsletter();
  initQtyControls();
  initHeaderSearch();
});
