# Postman Testing Guide for Code Runner Sandbox API

## Setup
1. Import the `Code_Runner_Sandbox_API.postman_collection.json` file into Postman
2. The collection uses a variable `{{base_url}}` set to your deployed service URL
3. Update the `base_url` variable in the collection settings if needed

## Test Endpoints

### 1. Health Check
```
GET {{base_url}}/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T14:57:40.158370",
  "service": "code-runner-sandbox"
}
```

### 2. Get Available Libraries
```
GET {{base_url}}/libraries
```

### 3. Execute Simple Code
```
POST {{base_url}}/execute
Content-Type: application/json

{
  "code": "import math\nprint(f'Pi = {math.pi:.4f}')\nresult = sum(range(1, 11))\nprint(f'Sum of 1 to 10: {result}')",
  "timeout": 10,
  "memory_limit_mb": 256
}
```

### 4. Execute Data Analysis
```
POST {{base_url}}/execute
Content-Type: application/json

{
  "code": "import pandas as pd\nimport numpy as np\n\n# Create sample data\nnp.random.seed(42)\ndata = pd.DataFrame({\n    'name': ['Alice', 'Bob', 'Charlie'],\n    'age': [25, 30, 35],\n    'salary': np.random.normal(50000, 10000, 3)\n})\n\nprint('Sample Data:')\nprint(data)\nprint(f'Mean salary: ${data[\"salary\"].mean():.2f}')",
  "timeout": 30,
  "memory_limit_mb": 512
}
```

### 5. Test Security (Should Fail)
```
POST {{base_url}}/execute
Content-Type: application/json

{
  "code": "import os\nprint(os.listdir('.'))",
  "timeout": 10,
  "memory_limit_mb": 256
}
```
**Expected Response:**
```json
{
  "success": false,
  "error": "Security violation: Restricted import 'os' found at line 1"
}
```

## CURL Examples

### Health Check
```bash
curl -X GET "https://sandbox-797563351214.europe-west1.run.app/health"
```

### Execute Simple Code
```bash
curl -X POST "https://sandbox-797563351214.europe-west1.run.app/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import math\nprint(f\"Pi = {math.pi:.4f}\")\nresult = sum(range(1, 11))\nprint(f\"Sum of 1 to 10: {result}\")",
    "timeout": 10,
    "memory_limit_mb": 256
  }'
```

### Execute Data Analysis
```bash
curl -X POST "https://sandbox-797563351214.europe-west1.run.app/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import pandas as pd\nimport numpy as np\n\nnp.random.seed(42)\ndata = pd.DataFrame({\"x\": np.random.randn(5), \"y\": np.random.randn(5)})\nprint(data)\nprint(f\"Mean x: {data[\"x\"].mean():.3f}\")",
    "timeout": 30,
    "memory_limit_mb": 512
  }'
```

## PowerShell Examples

### Health Check
```powershell
Invoke-RestMethod -Uri "https://sandbox-797563351214.europe-west1.run.app/health" -Method Get
```

### Execute Code
```powershell
$body = @{
    code = "import math`nprint(f'Pi = {math.pi:.4f}')`nresult = sum(range(1, 11))`nprint(f'Sum of 1 to 10: {result}')"
    timeout = 10
    memory_limit_mb = 256
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://sandbox-797563351214.europe-west1.run.app/execute" -Method Post -Body $body -ContentType "application/json"
```

## Expected Response Format

### Successful Execution
```json
{
  "success": true,
  "output": "Pi = 3.1416\nSum of 1 to 10: 55",
  "error": null,
  "execution_time": 0.123,
  "memory_used_mb": 2.45,
  "timestamp": "2025-11-10T15:00:00.000000"
}
```

### Failed Execution
```json
{
  "success": false,
  "output": "",
  "error": "Security violation: Restricted import 'os' found at line 1",
  "execution_time": 0.001,
  "memory_used_mb": null,
  "timestamp": "2025-11-10T15:00:00.000000"
}
```

## Notes
- Replace the base URL with your actual deployed service URL
- The timeout is in seconds (1-300)
- Memory limit is in MB (64-2048)
- Code should be properly escaped in JSON strings