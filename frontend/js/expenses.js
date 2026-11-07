// Expenses Controller
window.loadExpensesView = async function() {
  const tbody = document.getElementById('expensesTableBody');
  const catFilter = document.getElementById('expenseCategoryFilter') ? document.getElementById('expenseCategoryFilter').value : '';
  const search = document.getElementById('expenseSearchInput') ? document.getElementById('expenseSearchInput').value : '';

  try {
    let url = `/expenses?search=${encodeURIComponent(search)}`;
    if (catFilter && catFilter !== 'All') {
      url += `&category=${encodeURIComponent(catFilter)}`;
    }

    const expenses = await API.get(url);
    if (!tbody) return;

    if (!expenses || expenses.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 24px; color: #64748b;">No expenses found. Click "Add Expense" to log costs.</td></tr>';
      return;
    }

    let totalSum = 0;
    tbody.innerHTML = expenses.map(e => {
      totalSum += e.amount;
      return `
        <tr>
          <td>${e.date}</td>
          <td style="font-weight: 700; color: #0f172a;">${e.vehicle_number}</td>
          <td>
            <span class="badge-status info">${e.category}</span>
          </td>
          <td style="font-weight: 700; color: #dc2626;">₹ ${e.amount.toLocaleString('en-IN')}</td>
          <td>${e.paid_to}</td>
          <td>${e.payment_method}</td>
          <td>${e.description}</td>
        </tr>
      `;
    }).join('');

    const sumElem = document.getElementById('totalExpensesSumText');
    if (sumElem) {
      sumElem.textContent = `₹ ${totalSum.toLocaleString('en-IN')}`;
    }
  } catch (err) {
    console.error('Failed to load expenses:', err);
    showToast('Failed to load expenses: ' + err.message, 'error');
  }
};

async function handleCreateExpense(e) {
  e.preventDefault();
  const form = document.getElementById('addExpenseForm');
  const payload = {
    date: form.date.value,
    vehicle_id: form.vehicle_id.value ? parseInt(form.vehicle_id.value) : null,
    category: form.category.value,
    amount: parseFloat(form.amount.value),
    paid_to: form.paid_to.value.trim(),
    payment_method: form.payment_method.value,
    description: form.description.value.trim()
  };

  try {
    await API.post('/expenses', payload);
    showToast('Expense recorded successfully!', 'success');
    closeModal('modalAddExpense');
    form.reset();
    window.loadExpensesView();
    if (window.loadKPISummary) window.loadKPISummary();
    if (window.loadChartsData) window.loadChartsData();
  } catch (err) {
    showToast(err.message || 'Error recording expense', 'error');
  }
}

window.exportExpensesCSV = function() {
  const token = API.getToken();
  window.location.href = `/api/expenses/export/csv?token=${token}`;
};
