// Catalog page: filters + product list via AJAX

const _urlParams = new URLSearchParams(window.location.search);

// Favorites (guest: localStorage; auth: synced from backend)
const _favKey = 'velour_favorites';
let _favorites = new Set(JSON.parse(localStorage.getItem(_favKey) || '[]'));

function saveFavorites() { localStorage.setItem(_favKey, JSON.stringify([..._favorites])); }

async function toggleFavorite(productId, event) {
  if (event) event.preventDefault();
  const isAuth = document.body.dataset.authenticated === 'true';
  if (isAuth) {
    try {
      const res = await apiRequest(`/api/favorites/${productId}/`, 'POST');
      res.is_favorite ? _favorites.add(productId) : _favorites.delete(productId);
    } catch { return; }
  } else {
    _favorites.has(productId) ? _favorites.delete(productId) : _favorites.add(productId);
  }
  saveFavorites();
  const isFav = _favorites.has(productId);
  document.querySelectorAll(`.fav-btn[data-id="${productId}"]`).forEach(b => {
    b.classList.toggle('active', isFav);
    b.title = isFav ? 'Убрать из избранного' : 'В избранное';
  });
}

async function syncFavorites() {
  if (document.body.dataset.authenticated === 'true') {
    try {
      const res = await apiRequest('/api/favorites/status/');
      _favorites = new Set(res.favorite_ids);
      saveFavorites();
    } catch {}
  }
  document.querySelectorAll('.fav-btn').forEach(b => {
    const id = parseInt(b.dataset.id);
    b.classList.toggle('active', _favorites.has(id));
  });
  updateFavBadge();
}

function updateFavBadge() {
  const badge = document.getElementById('fav-count-badge');
  if (!badge) return;
  const count = _favorites.size;
  if (count > 0) {
    badge.textContent = count;
    badge.style.display = 'flex';
  } else {
    badge.style.display = 'none';
  }
}

const state = {
  page: 1,
  ordering: _urlParams.get('ordering') || '-created_at',
  filters: {},
  priceMin: _urlParams.get('price_min') || '',
  priceMax: _urlParams.get('price_max') || '',
  category: window.CATALOG_CATEGORY || '',
  subcategory: '',
  subsubcategory: '',
  search: _urlParams.get('search') || '',
  hasDiscount: _urlParams.get('has_discount') === 'true',
  isFeatured: _urlParams.get('is_featured') === 'true',
  isNew: _urlParams.get('is_new') === 'true',
};

const productGrid = document.getElementById('products-grid');
const loadingEl = document.getElementById('products-loading');
const countEl = document.getElementById('products-count');
const paginationEl = document.getElementById('pagination');
const activeFiltersEl = document.getElementById('active-filters');

function buildQuery() {
  const params = new URLSearchParams();
  if (state.category) params.set('category', state.category);
  if (state.subcategory) params.set('subcategory', state.subcategory);
  if (state.subsubcategory) params.set('subsubcategory', state.subsubcategory);
  if (state.search) params.set('search', state.search);
  if (state.priceMin) params.set('price_min', state.priceMin);
  if (state.priceMax) params.set('price_max', state.priceMax);
  if (state.ordering) params.set('ordering', state.ordering);
  if (state.hasDiscount) params.set('has_discount', 'true');
  if (state.isFeatured) params.set('is_featured', 'true');
  if (state.isNew) params.set('is_new', 'true');
  params.set('page', state.page);

  // Collect all selected option ids
  const optionIds = [];
  Object.values(state.filters).forEach(ids => optionIds.push(...ids));
  if (optionIds.length) params.set('options', optionIds.join(','));

  return params.toString();
}

