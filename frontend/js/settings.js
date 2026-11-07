// Settings & Owner Profile Controller

window.updateDisplayedOwnerName = function(name) {
  if (!name) return;
  localStorage.setItem('mtt_owner_name', name);
  const userElem = document.getElementById('ownerDisplayUsername');
  if (userElem) userElem.textContent = name;
  const greetElem = document.getElementById('welcomeHeroTitle');
  if (greetElem) greetElem.textContent = `Good Morning, ${name}!`;
};

window.loadOwnerProfile = async function() {
  try {
    const profile = await API.get('/auth/me');
    if (!profile) return null;

    // Populate modal inputs
    const modalName = document.getElementById('modalOwnerName');
    const modalPhone = document.getElementById('modalOwnerPhone');
    const modalEmail = document.getElementById('modalOwnerEmail');
    const modalCompany = document.getElementById('modalOwnerCompany');

    if (modalName) modalName.value = profile.full_name || '';
    if (modalPhone) modalPhone.value = profile.phone || '';
    if (modalEmail) modalEmail.value = profile.email || '';
    if (modalCompany) modalCompany.value = profile.company_name || '';

    // Populate settings view inputs
    const settiName = document.getElementById('settingsOwnerName');
    const settiPhone = document.getElementById('settingsOwnerPhone');
    const settiEmail = document.getElementById('settingsOwnerEmail');
    const settiCompany = document.getElementById('settingsOwnerCompany');

    if (settiName) settiName.value = profile.full_name || '';
    if (settiPhone) settiPhone.value = profile.phone || '';
    if (settiEmail) settiEmail.value = profile.email || '';
    if (settiCompany) settiCompany.value = profile.company_name || '';

    if (profile.full_name) {
      window.updateDisplayedOwnerName(profile.full_name);
    }
    return profile;
  } catch (err) {
    console.error('Failed to load owner profile:', err);
    return null;
  }
};

window.openOwnerProfileModal = async function() {
  const dropdown = document.getElementById('profileDropdown');
  if (dropdown) dropdown.classList.remove('show');

  await window.loadOwnerProfile();
  if (window.openModal) {
    window.openModal('modalOwnerProfile');
  }
};

window.handleSaveOwnerProfile = async function(e) {
  e.preventDefault();
  const form = e.target;
  const fullName = form.full_name ? form.full_name.value.trim() : '';
  const phone = form.phone ? form.phone.value.trim() : '';
  const email = form.email ? form.email.value.trim() : '';
  const companyName = form.company_name ? form.company_name.value.trim() : '';

  if (!fullName) {
    showToast('Owner Name is required', 'warning');
    return;
  }

  const payload = {
    full_name: fullName,
    phone: phone,
    email: email,
    company_name: companyName
  };

  try {
    const updated = await API.put('/auth/profile', payload);
    const newName = (updated && updated.full_name) || fullName;
    window.updateDisplayedOwnerName(newName);

    // Keep all profile inputs synced across modal and settings view
    const ids = [
      ['modalOwnerName', 'settingsOwnerName', newName],
      ['modalOwnerPhone', 'settingsOwnerPhone', (updated && updated.phone) || phone],
      ['modalOwnerEmail', 'settingsOwnerEmail', (updated && updated.email) || email],
      ['modalOwnerCompany', 'settingsOwnerCompany', (updated && updated.company_name) || companyName]
    ];
    ids.forEach(([mId, sId, val]) => {
      const mElem = document.getElementById(mId);
      const sElem = document.getElementById(sId);
      if (mElem) mElem.value = val || '';
      if (sElem) sElem.value = val || '';
    });

    // Also update company name in companySettingsForm if present
    const compForm = document.getElementById('companySettingsForm');
    if (compForm && compForm.company_name && companyName) {
      compForm.company_name.value = companyName;
    }

    if (window.closeModal) {
      window.closeModal('modalOwnerProfile');
    }

    showToast('Owner Profile updated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Error updating owner profile', 'error');
  }
};

window.loadSettingsView = async function() {
  const form = document.getElementById('companySettingsForm');

  // Load owner profile on settings view as well
  await window.loadOwnerProfile();

  if (!form) return;

  try {
    const s = await API.get('/settings');
    form.company_name.value = s.company_name || '';
    form.tagline.value = s.tagline || '';
    form.phone.value = s.phone || '';
    form.email.value = s.email || '';
    form.address.value = s.address || '';
    form.currency.value = s.currency || '₹';
    form.date_format.value = s.date_format || 'DD/MM/YYYY';
  } catch (err) {
    console.error('Failed to load settings:', err);
  }
};

async function handleSaveSettings(e) {
  e.preventDefault();
  const form = document.getElementById('companySettingsForm');
  const payload = {
    company_name: form.company_name.value.trim(),
    tagline: form.tagline.value.trim(),
    phone: form.phone.value.trim(),
    email: form.email.value.trim(),
    address: form.address.value.trim(),
    currency: form.currency.value,
    date_format: form.date_format.value,
    reminder_days_json: "[30, 15, 7]",
    salary_rules_json: "{}"
  };

  try {
    await API.put('/settings', payload);
    // Sync company name to owner profile inputs
    const mComp = document.getElementById('modalOwnerCompany');
    const sComp = document.getElementById('settingsOwnerCompany');
    if (mComp) mComp.value = payload.company_name;
    if (sComp) sComp.value = payload.company_name;

    showToast('Company settings updated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Error updating settings', 'error');
  }
}

window.downloadDataBackup = async function() {
  try {
    const backup = await API.get('/settings/backup');
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(backup, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Mother_Theresa_Transport_Backup_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    showToast('Backup downloaded successfully!', 'success');
  } catch (err) {
    showToast('Backup failed: ' + err.message, 'error');
  }
};
