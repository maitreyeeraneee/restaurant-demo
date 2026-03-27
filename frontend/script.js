const API_BASE = 'http://127.0.0.1:8000';
const TOKEN_KEY = 'matamaal_token';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function getHeaders() {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}

function decodeToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch (e) {
    return null;
  }
}

function showError(msg, element = document.getElementById('errorMsg') || document.getElementById('loginError')) {
  if (element) {
    element.textContent = msg;
    element.style.display = 'block';
  }
}

function hideError(element = document.getElementById('errorMsg') || document.getElementById('loginError')) {
  if (element) element.style.display = 'none';
}

// Login
document.addEventListener('DOMContentLoaded', () => {
  const token = getToken();
  if (token && window.location.pathname.includes('dashboard.html')) {
    checkAuth();
  }
});

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  console.log("login clicked");
  localStorage.setItem("matamaal_token", "test123");
  window.location.href = "dashboard.html";
});

// Logout
document.getElementById('logoutBtn')?.addEventListener('click', () => {
  removeToken();
  window.location.href = 'index.html';
});

// Check Auth
async function checkAuth() {
  console.log('checkAuth called');
  const token = getToken();
  if (!token) {
    console.log('No token, redirect to login');
    window.location.href = 'index.html';
    return;
  }
  
  const user = decodeToken(token);
  if (!user) {
    console.log('Invalid token, redirect to login');
    removeToken();
    window.location.href = 'index.html';
    return;
  }
  
  console.log('User authenticated:', user.sub);
  document.getElementById('userInfo').textContent = `Welcome, ${user.sub}`;
  
  const cookDash = document.getElementById('cookDashboard');
  const adminDash = document.getElementById('adminDashboard');
  
  if (user.role === 'admin') {
    adminDash.style.display = 'block';
    loadCategories();
    loadEntries();
  } else {
    cookDash.style.display = 'block';
  }
}

// Load Menu (Cook)
document.getElementById('loadMenu')?.addEventListener('click', async () => {
  const categoryId = parseInt(document.getElementById('categoryId').value);
  if (!categoryId) return showError('Enter category ID');
  
  try {
    const response = await fetch(`${API_BASE}/production-entries/menu-items/?category_id=${categoryId}`, {
      headers: getHeaders()
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Failed to load menu');
    }
    
    const items = await response.json();
    renderMenuTable(items);
    document.getElementById('submitAll').style.display = 'inline-block';
  } catch (err) {
    showError(err.message);
  }
});

function renderMenuTable(items) {
  const tbody = document.querySelector('#menuTable tbody');
  tbody.innerHTML = '';
  
  items.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.name}</td>
      <td>${item.type}</td>
      <td><input type="number" min="0" step="0.1" data-id="${item.id}" class="qty-input"></td>
      <td>
        <select data-id="${item.id}" class="unit-select">
          <option value="portion">Portion</option>
          <option value="kg">Kg</option>
          <option value="pieces">Pieces</option>
        </select>
      </td>
      <td><button class="submit-btn" onclick="submitSingle(${item.id})">Add</button></td>
    `;
    tbody.appendChild(row);
  });
}

// Submit single
window.submitSingle = async (menuItemId) => {
  const qtyInput = document.querySelector(`.qty-input[data-id="${menuItemId}"]`);
  const unitSelect = document.querySelector(`.unit-select[data-id="${menuItemId}"]`);
  
  const qty = parseFloat(qtyInput.value);
  const unit = unitSelect.value;
  
  if (!qty || qty <= 0) {
    showError('Enter valid quantity');
    return;
  }
  
  const categoryId = parseInt(document.getElementById('categoryId').value);
  
  try {
    const response = await fetch(`${API_BASE}/production-entries/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ menu_item_id: menuItemId, quantity: qty, unit, category_id: categoryId })
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Submit failed');
    }
    
    const result = await response.json();
    showError(`Added: ${result.menu_item_name} ${result.quantity} ${result.unit}`, document.getElementById('errorMsg'));
    qtyInput.value = '';
  } catch (err) {
    showError(err.message);
  }
};

// Submit all
document.getElementById('submitAll')?.addEventListener('click', async () => {
  const qtyInputs = document.querySelectorAll('.qty-input');
  const categoryId = parseInt(document.getElementById('categoryId').value);
  
  const entries = [];
  qtyInputs.forEach(input => {
    const qty = parseFloat(input.value);
    if (qty > 0) {
      const menuItemId = parseInt(input.dataset.id);
      const unitSelect = document.querySelector(`.unit-select[data-id="${menuItemId}"]`);
      entries.push({
        menu_item_id: menuItemId,
        quantity: qty,
        unit: unitSelect.value,
        category_id: categoryId
      });
      input.value = '';
    }
  });
  
  if (entries.length === 0) {
    showError('No items to submit');
    return;
  }
  
  try {
    const promises = entries.map(entry => 
      fetch(`${API_BASE}/production-entries/`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(entry)
      })
    );
    
    const responses = await Promise.all(promises);
    const errors = responses.filter(r => !r.ok);
    
    if (errors.length > 0) {
      throw new Error(`${errors.length} submissions failed`);
    }
    
    showError(`Submitted ${entries.length} items successfully!`);
  } catch (err) {
    showError(err.message);
  }
});

// Admin functions
async function loadCategories() {
  try {
    const response = await fetch(`${API_BASE}/admin/categories`, {
      headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to load');
    const categories = await response.json();
    
    const select = document.getElementById('categoryFilter');
    categories.forEach(cat => {
      const option = document.createElement('option');
      option.value = cat.id;
      option.textContent = cat.name;
      select.appendChild(option);
    });
  } catch (err) {
    console.error('Failed to load categories');
  }
}

async function loadEntries(filters = {}) {
  let url = `${API_BASE}/production-entries/?`;
  Object.entries(filters).forEach(([key, value]) => {
    if (value) url += `${key}=${value}&amp;`;
  });
  
  try {
    const response = await fetch(url, {
      headers: getHeaders()
    });
    const entries = await response.json();
    renderEntriesTable(entries);
  } catch (err) {
    showError('Failed to load entries');
  }
}

function renderEntriesTable(entries) {
  const tbody = document.querySelector('#entriesTable tbody');
  tbody.innerHTML = '';
  
  entries.forEach(entry => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${entry.id}</td>
      <td>${entry.menu_item_name}</td>
      <td>${entry.category_name}</td>
      <td>${entry.quantity}</td>
      <td>${entry.unit}</td>
      <td>${entry.timestamp}</td>
      <td>
        <button class="delete-btn" onclick="deleteEntry(${entry.id})">Delete</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

document.getElementById('filterBtn')?.addEventListener('click', () => {
  const filters = {
    category_id: document.getElementById('categoryFilter').value,
    // date filter logic here
  };
  loadEntries(filters);
});

document.getElementById('clearFilter')?.addEventListener('click', () => {
  document.getElementById('categoryFilter').value = '';
  document.getElementById('dateFilter').value = '';
  loadEntries();
});

window.deleteEntry = async (id) => {
  if (!confirm('Delete entry?')) return;
  
  try {
    const response = await fetch(`${API_BASE}/production-entries/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    
    if (response.ok) {
      loadEntries();
    } else {
      showError('Delete failed');
    }
  } catch (err) {
    showError('Delete failed');
  }
};

// Init admin
if (document.getElementById('adminDashboard')) {
  checkAuth();
}
