# Layer 1 - Data Preparation (Stage 1 Implementation)

## part 1: 

### Step 1: Create the Cloud Storage Bucket

```powershell
# Replace [YOUR_UNIQUE_SUFFIX] with your chosen identifier
$BUCKET_NAME = "aidelab-raw-uploads-mvp01"
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


