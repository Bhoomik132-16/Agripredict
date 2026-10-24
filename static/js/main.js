// --- Global State & Auth ---
function updateNav() {
    const userStr = localStorage.getItem('agripredict_user');
    const authBtn = document.getElementById('nav-auth');
    const logoutBtn = document.getElementById('nav-logout');
    const dashLink = document.getElementById('nav-dashboard');
    const marketLink = document.getElementById('nav-marketplace');
    const adminLink = document.getElementById('nav-admin');

    if(userStr) {
        const user = JSON.parse(userStr);
        if(authBtn) authBtn.style.display = 'none';
        if(logoutBtn) logoutBtn.style.display = 'inline-block';
        
        if(user.role === 'Admin') {
            if(adminLink) adminLink.style.display = 'inline';
            if(dashLink) dashLink.style.display = 'none';
            if(marketLink) marketLink.style.display = 'none';
        } else {
            if(adminLink) adminLink.style.display = 'none';
            if(dashLink) dashLink.style.display = 'inline'; // Now visible for all non-admins
            if(marketLink) marketLink.style.display = 'inline';
        }
    } else {
        if(authBtn) authBtn.style.display = 'inline-block';
        if(logoutBtn) logoutBtn.style.display = 'none';
        if(dashLink) dashLink.style.display = 'none';
        if(marketLink) marketLink.style.display = 'none';
        if(adminLink) adminLink.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('agripredict_user');
    window.location.href = '/';
}

function getUser() {
    const userStr = localStorage.getItem('agripredict_user');
    return userStr ? JSON.parse(userStr) : null;
}

function showError(msgId, message) {
    const el = document.getElementById(msgId);
    if(el) {
        el.innerText = message;
        el.style.display = 'block';
        setTimeout(() => el.style.display='none', 5000);
    } else {
        alert(message);
    }
}

// --- Auth Endpoints ---

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await res.json();
        
        if(res.ok) {
            localStorage.setItem('agripredict_user', JSON.stringify(data.user));
            if(data.user.role === 'Admin') window.location.href = '/admin';
            else window.location.href = '/dashboard'; // Farmer and Vendor go to dashboard
        } else {
            showError('auth-error', data.error);
        }
    } catch(err) {
        showError('auth-error', 'Connection error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    const phone = document.getElementById('reg-phone').value;
    const location = document.getElementById('reg-location').value;
    const requirements = document.getElementById('reg-requirements').value;

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, password, role, phone, location, requirements})
        });
        const data = await res.json();
        
        if(res.ok) {
            localStorage.setItem('agripredict_user', JSON.stringify(data.user));
            window.location.href = (role === 'Farmer') ? '/dashboard' : '/marketplace';
        } else {
            showError('auth-error', data.error);
        }
    } catch(err) {
        showError('auth-error', 'Connection error');
    }
}
