// Reports Controller
window.loadReportsView = async function() {
  await loadVehiclePLReport();
  await loadCustomerOutstandingReport();
  await loadFuelReport();
};

async function loadVehiclePLReport() {
  const tbody = document.getElementById('vehiclePLTableBody');
  if (!tbody) return;

  try {
    const data = await API.get('/reports/vehicle-pl');
    tbody.innerHTML = data.map(r => `
      <tr>
        <td style="font-weight: 700;">${r.vehicle_number}</td>
        <td>${r.make_model}</td>
        <td>${r.driver_name}</td>
        <td>${r.trips_count}</td>
        <td style="color: #16a34a; font-weight: 600;">₹ ${r.total_income.toLocaleString('en-IN')}</td>
        <td style="color: #dc2626;">₹ ${r.total_expenses.toLocaleString('en-IN')}</td>
        <td style="font-weight: 700; color: ${r.net_profit >= 0 ? '#0284c7' : '#dc2626'};">
          ₹ ${r.net_profit.toLocaleString('en-IN')}
        </td>
        <td>
          <span class="badge-status ${r.margin_percentage >= 20 ? 'success' : 'warning'}">
            ${r.margin_percentage}%
          </span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading Vehicle P&L:', err);
  }
}

async function loadCustomerOutstandingReport() {
  const tbody = document.getElementById('customerOutstandingTableBody');
  if (!tbody) return;

  try {
    const data = await API.get('/reports/customer-outstanding');
    tbody.innerHTML = data.map(c => `
      <tr>
        <td style="font-weight: 700;">${c.name}</td>
        <td>${c.company_name}</td>
        <td>${c.phone}</td>
        <td>${c.total_trips}</td>
        <td>₹ ${c.total_billed.toLocaleString('en-IN')}</td>
        <td>₹ ${c.total_paid.toLocaleString('en-IN')}</td>
        <td style="font-weight: 700; color: ${c.outstanding_balance > 0 ? '#b45309' : '#16a34a'};">
          ₹ ${c.outstanding_balance.toLocaleString('en-IN')}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading customer outstanding:', err);
  }
}

async function loadFuelReport() {
  const tbody = document.getElementById('fuelReportTableBody');
  if (!tbody) return;

  try {
    const data = await API.get('/reports/fuel');
    tbody.innerHTML = data.map(f => `
      <tr>
        <td style="font-weight: 700;">${f.vehicle_number}</td>
        <td style="color: #1e293b; font-weight: 700;">₹ ${f.total_fuel_cost.toLocaleString('en-IN')}</td>
        <td>${f.refills_count} refills</td>
        <td>${f.trips_count} trips</td>
        <td>₹ ${f.avg_fuel_per_trip.toLocaleString('en-IN')} / trip</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading fuel report:', err);
  }
}

window.downloadReportCSV = function(reportType) {
  const token = API.getToken();
  window.location.href = `/api/reports/export/${reportType}?token=${token}`;
};
