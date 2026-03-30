import streamlit as st
import pandas as pd
import numpy as np

# App title
st.title("Air Quality Dashboard")

# Short description
st.write("This dashboard shows air pollution data from the UCI Air Quality dataset.")

# Load CSV file (semicolon separator and comma decimal format)
df = pd.read_csv("AirQualityUCI.csv", sep=";", decimal=",")

df = df.drop(columns=[col for col in df.columns if "Unnamed" in col]) #drop empty columns
df = df.dropna(how='all') #drop empty raws

df["Date"] = df["Date"].astype(str).str.strip()
df["Date"] = df["Date"].str.replace(".", "/", regex=False)
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce") # convert date to datetime format
df["Time"] = pd.to_datetime(df["Time"], format="%H.%M.%S", errors="coerce").dt.time

def convert_decimal_to_float(df): #convert object to float
    for col in df.columns:
        if col not in ["Date", "Time"]:
            df[col] = (df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
df = convert_decimal_to_float(df)

for col in df.select_dtypes(include=[np.number]).columns: # replace -200 with NaN
    df[col] = df[col].mask(df[col] == -200, np.nan)

# Interpolation to handle the missing values
df = df.interpolate(method="linear")

# Dropdown menu to select pollutant (interactive element)
pollutant = st.selectbox(
    "Select pollutant",
    ["CO(GT)", "NOx(GT)", "NO2(GT)", "C6H6(GT)"]
)

# Combine Date and Time into Datetime
df["Datetime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Time"].astype(str))

# Date range filter (interactive)
start_date = st.date_input("Start date", df["Date"].min())
end_date = st.date_input("End date", df["Date"].max())

# Filter by selected date range
filtered_df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
]

# Keep only selected pollutant
filtered_df = filtered_df[["Datetime", pollutant]].dropna()

# Line chart
st.subheader("Pollution Over Time")
st.line_chart(filtered_df.set_index("Datetime"))

# Bar chart (average values)
st.subheader("Average Pollution Levels")
avg_values = df[["CO(GT)", "NOx(GT)", "NO2(GT)", "C6H6(GT)"]].mean()
st.bar_chart(avg_values)

# Show raw data
if st.checkbox("Show raw data"):
    st.write(filtered_df.head())

# Footer
st.write("Dataset: UCI Air Quality (processed)")