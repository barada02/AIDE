"""
Test script for the Code Runner Sandbox API
"""

import requests
import json
import time

# API base URL (change this to your deployed service URL)
BASE_URL = "https://sandbox-797563351214.europe-west1.run.app/"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_libraries_endpoint():
    """Test the libraries endpoint"""
    print("\n📚 Testing libraries endpoint...")
    response = requests.get(f"{BASE_URL}/libraries")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Available libraries: {data['total_count']}")
    return response.status_code == 200

def test_simple_code_execution():
    """Test simple code execution"""
    print("\n🧮 Testing simple code execution...")
    
    code = """
import math
import datetime

print("Hello from the sandbox!")
print(f"Current time: {datetime.datetime.now()}")
print(f"Pi = {math.pi:.4f}")

# Simple calculation
result = sum(range(1, 11))
print(f"Sum of 1 to 10: {result}")
"""
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "timeout": 10,
        "memory_limit_mb": 256
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Execution time: {data['execution_time']:.3f}s")
    print(f"Output:\n{data['output']}")
    
    return response.status_code == 200 and data['success']

def test_data_analysis():
    """Test data analysis capabilities"""
    print("\n📊 Testing data analysis...")
    
    code = """
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'salary': np.random.normal(50000, 10000, 5),
    'department': ['IT', 'HR', 'IT', 'Finance', 'IT']
})

print("Sample Data:")
print(data)
print(f"\\nData shape: {data.shape}")
print(f"\\nMean salary: ${data['salary'].mean():.2f}")
print(f"IT department count: {len(data[data['department'] == 'IT'])}")

# Group by department
dept_stats = data.groupby('department')['salary'].agg(['mean', 'count']).round(2)
print("\\nDepartment Statistics:")
print(dept_stats)
"""
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "timeout": 30,
        "memory_limit_mb": 512
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Execution time: {data['execution_time']:.3f}s")
    print(f"Memory used: {data['memory_used_mb']:.2f} MB" if data['memory_used_mb'] else "N/A")
    print(f"Output:\n{data['output']}")
    
    return response.status_code == 200 and data['success']

def test_security_restrictions():
    """Test security restrictions"""
    print("\n🔒 Testing security restrictions...")
    
    # Test restricted import
    code = """
import os
print(os.listdir('.'))
"""
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "timeout": 10
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Error: {data['error']}")
    
    # Should fail due to security restrictions
    return response.status_code == 200 and not data['success'] and "Security violation" in data['error']

def test_timeout():
    """Test timeout functionality"""
    print("\n⏱️ Testing timeout...")
    
    code = """
import time
print("Starting long operation...")
time.sleep(5)
print("This should not appear due to timeout")
"""
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "timeout": 2  # 2 second timeout
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Error: {data['error']}")
    
    # Should fail due to timeout
    return response.status_code == 200 and not data['success'] and "timed out" in data['error']

def test_visualization():
    """Test visualization capabilities"""
    print("\n📈 Testing visualization...")
    
    code = """
import matplotlib.pyplot as plt
import numpy as np

# Create a simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)

# Instead of showing, just print info about the plot
print(f"Created plot with {len(x)} data points")
print(f"X range: {x[0]:.2f} to {x[-1]:.2f}")
print(f"Y range: {y.min():.2f} to {y.max():.2f}")
print("Plot created successfully (would be saved to file in real scenario)")
"""
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "timeout": 30,
        "memory_limit_mb": 512
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Execution time: {data['execution_time']:.3f}s")
    print(f"Output:\n{data['output']}")
    
    return response.status_code == 200 and data['success']

def main():
    """Run all tests"""
    print("🧪 Starting Code Runner Sandbox Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_libraries_endpoint,
        test_simple_code_execution,
        test_data_analysis,
        test_security_restrictions,
        test_timeout,
        test_visualization
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
            print(f"✅ PASS" if result else "❌ FAIL")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append(False)
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()