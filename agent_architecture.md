# AIDE Multi-Agent System Architecture

## Overview
This document outlines the complete multi-agent architecture for AIDE (Autonomous Intelligent Data Engine), designed as a two-layer system: **Data Preparation Layer** and **Analysis & Presentation Layer**.

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 AIDE SYSTEM                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  UI Layer (Upload Interface) → Cloud Storage → Cloud Function (Trigger)            │
│                                      ↓                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┤
│  │                    LAYER 1: DATA PREPARATION AGENTS                            │
│  │  PubSub Topic: "file-uploaded" → Coordinator Agent → Specialized Agents        │
│  └─────────────────────────────────────────────────────────────────────────────────┤
│                                      ↓                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┤
│  │                   LAYER 2: ANALYSIS & PRESENTATION AGENTS                      │
│  │  PubSub Topic: "data-ready" → Lead Analysis Agent → Dashboard & Q&A Agents     │
│  └─────────────────────────────────────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow & Agent Interactions

### Phase 1: File Upload & Trigger
1. **User uploads files** via UI → Cloud Storage
2. **Cloud Function triggers** on finalized upload → Publishes to `file-uploaded` topic
3. **Message payload**: `{project_id, file_path, file_type, metadata}`

### Phase 2: Data Preparation Layer
4. **Coordinator Agent** receives PubSub message → Routes to appropriate specialist
5. **Specialist Agents** process files → Store data & generate reports
6. **Final trigger** → Publishes to `data-ready` topic

### Phase 3: Analysis & Presentation Layer  
7. **Lead Analysis Agent** analyzes all file reports → Plans analysis strategy
8. **Analysis Agents** execute data exploration → Generate insights
9. **Presentation Agents** create dashboards & enable Q&A

---

## 🤖 Agent System Design

### **LAYER 1: DATA PREPARATION AGENTS**

#### 1. **Coordinator Agent** (Cloud Run Service)
- **Role**: Traffic controller and orchestrator
- **Deployment**: Cloud Run service with PubSub trigger endpoint
- **Responsibilities**:
  - Receives `file-uploaded` messages
  - Determines file type and routing strategy
  - Orchestrates sequential/parallel processing
  - Manages project state in Firestore
  - Tracks completion status across all files

```python
# Message Flow Example
{
  "project_id": "proj_12345",
  "files": [
    {"path": "gs://bucket/proj_12345/sales_data.csv", "type": "csv"},
    {"path": "gs://bucket/proj_12345/user_manual.pdf", "type": "pdf"},
    {"path": "gs://bucket/proj_12345/logs.txt", "type": "text"}
  ],
  "status": "processing"
}
```

#### 2. **CSV/Excel Processing Agent** (Cloud Run Service)
- **Role**: Structured data specialist
- **Deployment**: Cloud Run service (called by Coordinator)
- **Tools Available**:
  - Sandbox service (code execution)
  - BigQuery client
  - Data validation libraries
- **Process**:
  1. Load file from Cloud Storage
  2. Perform data cleaning (handle nulls, types, duplicates)
  3. Generate data quality report
  4. Store cleaned data in BigQuery (table: `proj_12345_filename`)
  5. Create metadata report in Firestore

#### 3. **PDF Processing Agent** (Cloud Run Service)
- **Role**: Document specialist
- **Deployment**: Cloud Run service
- **Tools Available**:
  - Document AI API
  - Text extraction libraries
  - Sandbox service
- **Process**:
  1. Extract text and structure from PDF
  2. Identify key sections and data types
  3. Store extracted content in appropriate format
  4. Generate document summary report
  5. Create metadata report in Firestore

#### 4. **Generic File Processing Agent** (Cloud Run Service)
- **Role**: Catch-all processor for other file types
- **Handles**: Text files, logs, JSON, XML, etc.
- **Process**: Similar to PDF agent but with appropriate parsers

### **LAYER 2: ANALYSIS & PRESENTATION AGENTS**

#### 1. **Lead Analysis Agent** (Cloud Run Service)
- **Role**: Strategic analyst and planning coordinator
- **Triggered by**: PubSub message on `data-ready` topic
- **Responsibilities**:
  - Read all file reports from Firestore
  - Analyze data relationships and potential insights
  - Create analysis strategy (what charts, what questions to explore)
  - Orchestrate analysis execution across specialist agents
  - Coordinate final dashboard assembly

#### 2. **Exploratory Data Analysis (EDA) Agent** (Cloud Run Job)
- **Role**: Data exploration specialist
- **Deployment**: Cloud Run Job (for heavy computation)
- **Tools Available**:
  - Sandbox service (pandas, matplotlib, seaborn)
  - BigQuery client
  - Statistical analysis libraries
- **Process**:
  1. Generate descriptive statistics
  2. Create visualizations (histograms, scatter plots, correlation matrices)
  3. Identify patterns and anomalies
  4. Store results and charts in Cloud Storage

