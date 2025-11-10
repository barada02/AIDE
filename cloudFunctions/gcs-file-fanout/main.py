import json
import os
from google.cloud import pubsub_v1
from google.cloud import tasks_v2
from dotenv import load_dotenv

# --- ⚠️ REQUIRED THESE 4 VARIABLES ---
load_dotenv()  # load variables from a .env file in the working directory

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION_ID = os.getenv("LOCATION_ID", "us-central1")
QUEUE_ID = os.getenv("QUEUE_ID", "aide-job-queue")
MANAGER_URL = os.getenv("MANAGER_URL")

if not PROJECT_ID or not MANAGER_URL:
    raise EnvironmentError("Missing required env vars: PROJECT_ID and/or MANAGER_URL. Add them to your .env or environment.")
# ------------------------------------

# Initialize clients globally
pubsub_publisher = pubsub_v1.PublisherClient()
tasks_client = tasks_v2.CloudTasksClient()

# Build the full paths
topic_path = pubsub_publisher.topic_path(PROJECT_ID, "ui-notifications")
queue_path = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, QUEUE_ID)

def fan_out_to_services(event, context):
    """
    Triggered by GCS. Fans out to Pub/Sub (for UI) 
    and Cloud Tasks (for the Manager Agent).
    """

    # 1. Get the file data from the GCS event
    file_data = {
        "bucket": event['bucket'],
        "name": event['name']
    }
    print(f"Received file: {file_data['name']}")

    # --- TASK A: Publish to Pub/Sub for the UI ---
    try:
        ui_message = {"file_name": file_data['name'], "status": "PENDING"}
        data = json.dumps(ui_message).encode('utf-8')
        future = pubsub_publisher.publish(topic_path, data)
        print(f"Published to Pub/Sub: {future.result()}")

    except Exception as e:
        print(f"Error publishing to Pub/Sub: {e}")

    # --- TASK B: Create Task for the Manager Agent ---
    try:
        # Create the HTTP request for the task
        task = {
            "http_request": {
                "http_method": "POST",
                "url": MANAGER_URL,  # The endpoint on your Manager
                "body": json.dumps(file_data).encode('utf-8'),
                "headers": {"Content-Type": "application/json"},
            }
        }

        response = tasks_client.create_task(parent=queue_path, task=task)
        print(f"Created Cloud Task: {response.name}")

    except Exception as e:
        print(f"Error creating Cloud Task: {e}")

    return 'OK', 200