const API_URL = "http://127.0.0.1:5000/api";
let currentUserEmail = null;
let currentUserData = null;

// Utility: Show Toast
function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.borderColor = isError ? "#ff4d4d" : "#4CAF50";
    toast.style.color = isError ? "#ff4d4d" : "#4CAF50";
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 3000);
}

// Utility: Toggle Password Visibility
function togglePassword(id) {
    const input = document.getElementById(id);
    input.type = input.type === "password" ? "text" : "password";
}

// Navigation
function showPage(pageId) {
    // Logic to switch dashboard views
    document.querySelectorAll('.page-view').forEach(el => el.classList.add('hidden'));
    document.getElementById(`page-${pageId}`).classList.remove('hidden');

    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    // Find the button (this is a bit hacky selector wise but works)
    const btns = document.querySelectorAll('.nav-btn');
    btns.forEach(btn => {
        if (btn.innerText.toLowerCase().includes(pageId)) btn.classList.add('active');
    });

    document.getElementById("page-title").innerText = pageId.charAt(0).toUpperCase() + pageId.slice(1);

    // Refresh data if needed
    if (pageId === 'dashboard' || pageId === 'history' || pageId === 'profile') {
        fetchUserData();
    }
    if (pageId === 'admin') {
        fetchAdminData();
    }
}

// Authentication
let isOtpStep = false;
let pendingUserData = null;
let pendingOtp = null;

async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById("login-btn");

    // Step 2: Verify OTP
    if (isOtpStep) {
        const userOtp = document.getElementById("login-otp").value;
        if (userOtp === String(pendingOtp)) {
            // Login Success
            currentUserEmail = pendingUserData.email;
            currentUserData = pendingUserData;

            // Setup UI
            document.getElementById("auth-section").classList.add("hidden");

            // ROUTING: Admin vs User
            if (currentUserData.email === "admin@login.com") {
                document.getElementById("admin-portal").classList.remove("hidden");
                fetchAdminData();
            } else {
                document.getElementById("dashboard-section").classList.remove("hidden");
                document.getElementById("user-name-display").innerText = `Welcome, ${currentUserData.name}`;
                showPage('dashboard');
            }

            showToast("Login Successful");

            // Reset Login Form
            resetLoginForm();
        } else {
            showToast("Incorrect OTP", true);
        }
        return;
    }

    // Step 1: Request OTP
    const email = document.getElementById("login-email").value;
    const pin = document.getElementById("login-pin").value;

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, pin })
        });
        const data = await res.json();

        if (res.ok) {
            // Credentials valid, show OTP
            pendingUserData = data.user;
            pendingOtp = data.otp;

            // Show OTP on screen (Alert/Toast)
            alert(`Your OTP is: ${data.otp}`);
            showToast(`OTP Sent: ${data.otp}`);

            // Switch UI to OTP mode
            document.getElementById("otp-group").classList.remove("hidden");
            document.getElementById("login-email").disabled = true;
            document.getElementById("login-pin").disabled = true;

            btn.innerText = "Verify & Login";
            isOtpStep = true;

        } else {
            showToast(data.error, true);
        }
    } catch (err) {
        showToast("Server connection failed", true);
        console.error(err);
    }
}

function resetLoginForm() {
    isOtpStep = false;
    pendingUserData = null;
    pendingOtp = null;
    document.getElementById("login-form").reset();
    document.getElementById("otp-group").classList.add("hidden");
    document.getElementById("login-email").disabled = false;
    document.getElementById("login-pin").disabled = false;
    document.getElementById("login-btn").innerText = "Send OTP";
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById("reg-name").value;
    const age = document.getElementById("reg-age").value;
    const email = document.getElementById("reg-email").value;
    const pin = document.getElementById("reg-pin").value;

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, age, email, pin })
        });
        const data = await res.json();

        if (res.ok) {
            showToast("Account Created! Use your email/pin to login.");
            // Clear form
            document.getElementById("register-form").reset();
        } else {
            showToast(data.error, true);
        }
    } catch (err) {
        showToast("Registration failed", true);
    }
}

function logout() {
    if (!confirm("Are you sure you want to log out?")) return;

    currentUserEmail = null;
    currentUserData = null;
    document.getElementById("dashboard-section").classList.add("hidden");
    document.getElementById("admin-portal").classList.add("hidden"); // Hide admin portal too
    document.getElementById("auth-section").classList.remove("hidden");
    document.getElementById("login-form").reset();
    document.getElementById("login-btn").innerText = "Send OTP";
    showToast("Logged out");
}

