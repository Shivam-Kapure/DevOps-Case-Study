/**
 * Enterprise Payment & Notification Engine - Dashboard Logic
 */

(function () {
  'use strict';

  // Application State
  const state = {
    apiUrl: (window.__APP_CONFIG__ && window.__APP_CONFIG__.backendApiUrl) || 'http://localhost:28081',
    isOnline: false,
    latencyMs: null,
    health: null,
    payments: [],
    notifications: [],
    filterStatus: 'ALL',
    searchQuery: '',
    isLoading: false,
    pollTimer: null,
  };

  // DOM Elements Cache
  const elements = {
    // Header & Health
    healthPill: document.getElementById('health-pill'),
    connectionDot: document.getElementById('connection-dot'),
    connectionStatusText: document.getElementById('connection-status-text'),
    connectionUrlText: document.getElementById('connection-url-text'),
    btnRefresh: document.getElementById('btn-refresh'),
    refreshIcon: document.getElementById('refresh-icon'),
    btnNewPayment: document.getElementById('btn-new-payment'),
    btnSettings: document.getElementById('btn-settings'),
    envBadge: document.getElementById('env-badge'),

    // Alert Banner
    alertBanner: document.getElementById('alert-banner'),
    alertDetails: document.getElementById('alert-details'),
    alertUrl: document.getElementById('alert-url'),
    btnBannerRetry: document.getElementById('btn-banner-retry'),
    btnBannerConfig: document.getElementById('btn-banner-config'),

    // KPI Cards
    kpiHealthStatus: document.getElementById('kpi-health-status'),
    kpiStatusTag: document.getElementById('kpi-status-tag'),
    kpiUptime: document.getElementById('kpi-uptime'),
    kpiEnv: document.getElementById('kpi-env'),
    kpiTotalVolume: document.getElementById('kpi-total-volume'),
    kpiTransactionsCount: document.getElementById('kpi-transactions-count'),
    kpiSuccessRate: document.getElementById('kpi-success-rate'),
    kpiNotifsCount: document.getElementById('kpi-notifs-count'),
    kpiNotifsDelivered: document.getElementById('kpi-notifs-delivered'),
    kpiNotifsQueued: document.getElementById('kpi-notifs-queued'),
    kpiLatency: document.getElementById('kpi-latency'),

    // Payments Section
    paymentsBadge: document.getElementById('payments-badge'),
    paymentsSearchInput: document.getElementById('payments-search-input'),
    statusFilters: document.getElementById('status-filters'),
    paymentsTbody: document.getElementById('payments-tbody'),
    paymentsEmptyState: document.getElementById('payments-empty-state'),
    paymentsEmptyDesc: document.getElementById('payments-empty-desc'),
    paymentsLoadingState: document.getElementById('payments-loading-state'),
    btnResetFilters: document.getElementById('btn-reset-filters'),

    // Notifications Section
    notifsBadge: document.getElementById('notifs-badge'),
    notificationsStream: document.getElementById('notifications-stream'),
    notifsEmptyState: document.getElementById('notifs-empty-state'),

    // Modals
    modalPayment: document.getElementById('modal-payment'),
    formSimulatePayment: document.getElementById('form-simulate-payment'),
    btnClosePaymentModal: document.getElementById('btn-close-payment-modal'),
    btnCancelPayment: document.getElementById('btn-cancel-payment'),
    btnSubmitPayment: document.getElementById('btn-submit-payment'),

    modalDetails: document.getElementById('modal-details'),
    detailsGrid: document.getElementById('details-grid'),
    detailsJson: document.getElementById('details-json'),
    btnCloseDetailsModal: document.getElementById('btn-close-details-modal'),
    btnCloseDetailsBtn: document.getElementById('btn-close-details-btn'),

    modalSettings: document.getElementById('modal-settings'),
    inputApiUrl: document.getElementById('input-api-url'),
    btnTestConnection: document.getElementById('btn-test-connection'),
    testConnectionResult: document.getElementById('test-connection-result'),
    btnSaveSettings: document.getElementById('btn-save-settings'),
    btnResetApiUrl: document.getElementById('btn-reset-api-url'),
    btnCancelSettings: document.getElementById('btn-cancel-settings'),
    btnCloseSettingsModal: document.getElementById('btn-close-settings-modal'),

    // Toasts
    toastContainer: document.getElementById('toast-container'),
  };

  /**
   * Helper: Show Toast notification
   */
  function showToast(message, type = 'info') {
    if (!elements.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  /**
   * Helper: Format Currency
   */
  function formatMoney(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(amount);
  }

  /**
   * Helper: Format Date/Time
   */
  function formatDateTime(isoString) {
    if (!isoString) return '--';
    try {
      const d = new Date(isoString);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      });
    } catch {
      return isoString;
    }
  }

  /**
   * Helper: Format Uptime Seconds
   */
  function formatUptime(seconds) {
    if (seconds == null || isNaN(seconds)) return '--';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hrs > 0) return `${hrs}h ${mins}m`;
    if (mins > 0) return `${mins}m ${secs}s`;
    return `${secs}s`;
  }

  /**
   * Attempt dynamic runtime config discovery (/config.json)
   */
  async function discoverRuntimeConfig() {
    try {
      const res = await fetch('/config.json', { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        if (data && data.backendApiUrl) {
          // If user hasn't explicitly overridden in localStorage
          if (!window.localStorage.getItem('API_URL_OVERRIDE')) {
            state.apiUrl = data.backendApiUrl.replace(/\/$/, '');
          }
        }
      }
    } catch {
      // Ignore static environment without config.json
    }
  }

  /**
   * Fetch Health Status from Backend
   */
  async function fetchHealth() {
    const start = performance.now();
    try {
      const res = await fetch(`${state.apiUrl}/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      const end = performance.now();
      state.latencyMs = Math.round(end - start);

      if (res.ok) {
        const data = await res.json();
        state.isOnline = true;
        state.health = data;
        updateHealthUI(true);
        return true;
      } else {
        throw new Error(`HTTP ${res.status}`);
      }
    } catch (err) {
      state.isOnline = false;
      state.health = null;
      state.latencyMs = null;
      updateHealthUI(false, err.message);
      return false;
    }
  }

  /**
   * Update Health UI Indicator and Diagnostics Banner
   */
  function updateHealthUI(isOnline, errorDetail) {
    elements.connectionUrlText.textContent = state.apiUrl;

    if (isOnline) {
      elements.connectionDot.className = 'status-indicator status-connected';
      elements.connectionStatusText.textContent = `Online (${state.latencyMs}ms)`;
      elements.alertBanner.classList.add('hidden');

      elements.kpiHealthStatus.textContent = 'HEALTHY';
      elements.kpiHealthStatus.className = 'metric-value text-success';
      elements.kpiStatusTag.textContent = 'FastAPI v3.12';
      elements.kpiStatusTag.className = 'metric-tag tag-cyan';
      elements.kpiUptime.textContent = `Uptime: ${formatUptime(state.health?.uptime_seconds)}`;
      elements.kpiEnv.textContent = `Env: ${state.health?.environment || 'development'}`;
      elements.kpiLatency.textContent = `Latency: ${state.latencyMs}ms`;
    } else {
      elements.connectionDot.className = 'status-indicator status-error';
      elements.connectionStatusText.textContent = 'Disconnected';
      elements.alertBanner.classList.remove('hidden');
      elements.alertUrl.textContent = state.apiUrl;

      elements.kpiHealthStatus.textContent = 'OFFLINE';
      elements.kpiHealthStatus.className = 'metric-value text-danger';
      elements.kpiStatusTag.textContent = 'No Signal';
      elements.kpiStatusTag.className = 'metric-tag tag-amber';
      elements.kpiUptime.textContent = 'Uptime: N/A';
      elements.kpiLatency.textContent = 'Latency: Timeout';
    }
  }

  /**
   * Fetch Payments from Backend API
   */
  async function fetchPayments() {
    try {
      const res = await fetch(`${state.apiUrl}/api/payments`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      state.payments = data.items || [];
      renderPayments();
      updatePaymentMetrics();
    } catch (err) {
      console.warn('Failed to fetch payments:', err);
      // Keep existing payments in state if offline
      renderPayments();
    }
  }

  /**
   * Fetch Notifications from Backend API
   */
  async function fetchNotifications() {
    try {
      const res = await fetch(`${state.apiUrl}/api/notifications`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      state.notifications = data.items || [];
      renderNotifications();
      updateNotificationMetrics();
    } catch (err) {
      console.warn('Failed to fetch notifications:', err);
      renderNotifications();
    }
  }

  /**
   * Orchestrate Full Refresh
   */
  async function refreshAll() {
    if (state.isLoading) return;
    state.isLoading = true;
    elements.refreshIcon.classList.add('spinning');
    elements.paymentsLoadingState.classList.remove('hidden');

    try {
      const online = await fetchHealth();
      if (online) {
        await Promise.all([fetchPayments(), fetchNotifications()]);
      }
    } finally {
      state.isLoading = false;
      elements.refreshIcon.classList.remove('spinning');
      elements.paymentsLoadingState.classList.add('hidden');
    }
  }

  /**
   * Render Payments Table
   */
  function renderPayments() {
    const tbody = elements.paymentsTbody;
    tbody.innerHTML = '';

    const filtered = state.payments.filter((p) => {
      // Filter status
      const matchesStatus =
        state.filterStatus === 'ALL' ||
        p.status.toUpperCase() === state.filterStatus.toUpperCase();

      // Search query
      const q = state.searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        p.id.toLowerCase().includes(q) ||
        p.customer.toLowerCase().includes(q) ||
        (p.description && p.description.toLowerCase().includes(q)) ||
        p.method.toLowerCase().includes(q);

      return matchesStatus && matchesSearch;
    });

    elements.paymentsBadge.textContent = `${filtered.length} of ${state.payments.length} Records`;

    if (filtered.length === 0) {
      elements.paymentsEmptyState.classList.remove('hidden');
      return;
    }
    elements.paymentsEmptyState.classList.add('hidden');

    filtered.forEach((p) => {
      const tr = document.createElement('tr');

      const statusClass = `status-pill-${p.status.toLowerCase()}`;

      tr.innerHTML = `
        <td><span class="txn-id-pill">${p.id}</span></td>
        <td><strong>${escapeHtml(p.customer)}</strong></td>
        <td class="amount-cell">${formatMoney(p.amount, p.currency)}</td>
        <td><span class="font-sm text-muted">${escapeHtml(p.method)}</span></td>
        <td><span class="status-pill ${statusClass}">${p.status}</span></td>
        <td><span class="font-sm text-muted font-mono">${formatDateTime(p.timestamp)}</span></td>
        <td class="th-actions">
          <button class="btn btn-outline btn-sm btn-inspect" data-id="${p.id}" title="Inspect transaction">
            Details
          </button>
        </td>
      `;

      tbody.appendChild(tr);
    });

    // Attach inspect click handlers
    tbody.querySelectorAll('.btn-inspect').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        openDetailsModal(id);
      });
    });
  }

  /**
   * Render Notification Events Stream
   */
  function renderNotifications() {
    const container = elements.notificationsStream;
    container.innerHTML = '';

    elements.notifsBadge.textContent = `${state.notifications.length} Events`;

    if (state.notifications.length === 0) {
      elements.notifsEmptyState.classList.remove('hidden');
      return;
    }
    elements.notifsEmptyState.classList.add('hidden');

    state.notifications.forEach((n) => {
      const card = document.createElement('div');
      card.className = 'notif-card';

      const statusClass = n.status === 'DELIVERED' ? 'text-success' : n.status === 'FAILED' ? 'text-danger' : 'text-warning';

      card.innerHTML = `
        <div class="notif-card-header">
          <span class="notif-type">${n.event_type}</span>
          <span class="notif-channel-tag">${n.channel}</span>
        </div>
        <div class="notif-recipient font-mono">${escapeHtml(n.recipient)}</div>
        <div class="notif-summary">${escapeHtml(n.payload_summary)}</div>
        <div class="notif-footer">
          <span class="${statusClass} font-mono">● ${n.status}</span>
          <span class="font-mono">${formatDateTime(n.timestamp)}</span>
        </div>
      `;

      container.appendChild(card);
    });
  }

  /**
   * Update Payment KPI Metrics
   */
  function updatePaymentMetrics() {
    const totalVolume = state.payments.reduce((acc, curr) => acc + (curr.amount || 0), 0);
    elements.kpiTotalVolume.textContent = formatMoney(totalVolume, 'USD');
    elements.kpiTransactionsCount.textContent = `${state.payments.length} Transactions`;

    const completed = state.payments.filter((p) => p.status === 'COMPLETED').length;
    const rate = state.payments.length > 0 ? Math.round((completed / state.payments.length) * 100) : 100;
    elements.kpiSuccessRate.textContent = `${rate}% Success`;
  }

  /**
   * Update Notification KPI Metrics
   */
  function updateNotificationMetrics() {
    elements.kpiNotifsCount.textContent = state.notifications.length;
    const delivered = state.notifications.filter((n) => n.status === 'DELIVERED').length;
    const queued = state.notifications.filter((n) => n.status === 'QUEUED' || n.status === 'PROCESSING').length;
    elements.kpiNotifsDelivered.textContent = `${delivered} Delivered`;
    elements.kpiNotifsQueued.textContent = `${queued} In Pipeline`;
  }

  /**
   * Submit Payment Simulation
   */
  async function handleSimulatePayment(e) {
    e.preventDefault();
    const btn = elements.btnSubmitPayment;
    btn.disabled = true;
    btn.textContent = 'Submitting...';

    const payload = {
      amount: parseFloat(document.getElementById('input-amount').value),
      currency: document.getElementById('input-currency').value,
      customer: document.getElementById('input-customer').value.trim(),
      method: document.getElementById('input-method').value,
      status: document.getElementById('input-status').value,
      description: document.getElementById('input-description').value.trim(),
    };

    try {
      const res = await fetch(`${state.apiUrl}/api/payments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned HTTP ${res.status}`);
      }

      const created = await res.json();
      showToast(`Payment ${created.id} submitted successfully!`, 'success');
      elements.modalPayment.classList.add('hidden');
      elements.formSimulatePayment.reset();
      await refreshAll();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Submit Payment';
    }
  }

  /**
   * Open Details Modal
   */
  function openDetailsModal(transactionId) {
    const payment = state.payments.find((p) => p.id === transactionId);
    if (!payment) return;

    elements.detailsGrid.innerHTML = `
      <div class="detail-item">
        <span class="detail-label">Transaction ID</span>
        <div class="detail-val font-mono text-cyan">${payment.id}</div>
      </div>
      <div class="detail-item">
        <span class="detail-label">Monetary Amount</span>
        <div class="detail-val font-mono">${formatMoney(payment.amount, payment.currency)}</div>
      </div>
      <div class="detail-item">
        <span class="detail-label">Customer / Counterparty</span>
        <div class="detail-val">${escapeHtml(payment.customer)}</div>
      </div>
      <div class="detail-item">
        <span class="detail-label">Payment Rail / Method</span>
        <div class="detail-val">${escapeHtml(payment.method)}</div>
      </div>
      <div class="detail-item">
        <span class="detail-label">Settlement Status</span>
        <div class="detail-val"><span class="status-pill status-pill-${payment.status.toLowerCase()}">${payment.status}</span></div>
      </div>
      <div class="detail-item">
        <span class="detail-label">Timestamp</span>
        <div class="detail-val font-mono font-sm">${payment.timestamp}</div>
      </div>
    `;

    elements.detailsJson.textContent = JSON.stringify(payment, null, 2);
    elements.modalDetails.classList.remove('hidden');
  }

  /**
   * Test Connection to API URL
   */
  async function testBackendConnection(testUrl) {
    elements.testConnectionResult.textContent = 'Testing...';
    elements.testConnectionResult.className = 'test-result-text text-warning';

    const normalized = testUrl.replace(/\/$/, '');
    try {
      const res = await fetch(`${normalized}/health`, { method: 'GET' });
      if (res.ok) {
        elements.testConnectionResult.textContent = '✓ Connected successfully (200 OK)';
        elements.testConnectionResult.className = 'test-result-text text-success';
        return true;
      } else {
        throw new Error(`HTTP ${res.status}`);
      }
    } catch (err) {
      elements.testConnectionResult.textContent = `✗ Connection failed: ${err.message}`;
      elements.testConnectionResult.className = 'test-result-text text-danger';
      return false;
    }
  }

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Attach Event Listeners
   */
  function attachEventListeners() {
    // Refresh Button
    elements.btnRefresh.addEventListener('click', () => {
      refreshAll();
      showToast('Refreshing service health and records...', 'info');
    });

    // Retry from banner
    elements.btnBannerRetry.addEventListener('click', () => refreshAll());
    elements.btnBannerConfig.addEventListener('click', () => openSettingsModal());

    // Search Input
    elements.paymentsSearchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderPayments();
    });

    // Filter Tabs
    elements.statusFilters.querySelectorAll('.filter-tab').forEach((tab) => {
      tab.addEventListener('click', (e) => {
        elements.statusFilters.querySelectorAll('.filter-tab').forEach((t) => t.classList.remove('active'));
        e.currentTarget.classList.add('active');
        state.filterStatus = e.currentTarget.getAttribute('data-status');
        renderPayments();
      });
    });

    // Reset Filters button
    elements.btnResetFilters.addEventListener('click', () => {
      state.filterStatus = 'ALL';
      state.searchQuery = '';
      elements.paymentsSearchInput.value = '';
      elements.statusFilters.querySelectorAll('.filter-tab').forEach((t) => {
        if (t.getAttribute('data-status') === 'ALL') t.classList.add('active');
        else t.classList.remove('active');
      });
      renderPayments();
    });

    // Simulate Payment Modal
    elements.btnNewPayment.addEventListener('click', () => {
      elements.modalPayment.classList.remove('hidden');
    });
    elements.btnClosePaymentModal.addEventListener('click', () => {
      elements.modalPayment.classList.add('hidden');
    });
    elements.btnCancelPayment.addEventListener('click', () => {
      elements.modalPayment.classList.add('hidden');
    });
    elements.formSimulatePayment.addEventListener('submit', handleSimulatePayment);

    // Details Modal
    elements.btnCloseDetailsModal.addEventListener('click', () => {
      elements.modalDetails.classList.add('hidden');
    });
    elements.btnCloseDetailsBtn.addEventListener('click', () => {
      elements.modalDetails.classList.add('hidden');
    });

    // Settings Modal
    elements.btnSettings.addEventListener('click', openSettingsModal);
    elements.healthPill.addEventListener('click', openSettingsModal);
    elements.btnCloseSettingsModal.addEventListener('click', () => {
      elements.modalSettings.classList.add('hidden');
    });
    elements.btnCancelSettings.addEventListener('click', () => {
      elements.modalSettings.classList.add('hidden');
    });

    elements.btnTestConnection.addEventListener('click', () => {
      testBackendConnection(elements.inputApiUrl.value.trim());
    });

    elements.btnSaveSettings.addEventListener('click', () => {
      const newUrl = elements.inputApiUrl.value.trim().replace(/\/$/, '');
      if (!newUrl) {
        showToast('Please enter a valid Backend API URL', 'error');
        return;
      }
      state.apiUrl = newUrl;
      window.localStorage.setItem('API_URL_OVERRIDE', newUrl);
      elements.modalSettings.classList.add('hidden');
      showToast(`API URL updated to: ${newUrl}`, 'success');
      refreshAll();
    });

    elements.btnResetApiUrl.addEventListener('click', () => {
      window.localStorage.removeItem('API_URL_OVERRIDE');
      state.apiUrl = (window.__APP_CONFIG__ && window.__APP_CONFIG__.backendApiUrl) || 'http://localhost:28081';
      elements.inputApiUrl.value = state.apiUrl;
      elements.testConnectionResult.textContent = '';
      showToast('Reset to default API URL: ' + state.apiUrl, 'info');
    });

    // Close modals on backdrop click
    [elements.modalPayment, elements.modalDetails, elements.modalSettings].forEach((modal) => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
      });
    });
  }

  function openSettingsModal() {
    elements.inputApiUrl.value = state.apiUrl;
    elements.testConnectionResult.textContent = '';
    elements.modalSettings.classList.remove('hidden');
  }

  /**
   * Initialize App
   */
  async function init() {
    attachEventListeners();
    await discoverRuntimeConfig();
    await refreshAll();

    // Periodic Background Polling (30s)
    const interval = (window.__APP_CONFIG__ && window.__APP_CONFIG__.refreshIntervalMs) || 30000;
    state.pollTimer = setInterval(() => {
      fetchHealth();
    }, interval);
  }

  // Start on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
