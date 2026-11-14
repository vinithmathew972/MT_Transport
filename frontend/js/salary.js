// Salary & Bata Management Controller
window.loadSalaryView = async function() {
  await loadSalaryRecords();
  await loadBataRecords();
};

async function loadSalaryRecords() {
  const tbody = document.getElementById('salaryRecordsTableBody');
  if (!tbody) return;

  try {
    const records = await API.get('/salary/records');
    if (!records || records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 24px; color: #64748b;">No salary records yet. Click "Generate Salary Statement".</td></tr>';
      return;
    }

    tbody.innerHTML = records.map(r => `
      <tr>
        <td style="font-weight: 700; color: #0f172a;">${r.driver_name}</td>
        <td>${r.salary_period}</td>
        <td>${r.days_worked} days</td>
        <td>₹ ${r.base_salary_earned.toLocaleString('en-IN')}</td>
        <td style="font-weight: 600; color: #16a34a;">₹ ${r.net_payable.toLocaleString('en-IN')}</td>
        <td>₹ ${r.paid_amount.toLocaleString('en-IN')}</td>
        <td style="font-weight: 700; color: ${r.balance_payable > 0 ? '#b45309' : '#16a34a'};">
          ₹ ${r.balance_payable.toLocaleString('en-IN')}
        </td>
        <td>
          <div style="display: flex; gap: 6px;">
            <span class="badge-status ${r.status === 'Paid' ? 'success' : 'warning'}">
              ${r.status}
            </span>
            ${r.balance_payable > 0 ? `
              <button class="btn-secondary" style="padding: 3px 8px; font-size: 0.72rem; color: #0284c7;" onclick="openSalaryPayoutModal(${r.id}, ${r.driver_id}, '${r.driver_name}', ${r.balance_payable})">
                Pay
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading salary records:', err);
  }
}

async function loadBataRecords() {
  const tbody = document.getElementById('bataRecordsTableBody');
  if (!tbody) return;

  try {
    const batas = await API.get('/salary/bata');
    if (!batas || batas.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #64748b;">No Bata records logged.</td></tr>';
      return;
    }

    tbody.innerHTML = batas.map(b => `
      <tr>
        <td>${b.date}</td>
        <td style="font-weight: 600;">${b.driver_name}</td>
        <td style="font-weight: 700; color: #0f172a;">₹ ${b.amount.toLocaleString('en-IN')}</td>
        <td>
          <span class="badge-status ${b.status === 'Paid' ? 'success' : 'warning'}">
            ${b.status}
          </span>
        </td>
        <td>
          ${b.status !== 'Paid' ? `
            <button class="btn-secondary" style="padding: 3px 8px; font-size: 0.72rem; color: #16a34a;" onclick="markBataPaid(${b.id})">
              Mark Paid
            </button>
          ` : '<span style="color: #16a34a; font-size: 0.75rem;">Settled</span>'}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading bata records:', err);
  }
}

async function handleGenerateSalary(e) {
  e.preventDefault();
  const form = document.getElementById('generateSalaryForm');
  const payload = {
    driver_id: parseInt(form.driver_id.value),
    salary_period: form.salary_period.value.trim(),
    days_worked: parseInt(form.days_worked.value || 30),
    base_salary_rate: parseFloat(form.base_salary_rate.value || 0),
    bata_earned: parseFloat(form.bata_earned.value || 0),
    allowance: parseFloat(form.allowance.value || 0),
    advance_deduction: parseFloat(form.advance_deduction.value || 0),
    other_deductions: parseFloat(form.other_deductions.value || 0),
    notes: form.notes.value.trim()
  };

  try {
    await API.post('/salary/calculate', payload);
    showToast('Salary statement generated!', 'success');
    closeModal('modalGenerateSalary');
    form.reset();
    window.loadSalaryView();
    if (window.loadKPISummary) window.loadKPISummary();
  } catch (err) {
    showToast(err.message || 'Error generating salary', 'error');
  }
}

window.openSalaryPayoutModal = function(recId, driverId, driverName, balance) {
  document.getElementById('salaryRecId').value = recId;
  document.getElementById('salaryDriverId').value = driverId;
  document.getElementById('payoutDriverName').textContent = driverName;
  document.getElementById('payoutAmountInput').value = balance;
  openModal('modalSalaryPayout');
};

async function handleSalaryPayout(e) {
  e.preventDefault();
  const form = document.getElementById('salaryPayoutForm');
  const payload = {
    salary_record_id: parseInt(document.getElementById('salaryRecId').value),
    driver_id: parseInt(document.getElementById('salaryDriverId').value),
    payment_date: form.payment_date.value,
    amount: parseFloat(form.amount.value),
    payment_method: form.payment_method.value,
    notes: form.notes.value.trim()
  };

  try {
    await API.post('/salary/payments', payload);
    showToast('Salary payment recorded!', 'success');
    closeModal('modalSalaryPayout');
    form.reset();
    window.loadSalaryView();
    if (window.loadKPISummary) window.loadKPISummary();
  } catch (err) {
    showToast(err.message || 'Error processing payout', 'error');
  }
}

window.markBataPaid = async function(bataId) {
  try {
    await API.put(`/salary/bata/${bataId}/pay`, {});
    showToast('Bata marked as settled!', 'success');
    window.loadSalaryView();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// ------------------- Bata Delete functionality -------------------
window.deleteBataRecord = async function(bataId) {
  if (!confirm('Are you sure you want to permanently delete this Bata record?')) return;
  try {
    await API.delete(`/salary/bata/${bataId}`);
    showToast('Bata record deleted.', 'success');
    window.loadSalaryView(); // refresh both salary and bata tables
  } catch (err) {
    showToast(err.message || 'Failed to delete Bata record', 'error');
  }
};
