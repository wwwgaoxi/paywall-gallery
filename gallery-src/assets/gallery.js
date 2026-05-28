(() => {
  const dataNode = document.getElementById('apps-data');
  if (dataNode) {
    const apps = JSON.parse(dataNode.textContent);
    const grid = document.getElementById('card-grid');
    const emptyState = document.getElementById('empty-state');
    const resultsCount = document.getElementById('results-count');
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    const typeFilter = document.getElementById('type-filter');
    const pricingFilter = document.getElementById('pricing-filter');
    const sortSelect = document.getElementById('sort-select');

    const uniqueValues = (key) => [...new Set(apps.map((app) => app[key]).filter(Boolean))].sort();
    const populateOptions = (select, values) => {
      values.forEach((value) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.append(option);
      });
    };

    populateOptions(categoryFilter, uniqueValues('category'));
    populateOptions(typeFilter, uniqueValues('paywall_type'));
    populateOptions(pricingFilter, uniqueValues('pricing'));

    const formatMoney = (value) => {
      if (!value) return 'Not available';
      if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
      if (value >= 1000) return `$${(value / 1000).toFixed(2)}K`;
      return `$${Math.round(value)}`;
    };

    const escapeHtml = (value) => String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');

    const badge = (value) => `<span class="badge">${escapeHtml(value)}</span>`;
    const cardTemplate = (app) => `
      <article class="app-card">
        <a class="app-card__image" href="${app.detail_path}">
          <img src="../${app.featured_image}" alt="${escapeHtml(app.app_name)} cover" loading="lazy">
        </a>
        <div class="app-card__body">
          <div class="app-card__eyebrow">${badge(app.category)}${badge(app.paywall_type)}</div>
          <h2><a href="${app.detail_path}">${escapeHtml(app.app_name)}</a></h2>
          <p class="app-card__meta">${escapeHtml(app.developer)}</p>
          <p class="app-card__pricing">${escapeHtml(app.pricing)}</p>
          <dl class="metric-grid">
            <div><dt>MRR</dt><dd>${formatMoney(app.mrr_usd)}</dd></div>
            <div><dt>Images</dt><dd>${app.image_count}</dd></div>
            <div><dt>Onboarding</dt><dd>${app.onboarding_flows_count}</dd></div>
          </dl>
        </div>
      </article>`;

    const compare = (left, right, mode) => {
      switch (mode) {
        case 'mrr-asc':
          return (left.mrr_usd || 0) - (right.mrr_usd || 0);
        case 'images-desc':
          return (right.image_count || 0) - (left.image_count || 0);
        case 'onboarding-desc':
          return (right.onboarding_flows_count || 0) - (left.onboarding_flows_count || 0);
        case 'name-asc':
          return left.app_name.localeCompare(right.app_name);
        case 'category-asc':
          return left.category.localeCompare(right.category) || left.app_name.localeCompare(right.app_name);
        case 'mrr-desc':
        default:
          return (right.mrr_usd || 0) - (left.mrr_usd || 0);
      }
    };

    const render = () => {
      const query = searchInput.value.trim().toLowerCase();
      const filtered = apps
        .filter((app) => !query || app.search_blob.includes(query))
        .filter((app) => categoryFilter.value === 'all' || app.category === categoryFilter.value)
        .filter((app) => typeFilter.value === 'all' || app.paywall_type === typeFilter.value)
        .filter((app) => pricingFilter.value === 'all' || app.pricing === pricingFilter.value)
        .sort((left, right) => compare(left, right, sortSelect.value));

      grid.innerHTML = filtered.map(cardTemplate).join('');
      resultsCount.textContent = `Showing ${filtered.length} of ${apps.length} apps`;
      emptyState.hidden = filtered.length !== 0;
    };

    [searchInput, categoryFilter, typeFilter, pricingFilter, sortSelect].forEach((element) => {
      element.addEventListener('input', render);
      element.addEventListener('change', render);
    });

    render();
  }

  const lightbox = document.querySelector('.lightbox');
  if (!lightbox) return;

  const lightboxImage = lightbox.querySelector('.lightbox__image');
  const closeButton = lightbox.querySelector('.lightbox__close');
  const open = (src, alt) => {
    lightbox.hidden = false;
    lightboxImage.src = src;
    lightboxImage.alt = alt;
    document.body.style.overflow = 'hidden';
  };
  const close = () => {
    lightbox.hidden = true;
    lightboxImage.src = '';
    lightboxImage.alt = '';
    document.body.style.overflow = '';
  };

  document.querySelectorAll('[data-full-src]').forEach((button) => {
    button.addEventListener('click', () => open(button.dataset.fullSrc, button.dataset.alt || 'Screenshot preview'));
  });

  closeButton?.addEventListener('click', close);
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) close();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !lightbox.hidden) close();
  });
})();
