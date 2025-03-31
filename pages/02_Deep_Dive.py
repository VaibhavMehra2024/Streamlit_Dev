import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/home/vaibhav/streamlit_dev/Input_Sales_Data_v2.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)
df["Date"] = pd.to_datetime(df["Date"])

# Set the title at the top
st.title("Sales Dashboard")

# Create three separate columns for selectboxes
col1, col2, col3 = st.columns(3)

with col1:
    category_drop = st.selectbox("Select Category", df['Category'].unique())

filtered_category = df[df['Category'] == category_drop]

with col2:
    manufacturer_drop = st.selectbox("Select Manufacturer", filtered_category['Manufacturer'].unique())

filtered_category_manufacturer = filtered_category[filtered_category['Manufacturer'] == manufacturer_drop]

with col3:
    brand_drop = st.selectbox("Select Brand", filtered_category_manufacturer['Brand'].unique())

filtered_df = filtered_category_manufacturer[filtered_category_manufacturer['Brand'] == brand_drop]


ytd_volume_sales = filtered_df['Volume'].sum()
ytd_sales = filtered_df['Value'].sum()
total_sales = df['Value'].sum()
ytd_market_share = (ytd_sales / total_sales) * 100
count_of_skus = filtered_df['SKU Name'].nunique()


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(label="YTD Volume Sales", value=f"{ytd_volume_sales:,}")

with col2:
    st.metric(label="YTD Sales", value=f"${ytd_sales:,}")

with col3:
    st.metric(label="YTD Market Share", value=f"{ytd_market_share:.2f}%")

with col4:
    st.metric(label="Count of SKUs", value=f"{count_of_skus}")

df_weekly = filtered_df.groupby(pd.Grouper(key='Date', freq='W')).agg({
    'Value': 'sum',
    'Volume': 'sum',
    'Price': 'sum'
}).reset_index()


with st.container():

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots(figsize=(8, 6))

        ax1.plot(df_weekly['Date'], df_weekly['Value'], label='Weekly Sales', color='blue', marker='o')
        ax1.set_xlabel('Week')
        ax1.set_ylabel('Sales')
        ax1.set_title('Weekly Sales and Volume')

        ax2 = ax1.twinx()  # create secondary axis
        ax2.plot(df_weekly['Date'], df_weekly['Volume'], label='Weekly Volume', color='green', marker='o')
        ax2.set_ylabel('Volume')

        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        st.pyplot(fig1)

    # Graph 2: Pie chart showing % of value sales for the top 10 SKU
    with col2:
        # Top 10 SKU by Sales
        top_skus = filtered_df.groupby('SKU Name').agg({'Value': 'sum'}).sort_values(by='Value', ascending=False).head(10)

        # Plotting pie chart using Matplotlib
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.set_aspect('equal')
        ax2.pie(top_skus['Value'], labels=top_skus.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax2.set_title(f"Top 10 SKU Value Share for {brand_drop}")
        fig2.tight_layout()
        st.pyplot(fig2)
    
    with col3:
        fig3, ax3 = plt.subplots(figsize=(6, 6))  # Fixed size for the graph
        df_monthly = df_weekly.resample('M', on='Date').sum()  # Aggregating to monthly data
        ax3.plot(df_monthly.index, df_monthly['Value'], label='Value Sales (Monthly)', color='blue', marker='o')  # Updated column name
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Value')
        ax3.set_title('Value and Volume Trend (Monthly Aggregated)')

        ax4 = ax3.twinx()  # Create secondary y-axis
        ax4.plot(df_monthly.index, df_monthly['Volume'], label='Volume (Monthly)', color='green', marker='o')  # Updated column name
        ax4.set_ylabel('Volume')

        ax3.legend(loc='upper left')
        ax4.legend(loc='upper right')

        st.pyplot(fig3)

    # Graph 4: Aggregated monthly dollar value and volume on primary and secondary axes (NOT weekly level)
    with col4:
        fig4, ax4 = plt.subplots(figsize=(6, 6))  # Fixed size for the graph
        df_monthly = df_weekly.resample('M', on='Date').sum()  # Aggregating to monthly data
        ax4.plot(df_monthly.index, df_monthly['Price'], label='Prices (Monthly)', color='orange', marker='o')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Price Value')
        ax4.set_title('Price and Volume Trend (Monthly Aggregated)')

        ax5 = ax4.twinx()  # Create secondary y-axis for volume
        ax5.plot(df_monthly.index, df_monthly['Volume'], label='Volume (Monthly)', color='red', marker='o')  # Updated column name
        ax5.set_ylabel('Volume')

        ax4.legend(loc='upper left')
        ax5.legend(loc='upper right')

        st.pyplot(fig4)

sku_names = st.multiselect("Select SKU(s) to Filter", df['SKU Name'].unique())

# Filter data based on selected SKUs
if sku_names:
    filtered_skus = df[df['SKU Name'].isin(sku_names)]
else:
    filtered_skus = df

# Side-by-Side Charts Container
with st.container():
    col1, col2 = st.columns(2)

    # 1️⃣ Weekly Volume & Sales Line Chart
    with col1:
        fig, ax1 = plt.subplots(figsize=(8, 6))

        # Weekly aggregation for selected SKUs
        df_weekly = filtered_skus.groupby(pd.Grouper(key='Date', freq='W')).agg({
            'Volume': 'sum',
            'Value': 'sum'
        }).reset_index()

        # Plotting Volume
        ax1.plot(df_weekly['Date'], df_weekly['Volume'], color='blue', marker='o', label='Volume')
        ax1.set_xlabel('Week')
        ax1.set_ylabel('Volume', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        # Secondary Y-axis for Sales
        ax2 = ax1.twinx()
        ax2.plot(df_weekly['Date'], df_weekly['Value'], color='green', marker='o', label='Sales')
        ax2.set_ylabel('Sales ($)', color='green')
        ax2.tick_params(axis='y', labelcolor='green')

        plt.title('Weekly Volume and Sales Trend for Selected SKUs')
        fig.tight_layout()

        st.pyplot(fig)

    # 2️⃣ Monthly Average Price Bar Chart
    with col2:
        fig2, ax3 = plt.subplots(figsize=(8, 6))

        # Monthly average price for selected SKUs
        df_monthly = filtered_skus.resample('M', on='Date').agg({'Price': 'mean'}).reset_index()

        # Bar plot for average price
        ax3.bar(df_monthly['Date'], df_monthly['Price'], color='orange', width=20)

        # Formatting
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Average Price ($)')
        ax3.set_title('Average Dollar Value (Price) per Month for Selected SKUs')
        ax3.tick_params(axis='x', rotation=45)

        st.pyplot(fig2)
