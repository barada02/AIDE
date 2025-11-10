# Code Runner Sandbox

A secure Python code execution sandbox with FastAPI, designed for data analysis and Google Cloud services.

## Features

- **Secure Code Execution**: Sandboxed Python code execution with security restrictions
- **Resource Management**: Configurable timeout and memory limits
- **Comprehensive Libraries**: Pre-installed data analysis and Google Cloud libraries
- **RESTful API**: FastAPI-based endpoints for code execution
- **Cloud Ready**: Containerized for Google Cloud Run deployment

## Available Libraries

### Data Analysis & Processing
- pandas, numpy, scipy
- scikit-learn, xgboost, lightgbm
- matplotlib, seaborn, plotly, bokeh, altair

### Google Cloud Services
- google-cloud-storage
- google-cloud-firestore
- google-cloud-bigquery
- google-cloud-logging

### Utilities
- requests, aiohttp
- openpyxl, xlrd
- beautifulsoup4, lxml
- PyYAML, sqlalchemy, pymongo

## API Endpoints

- `POST /execute` - Execute Python code
- `GET /health` - Health check
- `GET /libraries` - List available libraries
- `GET /docs` - API documentation

## Security Features

- Restricted imports and functions
- Execution timeouts
- Memory usage monitoring
- Input validation and sanitization
- Sandboxed execution environment

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Docker Deployment

```bash
# Build the image
docker build -t code-runner-sandbox .

# Run locally
docker run -p 8080:8080 code-runner-sandbox
```

## Google Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
gcloud run deploy code-runner-sandbox \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300s
```

## Usage Example

```python
import requests

# Execute code
response = requests.post('http://localhost:8080/execute', json={
    "code": """
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100)
})

print(f"Data shape: {data.shape}")
print(f"Mean x: {data['x'].mean():.3f}")
print(f"Mean y: {data['y'].mean():.3f}")
""",
    "timeout": 30,
    "memory_limit_mb": 512
})

result = response.json()
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
```

## Environment Variables

- `PORT`: Server port (default: 8080)

## Security Considerations

This sandbox provides basic security through:
- Import restrictions
- Function blacklisting
- Resource limits
- Execution timeouts

**Note**: This is suitable for trusted code execution. For untrusted code, additional security measures should be implemented.