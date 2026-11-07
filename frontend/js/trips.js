// Trips & Loads Controller for Mother Theresa Transport

// Ensure Trucks and Drivers dropdowns are loaded
window.ensureDropdownsLoaded = async function() {
  try {
    if (!window.allTrucksCache || window.allTrucksCache.length === 0) {
      const trucks = await API.get('/trucks');
      if (window.populateVehicleDropdowns) {
        window.populateVehicleDropdowns(trucks);
      }
    }
    if (!window.allDriversCache || window.allDriversCache.length === 0) {
      const drivers = await API.get('/drivers');
      if (window.populateDriverDropdowns) {
        window.populateDriverDropdowns(drivers);
      }
    }
  } catch (err) {
    console.warn('Could not load vehicles/drivers for dropdown:', err);
  }
};

// Auto-fill driver when vehicle is chosen in Add Trip form
window.handleTripVehicleSelectChange = function(vehicleId) {
  if (!vehicleId || !window.allTrucksCache) return;
  const truck = window.allTrucksCache.find(t => String(t.id) === String(vehicleId));
  const driverSelect = document.getElementById('tripDriverSelect');
  if (truck && truck.assigned_driver_id && driverSelect && !driverSelect.value) {
    driverSelect.value = truck.assigned_driver_id;
  }
};

// Auto-fill driver when vehicle is chosen in Edit Trip form
window.handleEditTripVehicleSelectChange = function(vehicleId) {
  if (!vehicleId || !window.allTrucksCache) return;
  const truck = window.allTrucksCache.find(t => String(t.id) === String(vehicleId));
  const driverSelect = document.getElementById('editTripDriverSelect');
  if (truck && truck.assigned_driver_id && driverSelect && !driverSelect.value) {
    driverSelect.value = truck.assigned_driver_id;
  }
};

// Calculate live balance for Add Trip modal
window.calculateAddTripBalance = function() {
  const rent = parseFloat(document.getElementById('addTripRent')?.value) || 0;
  const adv = parseFloat(document.getElementById('addTripAdvance')?.value) || 0;
  const bal = Math.max(0, rent - adv);
  const display = document.getElementById('addTripBalanceDisplay');
  if (display) {
    display.value = `₹ ${bal.toLocaleString('en-IN')}`;
  }
};

// Calculate live balance for Edit Trip modal
window.calculateEditTripBalance = function() {
  const rent = parseFloat(document.getElementById('editTripRent')?.value) || 0;
  const adv = parseFloat(document.getElementById('editTripAdvance')?.value) || 0;
  const addlField = document.getElementById('editTripAdditionalPayments');
  const addl = parseFloat(addlField?.dataset?.amount) || 0;
  const bal = Math.max(0, rent - (adv + addl));
  const display = document.getElementById('editTripBalance');
  if (display) {
    display.value = `₹ ${bal.toLocaleString('en-IN')}`;
  }
};

