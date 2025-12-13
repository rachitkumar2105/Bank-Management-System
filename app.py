import json
import random
import string
from pathlib import Path
from datetime import datetime
from io import BytesIO

import streamlit as st

# Optional PDF export
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    HAS_PDF = True
except Exception:
    HAS_PDF = False

DB_PATH = Path("database.json")
ADMIN_EMAIL = "admin@bank.com"
ADMIN_PIN = 9999

# ----------------------------------------------------
#                  DATABASE / BACKEND
# ----------------------------------------------------


def load_db():
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"users": []}, indent=4))
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
        if pin is not None and u["pin"] != pin:
            continue
        if acc_no is not None and u["account_no"] != acc_no:
            continue
        return u
    return None


def create_user(name, age, email, pin):
    db = load_db()
    if age < 18:
        return False, "Age must be 18 or above."
    if find_user(db, email=email) is not None:
        return False, "User with this email already exists."

    user = {
        "name": name,
        "age": age,
        "email": email,
        "pin": pin,
        "account_no": generate_account_no(),
        "balance": 0,
        "transactions": []
    }
    db["users"].append(user)
    save_db(db)
    return True, user


def add_transaction(user, t_type, amount):
    user["transactions"].append({
        "type": t_type,
        "amount": amount,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "balance_after": user["balance"]
    })


def deposit_money(email, pin, amount):
    db = load_db()
    user = find_user(db, email=email, pin=pin)
    if not user:
        return False, "Invalid email or PIN."

    if amount <= 0 or amount > 100000:
        return False, "Amount must be between 1 and 100000."

    user["balance"] += amount
    add_transaction(user, "deposit", amount)
    save_db(db)
    return True, user["balance"]


def withdraw_money(email, pin, amount):
    db = load_db()
    user = find_user(db, email=email, pin=pin)
    if not user:
        return False, "Invalid email or PIN."

    if amount <= 0:
        return False, "Amount must be greater than 0."

    if amount > user["balance"]:
        return False, "Insufficient balance."

    user["balance"] -= amount
    add_transaction(user, "withdraw", amount)
    save_db(db)
    return True, user["balance"]


def update_profile(email, pin, new_name=None, new_email=None, new_pin=None):
    db = load_db()
    user = find_user(db, email=email, pin=pin)
    if not user:
        return False, "Invalid email or PIN."

    if new_email and new_email != email and find_user(db, email=new_email):
        return False, "Another user already has this email."

    if new_name:
        user["name"] = new_name
    if new_email:
        user["email"] = new_email
    if new_pin:
        user["pin"] = new_pin

    save_db(db)
    return True, "Profile updated successfully."


def delete_account(email, pin):
    db = load_db()
    user = find_user(db, email=email, pin=pin)
    if not user:
        return False, "Invalid email or PIN."

    db["users"].remove(user)
    save_db(db)
    return True, "Account deleted successfully."


def get_user_by_email(email):
    return find_user(load_db(), email=email)


def get_all_users():
    return load_db()["users"]


def export_user_pdf(user):
    if not HAS_PDF:
        return None
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    t = c.beginText(40, 750)
    t.setFont("Helvetica", 12)
    t.textLine("Bank Account Summary")
    t.textLine("--------------------")
    t.textLine(f"Name      : {user['name']}")
    t.textLine(f"Email     : {user['email']}")
    t.textLine(f"Age       : {user['age']}")
    t.textLine(f"Account # : {user['account_no']}")
    t.textLine(f"Balance   : {user['balance']}")
    t.textLine("")
    t.textLine("Recent Transactions:")
    for tx in user["transactions"][-5:][::-1]:
        t.textLine(
            f"{tx['time']} | {tx['type'].upper()} | {tx['amount']} | Balance: {tx['balance_after']}"
        )
    c.drawText(t)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


# ----------------------------------------------------
#                  STREAMLIT UI
# ----------------------------------------------------

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------- Theme System ---------

SOFT_DARK = {
    "bg": "#0F1115",
    "card": "#1A1D23",
    "sidebar": "#16191F",
    "text": "#E8E8E8",
    "sub": "#A0A0A0",
    "border": "#2A2F38",
    "input_bg": "#1E2127",
    "button": "#7A5CFA",
    "button_text": "#FFFFFF",
}

SOFT_LIGHT = {
    "bg": "#F2EFEA",
    "card": "#FFFFFF",
    "sidebar": "#EFECE6",
    "text": "#1B1B1B",
    "sub": "#5F6368",
    "border": "#D3D3D3",
    "input_bg": "#FAFAFA",
    "button": "#6AA8FF",
    "button_text": "#FFFFFF",
}

st.sidebar.markdown("### Theme")
theme_choice = st.sidebar.radio(" ", ["Dark", "Light"], label_visibility="collapsed")
THEME = SOFT_DARK if theme_choice == "Dark" else SOFT_LIGHT

st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-color: {THEME['bg']} !important;
}}

[data-testid="stSidebar"] {{
    background-color: {THEME['sidebar']} !important;
}}