function renderProductCard(p) {
  const img = p.main_image ? `<img src="${p.main_image}" alt="${p.name}" loading="lazy">` : '<div style="height:100%;background:var(--color-bg-alt)"></div>';
  const badgeNew = p.is_new ? '<span class="badge badge-new">Новинка</span>' : '';
  const badgeSale = p.discount_percent ? `<span class="badge badge-sale">-${p.discount_percent}%</span>` : '';
  const oldPrice = p.old_price ? `<span class="product-card-old-price">${Number(p.old_price).toLocaleString('ru')} ₽</span>` : '';
  const productUrl = `/catalog/${p.category_slug}/${p.slug}/`;
  // Products with variants require size/color selection → go to product page
  const cartAction = p.has_variants
    ? `window.location.href='${productUrl}'`
    : `addToCart(${p.id})`;
  const cartLabel = p.has_variants ? 'Выбрать' : 'В корзину';
  return `
    <a href="${productUrl}" class="product-card" data-product-id="${p.id}">
      <div class="product-card-img">
        ${img}
        <div class="product-card-badges">${badgeNew}${badgeSale}</div>
        <div class="product-card-actions">
          <button class="product-card-action-btn fav-btn ${_favorites.has(p.id) ? 'active' : ''}" data-id="${p.id}" title="${_favorites.has(p.id) ? 'Убрать из избранного' : 'В избранное'}" onclick="event.preventDefault();toggleFavorite(${p.id},event)">
            <svg viewBox="0 0 24 24" fill="transparent" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
          </button>
          <button class="product-card-action-btn" title="${cartLabel}" onclick="event.preventDefault();${cartAction}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          </button>
        </div>
      </div>
      <div class="product-card-body">
        <div class="product-card-category">${p.category_name || ''}</div>
        <div class="product-card-name">${p.name}</div>
        <div class="product-card-prices">
          <span class="product-card-price">${Number(p.price).toLocaleString('ru')} ₽</span>
          ${oldPrice}
        </div>
      </div>
      <button class="product-card-add" onclick="event.preventDefault();${cartAction}">${cartLabel}</button>
    </a>`;
}

async function loadProducts() {
  if (!productGrid) return;
  loadingEl?.classList.remove('hidden');
  productGrid.style.opacity = '0.5';

  try {
    const res = await fetch(`/api/products/?${buildQuery()}`);
    const data = await res.json();

    productGrid.innerHTML = data.results.length
      ? data.results.map(renderProductCard).join('')
      : '<div class="empty-state" style="grid-column:1/-1"><div class="empty-state-icon">🔍</div><h3>Товары не найдены</h3><p>Попробуйте изменить параметры фильтров</p></div>';

    if (countEl) countEl.innerHTML = `Найдено: <strong>${data.count}</strong> товаров`;
    renderPagination(data.count, data.next, data.previous);
  } catch (e) {
    productGrid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><p>Ошибка загрузки товаров</p></div>';
  } finally {
    loadingEl?.classList.add('hidden');
    productGrid.style.opacity = '1';
  }
}

