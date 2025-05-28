import hashlib
import pandas as pd

# Load the dataset
df = pd.read_csv("datasets/bank_transactions.csv")

# Map customer identifiers to unique ObjectId-like hashes
unique_customers = df[["CustomerID", "CustGender", "CustLocation"]].drop_duplicates().copy()
unique_customers["object_id"] = unique_customers.apply(
    lambda row: hashlib.md5(f"{row['CustomerID']}_{row['CustGender']}_{row['CustLocation']}".encode()).hexdigest()[:24],
    axis=1
)

# Merge back the ObjectId to the main DataFrame
df = df.merge(unique_customers, on=["CustomerID", "CustGender", "CustLocation"], how="left")

# Rebuild CUSTOMERS collection
customers = df[["CustomerID", "CustGender", "CustLocation", "CustAccountBalance", "object_id"]].drop_duplicates().copy()

customers.rename(columns={
    "CustomerID": "customer_id",
    "CustGender": "gender",
    "CustLocation": "location",
    "CustAccountBalance": "account_balance",
    "object_id": "_id"
}, inplace=True)

customers = customers[["_id", "customer_id", "gender", "location", "account_balance"]]

# Rebuild TRANSACTIONS collection with embedded customer reference
transactions = df[[
    "TransactionID", "TransactionDate", "TransactionTime", "TransactionAmount (INR)", "object_id"
]].copy()


# Generate full transaction ID
def generate_full_transaction_id(row):
    fields = [
        str(row["object_id"]),
        row["TransactionDate"],
        str(row["TransactionAmount (INR)"]),
        str(row["TransactionTime"])
    ]
    return hashlib.md5("_".join(fields).encode()).hexdigest()


transactions["_id"] = transactions.apply(generate_full_transaction_id, axis=1)
transactions["customer_id"] = transactions["object_id"]

# Final formatting for transactions
transactions.rename(columns={
    "TransactionID": "transaction_id",
    "TransactionDate": "transaction_date",
    "TransactionAmount (INR)": "transaction_amount",
    "TransactionTime": "transaction_time"
}, inplace=True)

transactions = transactions[
    ["_id", "customer_id", "transaction_id", "transaction_date", "transaction_amount", "transaction_time"]]

# Convert ObjectId fields to JSON serializable format
customers["_id"] = customers["_id"].apply(lambda oid: {"$oid": str(oid)})
transactions["customer_id"] = transactions["customer_id"].apply(lambda oid: {"$oid": str(oid)})

# Save to JSON files
customers.to_json("datasets/customers.json", orient="records", indent=2)
transactions.to_json("datasets/transactions.json", orient="records", indent=2)
