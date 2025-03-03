import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(page_title="Sales Analysis Dashboard", layout="wide")
st.title("📊 Sales Analysis Dashboard")

try:
    # Read data
    data = pd.read_csv('data_pembelian.csv')
    
    # Process datetime
    data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], 
                                    format='%d/%m/%Y %I:%M:%S %p', 
                                    errors='coerce')
    
    # Extract components
    data['Date'] = data['DateTime'].dt.date
    data['Time'] = data['DateTime'].dt.time
    data['Hour'] = data['DateTime'].dt.hour
    data['Month'] = data['DateTime'].dt.strftime('%Y-%m')
    
    # Clean Amount column
    data['Amount'] = data['Amount'].astype(str).str.replace(',', '')
    data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_value=data["Date"].min(), max_value=data["Date"].max())
    with col2:
        end_date = st.date_input("End Date", min_value=start_date, max_value=data["Date"].max())
    
    # Filter data
    filtered_data = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]
    
    if not filtered_data.empty:
        # Summary metrics
        st.markdown("### 📈 Summary")
        total_amount = filtered_data['Amount'].sum()
        total_transactions = len(filtered_data)
        unique_users = filtered_data['Username'].nunique()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sales", f"SGD {total_amount:,.2f}")
        with col2:
            st.metric("Total Transactions", f"{total_transactions:,}")
        with col3:
            st.metric("Unique Users", f"{unique_users:,}")
        
        # Daily Analysis
        st.markdown("### 📅 Daily Sales")
        daily_sales = filtered_data.groupby('Date').agg({
            'Amount': ['sum', 'count'],
            'Username': 'nunique'
        })
        daily_sales.columns = ['Total Amount', 'Transactions', 'Unique Users']
        daily_sales['Total Amount'] = daily_sales['Total Amount'].apply(lambda x: f"SGD {x:,.2f}")
        st.dataframe(daily_sales, use_container_width=True)
        
        # Monthly Analysis
        st.markdown("### 📊 Monthly Summary")
        monthly_sales = filtered_data.groupby('Month').agg({
            'Amount': ['sum', 'count'],
            'Username': 'nunique'
        })
        monthly_sales.columns = ['Total Amount', 'Transactions', 'Unique Users']
        monthly_sales['Total Amount'] = monthly_sales['Total Amount'].apply(lambda x: f"SGD {x:,.2f}")
        st.dataframe(monthly_sales, use_container_width=True)
        
        # User Analysis
        st.markdown("### 👥 User Analysis")
        user_sales = filtered_data.groupby('Username').agg({
            'Amount': ['sum', 'count'],
            'Date': 'nunique'
        })
        user_sales.columns = ['Total Amount', 'Transactions', 'Active Days']
        user_sales['Total Amount'] = user_sales['Total Amount'].apply(lambda x: f"SGD {x:,.2f}")
        user_sales = user_sales.sort_values('Transactions', ascending=False)
        st.dataframe(user_sales, use_container_width=True)
        
        # Detailed Transactions
        st.markdown("### 📋 Transaction Details")
        detailed_view = filtered_data[['Unique Code', 'Username', 'Date', 'Time', 'Amount']]
        detailed_view['Amount'] = detailed_view['Amount'].apply(lambda x: f"SGD {x:,.2f}")
        st.dataframe(detailed_view, use_container_width=True)
        
        # Sales by Hour
        st.markdown("### 🕒 Sales by Hour")
        sales_by_hour = filtered_data.groupby('Hour').agg({'Amount': 'sum', 'Username': 'nunique'}).reset_index()
        
        sns.set_style("whitegrid")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=sales_by_hour['Hour'], y=sales_by_hour['Amount'], palette='coolwarm', edgecolor='black', ax=ax)
        
        ax.set_xlabel('Hour of the Day', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Sales (SGD)', fontsize=12, fontweight='bold')
        ax.set_title('Sales by Hour of the Day', fontsize=14, fontweight='bold')
        
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Sales in 3-hour Intervals
        st.markdown("### 📅 Sales in 3-Hour Intervals")
        filtered_data['3-Hour Interval'] = (filtered_data['Hour'] // 3) * 3  # Grouping by 3-hour blocks
        sales_3hour = filtered_data.groupby('3-Hour Interval').agg({'Amount': 'sum', 'Username': 'nunique'}).reset_index()
        sales_3hour['Interval Label'] = sales_3hour['3-Hour Interval'].apply(lambda x: f"{x:02}:00 - {x+3:02}:00")
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        sns.barplot(x=sales_3hour['Interval Label'], y=sales_3hour['Amount'], palette='autumn', edgecolor='black', ax=ax2)
        
        ax2.set_xlabel('3-Hour Interval', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Total Sales (SGD)', fontsize=12, fontweight='bold')
        ax2.set_title('Sales in 3-Hour Intervals', fontsize=14, fontweight='bold')
        
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    else:
        st.warning("No data available for selected date range")

except Exception as e:
    st.error(f"Error: {str(e)}")
