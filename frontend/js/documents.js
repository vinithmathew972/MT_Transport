// Documents & Reminders Controller
window.loadDocumentsView = async function() {
  const tbody = document.getElementById('documentsTableBody');
  const typeFilter = document.getElementById('docTypeFilter') ? document.getElementById('docTypeFilter').value : '';
  const statusFilter = document.getElementById('docStatusFilter') ? document.getElementById('docStatusFilter').value : '';

  try {
    let url = `/documents?document_type=${encodeURIComponent(typeFilter)}`;
    if (statusFilter && statusFilter !== 'All') {
      url += `&status_filter=${encodeURIComponent(statusFilter)}`;
    }

    const docs = await API.get(url);
    if (!tbody) return;

    if (!docs || docs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 24px; color: #64748b;">No documents found. Click "Add Document" to register a certificate.</td></tr>';
      return;
    }

    tbody.innerHTML = docs.map(d => `
      <tr>
        <td style="font-weight: 700; color: #0f172a;">${d.vehicle_number}</td>
        <td>
          <span class="badge-status info">${d.document_type}</span>
        </td>
        <td>${d.document_number || '-'}</td>
        <td>${d.issue_date || '-'}</td>
        <td style="font-weight: 600;">${d.expiry_date}</td>
        <td>
          <span class="badge-status ${d.status_class}">
            ${d.status_label}
          </span>
        </td>
        <td>
          <button class="btn-secondary" style="padding: 3px 8px; font-size: 0.72rem; color: #dc2626;" onclick="deleteDocumentRecord(${d.id})">
            Delete
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading documents:', err);
    showToast('Failed to load documents: ' + err.message, 'error');
  }
};

async function handleAddDocument(e) {
  e.preventDefault();
  const form = document.getElementById('addDocumentForm');
  const payload = {
    vehicle_id: parseInt(form.vehicle_id.value),
    document_type: form.document_type.value,
    document_number: form.document_number.value.trim(),
    issue_date: form.issue_date.value || null,
    expiry_date: form.expiry_date.value,
    notes: form.notes.value.trim()
  };

  try {
    await API.post('/documents', payload);
    showToast('Document certificate logged!', 'success');
    closeModal('modalAddDocument');
    form.reset();
    window.loadDocumentsView();
    if (window.loadUpcomingExpiries) window.loadUpcomingExpiries();
    if (window.loadKPISummary) window.loadKPISummary();
  } catch (err) {
    showToast(err.message || 'Error adding document', 'error');
  }
}

window.deleteDocumentRecord = async function(docId) {
  if (!confirm('Are you sure you want to remove this document record?')) return;
  try {
    await API.delete(`/documents/${docId}`);
    showToast('Document removed', 'success');
    window.loadDocumentsView();
    if (window.loadUpcomingExpiries) window.loadUpcomingExpiries();
    if (window.loadKPISummary) window.loadKPISummary();
  } catch (err) {
    showToast(err.message, 'error');
  }
};