// Load and render Trips & Loads Table
window.loadTripsView = async function() {
  const tbody = document.getElementById('tripsTableBody');
  if (!tbody) return;

  const search = document.getElementById('tripsSearchInput') ? document.getElementById('tripsSearchInput').value : '';
  const statusFilter = document.getElementById('tripsStatusFilter') ? document.getElementById('tripsStatusFilter').value : '';

  try {
    let url = `/trips?search=${encodeURIComponent(search)}`;
    if (statusFilter && statusFilter !== 'All') {
      url += `&status=${encodeURIComponent(statusFilter)}`;
    }

    const trips = await API.get(url);
    if (!trips || trips.length === 0) {
      tbody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 28px; color: #64748b;">No trips found. Click "Add New Trip" to register a load.</td></tr>';
      return;
    }

    tbody.innerHTML = trips.map(t => {
      let badgeClass = 'info';
      if (t.trip_status === 'Completed') badgeClass = 'success';
      else if (t.trip_status === 'Planned') badgeClass = 'warning';
      else if (t.trip_status === 'Cancelled') badgeClass = 'danger';

      const safeVehicle = (t.vehicle_number || '').replace(/'/g, "\\'");
      const safeRoute = (t.route || '').replace(/'/g, "\\'");

      return `
        <tr id="trip-row-${t.id}">
          <td>${t.trip_date}</td>
          <td style="font-weight: 700; color: #0f172a;">${t.vehicle_number}</td>
          <td><span title="${t.load_description ? 'Cargo: ' + t.load_description : ''}">${t.route}</span></td>
          <td>${t.customer_name}</td>
          <td style="font-weight: 500; color: #1e293b;">${t.driver_name || 'N/A'}</td>
          <td>₹ ${t.total_rent.toLocaleString('en-IN')}</td>
          <td>₹ ${t.advance_received.toLocaleString('en-IN')}</td>
          <td style="color: #0284c7;">₹ ${(t.additional_payments || 0).toLocaleString('en-IN')}</td>
          <td style="font-weight: 700; color: ${t.balance_receivable > 0 ? '#b45309' : '#16a34a'};">
            ₹ ${t.balance_receivable.toLocaleString('en-IN')}
          </td>
          <td>
            <span class="badge-status ${badgeClass}">
              ${t.trip_status}
            </span>
          </td>
          <td>
            <div style="display: flex; gap: 4px; align-items: center;">
              ${t.balance_receivable > 0 && t.trip_status !== 'Cancelled' ? `
                <button class="btn-secondary" style="padding: 4px 8px; font-size: 0.72rem; color: #0284c7;" onclick="openRecordPaymentModal(${t.id}, '${safeVehicle}', ${t.balance_receivable})" title="Record Payment">
                  + Pay
                </button>
              ` : ''}
              <button class="btn-secondary" style="padding: 4px 8px; font-size: 0.72rem;" onclick="viewTripDetailModal(${t.id})" title="View Details">
                Detail
              </button>
              <button class="btn-secondary" style="padding: 4px 8px; font-size: 0.72rem; color: #d97706;" onclick="openEditTripModal(${t.id})" title="Edit Trip">
                Edit
              </button>
              <button class="btn-secondary" style="padding: 4px 8px; font-size: 0.72rem; color: #ef4444;" onclick="openDeleteTripModal(${t.id}, '${safeVehicle}', '${safeRoute}')" title="Delete Trip">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load trips:', err);
    showToast('Failed to load trips: ' + err.message, 'error');
  }
};

// Create Trip Handler
window.handleCreateTrip = async function(e) {
  e.preventDefault();
  const form = document.getElementById('addTripForm');

  const tripDate = form.trip_date.value;
  const vehicleId = parseInt(form.vehicle_id.value);
  const customerName = form.customer_name.value.trim();
  const fromLocation = form.from_location.value.trim();
  const toLocation = form.to_location.value.trim();
  const totalRent = parseFloat(form.total_rent.value);
  const advanceReceived = parseFloat(form.advance_received.value || 0);

  if (!tripDate) {
    showToast('Please select a valid Trip Date.', 'error');
    return;
  }
  if (!vehicleId || isNaN(vehicleId)) {
    showToast('Please select a valid Vehicle / Truck.', 'error');
    return;
  }
  if (!customerName) {
    showToast('Please enter Customer / Transporter Name.', 'error');
    return;
  }
  if (!fromLocation || !toLocation) {
    showToast('Please specify both From and To locations.', 'error');
    return;
  }
  if (isNaN(totalRent) || totalRent < 0) {
    showToast('Total rent must be a valid positive amount.', 'error');
    return;
  }
  if (isNaN(advanceReceived) || advanceReceived < 0) {
    showToast('Advance received cannot be negative.', 'error');
    return;
  }

  const payload = {
    trip_date: tripDate,
    vehicle_id: vehicleId,
    driver_id: form.driver_id.value ? parseInt(form.driver_id.value) : null,
    customer_name: customerName,
    from_location: fromLocation,
    to_location: toLocation,
    load_description: form.load_description.value.trim() || null,
    total_rent: totalRent,
    advance_received: advanceReceived,
    trip_status: form.trip_status.value,
    notes: form.notes.value.trim() || null
  };

  try {
    const res = await API.post('/trips', payload);
    showToast(res.message || 'Trip registered successfully!', 'success');
    closeModal('modalAddTrip');
    form.reset();
    const todayStr = new Date().toISOString().slice(0, 10);
    const dateInput = document.getElementById('addTripDate');
    if (dateInput) dateInput.value = todayStr;
    calculateAddTripBalance();

    await window.loadTripsView();
    if (window.loadKPISummary) window.loadKPISummary();
    if (window.loadRecentTrips) window.loadRecentTrips();
  } catch (err) {
    showToast(err.message || 'Error creating trip', 'error');
  }
};

// Open Edit Trip Modal and populate saved values
window.openEditTripModal = async function(tripId) {
  try {
    await window.ensureDropdownsLoaded();
    const trip = await API.get(`/trips/${tripId}`);
    if (!trip) throw new Error('Trip data could not be retrieved.');

    document.getElementById('editTripId').value = trip.id;
    document.getElementById('editTripDate').value = trip.trip_date;
    document.getElementById('editTripVehicleSelect').value = trip.vehicle_id;
    document.getElementById('editTripDriverSelect').value = trip.driver_id || '';
    document.getElementById('editTripCustomer').value = trip.customer_name;
    document.getElementById('editTripFrom').value = trip.from_location;
    document.getElementById('editTripTo').value = trip.to_location;
    document.getElementById('editTripLoad').value = trip.load_description || '';
    document.getElementById('editTripRent').value = trip.total_rent;
    document.getElementById('editTripAdvance').value = trip.advance_received;

    const addlElem = document.getElementById('editTripAdditionalPayments');
    if (addlElem) {
      addlElem.value = `₹ ${(trip.additional_payments || 0).toLocaleString('en-IN')}`;
      addlElem.dataset.amount = trip.additional_payments || 0;
    }

    const balElem = document.getElementById('editTripBalance');
    if (balElem) {
      balElem.value = `₹ ${(trip.balance_receivable || 0).toLocaleString('en-IN')}`;
    }

    document.getElementById('editTripStatus').value = trip.trip_status;
    document.getElementById('editTripNotes').value = trip.notes || '';

    openModal('modalEditTrip');
  } catch (err) {
    showToast('Failed to load trip for editing: ' + err.message, 'error');
  }
};

// Handle Update Trip Form Submission
window.handleUpdateTrip = async function(e) {
  e.preventDefault();
  const form = document.getElementById('editTripForm');
  const tripId = document.getElementById('editTripId').value;

  const tripDate = form.trip_date.value;
  const vehicleId = parseInt(form.vehicle_id.value);
  const customerName = form.customer_name.value.trim();
  const fromLocation = form.from_location.value.trim();
  const toLocation = form.to_location.value.trim();
  const totalRent = parseFloat(form.total_rent.value);
  const advanceReceived = parseFloat(form.advance_received.value || 0);

  if (!tripDate) {
    showToast('Please select a valid Trip Date.', 'error');
    return;
  }
  if (!vehicleId || isNaN(vehicleId)) {
    showToast('Please select a valid Vehicle / Truck.', 'error');
    return;
  }
  if (!customerName) {
    showToast('Please enter Customer / Transporter Name.', 'error');
    return;
  }
  if (!fromLocation || !toLocation) {
    showToast('Please specify both From and To locations.', 'error');
    return;
  }
  if (isNaN(totalRent) || totalRent < 0) {
    showToast('Total rent must be a valid positive amount.', 'error');
    return;
  }
  if (isNaN(advanceReceived) || advanceReceived < 0) {
    showToast('Advance received cannot be negative.', 'error');
    return;
  }

  const payload = {
    trip_date: tripDate,
    vehicle_id: vehicleId,
    driver_id: form.driver_id.value ? parseInt(form.driver_id.value) : null,
    customer_name: customerName,
    from_location: fromLocation,
    to_location: toLocation,
    load_description: form.load_description.value.trim() || null,
    total_rent: totalRent,
    advance_received: advanceReceived,
    trip_status: form.trip_status.value,
    notes: form.notes.value.trim() || null
  };

  try {
    const res = await API.put(`/trips/${tripId}`, payload);
    showToast(res.message || 'Trip updated successfully!', 'success');
    closeModal('modalEditTrip');
    await window.loadTripsView();
    if (window.loadKPISummary) window.loadKPISummary();
    if (window.loadRecentTrips) window.loadRecentTrips();
  } catch (err) {
    showToast(err.message || 'Error updating trip', 'error');
  }
};

// Open Delete Confirmation Modal
window.openDeleteTripModal = function(tripId, vehicleNumber, route) {
  window.pendingDeleteTripId = tripId;
  const summary = document.getElementById('deleteTripSummary');
  if (summary) {
    summary.innerHTML = `
      <div style="font-weight: 700; color: #0f172a; margin-bottom: 4px;">Trip #${tripId} — ${vehicleNumber}</div>
      <div style="color: #64748b;">Route: ${route}</div>
    `;
  }
  openModal('modalConfirmDeleteTrip');
};

// Execute Trip Deletion
window.executeDeleteTrip = async function() {
  const tripId = window.pendingDeleteTripId;
  if (!tripId) return;

  try {
    const res = await API.delete(`/trips/${tripId}`);
    closeModal('modalConfirmDeleteTrip');
    showToast(res.message || 'Trip processed successfully.', 'success');
    window.pendingDeleteTripId = null;

    // Immediately remove row from DOM if completely deleted
    const row = document.getElementById(`trip-row-${tripId}`);
    if (row && res.status === 'deleted') {
      row.remove();
    }

    // Refresh trips table and KPI summary
    await window.loadTripsView();
    if (window.loadKPISummary) window.loadKPISummary();
    if (window.loadRecentTrips) window.loadRecentTrips();
  } catch (err) {
    showToast(err.message || 'Failed to delete trip', 'error');
  }
};

// Record Payment Modal Opener
window.openRecordPaymentModal = function(tripId, vehNum, balance) {
  document.getElementById('payTripId').value = tripId;
  document.getElementById('payTripVehicle').textContent = vehNum;
  document.getElementById('payTripBalance').textContent = `₹ ${balance.toLocaleString('en-IN')}`;
  document.getElementById('payAmountInput').value = balance;
  openModal('modalRecordPayment');
};

// Submit Payment Handler
window.handleRecordPayment = async function(e) {
  e.preventDefault();
  const form = document.getElementById('recordPaymentForm');
  const tripId = document.getElementById('payTripId').value;
  const amount = parseFloat(form.amount.value);

  if (isNaN(amount) || amount <= 0) {
    showToast('Please enter a valid payment amount greater than zero.', 'error');
    return;
  }

  const payload = {
    payment_date: form.payment_date.value,
    amount: amount,
    payment_method: form.payment_method.value,
    reference_number: form.reference_number.value.trim() || null,
    notes: form.notes.value.trim() || null
  };

  try {
    const res = await API.post(`/trips/${tripId}/payments`, payload);
    showToast(res.message || 'Payment recorded successfully!', 'success');
    closeModal('modalRecordPayment');
    form.reset();
    await window.loadTripsView();
    if (window.loadKPISummary) window.loadKPISummary();
    if (window.loadRecentTrips) window.loadRecentTrips();
  } catch (err) {
    showToast(err.message || 'Error recording payment', 'error');
  }
};

// View Detailed Trip Information
window.viewTripDetailModal = async function(tripId) {
  try {
    const trip = await API.get(`/trips/${tripId}`);
    const modal = document.getElementById('modalTripDetails');
    const content = document.getElementById('tripDetailsContent');

    content.innerHTML = `
      <div style="margin-bottom: 16px;">
        <h3 style="font-size: 1.2rem; color: #0f172a;">Trip #${trip.id} - ${trip.vehicle_number}</h3>
        <p style="color: #64748b; font-size: 0.85rem;">${trip.from_location} &rarr; ${trip.to_location} | Date: ${trip.formatted_date || trip.trip_date}</p>
      </div>

      <div class="entity-stats-row" style="margin-bottom: 16px;">
        <div>
          <div class="entity-stat-label">Customer</div>
          <div class="entity-stat-val" style="font-size: 0.88rem;">${trip.customer_name}</div>
        </div>
        <div>
          <div class="entity-stat-label">Driver</div>
          <div class="entity-stat-val" style="font-size: 0.88rem;">${trip.driver_name || 'N/A'}</div>
        </div>
        <div>
          <div class="entity-stat-label">Total Rent</div>
          <div class="entity-stat-val" style="color: #16a34a;">₹ ${trip.total_rent.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Advance Received</div>
          <div class="entity-stat-val" style="color: #0284c7;">₹ ${trip.advance_received.toLocaleString('en-IN')}</div>
        </div>
      </div>

      <div class="entity-stats-row" style="margin-bottom: 16px;">
        <div>
          <div class="entity-stat-label">Additional Payments</div>
          <div class="entity-stat-val" style="color: #0284c7;">₹ ${(trip.additional_payments || 0).toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Balance Receivable</div>
          <div class="entity-stat-val" style="color: ${trip.balance_receivable > 0 ? '#b45309' : '#16a34a'};">₹ ${trip.balance_receivable.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <div class="entity-stat-label">Status</div>
          <div class="entity-stat-val" style="font-size: 0.88rem;">${trip.trip_status}</div>
        </div>
        <div>
          <div class="entity-stat-label">Cargo / Load</div>
          <div class="entity-stat-val" style="font-size: 0.85rem;">${trip.load_description || 'General Cargo'}</div>
        </div>
      </div>

      ${trip.notes ? `
        <div style="background: #f8fafc; border-left: 3px solid #0284c7; padding: 8px 12px; margin-bottom: 16px; border-radius: 4px; font-size: 0.85rem; color: #475569;">
          <strong>Notes:</strong> ${trip.notes}
        </div>
      ` : ''}

      <h4 style="font-size: 0.92rem; margin-bottom: 8px;">Payment History</h4>
      <div class="table-responsive">
        <table class="data-table-mini">
          <thead>
            <tr>
              <th>Date</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Ref No.</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>${trip.formatted_date || trip.trip_date}</td>
              <td>₹ ${trip.advance_received.toLocaleString('en-IN')}</td>
              <td>Advance Received</td>
              <td>Initial</td>
            </tr>
            ${trip.payments && trip.payments.length > 0 ? trip.payments.map(p => `
              <tr>
                <td>${p.payment_date}</td>
                <td>₹ ${p.amount.toLocaleString('en-IN')}</td>
                <td>${p.payment_method}</td>
                <td>${p.reference_number || '-'}</td>
              </tr>
            `).join('') : `<tr><td colspan="4" style="text-align: center; color: #94a3b8; padding: 10px;">No additional payments recorded yet.</td></tr>`}
          </tbody>
        </table>
      </div>
    `;

    openModal('modalTripDetails');
  } catch (err) {
    showToast('Failed to load trip details: ' + err.message, 'error');
  }
};

window.exportTripsCSV = async function() {
  const token = API.getToken();
  const searchInput = document.getElementById('tripsSearchInput');
  const statusFilterElem = document.getElementById('tripsStatusFilter');
  const search = searchInput ? searchInput.value.trim() : '';
  const statusFilter = statusFilterElem ? statusFilterElem.value : '';

  try {
    const params = new URLSearchParams();
    if (token) params.append('token', token);
    if (search) params.append('search', search);
    if (statusFilter && statusFilter !== 'All') params.append('status', statusFilter);

    const queryStr = params.toString();
    const url = `/api/trips/export/csv${queryStr ? '?' + queryStr : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    });

    if (!response.ok) {
      throw new Error(`Export server response: ${response.status} ${response.statusText}`);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `Mother_Theresa_Transport_Trips_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(downloadUrl);
    showToast('Trips CSV downloaded successfully!', 'success');
  } catch (err) {
    console.warn('Backend CSV download issue, generating from loaded records...', err);
    try {
      let fetchUrl = `/trips?search=${encodeURIComponent(search)}`;
      if (statusFilter && statusFilter !== 'All') {
        fetchUrl += `&status=${encodeURIComponent(statusFilter)}`;
      }
      const trips = await API.get(fetchUrl);
      if (!trips || trips.length === 0) {
        showToast('No trip records available to export.', 'warning');
        return;
      }
      const headers = [
        "Trip ID", "Date", "Vehicle Number", "Driver", "Customer",
        "From", "To", "Load Description", "Total Rent (INR)",
        "Advance Received (INR)", "Balance Receivable (INR)", "Status"
      ];
      const rows = trips.map(t => [
        t.id,
        t.trip_date || '',
        `"${(t.vehicle_number || '').replace(/"/g, '""')}"`,
        `"${(t.driver_name || '').replace(/"/g, '""')}"`,
        `"${(t.customer_name || '').replace(/"/g, '""')}"`,
        `"${(t.from_location || '').replace(/"/g, '""')}"`,
        `"${(t.to_location || '').replace(/"/g, '""')}"`,
        `"${(t.load_description || '').replace(/"/g, '""')}"`,
        Number(t.total_rent || 0).toFixed(2),
        Number(t.advance_received || 0).toFixed(2),
        Number(t.balance_receivable || 0).toFixed(2),
        `"${(t.trip_status || '').replace(/"/g, '""')}"`
      ]);
      const csvContent = "\uFEFF" + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `Mother_Theresa_Transport_Trips_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
      showToast('Trips CSV exported successfully!', 'success');
    } catch (fallbackErr) {
      showToast('Export failed: ' + fallbackErr.message, 'error');
    }
  }
};

// Also pre-load dropdowns whenever Trips view or Add Trip modal is opened
document.addEventListener('DOMContentLoaded', () => {
  const addTripBtn = document.querySelector('[onclick*="modalAddTrip"]');
  if (addTripBtn) {
    addTripBtn.addEventListener('click', () => {
      window.ensureDropdownsLoaded();
    });
  }
});
