import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="AI Food Waste Dashboard", layout="wide")

# ---------------- DB ----------------

def get_connection():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="sql#2025@yug#52",
    database="food_waste_db"
    )

conn = get_connection()

def load_data(query, params=None):
    return pd.read_sql(query, conn, params=params)

# ---------------- TITLE ----------------

st.title("🤖 AI Food Waste Dashboard")

# ---------------- LOAD DATA ----------------

all_data = load_data("SELECT * FROM Food_Listings")
all_data["Expiry_Date"] = pd.to_datetime(all_data["Expiry_Date"], errors="coerce")

# ---------------- FILTERS ----------------

st.sidebar.header("Filters")

cities = ["All"] + sorted(all_data["Location"].dropna().unique())
food_types = ["All"] + sorted(all_data["Food_Type"].dropna().unique())
meal_types = ["All"] + sorted(all_data["Meal_Type"].dropna().unique())

city = st.sidebar.selectbox("City", cities)
food_type = st.sidebar.selectbox("Food Type", food_types)
meal_type = st.sidebar.selectbox("Meal Type", meal_types)

query = "SELECT * FROM Food_Listings WHERE 1=1"
params = []

if city != "All":
    query += " AND Location=%s"
    params.append(city)

if food_type != "All":
    query += " AND Food_Type=%s"
    params.append(food_type)

if meal_type != "All":
    query += " AND Meal_Type=%s"
    params.append(meal_type)

df = load_data(query, params)
df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce")

# ---------------- KPI ----------------

st.markdown("## 📊 Key Metrics")

c1, c2, c3 = st.columns(3)
c1.metric("Listings", len(df))
c2.metric("Quantity", int(df["Quantity"].sum()) if not df.empty else 0)
c3.metric("Cities", df["Location"].nunique() if not df.empty else 0)

# ---------------- TABLE ----------------

st.dataframe(df, use_container_width=True)

# ---------------- CHARTS ----------------

if not df.empty:
    col1, col2 = st.columns(2)


    with col1:
        st.subheader("Food Type Distribution")
        st.bar_chart(df["Food_Type"].value_counts())
    
    with col2:
        st.subheader("Meal Type Distribution")
        st.bar_chart(df["Meal_Type"].value_counts())

# ---------------- EXPIRY ----------------

st.markdown("## 🚨 Expired Food")

today = pd.Timestamp.now()

expired = all_data[
all_data["Expiry_Date"].notna() &
(all_data["Expiry_Date"] < today)
]

st.dataframe(expired)

# ---------------- SQL INSIGHTS ----------------

st.markdown("## 📊 SQL Insights")

q1 = """
SELECT Food_Type, COUNT(*) AS Count
FROM Food_Listings
GROUP BY Food_Type
ORDER BY Count DESC
"""
st.subheader("Most Common Food Type")
st.dataframe(load_data(q1))

q2 = """
SELECT Status, COUNT(*) as Count
FROM Claims
GROUP BY Status
"""
st.subheader("Claim Status")
st.dataframe(load_data(q2))

# ---------------- CRUD ----------------

st.markdown("## 🛠 CRUD")

tab1, tab2, tab3 = st.tabs(["Add", "Update", "Delete"])

# ADD

with tab1:
    food_name = st.text_input("Food Name")
    quantity = st.number_input("Quantity", 1)
    expiry = st.date_input("Expiry Date")


if st.button("Add Food"):
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO Food_Listings (Food_Name, Quantity, Expiry_Date)
    VALUES (%s,%s,%s)
    """, (food_name, quantity, expiry))
    conn.commit()
    st.success("Added")

# UPDATE

with tab2:
    ids = load_data("SELECT Food_ID FROM Food_Listings")["Food_ID"]

if not ids.empty:
    fid = st.selectbox("Select ID", ids)
    new_qty = st.number_input("New Quantity", 1)

    if st.button("Update"):
        cur = conn.cursor()
        cur.execute("""
        UPDATE Food_Listings SET Quantity=%s WHERE Food_ID=%s
        """, (new_qty, int(fid)))
        conn.commit()
        st.success("Updated")

# DELETE

with tab3:
    ids = load_data("SELECT Food_ID FROM Food_Listings")["Food_ID"]


if not ids.empty:
    did = st.selectbox("Delete ID", ids)

    if st.button("Delete"):
        cur = conn.cursor()
        cur.execute("DELETE FROM Food_Listings WHERE Food_ID=%s", (int(did),))
        conn.commit()
        st.success("Deleted")


st.markdown("---")
st.markdown("🚀 Final Project Ready")