.card {{
    padding: 20px;
    border-radius: 16px;
    background-color: {THEME['card']};
    border: 1px solid {THEME['border']};
}}

.stButton>button {{
    border-radius: 999px;
    padding: 8px 18px;
    background-color: {THEME['button']} !important;
    color: {THEME['button_text']} !important;
    border: none;
    font-weight: 600;
}}

.stTextInput input, .stNumberInput input {{
    background-color: {THEME['input_bg']} !important;
    color: {THEME['text']} !important;
    border: 1px solid {THEME['border']} !important;
}}

h1, h2, h3, h4, h5, h6, label, .css-10trblm, .css-1ht1j8u {{
    color: {THEME['text']} !important;
}}

p, span {{
    color: {THEME['text']} !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

# --------- Session State ---------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "email" not in st.session_state:
    st.session_state.email = None
if "otp" not in st.session_state:
    st.session_state.otp = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --------- Title ---------

st.markdown(
    f"<h1 style='text-align:center; color:{THEME['text']};'>🏦 Bank Management System</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center; color:{THEME['sub']};'>Secure banking with OTP, dashboard, admin panel, and more.</p>",
    unsafe_allow_html=True,
)

# ====================================================
#                   LOGIN / REGISTER
# ====================================================

if not st.session_state.authenticated:
    col_login, col_reg = st.columns(2)

    # ------------ Login ------------
    with col_login:
        st.subheader("🔐 Login")
        login_email = st.text_input("Email")
        login_pin = st.text_input("PIN", type="password")

        if st.button("Send OTP"):
            if not login_pin.isdigit():
                st.error("PIN must be numeric.")
            else:
                pin_val = int(login_pin)
                if login_email == ADMIN_EMAIL and pin_val == ADMIN_PIN:
                    st.session_state.otp = random.randint(100000, 999999)
                    st.session_state.is_admin = True
                    st.info(f"(Demo OTP) {st.session_state.otp}")
                else:
                    user = find_user(load_db(), email=login_email, pin=pin_val)
                    if not user:
                        st.error("Invalid email or PIN.")
                    else:
                        st.session_state.otp = random.randint(100000, 999999)
                        st.session_state.is_admin = False
                        st.info(f"(Demo OTP) {st.session_state.otp}")

        if st.session_state.otp:
            otp_input = st.text_input("Enter OTP")
            if st.button("Verify OTP"):
                if otp_input == str(st.session_state.otp):
                    st.success("Login successful!")
                    st.session_state.authenticated = True
                    st.session_state.email = login_email
                    st.session_state.otp = None
                    st.rerun()
                else:
                    st.error("Incorrect OTP.")

    # ------------ Register ------------
    with col_reg:
        st.subheader("📝 Register")
        reg_name = st.text_input("Full Name")
        reg_age = st.number_input("Age", min_value=1, max_value=120, value=18)
        reg_email = st.text_input("New Email")
        reg_pin = st.text_input("New 4-digit PIN", type="password")

        if st.button("Create Account"):
            if not reg_pin.isdigit() or len(reg_pin) != 4:
                st.error("PIN must be exactly 4 digits.")
            else:
                ok, data = create_user(
                    reg_name, int(reg_age), reg_email, int(reg_pin)
                )
                if ok:
                    st.success("Account created successfully!")
                    st.write(
                        f"Your Account Number is: **{data['account_no']}**"
                    )
                else:
                    st.error(data)

    st.stop()

# ====================================================
#              AUTHENTICATED AREA
# ====================================================

email = st.session_state.email
current_user = None if st.session_state.is_admin else get_user_by_email(email)

# Sidebar menu
st.sidebar.markdown("### Menu")
menu_items = [
    "Dashboard",
    "Deposit",
    "Withdraw",
    "History",
    "Profile",
]
if st.session_state.is_admin:
    menu_items.append("Admin Panel")
menu_items.append("Logout")

menu_choice = st.sidebar.radio(" ", menu_items, label_visibility="collapsed")

# ------------ Logout ------------
if menu_choice == "Logout":
    st.session_state.authenticated = False
    st.session_state.email = None
    st.session_state.is_admin = False
    st.success("Logged out successfully.")
    st.stop()

# ====================================================
#                    DASHBOARD
# ====================================================

if menu_choice == "Dashboard":
    if st.session_state.is_admin:
        st.subheader("👑 Admin Dashboard")

        all_users = get_all_users()
        total_users = len(all_users)
        total_balance = sum(u["balance"] for u in all_users)
        total_txn = sum(len(u["transactions"]) for u in all_users)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Users", total_users)
        c2.metric("Total Balance", f"₹{total_balance}")
        c3.metric("Total Transactions", total_txn)

        st.write("### All Users")
        if all_users:
            import pandas as pd

            df = pd.DataFrame(
                [
                    {
                        "Name": u["name"],
                        "Email": u["email"],
                        "Account No.": u["account_no"],
                        "Balance": u["balance"],
                        "Transactions": len(u["transactions"]),
                    }
                    for u in all_users
                ]
            )
            st.dataframe(df)
        else:
            st.info("No users yet.")
    else:
        st.subheader(f"👋 Welcome {current_user['name']}")
        tx = current_user["transactions"]
        balance = current_user["balance"]
        deposits = sum(t["amount"] for t in tx if t["type"] == "deposit")
        withdrawals = sum(t["amount"] for t in tx if t["type"] == "withdraw")

        c1, c2, c3 = st.columns(3)
        c1.metric("Balance", f"₹{balance}")
        c2.metric("Total Deposits", f"₹{deposits}")
        c3.metric("Total Withdrawals", f"₹{withdrawals}")

        if tx:
            import pandas as pd

            df = pd.DataFrame(tx)
            df["time"] = pd.to_datetime(df["time"])
            df = df.sort_values("time")
            st.line_chart(df.set_index("time")["balance_after"])
        else:
            st.info("No transactions yet.")

# ====================================================
#                    DEPOSIT PAGE
# ====================================================

elif menu_choice == "Deposit":
    if st.session_state.is_admin:
        st.warning("Admin account cannot perform deposits.")
    else:
        st.subheader("💰 Deposit Money")
        amount = st.number_input("Amount to deposit", min_value=1)
        if st.button("Deposit"):
            ok, msg = deposit_money(email, current_user["pin"], amount)
            if ok:
                st.success(f"Deposit successful. New balance: ₹{msg}")
            else:
                st.error(msg)

# ====================================================
#                    WITHDRAW PAGE
# ====================================================

elif menu_choice == "Withdraw":
    if st.session_state.is_admin:
        st.warning("Admin account cannot perform withdrawals.")
    else:
        st.subheader("💸 Withdraw Money")
        amount = st.number_input("Amount to withdraw", min_value=1)
        if st.button("Withdraw"):
            ok, msg = withdraw_money(email, current_user["pin"], amount)
            if ok:
                st.success(f"Withdrawal successful. New balance: ₹{msg}")
            else:
                st.error(msg)

# ====================================================
#                    HISTORY PAGE
# ====================================================

elif menu_choice == "History":
    if st.session_state.is_admin:
        st.warning("Admin account has no personal transactions.")
    else:
        st.subheader("📜 Transaction History")
        if current_user["transactions"]:
            import pandas as pd

            df = pd.DataFrame(current_user["transactions"])
            df["time"] = pd.to_datetime(df["time"])
            df = df.sort_values("time", ascending=False)
            st.dataframe(df)
        else:
            st.info("No transactions yet.")

# ====================================================
#                    PROFILE PAGE
# ====================================================

elif menu_choice == "Profile":
    if st.session_state.is_admin:
        st.subheader("👑 Admin Profile")
        st.write(f"Email: {ADMIN_EMAIL}")
        st.info("Use Admin Panel to see all users.")
    else:
        st.subheader("🙍 Your Profile")
        st.write(f"**Name:** {current_user['name']}")
        st.write(f"**Email:** {current_user['email']}")
        st.write(f"**Age:** {current_user['age']}")
        st.write(f"**Account No.:** {current_user['account_no']}")
        st.write(f"**Balance:** ₹{current_user['balance']}")

        st.markdown("---")
        st.write("### Update Details")

        new_name = st.text_input("New Name", value=current_user["name"])
        new_email = st.text_input("New Email", value=current_user["email"])
        new_pin = st.text_input("New PIN (leave blank to keep same)", type="password")

        if st.button("Save Changes"):
            npin = int(new_pin) if new_pin.isdigit() else None
            ok, msg = update_profile(
                email,
                current_user["pin"],
                new_name,
                new_email,
                npin,
            )
            if ok:
                st.success(msg)
                st.session_state.email = new_email
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")
        st.write("### Export Summary")
        if HAS_PDF:
            pdf_buf = export_user_pdf(current_user)
            if pdf_buf:
                st.download_button(
                    "📄 Download PDF Summary",
                    data=pdf_buf,
                    file_name="account_summary.pdf",
                    mime="application/pdf",
                )
        else:
            st.info("Install `reportlab` for PDF export (pip install reportlab).")

        st.markdown("---")
        if st.button("🗑 Delete My Account"):
            ok, msg = delete_account(email, current_user["pin"])
            if ok:
                st.success(msg)
                st.session_state.authenticated = False
                st.session_state.email = None
                st.rerun()
            else:
                st.error(msg)

# ====================================================
#                    ADMIN PANEL
# ====================================================

elif menu_choice == "Admin Panel":
    if not st.session_state.is_admin:
        st.error("Only admin can access this page.")
    else:
        st.subheader("🛠 Admin Panel")
        users = get_all_users()
        if users:
            import pandas as pd

            df = pd.DataFrame(
                [
                    {
                        "Name": u["name"],
                        "Email": u["email"],
                        "Age": u["age"],
                        "Account No.": u["account_no"],
                        "Balance": u["balance"],
                        "Transactions": len(u["transactions"]),
                    }
                    for u in users
                ]
            )
            st.dataframe(df)
        else:
            st.info("No users found.")