// Data Fetching
async function fetchUserData() {
    if (!currentUserEmail) return;
    // Don't fetch for admin generic profile
    if (currentUserEmail === "admin@bank.com") {
        document.getElementById("dash-balance").innerText = "Admin";
        return;
    }

    try {
        const res = await fetch(`${API_URL}/user/${currentUserEmail}`);
        const data = await res.json();

        if (data.user) {
            currentUserData = data.user;
            updateDashboardUI(data.user);
        }
    } catch (err) {
        console.error("Failed to fetch user data", err);
    }
}

function updateDashboardUI(user) {
    // Stats
    document.getElementById("dash-balance").innerText = `₹${user.balance}`;

    let deposits = 0;
    let withdrawals = 0;

    // Process transactions
    const txList = user.transactions || [];
    txList.forEach(t => {
        if (t.type === 'deposit') deposits += t.amount;
        if (t.type === 'withdraw') withdrawals += t.amount;
    });

    document.getElementById("dash-deposits").innerText = `₹${deposits}`;
    document.getElementById("dash-withdrawals").innerText = `₹${withdrawals}`;

    // Activity List
    // Sort transactions
    const sortedTx = [...txList].reverse().slice(0, 5); // Last 5
    const activityDiv = document.getElementById("activity-list");

    if (sortedTx.length === 0) {
        activityDiv.innerHTML = "No transactions yet.";
    } else {
        activityDiv.innerHTML = sortedTx.map(t => `
            <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2A2F38;">
                <span>${t.type.toUpperCase()}</span>
                <span style="color: ${t.type === 'deposit' ? '#4CAF50' : '#ff4d4d'}">
                    ${t.type === 'deposit' ? '+' : '-'}₹${t.amount}
                </span>
            </div>
        `).join('');
    }

    // History Table
    const historyBody = document.querySelector("#history-table tbody");
    historyBody.innerHTML = txList.slice().reverse().map(t => `
        <tr>
            <td>${t.time}</td>
            <td style="text-transform: capitalize;">${t.type}</td>
            <td>₹${t.amount}</td>
            <td>₹${t.balance_after}</td>
        </tr>
    `).join('');

    // Profile
    document.getElementById("prof-name").innerText = user.name;
    document.getElementById("prof-email").innerText = user.email;
    document.getElementById("prof-acc").innerText = user.account_no;
    document.getElementById("prof-bal").innerText = `₹${user.balance}`;
}