#### 3. **Dashboard Generation Agent** (Cloud Run Service)
- **Role**: Visualization specialist
- **Responsibilities**:
  - Combine EDA results into cohesive dashboard
  - Generate interactive charts using Plotly/similar
  - Create executive summary
  - Store dashboard artifacts in Cloud Storage

#### 4. **Q&A Agent** (Cloud Run Service)
- **Role**: Natural language interface
- **Tools Available**:
  - Vertex AI/Gemini for NL processing
  - BigQuery for SQL generation
  - Sandbox service for query execution
- **Capabilities**:
  - Understand natural language questions
  - Generate appropriate SQL queries
  - Execute queries and format responses
  - Maintain conversation context

---

## 🛠️ Technical Implementation Details

### **Agent Deployment Patterns**

#### Pattern 1: Service Agents (Always Running)
```yaml
# Cloud Run Service Configuration
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: coordinator-agent
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/project/coordinator-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: PROJECT_ID
          value: "your-project-id"
        - name: PUBSUB_SUBSCRIPTION
          value: "file-uploaded-sub"
```

#### Pattern 2: Job Agents (On-Demand Execution)
```python
# Deploy analysis job programmatically
def trigger_analysis_job(project_id: str, analysis_type: str):
    """Deploy Cloud Run Job with specific configuration"""
    job_name = f"eda-agent-{project_id}"
    
    # Override environment variables for job-specific config
    env_vars = {
        "PROJECT_ID": project_id,
        "ANALYSIS_TYPE": analysis_type,
        "DATA_SOURCE": f"project.dataset.{project_id}_*"
    }
    
    # Deploy and execute job
    deploy_cloud_run_job(job_name, env_vars)
```

### **Communication & State Management**

#### PubSub Topics Structure
```
Topics:
├── file-uploaded          # Triggers Layer 1
├── data-ready            # Triggers Layer 2  
├── analysis-complete     # Internal coordination
└── error-notifications   # Error handling
```

#### Firestore Data Structure
```javascript
// Project State Document
{
  "projects": {
    "proj_12345": {
      "status": "processing",
      "files": {
        "sales_data.csv": {
          "status": "completed",
          "table_name": "proj_12345_sales_data",
          "report": {
            "rows": 10000,
            "columns": 15,
            "description": "Customer sales transaction data",
            "semantic_info": "Contains purchase history, customer demographics",
            "data_quality": "Good - 2% missing values in optional fields"
          }
        }
      },
      "analysis": {
        "status": "in_progress",
        "dashboard_url": "gs://bucket/dashboards/proj_12345/",
        "insights": [...]
      }
    }
  }
}
```

### **Agent Tools & Capabilities**

#### Sandbox Service Integration
```python
# Tool available to all agents
class SandboxTool:
    def execute_code(self, code: str, project_id: str):
        """Execute code in isolated environment with cloud access"""
        response = requests.post(
            f"{SANDBOX_URL}/execute",
            json={
                "code": code,
                "project_id": project_id,
                "cloud_access": True
            }
        )
        return response.json()

# Example usage in CSV Processing Agent
cleaning_code = f"""
import pandas as pd
from google.cloud import bigquery

# Load and clean data
df = pd.read_csv('gs://bucket/{project_id}/{filename}')
df_cleaned = df.dropna().drop_duplicates()

# Store in BigQuery
client = bigquery.Client()
table_id = f'{project_id}.dataset.{project_id}_{table_name}'
df_cleaned.to_gbq(table_id, if_exists='replace')

print(f"Processed {{len(df_cleaned)}} rows")
"""

result = sandbox_tool.execute_code(cleaning_code, project_id)
```

---

## 🚀 Implementation Phases

### **Phase 1: Core Infrastructure**
1. Set up PubSub topics and subscriptions
2. Implement Coordinator Agent with basic routing
3. Create CSV Processing Agent with sandbox integration
4. Set up Firestore schema for project state

### **Phase 2: Data Processing Layer**
1. Complete all file processing agents (PDF, generic)
2. Implement robust error handling and retry logic
3. Add comprehensive logging and monitoring
4. Test end-to-end data preparation pipeline

### **Phase 3: Analysis Layer**
1. Implement Lead Analysis Agent
2. Create EDA Agent with comprehensive analytics
3. Build Dashboard Generation Agent
4. Test analysis pipeline with various data types

### **Phase 4: Presentation Layer**
1. Implement Q&A Agent with NL → SQL capabilities
2. Create user-friendly dashboard interface
3. Add conversation context management
4. Implement real-time query execution

---

This architecture provides a robust, scalable foundation for AIDE's autonomous data processing capabilities while maintaining clear separation of concerns and leveraging Google Cloud's managed services effectively.