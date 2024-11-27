
# Solana Project - Real-Time TPS Tracking Dashboard

**Author:** Amil Shrivastava

## Introduction

The **Solana Project** demonstrates a real-time **Transactions Per Second (TPS)** dashboard for the **Solana blockchain**. This project leverages the following technologies:

- **Rust Backend**: Fetches real-time data from the **Solana blockchain** and stores it in **InfluxDB** for time-series data management.
- **InfluxDB**: A high-performance time-series database used to store Solana transaction data.
- **Streamlit**: A Python-based framework used to build interactive visualizations of the **TPS** and other key metrics.

This dashboard provides real-time insights into the Solana blockchain’s performance, helping users track and analyze transaction throughput and other relevant metrics. It is an example of integrating **Rust**, **Python**, and **InfluxDB** to build an efficient real-time data pipeline and visualization tool. *Additionally, it serves as a demonstration of my proficiency with these technologies.*

## Prerequisites

Before running the project, ensure the following tools are installed:

- **Docker**
- **Python 3.10 or above** - for running the run_project.py script
  
## How to Run

1. Clone the repository to your local machine.
2. Navigate to the `solana_project` directory.
3. Run the following command to start the project:

   ```bash
   python .\run_project.py
   ```

## To Stop and Clean

To stop all services and clean up the containers, run:

```bash
docker-compose down
```
