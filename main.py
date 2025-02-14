import streamlit as st
import pandas as pd
from datetime import datetime

df = pd.read_csv('Input_Sales_Data_v2.csv')
df.drop('Unnamed: 0', axis = 1, inplace = True)
df["Date"] = pd.to_datetime(df["Date"]).dt.date
#print(df.dtypes)
max_date, min_date = df["Date"].max(), df["Date"].min()

st.logo("favicon-Tiger-Analytics_.webp")
st.title("Sales Dashboard")
st.subheader("Welcome to the test dashboard")

date_range = st.slider(
    'Select the date range',
    min_value=min_date,
    max_value=max_date,
    value=(min_date,max_date),
    format="YYYY-MM-DD"
    )

filtered_df = df[(df["Date"] >= date_range[0]) & (df["Date"] <= date_range[1])]

grouped_df = filtered_df.groupby(by = 'Manufacturer')[['Volume','Value']].sum().reset_index()

top_5_manf = grouped_df.nlargest(5,"Value")
top_5_manufacturers = list(top_5_manf['Manufacturer'])

top_manf_data = filtered_df[filtered_df['Manufacturer'].isin(top_5_manufacturers)]
top_manf_data = top_manf_data.groupby(by = ['Manufacturer','Date'])['Value'].sum().reset_index()
#st.write(top_5_manufacturers)
#print(filtered_df.head(5))
st.dataframe(grouped_df)
#st.dataframe(top_manf_data)
st.line_chart(data = top_manf_data, x = 'Date', y = 'Value', color = 'Manufacturer')