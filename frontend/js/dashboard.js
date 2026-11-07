// Dashboard Controller matching Reference Image 1
let incomeExpenseChart = null;
let expenseDonutChart = null;
let currentFilterPeriod = 'month';

// Initialize Dashboard
async function initDashboard() {
  updateCurrentDateDisplay();
  setupSidebarNavigation();
  setupUserDropdown();
  setupFilterButtons();
  
  await loadKPISummary(currentFilterPeriod);
  await loadChartsData();
  await loadUpcomingExpiries();
  await loadRecentTrips();
  await loadQuickSummary();
  await loadNotifications();
  if (window.loadOwnerProfile) window.loadOwnerProfile();
  if (window.ensureDropdownsLoaded) window.ensureDropdownsLoaded();
}

function updateCurrentDateDisplay() {
  const dateElem = document.getElementById('currentDateText');
  if (dateElem) {
    const now = new Date();
    const options = { day: '2-digit', month: 'short', year: 'numeric', weekday: 'long' };
    dateElem.textContent = now.toLocaleDateString('en-GB', options);
  }
}

function setupSidebarNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const sidebar = document.getElementById('appSidebar');
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      toggleBtn.innerHTML = sidebar.classList.contains('collapsed') ? '&gt;' : '&lt;';
    });
  }

  if (mobileMenuBtn && sidebar) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetView = item.getAttribute('data-view');
      switchModuleView(targetView);
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      if (window.innerWidth <= 768 && sidebar) {
        sidebar.classList.remove('mobile-open');
      }
    });
  });
}

function switchModuleView(viewName) {
  const allViews = document.querySelectorAll('.module-view');
  allViews.forEach(v => v.classList.remove('active-view'));

  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.add('active-view');
  }

  // Trigger sub-module specific fetch
  if (viewName === 'trucks' && window.loadTrucksView) window.loadTrucksView();
  else if (viewName === 'trips' && window.loadTripsView) {
    window.loadTripsView();
    if (window.ensureDropdownsLoaded) window.ensureDropdownsLoaded();
  }
  else if (viewName === 'expenses' && window.loadExpensesView) window.loadExpensesView();
  else if (viewName === 'drivers' && window.loadDriversView) window.loadDriversView();
  else if (viewName === 'salary' && window.loadSalaryView) window.loadSalaryView();
  else if (viewName === 'documents' && window.loadDocumentsView) window.loadDocumentsView();
  else if (viewName === 'reports' && window.loadReportsView) window.loadReportsView();
  else if (viewName === 'settings' && window.loadSettingsView) window.loadSettingsView();
}

function setupUserDropdown() {
  const profilePill = document.getElementById('ownerProfilePill');
  const dropdown = document.getElementById('profileDropdown');
  const logoutBtn = document.getElementById('logoutDropdownBtn');

  if (profilePill && dropdown) {
    profilePill.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      dropdown.classList.remove('show');
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await API.post('/auth/logout');
      } catch (e) {}
      API.clearAuth();
      window.location.href = '/login';
    });
  }

  // Notification popover
  const notifBell = document.getElementById('notifBellBtn');
  const notifPopover = document.getElementById('notifPopover');
  if (notifBell && notifPopover) {
    notifBell.addEventListener('click', (e) => {
      e.stopPropagation();
      notifPopover.classList.toggle('show');
    });
    document.addEventListener('click', () => {
      notifPopover.classList.remove('show');
    });
  }
}

function setupFilterButtons() {
  const btns = document.querySelectorAll('.period-btn');
  btns.forEach(btn => {
    btn.addEventListener('click', async () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilterPeriod = btn.getAttribute('data-period');
      await loadKPISummary(currentFilterPeriod);
    });
  });
}

// Format Currency
function formatINR(val) {
  if (val === null || val === undefined) return '₹ 0';
  const num = Number(val);
  return '₹ ' + num.toLocaleString('en-IN');
}

