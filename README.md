# 🏦 Bank Management System

A secure, full-stack digital banking solution developed as a Final Year Project. This application features a robust backend, responsive frontend, and a comprehensive Admin Dashboard with analytics.

---

## 🚀 Live Demo
**[Deploy on Render](https://render.com)** (Follow deployment steps below)

---

## ✨ Features

### 👤 Customer Banking Panel
*   **Secure Authentication**: Login & Register with OTP (Simulated).
*   **Real-time Dashboard**: View Account Balance, Total Deposits, and Withdrawals.
*   **Transactions**:
    *   **Deposit Funds**: Securely add money to your account.
    *   **Withdraw Funds**: PIN-protected withdrawals.
*   **Passbook / History**: View detailed transaction logs.
*   **Download Statement**: Export account statement as a text file.
*   **Profile Manager**: View account details (Formatted with CSS Grid).

### 🛠 Admin Portal
*   **Dashboard Analytics**:
    *   **User Status Chart**: Visual breakdown of Active/Blocked users.
    *   **Financial Overview**: Interactive bar chart of Deposits vs. Withdrawals.
*   **User Management**:
    *   View all registered customers.
    *   **Block/Suspend** users to restrict access immediately.
    *   **Activate** users to restore access.

---

## 🛠 Tech Stack

*   **Frontend**: HTML5, CSS3 (Modern Dark Theme), Vanilla JavaScript.
*   **Backend**: Python, Flask, Gunicorn.
*   **Charts**: Chart.js (Data visualization).
*   **Database**: JSON-based flat file (`database.json`) - *No SQL setup required*.
*   **Containerization**: Docker.

---

## � Installation & Setup

### Option 1: Run Locally (Python)

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/Bank-Management-System.git
    cd "Bank Management System"
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start the Server**
    ```bash
    python backend/server.py
    ```

4.  **Access the App**
    Open [http://localhost:5000](http://localhost:5000) in your browser.

### Option 2: Run with Docker

1.  **Build Image**
    ```bash
    docker build -t bank-app .
    ```

2.  **Run Container**
    ```bash
    docker run -p 5000:5000 bank-app
    ```

---

## ☁️ Deployment Guide (Render)

This project is optimized for deployment on [Render.com](https://render.com) using Docker.

1.  **Push to GitHub**: ensure your repository is up to date.
2.  **Create Web Service**: Go to Render Dashboard > New Web Service.
3.  **Connect Repo**: Select your `Bank-Management-System` repository.
4.  **Select Runtime**: Choose **Docker** (Important!).
5.  **Deploy**: Click "Create Web Service". Render will automatically build the `Dockerfile`.

---

## 🔑 Default Admin Credentials

Use these credentials to access the Admin Portal:

*   **Email**: `admin@login.com`
*   **Password**: `admin@123`

---

## 📂 Project Structure

```
Bank Management System/
├── backend/
│   └── server.py        # Flask API & Server Logic
├── frontend/
│   ├── index.html       # Single Page Application HTML
│   ├── style.css        # Custom CSS Styles
│   └── script.js        # Frontend Logic & API calls
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
└── database.json        # Data storage (Created automatically)
```

---
*Developed by Rachit Kumar Singh*
