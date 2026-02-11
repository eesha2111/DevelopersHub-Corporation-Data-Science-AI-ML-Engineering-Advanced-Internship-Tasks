import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Task 3 - Global Superstore Dashboard", layout="wide")
st.title("Task 3: Interactive Business Dashboard (Global Superstore)")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin1")
    df.columns = [c.strip() for c in df.columns]

    # Parse Order Date safely (Superstore often uses day-first dates)
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce", dayfirst=True)

    return df

# -------- Sidebar: CSV path --------
st.sidebar.header("Controls")
DATA_PATH = st.sidebar.text_input("CSV file path", value="Global_Superstore2.csv")

df = load_data(DATA_PATH)

st.subheader("Data Preview")
st.dataframe(df.head(), width="stretch")

# -------- Filters --------
filtered = df.copy()

if "Region" in filtered.columns:
    regions = sorted(filtered["Region"].dropna().unique())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
    filtered = filtered[filtered["Region"].isin(selected_regions)]

if "Category" in filtered.columns:
    categories = sorted(filtered["Category"].dropna().unique())
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
    filtered = filtered[filtered["Category"].isin(selected_categories)]

if "Sub-Category" in filtered.columns:
    subcats = sorted(filtered["Sub-Category"].dropna().unique())
    selected_subcats = st.sidebar.multiselect("Sub-Category", subcats, default=subcats)
    filtered = filtered[filtered["Sub-Category"].isin(selected_subcats)]

st.divider()

# -------- KPIs --------
st.subheader("Key Performance Indicators")

k1, k2, k3 = st.columns(3)

total_sales = filtered["Sales"].sum() if "Sales" in filtered.columns else 0
total_profit = filtered["Profit"].sum() if "Profit" in filtered.columns else 0

k1.metric("Total Sales", f"${total_sales:,.2f}")
k2.metric("Total Profit", f"${total_profit:,.2f}")

if "Customer Name" in filtered.columns and "Sales" in filtered.columns and len(filtered) > 0:
    top_customer = (
        filtered.groupby("Customer Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(1)
    )
    k3.metric("Top Customer Sales", f"${top_customer.iloc[0]:,.2f}")
else:
    k3.metric("Top Customer Sales", "N/A")

st.divider()

# -------- Charts --------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Sales by Category")
    if "Category" in filtered.columns and "Sales" in filtered.columns:
        sales_by_cat = filtered.groupby("Category")["Sales"].sum().sort_values(ascending=False)
        fig = plt.figure()
        plt.bar(sales_by_cat.index.astype(str), sales_by_cat.values)
        plt.xticks(rotation=25, ha="right")
        plt.ylabel("Sales")
        st.pyplot(fig)
    else:
        st.info("Required columns not found: Category / Sales")

with c2:
    st.subheader("Profit by Region")
    if "Region" in filtered.columns and "Profit" in filtered.columns:
        profit_by_region = filtered.groupby("Region")["Profit"].sum().sort_values(ascending=False)
        fig = plt.figure()
        plt.bar(profit_by_region.index.astype(str), profit_by_region.values)
        plt.xticks(rotation=25, ha="right")
        plt.ylabel("Profit")
        st.pyplot(fig)
    else:
        st.info("Required columns not found: Region / Profit")

st.subheader("Top 5 Customers by Sales")
if "Customer Name" in filtered.columns and "Sales" in filtered.columns:
    top5 = (
        filtered.groupby("Customer Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    st.dataframe(top5, width="stretch")
else:
    st.info("Required columns not found: Customer Name / Sales")

# -------- Monthly Sales Trend --------
if "Order Date" in filtered.columns and "Sales" in filtered.columns:
    st.subheader("Monthly Sales Trend")
    temp = filtered.dropna(subset=["Order Date"]).copy()
    temp["Month"] = temp["Order Date"].dt.to_period("M").dt.to_timestamp()
    monthly_sales = temp.groupby("Month")["Sales"].sum().sort_index()

    fig = plt.figure()
    plt.plot(monthly_sales.index, monthly_sales.values)
    plt.xlabel("Month")
    plt.ylabel("Sales")
    st.pyplot(fig)
