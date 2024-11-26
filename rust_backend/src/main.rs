/*
* This application polls the Solana mainnet for recent performance samples,
* calculates transactions per second (TPS) from the data received,
* and inserts the calculated TPS along with other data into an InfluxDB database.
* 
* Author: Amil Shrivastava
*/

use chrono::{DateTime, Utc};
use influxdb::{Client as InfluxClient, InfluxDbWriteable};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use tokio::time::{sleep, Duration};

// Structure representing the response from the Solana RPC API
#[derive(Debug, Deserialize, Serialize)]
struct PerformanceSampleResponse {
    result: Vec<PerformanceSample>, // A vector of performance samples
}

// Structure representing a single performance sample
#[derive(Debug, Deserialize, Serialize, Clone)]
struct PerformanceSample {
    #[allow(non_snake_case)]
    numTransactions: u64, // Total number of transactions in the sample

    #[allow(non_snake_case)]
    samplePeriodSecs: u64, // Duration of the sample in seconds
    slot: u64,             // Slot number of the sample
}

// Structure for transaction statistics to be inserted into InfluxDB
#[derive(InfluxDbWriteable, Debug)]
struct TransactionStats {
    time: DateTime<Utc>,       // Timestamp for the data point
    num_transactions: u64,     // Total transactions in the sample
    sample_period_secs: u64,   // Duration of the sample in seconds
    tps: f64,                  // Calculated transactions per second (TPS)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Delay the start to ensure dependent services (like InfluxDB) are up
    sleep(Duration::from_secs(8)).await;
    println!("Data is now being sent to the DB......=)");

    // Initialize the InfluxDB client
    let influx_client = InfluxClient::new("http://influxdb:8086", "solana_TPS")
        .with_token("ULTRA_SECURE_KEY_THAT_NOBODY_CAN_HACK");

    // Main loop: fetch performance data and insert it into InfluxDB every second
    loop {
        // Fetch recent performance samples from the Solana RPC API
        match get_recent_performance_samples().await {
            Ok(sample) => {
                // Calculate transactions per second (TPS) from the sample
                let tps = calculate_tps(sample.numTransactions, sample.samplePeriodSecs);

                // Prepare the data to be sent to InfluxDB
                let transaction_stats = TransactionStats {
                    time: Utc::now(), // Use the current UTC time as the data point timestamp
                    num_transactions: sample.numTransactions,
                    sample_period_secs: sample.samplePeriodSecs,
                    tps,
                };

                // Insert the data into InfluxDB
                influx_client
                    .query(transaction_stats.into_query("transaction_stats"))
                    .await?; // Handle any errors in insertion
            }
            Err(e) => {
                // Log an error message if the performance sample fetch fails
                println!("Error fetching performance samples: {}", e);
            }
        }

        // Wait for 1 second before fetching data again
        sleep(Duration::from_secs(1)).await;
    }
}

// Fetch recent performance samples from the Solana RPC API
async fn get_recent_performance_samples() -> Result<PerformanceSample, Box<dyn std::error::Error>> {
    let rpc_url = "https://api.mainnet-beta.solana.com"; // Solana RPC endpoint
    let client = Client::new(); // HTTP client for making API requests

    // JSON-RPC payload to request recent performance samples
    let request = json!( {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getRecentPerformanceSamples",
        "params": [1] // Request one recent sample
    });

    // Send the request to the RPC endpoint and parse the response
    let response = client
        .post(rpc_url)
        .json(&request)
        .send()
        .await? // Send the HTTP POST request
        .json::<PerformanceSampleResponse>() // Parse JSON response into our struct
        .await?;

    // Extract the first sample from the response (if available)
    if let Some(sample) = response.result.get(0) {
        Ok(sample.clone()) // Return the sample
    } else {
        // Return an error if no samples are found
        Err("No performance sample data found".into())
    }
}

// Calculate transactions per second (TPS) from a performance sample
fn calculate_tps(num_transactions: u64, sample_period_secs: u64) -> f64 {
    if sample_period_secs == 0 {
        0.0 // Avoid division by zero
    } else {
        num_transactions as f64 / sample_period_secs as f64 // Calculate TPS
    }
}
