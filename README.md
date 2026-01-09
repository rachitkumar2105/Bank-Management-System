# 🏦 SmartBank - Bank Management System

A secure, full-stack digital banking solution built with **Python (Flask)** and **Vanilla JavaScript**. This project demonstrates a comprehensive banking application with user accounts, financial transactions, and a powerful Admin Dashboard with analytics.

---

## ✨ Features

### 👤 User Panel
*   **Secure Authentication**: Login/Register with OTP verification (Simulated).
*   **Dashboard**: Real-time balance updates and transaction summary.
*   **Banking Operations**: 
    *   **Deposit**: Add funds securely.
    *   **Withdraw**: Withdraw funds with PIN verification.
    *   **Transfer**: (Ready for expansion).
*   **Transaction History**: Detailed table of all account activities.
*   **Download Statement**: Export transaction history (Text-based).
*   **Profile**: View account details (formatted with CSS Grid).

### 🛠 Admin Portal
*   **Dedicated Login**: Secure access for administrators.
*   **User Management**: View all users, **Suspend** or **Block** accounts effectively stopping their access.
*   **Analytics Dashboard**: 
    *   **User Stats**: Visual breakdown of Active vs Blocked users (Chart.js).
    *   **Financials**: Overview of Total Deposits vs Withdrawals (Chart.js).

---

## 🏗 Tech Stack

*   **Backend**: Python, Flask, Gunicorn
*   **Frontend**: HTML5, CSS3 (Dark Theme), JavaScript (Fetch API)
*   **Database**: JSON-based flat file (`database.json`) for portability.
*   **Visualization**: Chart.js
*   **Deployment**: Docker

---

## 🚀 Installation & Run Locally

### Prerequisites
*   Python 3.8+ installed.

### Steps
1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd "Bank Management System"
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python backend/server.py
    ```

4.  **Access the App**:
    Open your browser and navigate to: `http://localhost:5000`

---

## 🐳 Docker Support

This project is containerized for easy deployment.

1.  **Build the Image**:
    ```bash
    docker build -t bank-system .
    ```

2.  **Run the Container**:
    ```bash
    docker run -p 5000:5000 bank-system
    ```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/login` | Authenticates user (Standard/Admin) |
| `POST` | `/api/register` | Creates a new customer account |
| `POST` | `/api/deposit` | Adds funds to user account |
| `POST` | `/api/withdraw` | Deducts funds (after PIN check) |
| `GET` | `/api/admin/users` | Admin: List all users |
| `POST` | `/api/admin/user-status` | Admin: Block/Suspend users |
| `GET` | `/api/admin/stats` | Admin: Get analytics data |

---

## 🔑 Default Credentials

### Admin Account
*   **Email**: `admin@login.com`
*   **Password**: `admin@123`

### Demo User
*   Create your own account via the **Register** page!

---

## ☁️ Deployment (Render)

1.  Push code to **GitHub**.
2.  Create a **New Web Service** on Render.
3.  Select **"Docker"** as the Runtime.
4.  Deploy!

---

*Developed for 4th Year Final Project.*
