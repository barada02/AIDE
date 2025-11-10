import os
import json
import functions_framework
from google.cloud import pubsub_v1
from google.cloud import tasks_v2



# --- 1. LOAD ALL CONFIG FROM ENVIRONMENT VARIABLES ---
# These must be set when you deploy the function (using your new names)
GCP_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION_ID = os.environ.get("GOOGLE_CLOUD_LOCATION")
MANAGER_URL = os.environ.get("MANAGER_AGENT_URL")
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC")   
TASK_QUEUE_ID = os.environ.get("TASK_QUEUE_ID") 

# Check for missing environment variables for a clearer error
REQUIRED_VARS = {
    "GOOGLE_CLOUD_PROJECT": GCP_PROJECT_ID,
    "GOOGLE_CLOUD_LOCATION": LOCATION_ID,
    "MANAGER_AGENT_URL": MANAGER_URL,
    "PUBSUB_TOPIC": PUBSUB_TOPIC,
    "TASK_QUEUE_ID": TASK_QUEUE_ID
}

if not all(REQUIRED_VARS.values()):
    missing = [k for k, v in REQUIRED_VARS.items() if v is None]
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# --- 2. INITIALIZE CLIENTS (GLOBAL SCOPE) ---
pubsub_publisher = pubsub_v1.PublisherClient()
tasks_client = tasks_v2.CloudTasksClient()

# Build the full resource paths
topic_path = pubsub_publisher.topic_path(GCP_PROJECT_ID, PUBSUB_TOPIC)
queue_path = tasks_client.queue_path(GCP_PROJECT_ID, LOCATION_ID, TASK_QUEUE_ID)


# --- 3. HELPER FUNCTION ---
def extract_pid_from_path(file_path):
    """Extracts the Project ID (the first directory prefix) from the GCS file path."""
    if file_path:
        parts = file_path.split('/')
        if len(parts) > 1:
            return parts[0]  # Returns the first segment (e.g., 'PID-1234')
    return None

# --- 4. THE CLOUD FUNCTION (GCS TRIGGER) ---
@functions_framework.cloud_event
def fan_out_to_services(cloud_event):
    """
    Triggered by GCS file upload.
    Fans out a UNIFIED payload to Pub/Sub (for UI) and Cloud Tasks (for Manager).
    """
    # 1. Get file data from the GCS event
    data = cloud_event.data
    bucket_name = data['bucket']
    file_name = data['name']
    
    if not file_name:
        print("No file name in event. Skipping.")
        return 'OK', 200

    print(f"Received file: {file_name} in bucket: {bucket_name}")

    # 2. Extract the End-User Project ID
    end_user_pid = extract_pid_from_path(file_name)
    
    if not end_user_pid:
        print(f"Error: File '{file_name}' is not in an end-user project folder. Skipping.")
        return 'OK', 200
        
    print(f"Extracted End-User PID: {end_user_pid}")

    # 3. Create GCS URI
    gcs_uri = f"gs://{bucket_name}/{file_name}"

    # 4. Create the UNIFIED Message Payload (Your new format)
    message_payload = {
        "project_id": end_user_pid,
        "gcs_uri": gcs_uri,
        "source_file_path": file_name,
        "event_type": "google.storage.object.finalize"
    }
    
    # Serialize the payload ONCE
    data_payload = json.dumps(message_payload).encode('utf-8')
    print(f"Unified payload created: {data_payload.decode()}")

    # --- TASK A: PUBLISH TO PUBSUB ---
    try:
        future = pubsub_publisher.publish(topic_path, data=data_payload)
        print(f"Published to Pub/Sub topic {PUBSUB_TOPIC}: {future.result()}")
        
    except Exception as e:
        print(f"CRITICAL: Failed to publish to Pub/Sub: {e}")
        # We still continue, to ensure the job gets created.

    # --- TASK B: CREATE CLOUD TASK ---
    try:
        task = {
            "http_request": {
                "http_method": "POST",
                "url": MANAGER_URL,  # The endpoint on your Manager
                "body": data_payload, # Send the same payload
                "headers": {"Content-Type": "application/json"},
            }
        }
        
        response = tasks_client.create_task(parent=queue_path, task=task)
        print(f"Created Cloud Task for Manager: {response.name}")
        
    except Exception as e:
        print(f"CRITICAL: Failed to create Cloud Task: {e}")
        # This is a critical failure, so we must raise it to force a retry.
        raise e

    return 'OK', 200