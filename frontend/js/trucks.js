// Trucks Management Controller
window.loadTrucksView = async function() {
  const container = document.getElementById('trucksGridContainer');
  const searchInput = document.getElementById('truckSearchInput');
  const searchVal = searchInput ? searchInput.value : '';

  try {
    const trucks = await API.get(`/trucks?search=${encodeURIComponent(searchVal)}`);
    if (!trucks || trucks.length === 0) {
      container.innerHTML = '<div style="grid-column: 1/-1; padding: 30px; text-align: center; color: #64748b;">No trucks found. Click "Add Truck" to register a vehicle.</div>';
      return;
    }

    container.innerHTML = trucks.map(t => `
      <div class="entity-card">
        <div class="entity-card-header">
          <div>
            <div class="entity-card-title">${t.vehicle_number}</div>
            <div class="entity-card-subtitle">${t.make_model} • ${t.vehicle_type}</div>
          </div>
          <span class="badge-status ${t.is_active ? 'success' : 'danger'}">
            ${t.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div style="font-size: 0.82rem; color: #475569;">
          <strong>Assigned Driver:</strong> ${t.assigned_driver_name}
        </div>

        <div class="entity-stats-row">
          <div>
            <div class="entity-stat-label">Total Earnings</div>
            <div class="entity-stat-val" style="color: #16a34a;">₹ ${t.total_earnings.toLocaleString('en-IN')}</div>
          </div>
          <div>
            <div class="entity-stat-label">Total Expenses</div>
            <div class="entity-stat-val" style="color: #dc2626;">₹ ${t.total_expenses.toLocaleString('en-IN')}</div>
          </div>
          <div>
            <div class="entity-stat-label">Net Profit</div>
            <div class="entity-stat-val" style="color: #0284c7;">₹ ${t.net_profit.toLocaleString('en-IN')}</div>
          </div>
          <div>
            <div class="entity-stat-label">Doc Alerts</div>
            <div class="entity-stat-val" style="color: ${t.document_alerts_count > 0 ? '#ea580c' : '#16a34a'};">
              ${t.document_alerts_count}
            </div>
          </div>
        </div>

        <div style="display: flex; gap: 8px; margin-top: 4px;">
          <button class="btn-secondary" style="flex: 1; padding: 7px 10px; font-size: 0.8rem;" onclick="viewTruckDetails(${t.id})">
            View Details
          </button>
          <button class="btn-secondary" style="color: #dc2626; border-color: #fecaca; padding: 7px 10px; font-size: 0.8rem;" onclick="deactivateTruck(${t.id}, '${t.vehicle_number}')">
            Deactivate
          </button>
        </div>
      </div>
    `).join('');

    // Also populate vehicle dropdowns across all modals
    populateVehicleDropdowns(trucks);
  } catch (err) {
    console.error('Failed to load trucks:', err);
    showToast('Failed to load trucks: ' + err.message, 'error');
  }
};

function populateVehicleDropdowns(trucks) {
  window.allTrucksCache = trucks;
  const dropdownIds = ['tripVehicleSelect', 'expenseVehicleSelect', 'docVehicleSelect', 'editTripVehicleSelect'];
  dropdownIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      const currentVal = el.value;
      el.innerHTML = '<option value="">Select Truck</option>' + trucks.map(t => `
        <option value="${t.id}">${t.vehicle_number} (${t.make_model})</option>
      `).join('');
      if (currentVal) el.value = currentVal;
    }
  });
}
window.populateVehicleDropdowns = populateVehicleDropdowns;

// Save New Truck
async function handleCreateTruck(e) {
  e.preventDefault();
  const form = document.getElementById('addTruckForm');
  const payload = {
    vehicle_number: form.vehicle_number.value.trim(),
    make_model: form.make_model.value.trim(),
    vehicle_type: form.vehicle_type.value,
    insurance_policy_number: form.insurance_policy_number.value.trim(),
    insurance_expiry: form.insurance_expiry.value || null,
    fc_expiry: form.fc_expiry.value || null,
    permit_number: form.permit_number.value.trim(),
    permit_expiry: form.permit_expiry.value || null,
    national_permit_expiry: form.national_permit_expiry.value || null,
    puc_expiry: form.puc_expiry.value || null,
    road_tax_expiry: form.road_tax_expiry.value || null,
    notes: form.notes.value.trim()
  };

  try {
    await API.post('/trucks', payload);
    showToast('Truck added successfully!', 'success');
    closeModal('modalAddTruck');
    form.reset();
    window.loadTrucksView();
    if (window.loadKPISummary) window.loadKPISummary();
  } catch (err) {
    showToast(err.message || 'Error adding truck', 'error');
  }
}

// View Truck Details
window.viewTruckDetails = async function(truckId) {
  try {
    const data = await API.get(`/trucks/${truckId}`);
    const modal = document.getElementById('modalTruckDetails');
    const content = document.getElementById('truckDetailsContent');

    content.innerHTML = `
      <div style="margin-bottom: 16px;">
        <h3 style="font-size: 1.3rem; color: #0f172a;">${data.truck.vehicle_number}</h3>
        <p style="color: #64748b; font-size: 0.85rem;">${data.truck.make_model} • ${data.truck.vehicle_type}</p>
      </div>

      <div class="entity-stats-row" style="margin-bottom: 16px;">
        <div>
          <div class="entity-stat-label">Total Earnings</div>
          <div class="entity-stat-val" style="color: #16a34a;">₹ ${data.truck.total_earnings.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Total Expenses</div>
          <div class="entity-stat-val" style="color: #dc2626;">₹ ${data.truck.total_expenses.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Net Profit</div>
          <div class="entity-stat-val" style="color: #0284c7;">₹ ${data.truck.net_profit.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Assigned Driver</div>
          <div class="entity-stat-val" style="font-size: 0.85rem;">${data.truck.assigned_driver_name}</div>
        </div>
      </div>

      <h4 style="font-size: 0.95rem; margin-bottom: 8px;">Recent Trips for this Truck</h4>
      <div class="table-responsive" style="margin-bottom: 16px;">
        <table class="data-table-mini">
          <thead>
            <tr>
              <th>Date</th>
              <th>Route</th>
              <th>Customer</th>
              <th>Rent</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${data.recent_trips.map(tr => `
              <tr>
                <td>${tr.date}</td>
                <td>${tr.route}</td>
                <td>${tr.customer}</td>
                <td>₹ ${tr.rent.toLocaleString('en-IN')}</td>
                <td><span class="badge-status ${tr.status === 'Ongoing' ? 'info' : 'success'}">${tr.status}</span></td>
              </tr>
            `).join('') || '<tr><td colspan="5">No trips yet.</td></tr>'}
          </tbody>
        </table>
      </div>
    `;

    openModal('modalTruckDetails');
  } catch (err) {
    showToast('Failed to load truck details: ' + err.message, 'error');
  }
};

window.deactivateTruck = async function(truckId, vehNum) {
  if (!confirm(`Are you sure you want to deactivate Truck ${vehNum}? Historical records will be preserved.`)) return;

  try {
    await API.delete(`/trucks/${truckId}`);
    showToast(`Truck ${vehNum} deactivated.`, 'success');
    window.loadTrucksView();
  } catch (err) {
    showToast(err.message, 'error');
  }
};