function renderPagination(total, next, prev) {
  if (!paginationEl) return;
  const pageSize = 24;
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) { paginationEl.innerHTML = ''; return; }

  let html = '';
  if (prev) html += `<button class="page-btn" data-page="${state.page - 1}">←</button>`;

  const delta = 2;
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= state.page - delta && i <= state.page + delta)) {
      html += `<button class="page-btn ${i === state.page ? 'active' : ''}" data-page="${i}">${i}</button>`;
    } else if (i === state.page - delta - 1 || i === state.page + delta + 1) {
      html += '<span style="padding:0 4px;color:var(--color-text-muted)">…</span>';
    }
  }
  if (next) html += `<button class="page-btn" data-page="${state.page + 1}">→</button>`;

  paginationEl.innerHTML = html;
  paginationEl.querySelectorAll('.page-btn[data-page]').forEach(btn => {
    btn.addEventListener('click', () => {
      state.page = parseInt(btn.dataset.page);
      loadProducts();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
}

function renderActiveFilters() {
  if (!activeFiltersEl) return;
  const chips = [];
  Object.entries(state.filters).forEach(([groupSlug, ids]) => {
    ids.forEach(id => {
      const label = document.querySelector(`input[data-group="${groupSlug}"][value="${id}"]`)?.dataset.label;
      if (label) chips.push(`<span class="filter-chip" data-group="${groupSlug}" data-id="${id}">${label} <button class="filter-chip-remove" onclick="removeFilter('${groupSlug}',${id})">✕</button></span>`);
    });
  });
  if (state.priceMin || state.priceMax) {
    const label = [state.priceMin ? `от ${state.priceMin} ₽` : '', state.priceMax ? `до ${state.priceMax} ₽` : ''].filter(Boolean).join(' ');
    chips.push(`<span class="filter-chip">Цена: ${label} <button class="filter-chip-remove" onclick="clearPrice()">✕</button></span>`);
  }
  activeFiltersEl.innerHTML = chips.join('');
}

window.removeFilter = function(groupSlug, id) {
  state.filters[groupSlug] = (state.filters[groupSlug] || []).filter(i => i !== id);
  if (!state.filters[groupSlug].length) delete state.filters[groupSlug];
  // Uncheck checkbox
  const cb = document.querySelector(`input[data-group="${groupSlug}"][value="${id}"]`);
  if (cb) cb.checked = false;
  refreshFiltersAndLoad();
};

window.clearPrice = function() {
  state.priceMin = ''; state.priceMax = '';
  document.getElementById('price-min')?.value && (document.getElementById('price-min').value = '');
  document.getElementById('price-max')?.value && (document.getElementById('price-max').value = '');
  refreshFiltersAndLoad();
};

function refreshFiltersAndLoad() {
  state.page = 1;
  renderActiveFilters();
  loadProducts();
}

function initCatalogFilters() {
  // Checkbox filters
  document.querySelectorAll('.filter-option input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
      const group = cb.dataset.group;
      const id = parseInt(cb.value);
      if (!state.filters[group]) state.filters[group] = [];
      if (cb.checked) {
        if (!state.filters[group].includes(id)) state.filters[group].push(id);
      } else {
        state.filters[group] = state.filters[group].filter(i => i !== id);
      }
      cb.closest('.filter-option').classList.toggle('active', cb.checked);
      refreshFiltersAndLoad();
    });
  });

  // Price range
  let priceTimer;
  document.getElementById('price-min')?.addEventListener('input', e => {
    clearTimeout(priceTimer);
    priceTimer = setTimeout(() => { state.priceMin = e.target.value; refreshFiltersAndLoad(); }, 600);
  });
  document.getElementById('price-max')?.addEventListener('input', e => {
    clearTimeout(priceTimer);
    priceTimer = setTimeout(() => { state.priceMax = e.target.value; refreshFiltersAndLoad(); }, 600);
  });

  // Sort
  document.getElementById('catalog-sort')?.addEventListener('change', e => {
    state.ordering = e.target.value;
    state.page = 1;
    loadProducts();
  });

  // Subcategory links
  document.querySelectorAll('[data-subcategory]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const sub = link.dataset.subcategory;
      state.subcategory = sub;
      document.querySelectorAll('[data-subcategory]').forEach(l => {
        const isAllEmpty = l.dataset.subcategory === '';
        const isActive = sub === '' ? isAllEmpty : l.dataset.subcategory === sub;
        l.classList.toggle('active', isActive);
        l.classList.toggle('btn-dark', isActive);
        l.classList.toggle('btn-secondary', !isActive);
      });
      refreshFiltersAndLoad();
    });
  });

  // Clear all
  document.querySelector('.filters-clear')?.addEventListener('click', () => {
    state.filters = {}; state.priceMin = ''; state.priceMax = '';
    document.querySelectorAll('.filter-option input').forEach(cb => cb.checked = false);
    document.getElementById('price-min') && (document.getElementById('price-min').value = '');
    document.getElementById('price-max') && (document.getElementById('price-max').value = '');
    refreshFiltersAndLoad();
  });

  // Search
  let searchTimer;
  document.getElementById('catalog-search')?.addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { state.search = e.target.value; refreshFiltersAndLoad(); }, 400);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Restore filter state from URL params
  Object.entries(state.filters).forEach(([group, ids]) => {
    ids.forEach(id => {
      const cb = document.querySelector(`input[data-group="${group}"][value="${id}"]`);
      if (cb) { cb.checked = true; cb.closest('.filter-option').classList.add('active'); }
    });
  });

  // Restore subcategory active state from URL
  document.querySelectorAll('[data-subcategory]').forEach(btn => {
    const isEmpty = btn.dataset.subcategory === '';
    const isActive = !state.subcategory ? isEmpty : btn.dataset.subcategory === state.subcategory;
    btn.classList.toggle('active', isActive);
  });

  // Pre-fill sort from URL
  const sortEl = document.getElementById('catalog-sort');
  if (sortEl && state.ordering) sortEl.value = state.ordering;

  // Pre-fill inputs from URL params
  if (state.search) {
    const inp = document.getElementById('catalog-search');
    if (inp) inp.value = state.search;
    const headerInp = document.getElementById('header-search-input');
    if (headerInp) headerInp.value = state.search;
  }
  if (state.priceMin) { const el = document.getElementById('price-min'); if (el) el.value = state.priceMin; }
  if (state.priceMax) { const el = document.getElementById('price-max'); if (el) el.value = state.priceMax; }

  initCatalogFilters();
  loadProducts().then(() => syncFavorites());
});
