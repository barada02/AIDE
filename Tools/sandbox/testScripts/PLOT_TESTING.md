# Plot Testing Guide

## Plot Support Added ✅

The Code Runner Sandbox now supports matplotlib plot generation and returns plots as base64-encoded PNG images.

**Important**: The API runs on Cloud Run and does NOT save files to disk. Instead, it captures matplotlib figures in memory, converts them to PNG format, encodes them as base64 strings, and returns them in the JSON response.

### New Response Format

```json
{
  "success": true,
  "output": "Created plot with 100 data points\nPlot should be captured and returned as base64",
  "error": null,
  "execution_time": 2.45,
  "memory_used_mb": 12.34,
  "timestamp": "2025-11-10T15:30:00.000000",
  "plots": ["iVBORw0KGgoAAAANSUhEUgAAA...base64data..."]
}
```

### Testing Plots

#### Postman Test - Single Plot
```json
POST {{base_url}}/execute
Content-Type: application/json

{
  "code": "import matplotlib.pyplot as plt\nimport numpy as np\n\nx = np.linspace(0, 10, 100)\ny = np.sin(x)\n\nplt.figure(figsize=(10, 6))\nplt.plot(x, y, 'b-', linewidth=2, label='sin(x)')\nplt.xlabel('x')\nplt.ylabel('sin(x)')\nplt.title('Sine Wave Plot')\nplt.legend()\nplt.grid(True)\n\nprint('Plot generated successfully!')",
  "timeout": 30,
  "memory_limit_mb": 512
}
```

#### Postman Test - Multiple Plots
```json
POST {{base_url}}/execute
Content-Type: application/json

{
  "code": "import matplotlib.pyplot as plt\nimport numpy as np\n\n# Plot 1\nfig1 = plt.figure(figsize=(8, 6))\nx = np.linspace(0, 5, 50)\nplt.plot(x, np.sin(x), 'r-', label='sin(x)')\nplt.title('Sine Function')\nplt.legend()\n\n# Plot 2\nfig2 = plt.figure(figsize=(8, 6))\nplt.plot(x, np.cos(x), 'g-', label='cos(x)')\nplt.title('Cosine Function')\nplt.legend()\n\nprint('Created 2 plots')",
  "timeout": 30,
  "memory_limit_mb": 512
}
```

### Decoding Base64 Plots

#### JavaScript (Browser)
```javascript
// In Postman Tests tab or browser console
const plotData = pm.response.json().plots[0]; // First plot
const img = document.createElement('img');
img.src = 'data:image/png;base64,' + plotData;
document.body.appendChild(img);
```

#### Python
```python
import base64
from PIL import Image
import io

# Get the plot data from API response
plot_data = response.json()['plots'][0]

# Decode and save
image_data = base64.b64decode(plot_data)
image = Image.open(io.BytesIO(image_data))
image.save('plot.png')
```

#### PowerShell
```powershell
# Decode base64 plot
$plotData = $response.plots[0]
$bytes = [Convert]::FromBase64String($plotData)
[System.IO.File]::WriteAllBytes("plot.png", $bytes)
```

### Features

✅ **Automatic Plot Detection** - Detects matplotlib figures automatically  
✅ **Multiple Plots** - Supports multiple figures in one execution  
✅ **High Quality** - 150 DPI PNG format  
✅ **Memory Management** - Automatically closes figures after capture  
✅ **Error Handling** - Graceful handling of plot errors  

### Supported Plot Types
- Line plots
- Scatter plots  
- Bar charts
- Histograms
- Subplots
- Seaborn plots (built on matplotlib)
- Any matplotlib-based visualization

### How It Works:
1. Your code creates matplotlib figures in Cloud Run container
2. The sandbox automatically detects active figures in memory
3. Each figure is converted to PNG format in memory (using io.BytesIO buffer)
4. PNG data is base64-encoded and included in JSON response
5. **Client side**: You decode the base64 to display/save images locally
6. **No files are saved on Cloud Run** - everything happens in memory

### Notes
- Plots are automatically captured when `plt.figure()` is used
- No need to call `plt.show()` or `plt.savefig()` in your code
- All figures are automatically closed after capture to free memory
- Base64 data can be directly used in HTML img tags
- Large/complex plots may increase response time and size
- **Files are only saved on your local machine** when you decode the base64 data