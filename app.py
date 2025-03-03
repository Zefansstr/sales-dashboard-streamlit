import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(page_title="Sales Analysis Dashboard", layout="wide")
st.markdown(
    """
    <style>
        .reportview-container {
            background-color: #F5F5F5;
        }
        .sidebar .sidebar-content {
            background-color: #2E3B4E;
            color: white;
        }
        h1, h2, h3, h4 {
            color: #1F77B4;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("📌 Menu")
menu = st.sidebar.selectbox("Select Page", ["Dashboard", "Daily Analysis", "Monthly Analysis", "Customer Details"])

# Read data
data = pd.read_csv('data_pembelian.csv')
data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%d/%m/%Y %I:%M:%S %p', errors='coerce')
data['Date'] = data['DateTime'].dt.date
data['Hour'] = data['DateTime'].dt.hour
data['Month'] = data['DateTime'].dt.strftime('%Y-%m')
data['Amount'] = data['Amount'].astype(str).str.replace(',', '').astype(float)

def sales_by_hour(df):
    return df.groupby('Hour').agg({'Amount': 'sum', 'Username': 'count'}).reset_index()

def sales_by_3hour(df):
    df['3-Hour Interval'] = (df['Hour'] // 3) * 3
    return df.groupby('3-Hour Interval').agg({'Amount': 'sum', 'Username': 'count'}).reset_index()

if menu == "Dashboard":
    st.title("📊 Sales Analysis Dashboard M24SG🚀")
    total_amount = data['Amount'].sum()
    total_transactions = len(data)
    unique_users = data['Username'].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"SGD {total_amount:,.2f}")
    with col2:
        st.metric("Total Transactions", f"{total_transactions:,}")
    with col3:
        st.metric("Unique Users", f"{unique_users:,}")
    
    # Total Transactions Graph
    daily_transactions = data.groupby('Date').size().reset_index(name='Total Transactions')
    fig_trans = px.line(daily_transactions, x='Date', y='Total Transactions', title="📈 Daily Total Transactions Graph", markers=True)
    st.plotly_chart(fig_trans)

elif menu == "Daily Analysis":
    st.title("📅 Daily Analysis")
    selected_date = st.date_input("Select Date", min_value=data["Date"].min(), max_value=data["Date"].max())
    daily_sales = data[data["Date"] == selected_date].groupby('Date').agg({'Amount': 'sum', 'Username': 'count'}).reset_index()
    st.dataframe(daily_sales, use_container_width=True)
    
    hourly_sales = sales_by_hour(data[data["Date"] == selected_date])
    fig = px.bar(hourly_sales, x='Hour', y=['Amount', 'Username'], title="Sales & Transactions Per Hour", barmode='group', color_discrete_map={"Amount": "blue", "Username": "orange"})
    st.plotly_chart(fig)
    
    sales_3hour = sales_by_3hour(data[data["Date"] == selected_date])
    fig2 = px.bar(sales_3hour, x='3-Hour Interval', y=['Amount', 'Username'], title="Sales & Transactions Per 3 Hours", barmode='group', color_discrete_map={"Amount": "red", "Username": "green"})
    st.plotly_chart(fig2)
    
    most_frequent_user = data[data["Date"] == selected_date]['Username'].mode()[0]
    st.markdown(f"### 🏆 User with Most Transactions: **{most_frequent_user}**")

elif menu == "Monthly Analysis":
    st.title("📈 Monthly Analysis")
    monthly_sales = data.groupby('Month').agg({'Amount': 'sum', 'Username': 'count'}).reset_index()
    st.dataframe(monthly_sales, use_container_width=True)
    
    hourly_sales = sales_by_hour(data)
    fig = px.bar(hourly_sales, x='Hour', y=['Amount', 'Username'], title="Sales & Transactions Per Hour", barmode='group', color_discrete_map={"Amount": "blue", "Username": "orange"})
    st.plotly_chart(fig)
    
    sales_3hour = sales_by_3hour(data)
    fig2 = px.bar(sales_3hour, x='3-Hour Interval', y=['Amount', 'Username'], title="Sales & Transactions Per 3 Hours", barmode='group', color_discrete_map={"Amount": "red", "Username": "green"})
    st.plotly_chart(fig2)
    
    most_frequent_user = data['Username'].mode()[0]
    st.markdown(f"### 🏆 User with Most Transactions: **{most_frequent_user}**")

elif menu == "Customer Details":
    st.title("📋 Customer Details")
    user_sales = data.groupby('Username').agg({'Amount': 'sum', 'Date': 'nunique'}).reset_index()
    user_sales.columns = ['Username', 'Total Amount', 'Active Days']
    user_sales = user_sales.sort_values('Total Amount', ascending=False)
    st.dataframe(user_sales, use_container_width=True)