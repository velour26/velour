// Cart page

async function loadCart() {
  const container = document.getElementById('cart-container');
  if (!container) return;

  const data = await apiRequest('/api/cart/');
  renderCart(data);
}

function renderCart(data) {
  const container = document.getElementById('cart-container');
  const summaryContainer = document.getElementById('cart-summary');
  if (!container) return;

  if (!data.items || !data.items.length) {
    const layout = document.getElementById('cart-layout');
    if (layout) {
      layout.setAttribute('style', 'display:flex !important;justify-content:center;align-items:center;min-height:350px');
      layout.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:var(--space-4xl) var(--space-xl)">
        <div style="font-size:4rem;margin-bottom:var(--space-lg);opacity:.4">🛍️</div>
        <h3 style="margin-bottom:var(--space-md);color:var(--color-text)">Корзина пуста</h3>
        <p style="color:var(--color-text-muted)">Добавьте товары из нашего каталога</p>
        <a href="/catalog/" class="btn btn-primary" style="margin-top:24px">Перейти в каталог</a>
      </div>`;
    }
    return;
  }

  container.innerHTML = data.items.map(item => {
    const img = item.product?.main_image
      ? `<img src="${item.product.main_image}" alt="${item.product?.name}">`
      : '<div style="width:100%;height:100%;background:var(--color-bg-alt)"></div>';
    const variant = item.variant_info ? `<div class="cart-item-meta">${item.variant_info}</div>` : '';
    const stock = item.variant_stock;  // null = без лимита
    const atMax = stock !== null && item.quantity >= stock;
    const plusDisabled = atMax ? 'disabled title="Максимальное количество"' : '';
    const stockHint = atMax ? `<div style="font-size:.75rem;color:var(--color-error);margin-top:4px">Максимум: ${stock} шт.</div>` : '';
    return `
      <div class="cart-item" data-item-id="${item.id}" data-stock="${stock ?? ''}">
        <div class="cart-item-img">${img}</div>
        <div>
          <a href="/catalog/${item.product?.slug}/" class="cart-item-name">${item.product?.name}</a>
          ${variant}
          <div class="qty-control" style="margin-top:12px;display:inline-flex">
            <button class="qty-btn qty-minus" onclick="updateItem(${item.id}, ${item.quantity - 1})">−</button>
            <div class="qty-value">${item.quantity}</div>
            <button class="qty-btn qty-plus" ${plusDisabled} onclick="updateItem(${item.id}, ${item.quantity + 1}, ${stock ?? 'null'})">+</button>
          </div>
          ${stockHint}
          <div><button class="cart-item-remove" onclick="removeItem(${item.id})">Удалить</button></div>
        </div>
        <div>
          <div class="cart-item-price">${Number(item.subtotal).toLocaleString('ru')} ₽</div>
          ${item.product?.old_price ? `<div style="font-size:.8rem;color:var(--color-text-light);text-decoration:line-through">${Number(item.product.old_price * item.quantity).toLocaleString('ru')} ₽</div>` : ''}
        </div>
      </div>`;
  }).join('');

  // Summary
  if (summaryContainer) {
    summaryContainer.style.display = '';
    const freeFrom = window.FREE_DELIVERY_FROM || 5000;
    const deliveryCost = Number(data.total) >= freeFrom ? 0 : 300;
    const total = Number(data.total) + deliveryCost;
    summaryContainer.querySelector('.summary-subtotal-val').textContent = `${Number(data.total).toLocaleString('ru')} ₽`;
    summaryContainer.querySelector('.summary-delivery-val').textContent = deliveryCost === 0 ? 'Бесплатно' : `${deliveryCost} ₽`;
    summaryContainer.querySelector('.summary-total-val').textContent = `${total.toLocaleString('ru')} ₽`;
    const freeEl = summaryContainer.querySelector('.delivery-hint');
    if (freeEl) {
      if (deliveryCost > 0) {
        const left = freeFrom - Number(data.total);
        freeEl.textContent = `До бесплатной доставки: ${left.toLocaleString('ru')} ₽`;
        freeEl.style.display = '';
      } else {
        freeEl.textContent = '✓ Бесплатная доставка';
        freeEl.style.color = 'var(--color-success)';
      }
    }
    document.getElementById('cart-checkout-btn')?.removeAttribute('disabled');
  }
}

async function updateItem(itemId, quantity, stock = null) {
  if (quantity < 0) return;
  // Клиентская проверка лимита
  if (stock !== null && quantity > stock) {
    showToast(`Доступно только ${stock} шт.`, 'error');
    return;
  }
  try {
    const data = await apiRequest(`/api/cart/items/${itemId}/`, 'PATCH', { quantity });
    updateCartBadge(data.count);
    renderCart(data);
  } catch (e) {
    showToast(e?.detail || 'Ошибка обновления корзины', 'error');
  }
}

async function removeItem(itemId) {
  try {
    const data = await apiRequest(`/api/cart/items/${itemId}/`, 'DELETE');
    updateCartBadge(data.count);
    renderCart(data);
    showToast('Товар удалён из корзины');
  } catch (e) {
    showToast('Ошибка', 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadCart);
