// Checkout page

document.addEventListener('DOMContentLoaded', () => {
  loadCartSummary();
  initPaymentMethods();
  initCreateAccount();
  initAddressSelect();
  initOrderSubmit();
});

async function loadCartSummary() {
  const el = document.getElementById('checkout-summary');
  if (!el) return;
  const data = await apiRequest('/api/cart/');
  if (!data.items?.length) { window.location.href = '/cart/'; return; }

  el.querySelector('.summary-subtotal-val').textContent = `${Number(data.total).toLocaleString('ru')} ₽`;
  const freeFrom = window.FREE_DELIVERY_FROM || 5000;
  const delivery = Number(data.total) >= freeFrom ? 0 : 300;
  el.querySelector('.summary-delivery-val').textContent = delivery ? `${delivery} ₽` : 'Бесплатно';
  el.querySelector('.summary-total-val').textContent = `${(Number(data.total) + delivery).toLocaleString('ru')} ₽`;

  const itemsEl = el.querySelector('.checkout-items');
  if (itemsEl) {
    itemsEl.innerHTML = data.items.map(i => `
      <div style="display:flex;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid var(--color-border-light)">
        <img src="${i.product?.main_image || ''}" style="width:48px;height:64px;object-fit:cover;border-radius:4px;background:var(--color-bg-alt)">
        <div style="flex:1;min-width:0">
          <div style="font-size:.85rem;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${i.product?.name}</div>
          ${i.variant_info ? `<div style="font-size:.75rem;color:var(--color-text-muted)">${i.variant_info}</div>` : ''}
          <div style="font-size:.82rem;color:var(--color-text-muted)">× ${i.quantity}</div>
        </div>
        <div style="font-weight:600;font-size:.88rem;white-space:nowrap">${Number(i.subtotal).toLocaleString('ru')} ₽</div>
      </div>`).join('');
  }
}

function initPaymentMethods() {
  document.querySelectorAll('.payment-method').forEach(method => {
    method.addEventListener('click', () => {
      document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('selected'));
      method.classList.add('selected');
      method.querySelector('input').checked = true;

      // Show/hide payment detail block
      const type = method.querySelector('input').value;
      document.getElementById('payment-sbp-qr')?.style.setProperty('display', type === 'sbp' ? 'block' : 'none');
      document.getElementById('payment-card-form')?.style.setProperty('display', type === 'card' ? 'block' : 'none');
    });
  });
  // Select first by default
  document.querySelector('.payment-method')?.click();
}

function initCreateAccount() {
  const toggle = document.getElementById('create-account-toggle');
  const block = document.getElementById('create-account-block');
  if (!toggle || !block) return;
  toggle.addEventListener('change', () => {
    block.style.display = toggle.checked ? 'block' : 'none';
  });
}

function initAddressSelect() {
  const select = document.getElementById('saved-address-select');
  if (!select) return;
  select.addEventListener('change', () => {
    const opt = select.options[select.selectedIndex];
    if (!opt.value) return;
    document.getElementById('delivery_city').value = opt.dataset.city || '';
    document.getElementById('delivery_street').value = opt.dataset.street || '';
    document.getElementById('delivery_apartment').value = opt.dataset.apt || '';
    document.getElementById('delivery_postal_code').value = opt.dataset.postal || '';
  });
}

function initOrderSubmit() {
  const form = document.getElementById('checkout-form');
  if (!form) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Оформляем...';

    const fd = new FormData(form);
    const payload = {
      payment_method: fd.get('payment_method') || document.querySelector('.payment-method.selected input')?.value || 'cash',
      delivery_city: fd.get('delivery_city'),
      delivery_street: fd.get('delivery_street'),
      delivery_apartment: fd.get('delivery_apartment') || '',
      delivery_postal_code: fd.get('delivery_postal_code'),
      comment: fd.get('comment') || '',
      guest_name: fd.get('guest_name') || '',
      guest_email: fd.get('guest_email') || '',
      guest_phone: fd.get('guest_phone') || '',
      create_account: document.getElementById('create-account-toggle')?.checked || false,
      account_password: fd.get('account_password') || '',
    };

    try {
      const res = await apiRequest('/api/orders/create/', 'POST', payload);
      window.location.href = `/orders/payment/${res.order_number}/`;
    } catch (err) {
      showToast(err.detail || JSON.stringify(err), 'error');
      btn.disabled = false;
      btn.textContent = 'Оформить заказ';
    }
  });
}
