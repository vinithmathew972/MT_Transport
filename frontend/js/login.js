document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const usernameInput = document.getElementById('usernameInput');
  const passwordInput = document.getElementById('passwordInput');
  const togglePasswordBtn = document.getElementById('togglePasswordBtn');
  const eyeIcon = document.getElementById('eyeIcon');
  const submitBtn = document.getElementById('submitBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const alertBox = document.getElementById('alertBox');

  // Toggle password visibility
  togglePasswordBtn.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    eyeIcon.innerHTML = isPassword 
      ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>'
      : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
  });

  function showAlert(msg, type = 'error') {
    alertBox.textContent = msg;
    alertBox.className = `alert-box ${type}`;
  }

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnSpinner.style.display = isLoading ? 'inline-block' : 'none';
    btnText.textContent = isLoading ? 'Authenticating...' : 'Secure Owner Login';
  }

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
      showAlert('Please enter both username and password.');
      return;
    }

    setLoading(true);
    alertBox.className = 'alert-box';
    alertBox.style.display = 'none';

    try {
      const res = await API.post('/auth/login', { username, password });
      API.setToken(res.access_token, res.owner_name, res.username);
      showAlert('Login successful! Redirecting to dashboard...', 'success');
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 500);
    } catch (err) {
      showAlert(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  });
});
