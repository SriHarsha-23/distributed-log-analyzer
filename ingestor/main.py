from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import boto3
import json
import os
import time

app = FastAPI()

# Get settings from Docker Environment Variables
QUEUE_URL = os.getenv("QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize AWS SQS Client
sqs = boto3.client(
    'sqs',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

class LogEntry(BaseModel):
    timestamp: float
    level: str
    message: str
    service_id: str

@app.post("/logs")
async def receive_log(entry: LogEntry):
    # Convert the log entry to JSON
    message_body = json.dumps(entry.dict())
    
    try:
        # Send to AWS SQS
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=message_body
        )
        print(f"SENT TO SQS: {entry.level} | ID: {response['MessageId']}")
        return {"status": "queued", "sqs_id": response['MessageId']}
    except Exception as e:
        print(f"FAILED to send to SQS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)