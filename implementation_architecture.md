# AIDE Implementation Architecture - Stage 1

## First Layer - Data Preparation (Stage 1 Implementation)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 STAGE 1 FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

User Upload (UI)
    ↓
Cloud Storage (File Finalized)
    ↓
Cloud Function (Trigger)
    ↓
Cloud Task Queue + PubSub Publish
    ↓
Manager Agent (Cloud Run Service)
    ↓
Expert Agent Selection & Call
    ├── CSV Expert Agent (Cloud Run Service) - Function Tool
    ├── PDF Expert Agent (Cloud Run Service) - Function Tool  
    └── Generic Expert Agent (Cloud Run Service) - Function Tool

```

## Component Details

### Upload Flow
```
UI → Cloud Storage → Cloud Function → [Cloud Task Queue + PubSub] → Manager Agent
```

### Manager Agent Flow  
```
Manager Agent
    ├── Receive PubSub Message
    ├── Parse File Type & Project ID
    ├── Route to Expert Agent
    └── Call Expert as Function Tool
```

### Expert Agents (Function Tools)
```
CSV Expert Agent
    ├── Process CSV Files
    ├── Clean & Validate Data
    ├── Store in BigQuery
    └── Generate Report

PDF Expert Agent  
    ├── Extract Text/Structure
    ├── Parse Document
    ├── Store Content
    └── Generate Report

Generic Expert Agent
    ├── Handle Other File Types
    ├── Basic Processing
    ├── Store Content  
    └── Generate Report
```

## Current Implementation Status

### ✅ Implemented
- Basic Manager Agent Structure (from Brad Agent)
- Config Setup
- Tool Structure (csv_expert.py)

### 🔄 In Progress  
- Manager Agent Logic
- Expert Agent Function Tools
- PubSub Integration

### ⏳ Planned
- Cloud Task Queue Integration
- Expert Agent Services
- Error Handling & Monitoring
