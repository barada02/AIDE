# Layer 1 - Data Preparation (Stage 1 Implementation)

## part 1: 

### Step 1: Create the Cloud Storage Bucket

```powershell
# Replace [YOUR_UNIQUE_SUFFIX] with your chosen identifier
$BUCKET_NAME ="aidelab-raw-uploads-mvp01"
$REGION = "us-central1"

gcloud storage buckets create gs://$BUCKET_NAME `
    --location=$REGION `
    --default-storage-class=STANDARD `
    --uniform-bucket-level-access
```
### step 2: cloud task queue setup

```powershell
gcloud tasks queues create aide-job-queue `
  --location=us-central1 `
  --max-dispatches-per-second=10 `
  --max-concurrent-dispatches=20
```
### Step 3: Create the Pub/Sub Topic

```powershell
$TOPIC_NAME="aide-file-fanout-topic"
gcloud pubsub topics create ${TOPIC_NAME}
```
### Step 4: Deploy the Cloud Function


# Set your variables first (replace YOUR_BUCKET_NAME)
```powershell
$FUNCTION_NAME="gcs-file-fanout"
$BUCKET_NAME ="aidelab-raw-uploads-mvp01"
$REGION="us-central1" 
$ENTRY_POINT = "fan_out_to_services"

$GOOGLE_CLOUD_PROJECT="social-463809"
$GOOGLE_CLOUD_LOCATION="us-central1"
$MANAGER_AGENT_URL="https://manager-agent-797563351214.us-central1.run.app/process"
$PUBSUB_TOPIC="aide-file-fanout-topic"
$TASK_QUEUE_ID="aide-job-queue"

gcloud functions deploy ${FUNCTION_NAME} `
    --gen2 `
    --runtime python311 `
    --region ${REGION} `
    --source . `
    --entry-point ${ENTRY_POINT} `
    --trigger-bucket ${BUCKET_NAME} `
    --trigger-event google.cloud.storage.object.v1.finalized `
    --set-env-vars GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},MANAGER_AGENT_URL=${MANAGER_AGENT_URL},PUBSUB_TOPIC=${PUBSUB_TOPIC},TASK_QUEUE_ID=${TASK_QUEUE_ID} 
```