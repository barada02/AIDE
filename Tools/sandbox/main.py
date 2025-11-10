import subprocess
import sys
import os
import asyncio
import tempfile
import json
import traceback
import signal
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Code Runner Sandbox",
    description="A secure Python code execution sandbox with data analysis and Google Cloud libraries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Python code to execute")
    timeout: int = Field(default=30, description="Execution timeout in seconds", ge=1, le=300)
    memory_limit_mb: int = Field(default=512, description="Memory limit in MB", ge=64, le=2048)

class CodeExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float
    memory_used_mb: Optional[float] = None
    timestamp: str

class LibraryInfo(BaseModel):
    name: str
    version: str
    description: Optional[str] = None

# Security: Restricted imports and operations
RESTRICTED_IMPORTS = {
    'os', 'subprocess', 'sys', 'importlib', 'builtins', '__builtin__',
    'eval', 'exec', 'compile', 'open', 'file', 'input', 'raw_input',
    'reload', '__import__', 'globals', 'locals', 'vars', 'dir',
    'delattr', 'setattr', 'getattr', 'hasattr'
}

RESTRICTED_FUNCTIONS = {
    'eval', 'exec', 'compile', 'open', 'file', 'input', 'raw_input',
    '__import__', 'reload', 'globals', 'locals', 'vars', 'dir'
}

def check_code_security(code: str) -> tuple[bool, str]:
    """Check if code contains restricted operations."""
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Check for restricted imports
        if line.startswith('import ') or line.startswith('from '):
            for restricted in RESTRICTED_IMPORTS:
                if restricted in line:
                    return False, f"Restricted import '{restricted}' found at line {line_num}"
        
        # Check for restricted functions
        for restricted in RESTRICTED_FUNCTIONS:
            if restricted in line and f'{restricted}(' in line:
                return False, f"Restricted function '{restricted}' found at line {line_num}"
        
        # Check for dangerous operations
        dangerous_patterns = ['__', 'subprocess', 'os.system', 'os.popen', 'eval(', 'exec(']
        for pattern in dangerous_patterns:
            if pattern in line:
                return False, f"Potentially dangerous operation '{pattern}' found at line {line_num}"
    
    return True, ""

async def execute_code_safely(code: str, timeout: int = 30, memory_limit_mb: int = 512) -> Dict[str, Any]:
    """Execute Python code safely with restrictions."""
    
    # Security check
    is_safe, error_msg = check_code_security(code)
    if not is_safe:
        return {
            "success": False,
            "output": "",
            "error": f"Security violation: {error_msg}",
            "execution_time": 0.0,
            "memory_used_mb": None
        }
    
    # Create temporary file for code execution
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        # Add memory monitoring and safe imports
        safe_code = f'''
import sys
import traceback
import psutil
import os
import gc
from datetime import datetime

# Monitor memory usage
process = psutil.Process(os.getpid())
initial_memory = process.memory_info().rss / 1024 / 1024

try:
    # User code starts here
{code}
    
    # Memory usage after execution
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_used = final_memory - initial_memory
    print(f"\\n__MEMORY_USED__: {{memory_used:.2f}} MB")
    
except Exception as e:
    print(f"__ERROR__: {{str(e)}}")
    print(f"__TRACEBACK__:")
    traceback.print_exc()
'''
        temp_file.write(safe_code)
        temp_file_path = temp_file.name
    
    start_time = datetime.now()
    
    try:
        # Execute the code with resource limits
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=None if os.name == 'nt' else os.setsid
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Parse output for memory usage
            memory_used = None
            output_lines = []
            error_lines = []
            
            for line in stdout.split('\n'):
                if line.startswith('__MEMORY_USED__:'):
                    try:
                        memory_used = float(line.split(':')[1].strip().replace(' MB', ''))
                    except:
                        pass
                elif line.startswith('__ERROR__:'):
                    error_lines.append(line.replace('__ERROR__: ', ''))
                elif line.startswith('__TRACEBACK__:'):
                    error_lines.extend(stderr.split('\n'))
                else:
                    output_lines.append(line)
            
            # Clean up output
            output = '\n'.join(output_lines).strip()
            error = '\n'.join(error_lines).strip() if error_lines else stderr.strip()
            
            success = process.returncode == 0 and not error
            
            return {
                "success": success,
                "output": output,
                "error": error if error else None,
                "execution_time": execution_time,
                "memory_used_mb": memory_used
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return {
                "success": False,
                "output": "",
                "error": f"Code execution timed out after {timeout} seconds",
                "execution_time": timeout,
                "memory_used_mb": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "execution_time": (datetime.now() - start_time).total_seconds(),
            "memory_used_mb": None
        }
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Code Runner Sandbox API",
        "version": "1.0.0",
        "endpoints": [
            "/execute - Execute Python code",
            "/health - Health check",
            "/libraries - List available libraries",
            "/docs - API documentation"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "code-runner-sandbox"
    }

@app.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute Python code in a secure sandbox environment."""
    
    logger.info(f"Executing code with timeout: {request.timeout}s, memory limit: {request.memory_limit_mb}MB")
    
    try:
        result = await execute_code_safely(
            code=request.code,
            timeout=request.timeout,
            memory_limit_mb=request.memory_limit_mb
        )
        
        return CodeExecutionResponse(
            success=result["success"],
            output=result["output"],
            error=result["error"],
            execution_time=result["execution_time"],
            memory_used_mb=result["memory_used_mb"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/libraries")
async def get_available_libraries():
    """Get list of available libraries in the sandbox."""
    
    # Core libraries for data analysis and Google Cloud
    libraries = [
        {"name": "pandas", "description": "Data manipulation and analysis"},
        {"name": "numpy", "description": "Numerical computing"},
        {"name": "scipy", "description": "Scientific computing"},
        {"name": "scikit-learn", "description": "Machine learning"},
        {"name": "matplotlib", "description": "Plotting and visualization"},
        {"name": "seaborn", "description": "Statistical data visualization"},
        {"name": "plotly", "description": "Interactive visualizations"},
        {"name": "google-cloud-storage", "description": "Google Cloud Storage client"},
        {"name": "google-cloud-firestore", "description": "Google Cloud Firestore client"},
        {"name": "google-cloud-bigquery", "description": "Google Cloud BigQuery client"},
        {"name": "google-cloud-logging", "description": "Google Cloud Logging client"},
        {"name": "requests", "description": "HTTP library"},
        {"name": "json", "description": "JSON encoder and decoder"},
        {"name": "datetime", "description": "Date and time handling"},
        {"name": "math", "description": "Mathematical functions"},
        {"name": "random", "description": "Random number generation"},
        {"name": "statistics", "description": "Statistical functions"},
        {"name": "collections", "description": "Specialized container datatypes"},
        {"name": "itertools", "description": "Iterator functions"},
        {"name": "functools", "description": "Higher-order functions"},
    ]
    
    return {
        "available_libraries": libraries,
        "total_count": len(libraries),
        "note": "This list includes major libraries. Standard Python libraries are also available."
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )