"""
Test script to verify plot functionality
"""

import requests
import json
import base64
from PIL import Image
import io

# API base URL  
BASE_URL = "https://sandbox-797563351214.europe-west1.run.app"  # Your deployed Cloud Run URL

def test_plot_generation():
    """Test matplotlib plot generation"""
    print("📈 Testing plot generation...")
    
    code = """
import matplotlib.pyplot as plt
import numpy as np

# Create a simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.title('Sine Wave Plot')
plt.legend()
plt.grid(True)

print(f"Created plot with {len(x)} data points")
print("Plot will be returned as base64 in API response")
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
    
    if data.get('plots'):
        print(f"\n🎨 Found {len(data['plots'])} plot(s)!")
        for i, plot_data in enumerate(data['plots']):
            print(f"Plot {i+1} - Base64 length: {len(plot_data)} characters")
            
            # Try to decode and save the plot
            try:
                image_data = base64.b64decode(plot_data)
                image = Image.open(io.BytesIO(image_data))
                filename = f"plot_{i+1}.png"
                image.save(filename)
                print(f"✅ Saved plot as {filename}")
            except Exception as e:
                print(f"❌ Error saving plot: {e}")
    else:
        print("❌ No plots returned")
    
    return response.status_code == 200 and data['success'] and data.get('plots')

def test_multiple_plots():
    """Test multiple plot generation"""
    print("\n📊 Testing multiple plots...")
    
    code = """
import matplotlib.pyplot as plt
import numpy as np

# Create multiple plots
fig1 = plt.figure(figsize=(8, 6))
x = np.linspace(0, 5, 50)
plt.plot(x, np.sin(x), 'r-', label='sin(x)')
plt.title('Sine Function')
plt.legend()

fig2 = plt.figure(figsize=(8, 6))
x = np.linspace(0, 5, 50)
plt.plot(x, np.cos(x), 'g-', label='cos(x)')
plt.title('Cosine Function')
plt.legend()

print("Created 2 separate plots")
"""
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "timeout": 30,
        "memory_limit_mb": 512
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Output:\n{data['output']}")
    
    if data.get('plots'):
        print(f"\n🎨 Found {len(data['plots'])} plot(s)!")
        return len(data['plots']) == 2
    else:
        print("❌ No plots returned")
        return False

def main():
    """Run plot tests"""
    print("🧪 Testing Plot Functionality")
    print("=" * 40)
    
    try:
        # Test single plot
        result1 = test_plot_generation()
        print(f"Single plot test: {'✅ PASS' if result1 else '❌ FAIL'}")
        
        # Test multiple plots
        result2 = test_multiple_plots()
        print(f"Multiple plots test: {'✅ PASS' if result2 else '❌ FAIL'}")
        
        print("\n" + "=" * 40)
        if result1 and result2:
            print("🎉 All plot tests passed!")
        else:
            print("⚠️ Some plot tests failed.")
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")

if __name__ == "__main__":
    main()