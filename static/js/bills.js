// This handles the client side rendering of My Bills and Bill Search
// This was written in one go, mutated a lot to fit emerging needs in constrained time


// state stuff

const SEARCH_PAGE_SIZE = 20;
const searchState = { bills: [], meta: {}, page: 1, hydrated: false };
const savedBillsIndex = new Map();

// init

// Initializes listeners
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#dashboardTab [data-bs-target]').forEach(btn => {
        btn.addEventListener('shown.bs.tab', () => {
            const target = btn.getAttribute('data-bs-target') ?? '';
            syncTabToUrl(target.replace('#', ''));
        });
    });

    const searchTabBtn = document.querySelector('[data-bs-target="#mysearch"]');
    if (searchTabBtn) {
        searchTabBtn.addEventListener('shown.bs.tab', onSearchTabActivated);
        if (searchTabBtn.classList.contains('active')) {
            onSearchTabActivated();
        }
    }

    const mybillsTabBtn = document.querySelector('[data-bs-target="#mybills"]');
    if (mybillsTabBtn) {
        mybillsTabBtn.addEventListener('shown.bs.tab', onMyBillsTabActivated);
        if (mybillsTabBtn.classList.contains('active')) {
            onMyBillsTabActivated();
        }
    }

    const overviewTabBtn = document.querySelector('[data-bs-target="#overview"]');
    if (overviewTabBtn) {
        overviewTabBtn.addEventListener('shown.bs.tab', onOverviewTabActivated);
        if (overviewTabBtn.classList.contains('active')) {
            onOverviewTabActivated();
        }
    }

    document.querySelector('[data-search-page="prev"]')?.addEventListener('click', () => changeSearchPage(-1));
    document.querySelector('[data-search-page="next"]')?.addEventListener('click', () => changeSearchPage(1));

    const onFilterChange = () => {
        searchState.page = 1;
        populateSearchResultsList(searchState.bills, searchState.meta, searchState.page);
    }

    document.querySelector('#bill-search-keyword')?.addEventListener('input', onFilterChange);
    document.querySelector('#bill-search-type-selector')?.addEventListener('change', onFilterChange);
});


// --- Helpers ---

// Pushes the active tab into ?tab=... so refresh lands you back where you were
function syncTabToUrl(tabName) {
    const url = new URL(window.location.href);
    url.searchParams.set('tab', tabName);
    window.history.replaceState({}, '', url);
}

// Stable string key for a bill so saved/search lists can find each other
function billKey(bill) {
    const type = bill.type ?? bill.bill_type ?? '';
    return `${type}-${bill.number ?? ''}`;
}

// Re-flags search results based on what's currently in the saved index
function reconcileSearchBillsSaved() {
    searchState.bills.forEach(b => {
        const id = savedBillsIndex.get(billKey(b));
        b.saved = id != null;
        b.saved_id = id ?? null;
    });
}

// Clones the markup out of a <template> tag so we can populate it
function instantiateTemplate(id) {
    const tpl = document.getElementById(id);
    return tpl.content.firstElementChild.cloneNode(true);
}

// Grabs every [data-field="..."] inside a card so we can set them by name
function fields(root) {
    const map = {};
    root.querySelectorAll('[data-field]').forEach(el => {
        map[el.dataset.field] = el;
    });
    return map;
}

// Shows a card row if there's a value, hides it if not — keeps cards from looking empty
function setOptionalRow(rowEl, valueEl, value) {
    if (value) {
        valueEl.textContent = value;
        rowEl.hidden = false;
    } else {
        rowEl.hidden = true;
    }
}


// --- Overview Tab ---

