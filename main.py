import pandas as pd
import streamlit as st
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://root:root@localhost:27020")  # Adjust MongoDB connection URL
db = client["bank"]
customers_col = db["customers"]
transactions_col = db["transactions"]

st.set_page_config(page_title="Bank Customer Dashboard", layout="wide")

st.title("🏦 Bank Customer Dashboard")

tab1, tab2, tab3 = st.tabs(["✍️ Add Data", "📊 View Data", "🔍 Search and Update"])

# =====================
# 1. ADD DATA
# =====================
with tab1:
    st.subheader("Add a New Customer and Transaction")

    # Add customer details
    with st.form("add_customer"):
        customer_id = st.text_input("Customer ID")
        gender = st.selectbox("Gender", ["Male", "Female"])
        location = st.text_input("Location")
        account_balance = st.number_input("Account Balance", min_value=0.0, step=100.0)
        submit_customer = st.form_submit_button("Add Customer")

        if submit_customer:
            customers_col.insert_one({
                "customer_id": customer_id,
                "gender": gender,
                "location": location,
                "account_balance": account_balance
            })
            st.success("✅ Customer successfully added!")

    # Add transaction details
    with st.form("add_transaction"):
        transaction_id = st.text_input("Transaction ID")
        customer_id = st.selectbox("Select Customer", options=[c["customer_id"] for c in customers_col.find()])
        transaction_date = st.date_input("Transaction Date")
        transaction_time = st.time_input("Transaction Time")
        transaction_amount = st.number_input("Transaction Amount", min_value=0.0, step=100.0)
        submit_transaction = st.form_submit_button("Add Transaction")

        if submit_transaction:
            customer = customers_col.find_one({"customer_id": customer_id})
            if customer:
                transactions_col.insert_one({
                    "transaction_id": transaction_id,
                    "transaction_date": transaction_date.isoformat(),
                    "transaction_time": transaction_time.isoformat(),
                    "transaction_amount": transaction_amount,
                    "customer_id": customer["_id"]  # Reference to customer _id
                })
                st.success("✅ Transaction successfully added!")

# =====================
# 2. VIEW DATA
# =====================
with tab2:
    st.subheader("View and Filter Customers and Transactions")

    # ----- Customers Section -----
    st.markdown("### 🧍 Customers")

    # Filter options for customers
    customer_gender = st.selectbox("Filter by Gender", options=["All", "Male", "Female"])
    customer_location = st.text_input("Filter by Location (optional)")
    customer_page = st.number_input("Customer Page", min_value=1, value=1)
    customer_page_size = 50

    # Build customer query
    customer_query = {}
    if customer_gender != "All":
        customer_query["gender"] = customer_gender
    if customer_location:
        customer_query["location"] = {"$regex": customer_location, "$options": "i"}

    # Fetch paginated customers
    customer_cursor = customers_col.find(customer_query).skip((customer_page - 1) * customer_page_size).limit(customer_page_size)
    customers_df = pd.DataFrame(list(customer_cursor))

    if not customers_df.empty:
        customers_df["_id"] = customers_df["_id"].apply(lambda oid: str(oid))
        st.dataframe(customers_df)
    else:
        st.info("No customers found for selected filters.")

    # ----- Transactions Section -----
    st.markdown("### 💳 Transactions")

    # Filter options for transactions
    transaction_type = st.text_input("Filter by Transaction Type (optional)")
    transaction_min_amount = st.number_input("Minimum Amount", min_value=0.0, value=0.0)
    transaction_page = st.number_input("Transaction Page", min_value=1, value=1, key="txn_page")
    transaction_page_size = 50

    # Build transaction query
    transaction_query = {"transaction_amount": {"$gte": transaction_min_amount}}
    if transaction_type:
        transaction_query["transaction_type"] = {"$regex": transaction_type, "$options": "i"}

    # Fetch paginated transactions
    transaction_cursor = transactions_col.find(transaction_query).skip((transaction_page - 1) * transaction_page_size).limit(transaction_page_size)
    transactions_df = pd.DataFrame(list(transaction_cursor))

    if not transactions_df.empty:
        transactions_df["_id"] = transactions_df["_id"].apply(lambda oid: str(oid))
        transactions_df["customer_id"] = transactions_df["customer_id"].apply(lambda oid: str(oid))
        st.dataframe(transactions_df)
    else:
        st.info("No transactions found for selected filters.")


# =====================
# 3. SEARCH AND UPDATE DATA
# =====================
with tab3:
    st.subheader("Search and Update Data")

    # Search for a customer to update
    search_customer_id = st.text_input("Search Customer by ID")
    if search_customer_id:
        customer = customers_col.find_one({"customer_id": search_customer_id})
        if customer:
            st.write(f"Found Customer: {customer}")
            with st.form("update_customer"):
                new_balance = st.number_input("Update Account Balance", value=customer["account_balance"], step=100.0)
                submit_update_customer = st.form_submit_button("Update Customer")

                if submit_update_customer:
                    customers_col.update_one(
                        {"_id": customer["_id"]},
                        {"$set": {"account_balance": new_balance}}
                    )
                    st.success(f"✅ Customer {search_customer_id} updated!")
        else:
            st.error("Customer not found!")

    # Search for a transaction to update
    search_transaction_id = st.text_input("Search Transaction by ID")
    if search_transaction_id:
        transaction = transactions_col.find_one({"transaction_id": search_transaction_id})
        if transaction:
            st.write(f"Found Transaction: {transaction}")
            with st.form("update_transaction"):
                new_amount = st.number_input("Update Transaction Amount", value=transaction["transaction_amount"],
                                             step=100.0)
                submit_update_transaction = st.form_submit_button("Update Transaction")

                if submit_update_transaction:
                    transactions_col.update_one(
                        {"_id": transaction["_id"]},
                        {"$set": {"transaction_amount": new_amount}}
                    )
                    st.success(f"✅ Transaction {search_transaction_id} updated!")
        else:
            st.error("Transaction not found!")

    # Delete a customer
    delete_customer_id = st.text_input("Delete Customer by ID")
    if delete_customer_id:
        delete_customer = customers_col.find_one({"customer_id": delete_customer_id})
        if delete_customer:
            if st.button(f"Delete Customer {delete_customer_id}"):
                customers_col.delete_one({"_id": delete_customer["_id"]})
                st.success(f"✅ Customer {delete_customer_id} deleted!")
        else:
            st.error("Customer not found!")

    # Delete a transaction
    delete_transaction_id = st.text_input("Delete Transaction by ID")
    if delete_transaction_id:
        delete_transaction = transactions_col.find_one({"transaction_id": delete_transaction_id})
        if delete_transaction:
            if st.button(f"Delete Transaction {delete_transaction_id}"):
                transactions_col.delete_one({"_id": delete_transaction["_id"]})
                st.success(f"✅ Transaction {delete_transaction_id} deleted!")
        else:
            st.error("Transaction not found!")
