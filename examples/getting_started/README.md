# Getting Started with DeepEval

This guide will help you run your first evaluation test and visualize the results in the DeepEval dashboard.

## Configuration

DeepEval supports two modes for saving evaluation results:
1. **Local Mode** (default): Results are saved to your local filesystem
2. **Cloud Mode**: Results are saved to DeepEval's cloud service

You can configure DeepEval in three ways (in order of precedence):

### 1. Environment Variables
Environment variables have the highest priority and will override other settings:

```bash
# For local storage (default)
export DEEPEVAL_SAVE_MODE=local
export DEEPEVAL_RESULTS_DIR=.deepeval_results

# For cloud storage
export DEEPEVAL_SAVE_MODE=cloud
export DEEPEVAL_API_KEY=your_api_key
```

### 2. .env File
Create a `.env` file in your project root (copy from `.env.example`):

```ini
# Storage Mode ('local' or 'cloud')
DEEPEVAL_SAVE_MODE=local

# Local Storage Configuration
DEEPEVAL_RESULTS_DIR=.deepeval_results

# Cloud Storage Configuration
DEEPEVAL_API_KEY=your_api_key_here

# Optional: Metric Configuration
DEEPEVAL_HALLUCINATION_THRESHOLD=0.7
DEEPEVAL_RELEVANCY_THRESHOLD=0.7

# Optional: API Configuration
DEEPEVAL_API_URL=https://api.confident-ai.com
DEEPEVAL_API_VERSION=v1
```

### 3. Direct Configuration
You can also configure settings in your code (lowest priority):

```python
from config import config

# For local storage
config.save_mode = "local"
config.local_save_dir = Path(".deepeval_results")

# For cloud storage
config.save_mode = "cloud"
config.api_key = "your_api_key"

# Custom metric thresholds
config.metric_thresholds["hallucination"] = 0.8
config.metric_thresholds["relevancy"] = 0.75
```

## Running the Example Test

1. First, make sure you're in the project root directory:
   ```bash
   cd /path/to/deepeval
   ```

2. Copy the example environment file:
   ```bash
   cp examples/getting_started/.env.example .env
   ```

3. Edit the `.env` file with your settings:
   ```bash
   # For local storage (default)
   DEEPEVAL_SAVE_MODE=local
   
   # For cloud storage
   # DEEPEVAL_SAVE_MODE=cloud
   # DEEPEVAL_API_KEY=your_api_key
   ```

4. Run the basic test example:
   ```bash
   uv run examples/getting_started/basic_test.py
   ```

   This will:
   - Load configuration from your .env file
   - Create a test case with sample context and outputs
   - Run evaluation using Hallucination and Answer Relevancy metrics
   - Save results based on your configuration:
     - Local mode: Saves to `.deepeval_results` directory
     - Cloud mode: Saves to DeepEval's cloud service

## Viewing Results

### Local Dashboard
1. Start the DeepEval dashboard:
   ```bash
   ./examples/dashboard/run_server.sh
   ```

2. If prompted about an existing Streamlit process:
   - Enter 'y' to terminate the existing process
   - The dashboard will automatically start

3. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

### Cloud Dashboard
When using cloud mode:
1. Log in to your DeepEval account:
   ```bash
   deepeval login
   ```

2. View results at https://app.confident-ai.com

You should now see your test results in the dashboard, including:
- Overall test status
- Individual metric scores
- Detailed analysis for each metric
- Visualization of results

## Understanding the Example

The basic test (`basic_test.py`) demonstrates:
- Creating a test case with context, query, and outputs
- Using multiple evaluation metrics
- Setting custom thresholds for pass/fail criteria
- Running evaluation and getting results
- Configuring storage modes (local vs cloud)

The dashboard provides:
- Visual representation of test results
- Detailed breakdown of each metric
- Historical test data comparison
- Export and sharing capabilities

## Switching Between Modes

You can easily switch between local and cloud modes:

1. **Temporary Switch**: Use environment variables when running tests
   ```bash
   # Switch to cloud mode for a single run
   DEEPEVAL_SAVE_MODE=cloud DEEPEVAL_API_KEY=your_api_key uv run your_test.py

   # Switch back to local mode
   DEEPEVAL_SAVE_MODE=local uv run your_test.py
   ```

2. **Permanent Switch**: Set environment variables in your shell profile
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export DEEPEVAL_SAVE_MODE=cloud
   export DEEPEVAL_API_KEY=your_api_key
   ```

3. **Code-level Switch**: Modify configuration in your test code
   ```python
   from config import config
   
   # Switch to cloud mode
   config.save_mode = "cloud"
   config.api_key = "your_api_key"
   ``` 