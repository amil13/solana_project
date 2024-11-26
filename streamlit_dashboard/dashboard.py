"""
dashboard.py

This script initializes and implements the Streamlit dashboard to display
real-time transaction per second (TPS) data from the Solana blockchain 
which is stored in an influxdb bucket.

Author: Amil Shrivastava
"""

import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import plotly.express as px
import time
import os

# ---- Environment Variables for Configuration ----
# These values are pulled from the environment variables set in your Docker setup.
INFLUX_URL = os.getenv("INFLUXDB_URL")  # URL for InfluxDB
INFLUX_TOKEN = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")  # Admin token for authentication
INFLUX_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG")  # Organization name in InfluxDB
INFLUX_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")  # Bucket name in InfluxDB

# ---- Global Variables ----
KEY_COUNTER = 0  # Counter to provide unique keys for Streamlit charts

# ---- Initialize InfluxDB Client ----
# The client is used to query data from the InfluxDB database.
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()


def fetch_data():
    """
    Fetch data from the InfluxDB bucket using Flux queries.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the following columns:
            - time: Timestamp of the record.
            - Number of Transactions: Total number of transactions.
            - Sample Period in Seconds: Time interval of the sample.
            - Transactions per Seconds: Calculated TPS values.
    """
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -5m)  // Fetch data from the last 5 minutes
        |> filter(fn: (r) => r["_measurement"] == "transaction_stats")
        |> filter(fn: (r) => r["_field"] == "num_transactions" or r["_field"] == "sample_period_secs" or r["_field"] == "tps")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> limit(n: 300)  // Limit to 300 records
    '''
    try:
        # Execute the query and process the results into a DataFrame
        result = query_api.query(org=INFLUX_ORG, query=query)
        records = [
            {
                "time": record.get_time(),
                "Number of Transactions": record.values.get("num_transactions"),
                "Sample Period in Seconds": record.values.get("sample_period_secs"),
                "Transactions per Seconds": record.values.get("tps")
            }
            for table in result for record in table.records
        ]
        return pd.DataFrame(records)
    except Exception as e:
        # Display an error message in the Streamlit UI
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def setup_streamlit():
    """
    Set up the Streamlit UI elements.
    """
    # Title and description
    st.title("Solana Blockchain TPS Dashboard")
    st.write("Real-time display of transactions per second (TPS) on the Solana blockchain.")
    st.write("By Amil Shrivastava")


def setup_charts(data, key):
    """
    Render line charts and display the data in a tabular format.

    Args:
        data (pd.DataFrame): The data to be visualized.
        key (int): A unique key for each chart to prevent caching issues.
    """
    # Line chart for Transactions Per Second
    fig = px.line(
        data,
        x="time",
        y="Transactions per Seconds",
        title="Real-Time Transactions Per Second",
        labels={"time": "Time (Seconds)", "tps": "Transactions Per Second"}
    )
    # Calculate the max value of the y-axis based on your data (you can also set it to a fixed value)
    max_tps = data["Transactions per Seconds"].max() if not data.empty else 1  # Set a minimum max if data is empty

    fig.update_layout(
        xaxis=dict(title="Time"),
        yaxis=dict(title="Transactions/Sec", tickformat=",",range=[1000, max_tps * 1.7]),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"{key}_key")

    # Display the raw data as a table
    st.write("### Transactions Data")
    st.dataframe(data.iloc[::-1], use_container_width=True)

def main():
    """
    Main function to initialize and run the Streamlit dashboard.

    Polls data from InfluxDB every second and updates the dashboard in real-time.
    """
    # Set up the Streamlit UI
    setup_streamlit()
    key = 0  # Initialize the unique key counter
    placeholder = st.empty()  # Placeholder for dynamic content

    # Continuous loop to fetch and update data
    while True:
        # Fetch data from InfluxDB
        data = fetch_data()

        if not data.empty:
            # Increment the unique key and update the dashboard with new data
            key += 1
            with placeholder.container():
                setup_charts(data, key)
        else:
            # Display a spinner if no data is available
            with st.spinner("No data available. Waiting for new data..."):
                time.sleep(5)

        # Refresh the data every second
        time.sleep(1)


# ---- Boilerplate to Run the Script ----
if __name__ == "__main__":
    # Configure the Streamlit app layout and title
    st.set_page_config(page_title="Solana Blockchain Dashboard", layout="wide")
    main()
