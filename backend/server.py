import json
import random
import string
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

DB_PATH = Path("database.json")
ADMIN_EMAIL = "admin@login.com"
ADMIN_PASSWORD = "admin@123"

# ----------------------------------------------------
#                  DATABASE LOGIC
# ----------------------------------------------------

def load_db():
    if not DB_PATH.exists():
        with open(DB_PATH, "w") as f:
            json.dump({"users": []}, f, indent=4)
    with open(DB_PATH) as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def generate_account_no():
    chars = random.choices(string.ascii_letters, k=3) + \
            random.choices(string.digits, k=3) + \
            random.choices("!@#$%^&*", k=1)
    random.shuffle(chars)
    return "".join(chars)

def find_user(db, email=None, pin=None, acc_no=None):
    for u in db["users"]:
        if email is not None and u["email"] != email:
            continue
        if pin is not None and int(u["pin"]) != int(pin):
            continue
        if acc_no is not None and u["account_no"] != acc_no:
            continue
        return u
    return None

def add_transaction(user, t_type, amount):
    user["transactions"].append({
        "type": t_type,
        "amount": amount,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "balance_after": user["balance"]
    })

# ----------------------------------------------------
#                  API ROUTES
# ----------------------------------------------------

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    pin = data.get('pin')

    if not email or not pin:
        return jsonify({"error": "Email and PIN are required"}), 400

    # Admin Check
    if email == ADMIN_EMAIL and str(pin) == ADMIN_PASSWORD:
         otp = random.randint(100000, 999999)
         return jsonify({
            "message": "Credentials Valid",
            "otp": otp,
            "is_admin": True,
            "user": {"name": "Admin", "email": ADMIN_EMAIL}
        }), 200

    db = load_db()
    user = find_user(db, email=email, pin=pin)
    
    if user:
        # Check Status
        if user.get("status") == "Blocked":
             return jsonify({"error": "Your account has been BLOCKED. Contact Admin."}), 403
        if user.get("status") == "Suspended":
             return jsonify({"error": "Your account is SUSPENDED. Contact Admin."}), 403

        otp = random.randint(100000, 999999)
        return jsonify({
            "message": "Credentials Valid",
            "otp": otp,
            "is_admin": False,
            "user": user
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    email = data.get('email')
    pin = data.get('pin')

    if not all([name, age, email, pin]):
        return jsonify({"error": "All fields are required"}), 400

    if int(age) < 18:
        return jsonify({"error": "Age must be 18 or above"}), 400

    if len(str(pin)) != 4 or not str(pin).isdigit():
        return jsonify({"error": "PIN must be 4 digits"}), 400

    db = load_db()
    if find_user(db, email=email) is not None:
        return jsonify({"error": "User with this email already exists"}), 400

    user = {
        "name": name,
        "age": int(age),
        "email": email,
        "pin": int(pin),
        "account_no": generate_account_no(),
        "balance": 0,
        "status": "Active",
        "transactions": []
    }
    db["users"].append(user)
    save_db(db)

    return jsonify({"message": "Account created successfully", "user": user}), 201

@app.route('/api/user/<email>', methods=['GET'])
def get_user_data(email):
    db = load_db()
    user = find_user(db, email=email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user}), 200

@app.route('/api/admin/user-status', methods=['POST'])
def update_user_status():
    data = request.json
    target_email = data.get('email')
    new_status = data.get('status') # Active, Suspended, Blocked

    if not target_email or not new_status:
         return jsonify({"error": "Email and Status required"}), 400

    db = load_db()
    user = find_user(db, email=target_email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user["status"] = new_status
    save_db(db)
    return jsonify({"message": f"User status updated to {new_status}"}), 200

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # In a real app, verify admin token/session here.
    db = load_db()
    return jsonify(db["users"]), 200

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    db = load_db()
    users = db["users"]
    
    # User Status Counts
    status_counts = {"Active": 0, "Suspended": 0, "Blocked": 0}
    for u in users:
        s = u.get("status", "Active")
        status_counts[s] = status_counts.get(s, 0) + 1
        
    # Financial Totals
    total_deposits = 0
    total_withdrawals = 0
    
    for u in users:
        for t in u.get("transactions", []):
            if t["type"] == "deposit":
                total_deposits += t["amount"]
            elif t["type"] == "withdraw": 
                total_withdrawals += t["amount"]
                
    return jsonify({
        "user_status": status_counts,
        "financials": {
            "deposits": total_deposits,
            "withdrawals": total_withdrawals
        }
    }), 200

@app.route('/api/deposit', methods=['POST'])
def deposit():
    data = request.json
    email = data.get('email')
    amount = data.get('amount')
    
    if not email or amount is None:
        return jsonify({"error": "Email and amount are required"}), 400
        
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    db = load_db()
    user = find_user(db, email=email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user["balance"] += amount
    add_transaction(user, "deposit", amount)
    save_db(db)
    
    return jsonify({"message": "Deposit successful", "balance": user["balance"]}), 200

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    email = data.get('email')
    amount = data.get('amount')
    pin = data.get('pin') # Secure withdraw

    if not email or amount is None or not pin:
        return jsonify({"error": "Email, amount and PIN are required"}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400

    db = load_db()
    user = find_user(db, email=email, pin=pin)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if user.get("status", "Active") != "Active":
        return jsonify({"error": "Transaction denied. Account is not Active."}), 403

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    if user["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    user["balance"] -= amount
    add_transaction(user, "withdraw", amount)
    save_db(db)

    return jsonify({"message": "Withdrawal successful", "balance": user["balance"]}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
