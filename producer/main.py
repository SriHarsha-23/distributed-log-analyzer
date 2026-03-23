import time
import random
import requests
import json
import os

# Where are we sending logs? 
# In Docker, 'ingestor' is the hostname of the other container
API_URL = os.getenv("API_URL", "http://localhost:8000/logs")

log_levels = ["INFO", "WARNING", "ERROR"]
messages = [
    "User logged in",
    "Database connection timeout",
    "Payment processed",
    "File not found",
    "Service started"
]

def generate_log():
    return {
        "timestamp": time.time(),
        "level": random.choice(log_levels),
        "message": random.choice(messages),
        "service_id": "payment-service-01"
    }

if __name__ == "__main__":
    print("Starting Log Producer...")
    while True:
        log_data = generate_log()
        try:
            response = requests.post(API_URL, json=log_data)
            print(f"Sent: {log_data['level']} | Status: {response.status_code}")
        except Exception as e:
            print(f"Connection Failed: {e}")
        
        # Wait randomly between 1 to 3 seconds
        time.sleep(random.uniform(1, 3))