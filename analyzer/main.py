import boto3
import json
import os
import time
import numpy as np
from decimal import Decimal
from sklearn.ensemble import IsolationForest

# Configuration
QUEUE_URL = os.getenv("QUEUE_URL")
TABLE_NAME = os.getenv("TABLE_NAME", "LogAnomalies")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize AWS Clients
sqs = boto3.client('sqs', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

# ML Model State
log_history = []  # To store recent features for training
model = IsolationForest(contamination=0.1)  # Expect 10% anomalies
is_fitted = False

def extract_features(level, message):
    # Convert text data into numbers for the AI
    # Feature 1: Severity Score (Info=0, Warning=5, Error=10)
    level_score = 0
    if level == "WARNING": level_score = 5
    if level == "ERROR": level_score = 10
    
    # Feature 2: Message Length (Longer messages might be stack traces/crashes)
    msg_length = len(message)
    
    return [level_score, msg_length]

def process_message(message):
    global is_fitted
    
    try:
        body = json.loads(message['Body'])
        features = extract_features(body['level'], body['message'])
        
        # Add to history for training
        log_history.append(features)
        
        # Keep history small (last 50 logs)
        if len(log_history) > 50:
            log_history.pop(0)
            
        # Retrain model every 10 logs (Simulated "Online Learning")
        if len(log_history) >= 10 and len(log_history) % 5 == 0:
            print(f"Retraining ML Model on {len(log_history)} logs...")
            model.fit(log_history)
            is_fitted = True

        # AI Prediction
        anomaly_score = "PENDING"
        is_anomaly = False
        
        if is_fitted:
            # Predict: 1 = Normal, -1 = Anomaly
            prediction = model.predict([features])[0]
            if prediction == -1:
                is_anomaly = True
                anomaly_score = "ANOMALY DETECTED"
            else:
                anomaly_score = "NORMAL"

        # Save to DynamoDB
        item = {
            'service_id': body['service_id'],
            'timestamp': Decimal(str(body['timestamp'])), 
            'level': body['level'],
            'message': body['message'],
            'ai_tag': anomaly_score,
            'processed_at': Decimal(str(time.time()))
        }
        
        table.put_item(Item=item)
        
        icon = "🚨" if is_anomaly else "✅"
        print(f"{icon} SAVED: {body['level']} | AI Says: {anomaly_score}")

    except Exception as e:
        print(f"Error processing message: {e}")

def run():
    print("Analyzer Service Started (with ML Brain)...")
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=5
            )

            messages = response.get('Messages', [])
            
            if not messages:
                print("No messages... waiting.")
                continue

            for msg in messages:
                process_message(msg)
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=msg['ReceiptHandle']
                )

        except Exception as e:
            print(f"Crash loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()