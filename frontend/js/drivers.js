// Driver Management Controller
window.loadDriversView = async function() {
  const container = document.getElementById('driversGridContainer');
  const search = document.getElementById('driverSearchInput') ? document.getElementById('driverSearchInput').value : '';

  try {
    const drivers = await API.get(`/drivers?search=${encodeURIComponent(search)}`);
    if (!container) return;

    if (!drivers || drivers.length === 0) {
      container.innerHTML = '<div style="grid-column: 1/-1; padding: 30px; text-align: center; color: #64748b;">No drivers registered. Click "Add Driver" to register.</div>';
      return;
    }

    container.innerHTML = drivers.map(d => `
      <div class="entity-card">
        <div class="entity-card-header">
          <div>
            <div class="entity-card-title">${d.full_name}</div>
            <div class="entity-card-subtitle">${d.phone_number} • License: ${d.license_number}</div>
          </div>
          <span class="badge-status ${d.employment_status === 'Active' ? 'success' : 'secondary'}">
            ${d.employment_status}
          </span>
        </div>

        <div style="font-size: 0.82rem; color: #475569;">
          <strong>Assigned Truck(s):</strong> ${d.assigned_truck_text}
        </div>

        <div style="font-size: 0.82rem; color: #475569;">
          <strong>License Status:</strong>
          <span class="badge-status ${d.license_status_class}">${d.license_status}</span>
        </div>

        <div class="entity-stats-row">
          <div>
            <div class="entity-stat-label">Salary Scheme</div>
            <div class="entity-stat-val" style="font-size: 0.85rem;">${d.salary_type}</div>
          </div>
          <div>
            <div class="entity-stat-label">Monthly Rate</div>
            <div class="entity-stat-val">₹ ${d.monthly_salary.toLocaleString('en-IN')}</div>
          </div>
          <div>
            <div class="entity-stat-label">Trips Completed</div>
            <div class="entity-stat-val" style="color: #0284c7;">${d.trips_count}</div>
          </div>
          <div>
            <div class="entity-stat-label">Pending Salary</div>
            <div class="entity-stat-val" style="color: #b45309;">₹ ${d.pending_salary.toLocaleString('en-IN')}</div>
          </div>
        </div>

        <div style="display: flex; gap: 8px; margin-top: 4px;">
          <button class="btn-secondary" style="flex: 1; padding: 7px 10px; font-size: 0.8rem;" onclick="viewDriverDetails(${d.id})">
            Driver History
          </button>
        </div>
      </div>
    `).join('');

    populateDriverDropdowns(drivers);
  } catch (err) {
    console.error('Failed to load drivers:', err);
    showToast('Failed to load drivers: ' + err.message, 'error');
  }
};

function populateDriverDropdowns(drivers) {
  window.allDriversCache = drivers;
  const ids = ['tripDriverSelect', 'salaryDriverSelect', 'bataDriverSelect', 'editTripDriverSelect'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      const currentVal = el.value;
      el.innerHTML = '<option value="">Select Driver</option>' + drivers.map(d => `
        <option value="${d.id}">${d.full_name} (${d.phone_number})</option>
      `).join('');
      if (currentVal) el.value = currentVal;
    }
  });
}
window.populateDriverDropdowns = populateDriverDropdowns;

async function handleCreateDriver(e) {
  e.preventDefault();
  const form = document.getElementById('addDriverForm');
  const payload = {
    full_name: form.full_name.value.trim(),
    phone_number: form.phone_number.value.trim(),
    address: form.address.value.trim(),
    license_number: form.license_number.value.trim(),
    license_expiry: form.license_expiry.value || null,
    salary_type: form.salary_type.value,
    monthly_salary: parseFloat(form.monthly_salary.value || 0),
    daily_salary: parseFloat(form.daily_salary.value || 0),
    bata_per_trip: parseFloat(form.bata_per_trip.value || 500),
    notes: form.notes.value.trim()
  };

  try {
    await API.post('/drivers', payload);
    showToast('Driver added successfully!', 'success');
    closeModal('modalAddDriver');
    form.reset();
    window.loadDriversView();
  } catch (err) {
    showToast(err.message || 'Error adding driver', 'error');
  }
}

window.viewDriverDetails = async function(driverId) {
  try {
    const data = await API.get(`/drivers/${driverId}`);
    const modal = document.getElementById('modalDriverDetails');
    const content = document.getElementById('driverDetailsContent');

    content.innerHTML = `
      <div style="margin-bottom: 16px;">
        <h3 style="font-size: 1.3rem; color: #0f172a;">${data.full_name}</h3>
        <p style="color: #64748b; font-size: 0.85rem;">Phone: ${data.phone_number} | License: ${data.license_number} (${data.license_status})</p>
      </div>

      <div class="entity-stats-row" style="margin-bottom: 16px;">
        <div>
          <div class="entity-stat-label">Salary Scheme</div>
          <div class="entity-stat-val">${data.salary_type}</div>
        </div>
        <div>
          <div class="entity-stat-label">Monthly Rate</div>
          <div class="entity-stat-val">₹ ${data.monthly_salary.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Daily Wage Rate</div>
          <div class="entity-stat-val">₹ ${data.daily_salary.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Standard Bata / Trip</div>
          <div class="entity-stat-val">₹ ${data.bata_per_trip.toLocaleString('en-IN')}</div>
        </div>
      </div>

      <h4 style="font-size: 0.95rem; margin-bottom: 8px;">Recent Trips Handled</h4>
      <div class="table-responsive" style="margin-bottom: 16px;">
        <table class="data-table-mini">
          <thead>
            <tr>
              <th>Date</th>
              <th>Route</th>
              <th>Customer</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${data.recent_trips.map(tr => `
              <tr>
                <td>${tr.date}</td>
                <td>${tr.route}</td>
                <td>${tr.customer}</td>
                <td><span class="badge-status ${tr.status === 'Ongoing' ? 'info' : 'success'}">${tr.status}</span></td>
              </tr>
            `).join('') || '<tr><td colspan="4">No trips assigned yet.</td></tr>'}
          </tbody>
        </table>
      </div>
    `;

    openModal('modalDriverDetails');
  } catch (err) {
    showToast('Failed to load driver details: ' + err.message, 'error');
  }
};
