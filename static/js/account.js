// Profile & account pages

document.addEventListener('DOMContentLoaded', () => {
  initProfileTabs();
  loadOrders();
  initProfileForm();
  initPasswordForm();
  initAddressForm();
});

function initProfileTabs() {
  const hash = window.location.hash || '#orders';
  document.querySelectorAll('.account-nav-link[data-tab]').forEach(link => {
    if ('#' + link.dataset.tab === hash) link.classList.add('active');
    link.addEventListener('click', e => {
      e.preventDefault();
      document.querySelectorAll('.account-nav-link').forEach(l => l.classList.remove('active'));
      document.querySelectorAll('.account-tab').forEach(t => t.style.display = 'none');
      link.classList.add('active');
      document.getElementById(link.dataset.tab)?.style.setProperty('display', 'block');
      history.replaceState(null, '', '#' + link.dataset.tab);
    });
  });
  // Show active tab
  document.querySelectorAll('.account-tab').forEach(t => t.style.display = 'none');
  const activeTab = hash.slice(1);
  const el = document.getElementById(activeTab);
  if (el) el.style.display = 'block';
  else document.querySelector('.account-tab')?.style.setProperty('display', 'block');
}

async function loadOrders() {
  const tbody = document.getElementById('orders-tbody');
  if (!tbody) return;
  try {
    const data = await apiRequest('/api/orders/');
    if (!data.results?.length) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--color-text-muted)">Заказов пока нет</td></tr>';
      return;
    }
    tbody.innerHTML = data.results.map(o => `
      <tr>
        <td><a href="/orders/my/${o.number}/" style="font-weight:600;color:var(--color-primary)">${o.number}</a></td>
        <td>${new Date(o.created_at).toLocaleDateString('ru')}</td>
        <td><span class="order-status-badge status-${o.status}">${o.status_display}</span></td>
        <td>${o.items_count} поз.</td>
        <td><strong>${Number(o.total).toLocaleString('ru')} ₽</strong></td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--color-error)">Ошибка загрузки</td></tr>';
  }
}

function initProfileForm() {
  const form = document.getElementById('profile-form');
  if (!form) return;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const fd = Object.fromEntries(new FormData(form));
    try {
      await apiRequest('/api/auth/profile/', 'PATCH', fd);
      showToast('Профиль обновлён');
    } catch (err) {
      showToast(Object.values(err).flat().join(', '), 'error');
    }
  });
}

function initPasswordForm() {
  const form = document.getElementById('password-form');
  if (!form) return;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const fd = Object.fromEntries(new FormData(form));
    try {
      await apiRequest('/api/auth/change-password/', 'POST', fd);
      showToast('Пароль изменён');
      form.reset();
    } catch (err) {
      showToast(Object.values(err).flat().join(', '), 'error');
    }
  });
}

function initAddressForm() {
  const form = document.getElementById('address-form');
  if (!form) return;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const fd = Object.fromEntries(new FormData(form));
    try {
      await apiRequest('/api/auth/addresses/', 'POST', fd);
      showToast('Адрес сохранён');
      form.reset();
      loadAddresses();
    } catch (err) {
      showToast(Object.values(err).flat().join(', '), 'error');
    }
  });
  loadAddresses();
}

async function loadAddresses() {
  const container = document.getElementById('addresses-list');
  if (!container) return;
  const data = await apiRequest('/api/auth/addresses/');
  if (!data.length) { container.innerHTML = '<p style="color:var(--color-text-muted)">Адресов пока нет</p>'; return; }
  container.innerHTML = data.map(a => `
    <div style="padding:12px 16px;border:1.5px solid var(--color-border);border-radius:var(--radius-md);margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-weight:600;font-size:.88rem">${a.label}</div>
        <div style="font-size:.82rem;color:var(--color-text-muted)">${a.city}, ${a.street}${a.apartment ? `, кв. ${a.apartment}` : ''}</div>
      </div>
      <button onclick="deleteAddress(${a.id})" style="color:var(--color-text-muted);font-size:.8rem;padding:4px 8px;border-radius:4px;" class="btn btn-ghost btn-sm">Удалить</button>
    </div>`).join('');
}

async function deleteAddress(id) {
  if (!confirm('Удалить адрес?')) return;
  await apiRequest(`/api/auth/addresses/${id}/`, 'DELETE');
  loadAddresses();
}