// 1. Load KPI Summary matching the 8 cards
async function loadKPISummary(period = 'month') {
  try {
    const kpi = await API.get(`/dashboard/kpi?period=${period}`);
    
    // Total Trucks
    document.getElementById('kpiTotalTrucks').textContent = kpi.total_trucks;
    document.getElementById('kpiTrucksSub').textContent = kpi.trucks_subtext;

    // Active Trips
    document.getElementById('kpiActiveTrips').textContent = kpi.active_trips;
    document.getElementById('kpiActiveTripsSub').textContent = kpi.active_trips_subtext;

    // Total Income
    document.getElementById('kpiTotalIncome').textContent = formatINR(kpi.total_income);
    document.getElementById('kpiIncomeSub').textContent = kpi.income_subtext;

    // Total Expenses
    document.getElementById('kpiTotalExpenses').textContent = formatINR(kpi.total_expenses);
    document.getElementById('kpiExpensesSub').textContent = kpi.expenses_subtext;

    // Balance Receivable
    document.getElementById('kpiReceivable').textContent = formatINR(kpi.balance_receivable);
    document.getElementById('kpiReceivableSub').textContent = kpi.receivable_subtext;

    // Driver Salary Pending
    document.getElementById('kpiDriverSalary').textContent = formatINR(kpi.driver_salary_pending);
    document.getElementById('kpiDriverSalarySub').textContent = kpi.salary_subtext;

    // Document Alerts
    document.getElementById('kpiDocAlerts').textContent = kpi.document_alerts;
    document.getElementById('kpiDocAlertsSub').textContent = kpi.alerts_subtext;

    // Fuel Expenses
    document.getElementById('kpiFuelExpenses').textContent = formatINR(kpi.fuel_expenses);
    document.getElementById('kpiFuelExpensesSub').textContent = kpi.fuel_subtext;

  } catch (err) {
    console.error('Failed to load KPIs:', err);
  }
}

// 2. Charts (Income vs Expenses bar chart & Expense Breakdown doughnut)
async function loadChartsData() {
  try {
    const res = await API.get('/dashboard/charts');
    renderIncomeExpenseChart(res.monthly_comparison);
    renderExpenseDonutChart(res.expense_breakdown);
  } catch (err) {
    console.error('Failed to load chart data:', err);
  }
}

function renderIncomeExpenseChart(data) {
  const ctx = document.getElementById('incomeExpenseChartCanvas');
  if (!ctx) return;

  const labels = data.map(d => d.month);
  const incomeData = data.map(d => d.income);
  const expenseData = data.map(d => d.expenses);

  if (incomeExpenseChart) {
    incomeExpenseChart.destroy();
  }

  incomeExpenseChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Income',
          data: incomeData,
          backgroundColor: '#10b981', // emerald green matching reference
          borderRadius: 4,
          barPercentage: 0.55,
          categoryPercentage: 0.6
        },
        {
          label: 'Expenses',
          data: expenseData,
          backgroundColor: '#f43f5e', // coral red matching reference
          borderRadius: 4,
          barPercentage: 0.55,
          categoryPercentage: 0.6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            boxHeight: 8,
            font: { size: 11, family: 'Plus Jakarta Sans', weight: '600' }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ₹ ${Number(context.raw).toLocaleString('en-IN')}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false }
        },
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(val) {
              if (val >= 100000) return (val / 100000).toFixed(0) + 'L';
              if (val >= 1000) return (val / 1000).toFixed(0) + 'K';
              return val;
            }
          },
          grid: { color: '#f1f5f9' }
        }
      }
    }
  });
}

function renderExpenseDonutChart(breakdown) {
  const ctx = document.getElementById('expenseDonutChartCanvas');
  if (!ctx) return;

  const items = breakdown.items || [];
  const labels = items.map(i => `${i.category} ${i.percentage}%`);
  const values = items.map(i => i.amount);

  // Set donut center total
  const centerElem = document.getElementById('donutCenterVal');
  if (centerElem) {
    centerElem.textContent = formatINR(breakdown.total_expenses);
  }

  if (expenseDonutChart) {
    expenseDonutChart.destroy();
  }

  // Exact colors matching reference: Diesel (Blue), Toll (Orange), Bata (Green), Repair (Purple), Other (Cyan)
  const categoryColors = ['#007bff', '#f59e0b', '#10b981', '#8b5cf6', '#06b6d4'];

  expenseDonutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: categoryColors,
        borderWidth: 2,
        borderColor: '#ffffff',
        cutout: '72%'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            usePointStyle: true,
            boxWidth: 7,
            font: { size: 11, family: 'Plus Jakarta Sans', weight: '500' },
            padding: 12
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ` ₹ ${Number(context.raw).toLocaleString('en-IN')}`;
            }
          }
        }
      }
    }
  });
}

