import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Food Waste Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    food = pd.read_csv("food_listings_data.csv")
    claims = pd.read_csv("claims_data.csv")
    return food, claims

food, claims = load_data()

food["Expiry_Date"] = pd.to_datetime(food["Expiry_Date"], errors="coerce")

# ---------------- TITLE ----------------

st.title("🤖 AI Food Waste Dashboard")

# ---------------- FILTERS ----------------

st.sidebar.header("Filters")

cities = ["All"] + sorted(food["Location"].dropna().unique())
food_types = ["All"] + sorted(food["Food_Type"].dropna().unique())
meal_types = ["All"] + sorted(food["Meal_Type"].dropna().unique())

city = st.sidebar.selectbox("City", cities)
food_type = st.sidebar.selectbox("Food Type", food_types)
meal_type = st.sidebar.selectbox("Meal Type", meal_types)

df = food.copy()

if city != "All":
    df = df[df["Location"] == city]

if food_type != "All":
    df = df[df["Food_Type"] == food_type]

if meal_type != "All":
    df = df[df["Meal_Type"] == meal_type]

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

expired = food[
    food["Expiry_Date"].notna() &
    (food["Expiry_Date"] < today)
]

if not expired.empty:
    st.error(f"{len(expired)} expired items found")
    st.dataframe(expired)
else:
    st.success("No expired food")

# ---------------- INSIGHTS ----------------

st.markdown("## 📊 Insights")

# Most common food type
st.subheader("Most Common Food Type")
st.dataframe(food["Food_Type"].value_counts().reset_index().rename(
    columns={"index": "Food_Type", "Food_Type": "Count"}
))

# Claim status
st.subheader("Claim Status")
st.dataframe(claims["Status"].value_counts().reset_index().rename(
    columns={"index": "Status", "Status": "Count"}
))

# ---------------- CRUD (CSV BASED) ----------------

st.markdown("## 🛠 CRUD Operations")

tab1, tab2, tab3 = st.tabs(["Add", "Update", "Delete"])

# ADD
with tab1:
    food_name = st.text_input("Food Name")
    quantity = st.number_input("Quantity", 1)
    expiry = st.date_input("Expiry Date")

    if st.button("Add Food"):
        new_row = pd.DataFrame([{
            "Food_ID": food["Food_ID"].max() + 1,
            "Food_Name": food_name,
            "Quantity": quantity,
            "Expiry_Date": expiry,
            "Location": "Manual",
            "Food_Type": "Manual",
            "Meal_Type": "Manual"
        }])

        food_updated = pd.concat([food, new_row], ignore_index=True)
        food_updated.to_csv("food_listings_data.csv", index=False)

        st.success("Food Added (Refresh app)")

# UPDATE
with tab2:
    if not food.empty:
        fid = st.selectbox("Select Food ID", food["Food_ID"])
        new_qty = st.number_input("New Quantity", 1)

        if st.button("Update Food"):
            food.loc[food["Food_ID"] == fid, "Quantity"] = new_qty
            food.to_csv("food_listings_data.csv", index=False)
            st.success("Updated (Refresh app)")

# DELETE
with tab3:
    if not food.empty:
        did = st.selectbox("Delete Food ID", food["Food_ID"])

        if st.button("Delete Food"):
            food_updated = food[food["Food_ID"] != did]
            food_updated.to_csv("food_listings_data.csv", index=False)
            st.success("Deleted (Refresh app)")

# ---------------- FOOTER ----------------

st.markdown("---")
st.markdown("🚀 Final Project Ready | CSV Based | Deployable")