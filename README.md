# Distributed Log Analyzer with AI Anomaly Detection

A fault-tolerant microservices pipeline designed to process system logs and detect anomalies in real-time without data loss during traffic spikes.

## Architecture Overview

This system decouples log generation from processing using a message queue, ensuring high availability and backpressure management. It consists of three core microservices containerized with Docker:

* **Producer:** Generates simulated system logs at varying volumes to mimic real-world traffic.
* **Ingestor:** Acts as the API gateway, receiving logs from the producer and pushing them securely into an AWS SQS queue.
* **Analyzer:** A background worker that continuously polls AWS SQS for new logs. It runs the data through an Isolation Forest (Machine Learning) model to autonomously detect system errors and anomalies, bypassing the need for manual, static monitoring rules.

## Tech Stack
* **Languages & Frameworks:** Python
* **Infrastructure:** Docker, Docker Compose
* **Cloud (AWS):** SQS (Message Queuing), DynamoDB (Storage)
* **Machine Learning:** Scikit-Learn (Isolation Forest)

## How to Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/SriHarsha-23/distributed-log-analyzer.git](https://github.com/SriHarsha-23/distributed-log-analyzer.git)