// 3. Upcoming Document Expiry Table
async function loadUpcomingExpiries() {
  const tbody = document.getElementById('upcomingExpiryTableBody');
  if (!tbody) return;

  try {
    const list = await API.get('/dashboard/upcoming-expiries');
    if (!list || list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-center">No document alerts.</td></tr>';
      return;
    }

    tbody.innerHTML = list.map(item => `
      <tr>
        <td style="font-weight: 600;">${item.vehicle_number}</td>
        <td>${item.document_type}</td>
        <td>${item.expiry_date}</td>
        <td>
          <span class="badge-status ${item.status_class}">
            ${item.status_label}
          </span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading expiries:', err);
  }
}

// 4. Recent Trips Table
async function loadRecentTrips() {
  const tbody = document.getElementById('recentTripsTableBody');
  if (!tbody) return;

  try {
    const trips = await API.get('/dashboard/recent-trips');
    if (!trips || trips.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center">No recent trips.</td></tr>';
      return;
    }

    tbody.innerHTML = trips.map(t => {
      const isOngoing = t.status === 'Ongoing';
      return `
        <tr>
          <td>${t.date}</td>
          <td style="font-weight: 700; color: #0f172a;">${t.vehicle_number}</td>
          <td>${t.route}</td>
          <td>${t.customer_name}</td>
          <td>${formatINR(t.rent)}</td>
          <td>${formatINR(t.advance)}</td>
          <td style="font-weight: 600; color: #b45309;">${formatINR(t.balance)}</td>
          <td>
            <span class="badge-status ${isOngoing ? 'info' : 'success'}">
              ${t.status}
            </span>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading recent trips:', err);
  }
}

// 5. Quick Summary Section
async function loadQuickSummary() {
  try {
    const qs = await API.get('/dashboard/quick-summary');
    document.getElementById('qsTripsMonth').textContent = qs.total_trips_month;
    document.getElementById('qsDistance').textContent = `${qs.total_distance_approx.toLocaleString('en-IN')} km`;
    document.getElementById('qsFuelCost').textContent = formatINR(qs.total_fuel_cost);
    document.getElementById('qsTollCost').textContent = formatINR(qs.total_toll_cost);
    document.getElementById('qsTotalProfit').textContent = formatINR(qs.total_profit_approx);
  } catch (err) {
    console.error('Error loading quick summary:', err);
  }
}

// 6. Notifications Popover
async function loadNotifications() {
  try {
    const res = await API.get('/dashboard/notifications');
    const badge = document.getElementById('notifCountBadge');
    if (badge) {
      badge.textContent = res.unread_count || 0;
      badge.style.display = res.unread_count > 0 ? 'flex' : 'none';
    }

    const list = document.getElementById('notifListContainer');
    if (list && res.items) {
      list.innerHTML = res.items.map(n => `
        <div class="notif-item">
          <div class="notif-item-title">${n.title}</div>
          <div>${n.message}</div>
          <div class="notif-item-time">${n.created_at}</div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading notifications:', err);
  }
}

// Global modal helpers
window.openModal = function(modalId) {
  if (modalId === 'modalAddTrip' || modalId === 'modalEditTrip') {
    if (window.ensureDropdownsLoaded) window.ensureDropdownsLoaded();
  }
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('show');
};

window.closeModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('show');
};

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
  // Check auth
  if (!API.getToken()) {
    window.location.href = '/login';
    return;
  }
  initDashboard();
});