// Entrypoint when user clicks the 'Overview' tab
async function onOverviewTabActivated() {
    const container = document.querySelector('#overview-bill-list');
    if (!container) return;
    try {
        const res = await fetch('/tracked-bills/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await res.json();
        populateOverviewBillsList(data.bills ?? []);
    } catch (err) {
        container.innerHTML = '';
        const p = document.createElement('p');
        p.className = 'text-muted mb-0';
        p.textContent = 'Failed to load tracked bills.';
        container.appendChild(p);
    }
}

// Drops the tracked-bills cards into the Overview tab, or the empty-state if none
function populateOverviewBillsList(bills) {
    const container = document.querySelector('#overview-bill-list');
    if (!container) return;
    container.innerHTML = '';

    if (!bills.length) {
        const p = document.createElement('p');
        p.className = 'text-muted mb-0';
        p.textContent = 'No bills tracked yet.';
        container.appendChild(p);
        return;
    }

    bills.forEach(bill => container.appendChild(buildOverviewBillCard(bill)));
}

// Stamps out one Overview bill card from the template
function buildOverviewBillCard(bill) {
    const card = instantiateTemplate('overview-bill-card-template');
    const f = fields(card);
    const title = bill.title ?? '';

    f.code.textContent = `${bill.type ?? ''}. ${bill.number ?? ''}`;
    f.title.textContent = title.length > 80 ? title.slice(0, 79) + '…' : title;
    return card;
}


// --- My Bills Tab --- 

// Entrypoint when user clicks 'My Bills'
async function onMyBillsTabActivated() {
    const container = document.querySelector('#my-bills-list');
    if (!container) return;
    // !!! this attempts to refresh bills from server without re-rendering entire view
    try {
        const res = await fetch('/tracked-bills/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await res.json();
        const bills = data.bills ?? [];
        savedBillsIndex.clear();
        bills.forEach(b => savedBillsIndex.set(billKey(b), b.id));
        populateMyBillsList(bills);
    } catch (err) {
        container.innerHTML = '';
        const col = document.createElement('div');
        col.className = 'col-12';
        const p = document.createElement('p');
        p.className = 'text-muted mb-0';
        p.textContent = 'Failed to load saved bills.';
        col.appendChild(p);
        container.appendChild(col);
    }
}

// Drops saved-bill cards into the My Bills tab, or the empty-state if none
function populateMyBillsList(bills) {
    const container = document.querySelector('#my-bills-list');
    if (!container) return;
    container.innerHTML = '';

    if (!bills || bills.length === 0) {
        const col = document.createElement('div');
        col.className = 'col-12';
        const p = document.createElement('p');
        p.className = 'text-muted mb-0';
        p.textContent = 'No saved bills yet.';
        col.appendChild(p);
        container.appendChild(col);
        return;
    }

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ?? '';
    bills.forEach(bill => container.appendChild(buildMyBillCard(bill, csrfToken)));
}

// Stamps out one My Bills card and wires up its remove form
function buildMyBillCard(bill, csrfToken) {
    const detail = bill.detail ?? {};
    const col = instantiateTemplate('my-bill-card-template');
    const f = fields(col);

    f.code.textContent = `${bill.type ?? ''}. ${bill.number ?? ''}`;
    f.status.textContent = detail.bill_status ?? '';
    f.title.textContent = bill.title ?? '';
    f.congress.textContent = `Congress: ${bill.congress ?? ''}`;
    f.chamber.textContent = bill.originChamberCode ?? '';

    setOptionalRow(f['introduced-row'], f.introduced, detail.introducedDate);
    setOptionalRow(f['summary-row'], f.summary, detail.bill_summary);
    setOptionalRow(f['action-row'], f.action, detail.actionDesc);

    f.form.action = `/remove-bill/${encodeURIComponent(bill.id)}/`;
    f.csrf.value = csrfToken;
    f.form.addEventListener('submit', (e) => handleMyBillRemoveSubmit(e, bill, col));

    return col;
}

// AJAX submit for the Remove button — yanks the card without a full reload
async function handleMyBillRemoveSubmit(e, bill, col) {
    e.preventDefault();
    const form = e.currentTarget;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    try {
        const res = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await res.json();
        if (!res.ok || !data.ok) {
            showMyBillsMessage(data.error ?? 'Something went wrong.', 'danger');
            submitBtn.disabled = false;
            return;
        }

        savedBillsIndex.delete(billKey(bill));
        col.remove();

        const container = document.querySelector('#my-bills-list');
        if (container && container.children.length === 0) {
            const emptyCol = document.createElement('div');
            emptyCol.className = 'col-12';
            const p = document.createElement('p');
            p.className = 'text-muted mb-0';
            p.textContent = 'No saved bills yet.';
            emptyCol.appendChild(p);
            container.appendChild(emptyCol);
        }

        reconcileSearchBillsSaved();
        showMyBillsMessage(data.message ?? 'Removed.', 'success');
    } catch (err) {
        showMyBillsMessage('Network error — please try again.', 'danger');
        submitBtn.disabled = false;
    }
}

// Pops a single alert in the My Bills tab — only one at a time, no spam down the page
function showMyBillsMessage(text, variant) {
    const host = document.querySelector('#mybills');
    if (!host) return;
    host.querySelectorAll(':scope > .alert').forEach(el => el.remove());

    const alert = document.createElement('div');
    alert.className = `alert alert-${variant} alert-dismissible fade show mt-2`;
    alert.setAttribute('role', 'alert');
    alert.textContent = text;

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'btn-close';
    close.setAttribute('data-bs-dismiss', 'alert');
    alert.appendChild(close);

    host.prepend(alert);
    setTimeout(() => alert.remove(), 4000);
}


// --- Search Tab --- 

// Entrypoint when user clicks the 'My Search' tab
function onSearchTabActivated() {
    if (!searchState.hydrated) {
        const dataEl = document.getElementById('search-results-data');
        if (!dataEl) return;
        const data = JSON.parse(dataEl.textContent);
        searchState.bills = data.bills ?? [];
        searchState.meta = data.meta ?? {};
        searchState.page = 1;
        searchState.hydrated = true;
        searchState.bills.forEach(b => {
            if (b.saved && b.saved_id != null) savedBillsIndex.set(billKey(b), b.saved_id);
        });
    }
    reconcileSearchBillsSaved();
    populateSearchResultsList(searchState.bills, searchState.meta, searchState.page);
}

// Bumps the search results page +/- 1 and re-renders
function changeSearchPage(delta) {
    const totalPages = Math.max(1, Math.ceil(searchState.bills.length / SEARCH_PAGE_SIZE));
    const next = Math.min(totalPages, Math.max(1, searchState.page + delta));
    if (next === searchState.page) return;
    searchState.page = next;
    populateSearchResultsList(searchState.bills, searchState.meta, searchState.page);
}

// Applies the keyword + chamber filters from the Search form to the bill list
function getFilteredBills(bills) {
    const keyword = document.querySelector('#bill-search-keyword')?.value.trim().toLowerCase() ?? '';
    const billType = document.querySelector('#bill-search-type-selector')?.value ?? '';

    let filtered = bills;

    if (billType !== '') {
        filtered = filtered.filter(bill => bill.chamber === billType);
    }

    if (keyword !== '') {
        filtered = filtered.filter(bill => (bill.title ?? '').toLowerCase().includes(keyword));
    }

    return filtered;
}

// Updates the "X results" label above the search list
function updateResultsCount(count) {
    const resultsCountEl = document.querySelector('#results-count');
    resultsCountEl.innerHTML = `${count} results`;
}

// Filters, paginates, and renders the Search tab — also wires up the prev/next buttons
function populateSearchResultsList(bills, meta, page) {
    const container = document.querySelector('#mysearch .bill-list');
    if (!container) return;

    container.innerHTML = '';

    let filtered_bills = getFilteredBills(bills ?? []);

    updateResultsCount(filtered_bills.length);

    const totalPages = Math.max(1, Math.ceil(filtered_bills.length / SEARCH_PAGE_SIZE));
    const pageNum = Math.min(totalPages, Math.max(1, page || 1));
    searchState.page = pageNum;

    const pageIndicator = document.querySelector('[data-search-page-current]');
    if (pageIndicator) pageIndicator.textContent = String(pageNum);

    const prevBtn = document.querySelector('[data-search-page="prev"]');
    const nextBtn = document.querySelector('[data-search-page="next"]');

    if (prevBtn) prevBtn.disabled = pageNum <= 1;
    if (nextBtn) nextBtn.disabled = pageNum >= totalPages;

    if (!filtered_bills || filtered_bills.length === 0) {
        const empty = document.createElement('p');
        empty.className = 'text-muted mb-0';
        empty.textContent = 'No bills found.';
        container.appendChild(empty);
        return;
    }

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ?? '';
    const userId = document.querySelector('#hidden_id')?.value ?? '';

    const start = (pageNum - 1) * SEARCH_PAGE_SIZE;
    const end = Math.min(start + SEARCH_PAGE_SIZE, filtered_bills.length);
    for (let i = start; i < end; i++) {
        container.appendChild(buildBillCard(filtered_bills[i], meta, csrfToken, userId));
    }
}

// Stamps out one Search result card — Save vs Remove depending on whether it's tracked
function buildBillCard(bill, meta, csrfToken, userId) {
    const congress = meta.congress ?? '';
    const card = instantiateTemplate('search-bill-card-template');
    const f = fields(card);

    f.code.textContent = `${bill.bill_type ?? ''} ${bill.number ?? ''}`.trim();
    f.title.textContent = bill.title ?? '';
    f.congress.textContent = `Congress: ${congress}`;
    f.csrf.value = csrfToken;

    if (bill.saved) {
        f.form.action = `/remove-bill/${encodeURIComponent(bill.saved_id)}/`;
        f.button.className = 'btn btn-outline-danger btn-sm remove-bill-btn';
        f.button.textContent = 'Remove';
    } else {
        f.form.action = `/save-bill/${encodeURIComponent(bill.number)}/`;
        f['save-title'].value = bill.title ?? '';
        f['save-congress'].value = congress;
        f['save-type'].value = bill.bill_type ?? '';
        f['save-userid'].value = userId;
        f.button.className = 'btn btn-primary btn-sm save-bill-btn';
        f.button.textContent = 'Save Bill';
    }

    f.form.addEventListener('submit', (e) => handleBillFormSubmit(e, bill, card, meta, csrfToken, userId));
    return card;
}

// AJAX submit for the Save/Remove button in Search — flips the card without reloading
async function handleBillFormSubmit(e, bill, card, meta, csrfToken, userId) {
    e.preventDefault();
    const form = e.currentTarget;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    try {
        const res = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await res.json();
        if (!res.ok || !data.ok) {
            showSearchMessage(data.error ?? 'Something went wrong.', 'danger');
            submitBtn.disabled = false;
            return;
        }

        if (bill.saved) {
            bill.saved = false;
            bill.saved_id = null;
            savedBillsIndex.delete(billKey(bill));
        } else {
            bill.saved = true;
            bill.saved_id = data.id;
            savedBillsIndex.set(billKey(bill), data.id);
        }

        const newCard = buildBillCard(bill, meta, csrfToken, userId);
        card.replaceWith(newCard);
        showSearchMessage(data.message ?? 'Done.', 'success');
    } catch (err) {
        showSearchMessage('Network error — please try again.', 'danger');
        submitBtn.disabled = false;
    }
}

// Pops a single alert in the Search tab — only one at a time, no spam down the page
function showSearchMessage(text, variant) {
    const host = document.querySelector('#mysearch');
    if (!host) return;
    host.querySelectorAll(':scope > .alert').forEach(el => el.remove());

    const alert = document.createElement('div');
    alert.className = `alert alert-${variant} alert-dismissible fade show mt-2`;
    alert.setAttribute('role', 'alert');
    alert.textContent = text;

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'btn-close';
    close.setAttribute('data-bs-dismiss', 'alert');
    alert.appendChild(close);

    host.prepend(alert);
    setTimeout(() => alert.remove(), 4000);
}