async function performDeposit() {
    const amount = document.getElementById("deposit-amount").value;
    if (!amount) return;

    try {
        const res = await fetch(`${API_URL}/deposit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: currentUserEmail, amount: Number(amount) })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(`Deposit Successful! New Balance: ₹${data.balance}`);
            document.getElementById("deposit-amount").value = "";
            fetchUserData();
        } else {
            showToast(data.error, true);
        }
    } catch (e) {
        showToast("Error performing deposit", true);
    }
}

async function performWithdraw() {
    const amount = document.getElementById("withdraw-amount").value;
    const pin = document.getElementById("withdraw-pin").value;

    if (!amount || !pin) {
        showToast("Amount and PIN required", true);
        return;
    }

    try {
        const res = await fetch(`${API_URL}/withdraw`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: currentUserEmail, amount: Number(amount), pin })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(`Withdraw Successful! New Balance: ₹${data.balance}`);
            document.getElementById("withdraw-amount").value = "";
            document.getElementById("withdraw-pin").value = "";
            fetchUserData();
        } else {
            showToast(data.error, true);
        }
    } catch (e) {
        showToast("Error performing withdraw", true);
    }
}

// ---- Admin Functions ----
let userChartInstance = null;
let financeChartInstance = null;

async function fetchAdminData() {
    try {
        // 1. Fetch Users
        const resUsers = await fetch(`${API_URL}/admin/users`);
        const users = await resUsers.json();

        const tbody = document.querySelector("#admin-users-table tbody");
        tbody.innerHTML = users.map(u => {
            const status = u.status || "Active";
            const statusColor = status === "Active" ? "#4CAF50" : (status === "Suspended" ? "#ff9800" : "#ff4d4d");

            return `
             <tr style="border-bottom: 1px solid #2A2F38;">
                <td style="padding: 15px;">${u.name}</td>
                <td style="padding: 15px;">
                    <div>${u.email}</div>
                    <small style="color:#adaeb3">${u.account_no}</small>
                </td>
                <td style="padding: 15px;">
                    <span style="color: ${statusColor}; font-weight: bold;">${status}</span>
                </td>
                <td style="padding: 15px;">
                    ${status !== 'Active' ?
                    `<button onclick="changeUserStatus('${u.email}', 'Active')" 
                            style="padding: 5px 10px; border-radius: 4px; border:none; background:#4CAF50; color:white; cursor:pointer;">Activate</button>`
                    : ''}
                    ${status !== 'Suspended' ?
                    `<button onclick="changeUserStatus('${u.email}', 'Suspended')" 
                            style="padding: 5px 10px; border-radius: 4px; border:none; background:#ff9800; color:white; cursor:pointer;">Suspend</button>`
                    : ''}
                    ${status !== 'Blocked' ?
                    `<button onclick="changeUserStatus('${u.email}', 'Blocked')" 
                            style="padding: 5px 10px; border-radius: 4px; border:none; background:#ff4d4d; color:white; cursor:pointer;">Block</button>`
                    : ''}
                </td>
            </tr>
        `}).join('');

        // 2. Fetch Stats & Render Charts
        const resStats = await fetch(`${API_URL}/admin/stats`);
        const stats = await resStats.json();
        renderAdminCharts(stats);

    } catch (e) {
        console.error(e);
    }
}

function renderAdminCharts(stats) {
    // Destroy existing charts if any to allow update
    if (userChartInstance) userChartInstance.destroy();
    if (financeChartInstance) financeChartInstance.destroy();

    // 1. User Status Chart (Pie)
    const ctxUser = document.getElementById('userChart').getContext('2d');
    userChartInstance = new Chart(ctxUser, {
        type: 'doughnut',
        data: {
            labels: ['Active', 'Suspended', 'Blocked'],
            datasets: [{
                data: [stats.user_status.Active, stats.user_status.Suspended, stats.user_status.Blocked],
                backgroundColor: ['#4CAF50', '#FF9800', '#F44336'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#fff' } }
            }
        }
    });

    // 2. Financial Chart (Bar)
    const ctxFin = document.getElementById('financeChart').getContext('2d');
    financeChartInstance = new Chart(ctxFin, {
        type: 'bar',
        data: {
            labels: ['Total Deposits', 'Total Withdrawals'],
            datasets: [{
                label: 'Amount (₹)',
                data: [stats.financials.deposits, stats.financials.withdrawals],
                backgroundColor: ['#4CAF50', '#F44336'],
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Transaction Volume', color: '#fff' }
            },
            scales: {
                y: { grid: { color: '#2A2F38' }, ticks: { color: '#adaeb3' } },
                x: { grid: { display: false }, ticks: { color: '#adaeb3' } }
            }
        }
    });
}

async function changeUserStatus(email, status) {
    if (!confirm(`Are you sure you want to set ${email} to ${status}?`)) return;

    try {
        const res = await fetch(`${API_URL}/admin/user-status`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, status })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(data.message);
            fetchAdminData();
        } else {
            showToast(data.error, true);
        }
    } catch (e) {
        showToast("Error update status", true);
    }
}

function downloadReceipt() {
    // Generate simple text receipt for now as a blob
    if (!currentUserData) return;

    let content = `BANK STATEMENT\n`;
    content += `Generated on: ${new Date().toLocaleString()}\n`;
    content += `--------------------------------\n`;
    content += `Name: ${currentUserData.name}\n`;
    content += `Account: ${currentUserData.account_no}\n`;
    content += `Balance: Rs. ${currentUserData.balance}\n\n`;
    content += `TRANSACTIONS:\n`;
    content += `--------------------------------\n`;

    (currentUserData.transactions || []).forEach(t => {
        content += `${t.time} | ${t.type.toUpperCase()} | Rs. ${t.amount} | Bal: ${t.balance_after}\n`;
    });

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Statement_${currentUserData.account_no}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Event Listeners
document.getElementById("login-form").addEventListener("submit", handleLogin);
document.getElementById("register-form").addEventListener("submit", handleRegister);
