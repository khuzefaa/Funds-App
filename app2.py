import streamlit as st
import pandas as pd
import datetime
import os

# ---------- Simple Authentication ----------
ADMIN_PASSWORD = "admin123"  # change this in real app
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ---------- Data File ----------
DATA_FILE = "transactions.csv"

# ---------- Load or Initialize Data ----------
if os.path.exists(DATA_FILE):
    transactions = pd.read_csv(DATA_FILE)
else:
    transactions = pd.DataFrame(columns=["Date", "Type", "Amount", "Description"])

if "transactions" not in st.session_state:
    st.session_state.transactions = transactions

def save_data():
    st.session_state.transactions.to_csv(DATA_FILE, index=False)

def add_transaction(t_type, amount, description):
    new_entry = {
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Type": t_type,
        "Amount": amount,
        "Description": description
    }
    st.session_state.transactions = pd.concat(
        [st.session_state.transactions, pd.DataFrame([new_entry])],
        ignore_index=True
    )
    save_data()  # save to CSV immediately

# ---------- Dashboard ----------
st.title("💰 Masjid Funds")

transactions = st.session_state.transactions

total_funds = transactions.apply(lambda row: row["Amount"] if row["Type"] == "Add" else -row["Amount"], axis=1).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Funds", f"{total_funds}")

if not transactions.empty:
    last_add = transactions[transactions["Type"] == "Add"].tail(1)
    last_use = transactions[transactions["Type"] == "Minus"].tail(1)
    
    col2.metric("Last Added", f"{last_add['Amount'].values[0]}" if not last_add.empty else "N/A")
    col3.metric("Last Used", f"{last_use['Amount'].values[0]}" if not last_use.empty else "N/A")

# ---------- Admin Login ----------
if not st.session_state.is_admin:
    password = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("Logged in as Admin")
        else:
            st.error("Wrong password")

# ---------- Admin Actions ----------
if st.session_state.is_admin:
    st.subheader("Admin Actions")
    action = st.radio("Select Action", ["Add Funds", "Minus Funds"])
    amount = st.number_input("Enter Amount", min_value=1, step=1)
    desc = st.text_area("Enter Description")
    if st.button("Submit Transaction"):
        if action == "Add Funds":
            add_transaction("Add", amount, desc)
            st.success(f"Added {amount}")
        else:
            add_transaction("Minus", amount, desc)
            st.warning(f"Deducted {amount}")

# ---------- Show All Transactions ----------
st.subheader("Transaction History")
st.dataframe(transactions)

# ---------- Download Option ----------
csv = transactions.to_csv(index=False).encode("utf-8")
st.download_button("Download Data as CSV", csv, "transactions.csv", "text/csv")
