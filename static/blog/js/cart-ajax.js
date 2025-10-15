(function(){
  function post(url, data, onDone){
    fetch(url, {method:'POST', headers:{'X-Requested-With':'XMLHttpRequest','X-CSRFToken':getCSRF()}, body: toFormData(data)})
      .then(r=>r.json()).then(onDone).catch(()=>{});
  }
  function getCSRF(){
    const m = document.cookie.match(/csrftoken=([^;]+)/); return m?m[1]:'';
  }
  function toFormData(obj){
    const fd = new FormData(); Object.entries(obj).forEach(([k,v])=>fd.append(k,v)); return fd;
  }
  function updateBadge(count){
    const b = document.getElementById('cart-count-badge');
    if(!b) return; b.textContent = count; b.classList.toggle('d-none', !count);
  }
  function updateTotals(row, data){
    if(!data) return;
    const subtotalCell = row.querySelector('[data-subtotal]');
    if(subtotalCell) subtotalCell.textContent = data.subtotal + ' ₴';
    const totalEl = document.getElementById('cart-total');
    if(totalEl) totalEl.textContent = data.total + ' ₴';
    updateBadge(data.count);
    if(data.removed){ row.remove(); }
    toggleEmptyState();
  }
  function toggleEmptyState(){
    const table = document.getElementById('cart-table');
    const rows = table ? table.querySelectorAll('tbody tr') : [];
    const empty = document.getElementById('cart-empty');
    const summary = document.getElementById('cart-summary');
    const hasRows = rows && rows.length>0;
    if(empty) empty.classList.toggle('d-none', hasRows);
    if(table) table.classList.toggle('d-none', !hasRows);
    if(summary) summary.classList.toggle('d-none', !hasRows);
  }

  document.addEventListener('click', function(e){
    const minusBtn = e.target.closest('[data-cart-minus]');
    if(minusBtn){
      e.preventDefault();
      const row = minusBtn.closest('tr');
      const url = minusBtn.dataset.url;
      const qty = minusBtn.dataset.qty;
      post(url, {qty: qty}, data=>updateTotals(row, data));
      return;
    }
    const plusBtn = e.target.closest('[data-cart-plus]');
    if(plusBtn){
      e.preventDefault();
      const row = plusBtn.closest('tr');
      const url = plusBtn.dataset.url;
      const qty = plusBtn.dataset.qty;
      post(url, {qty: qty}, data=>updateTotals(row, data));
      return;
    }
    const removeBtn = e.target.closest('[data-cart-remove]');
    if(removeBtn){
      e.preventDefault();
      const row = removeBtn.closest('tr');
      const url = removeBtn.dataset.url;
      post(url, {}, data=>updateTotals(row, data));
      return;
    }
    const clearBtn = e.target.closest('[data-cart-clear]');
    if(clearBtn){
      e.preventDefault();
      const url = clearBtn.dataset.url;
      post(url, {}, data=>{
        const table = document.getElementById('cart-table');
        if(table){
          const tbody = table.querySelector('tbody');
          if(tbody) tbody.innerHTML = '';
        }
        const totalEl = document.getElementById('cart-total');
        if(totalEl) totalEl.textContent = (data && data.total ? data.total : '0') + ' ₴';
        updateBadge(data && typeof data.count==='number' ? data.count : 0);
        toggleEmptyState();
      });
      return;
    }
  });
})();
