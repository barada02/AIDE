# AIDE Tools

This directory contains various tools and utilities for the AIDE (AI Development Environment) project.

## Sandbox

The `sandbox/` directory contains a secure Python code execution environment with the following features:

### 🔧 Code Runner Sandbox

A secure, containerized Python code execution service built with FastAPI, designed for data analysis and Google Cloud integration.

**Key Features:**
- Secure code execution with safety restrictions
- Comprehensive data analysis libraries (pandas, numpy, scipy, scikit-learn)
- Google Cloud services integration (Storage, Firestore, BigQuery, Logging)
- RESTful API with FastAPI
- Docker containerization for Cloud Run deployment
- Resource monitoring and limits
- Timeout protection

**Quick Start:**
```bash
cd sandbox/
pip install -r requirements.txt
python main.py
```

**API Endpoints:**
- `POST /execute` - Execute Python code securely
- `GET /health` - Service health check
- `GET /libraries` - List available libraries
- `GET /docs` - Interactive API documentation

**Deployment:**
```bash
# Local with Docker
docker build -t code-runner-sandbox .
docker run -p 8080:8080 code-runner-sandbox

# Google Cloud Run (Windows)
./deploy.ps1 -ProjectId "your-gcp-project-id"
```

**Security Features:**
- Restricted imports and dangerous functions
- Execution timeouts and memory limits
- Input validation and sanitization
- Sandboxed execution environment

See `sandbox/README.md` for detailed documentation and usage examples.

## Future Tools

This directory will be expanded with additional tools and utilities as the AIDE project grows.