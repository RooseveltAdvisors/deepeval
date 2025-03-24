# DeepEval - Local LLM Evaluation Framework

A simple, open-source framework for evaluating and testing LLM outputs locally. Built on top of pytest for seamless integration with your existing test suite.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RooseveltAdvisors/deepeval.git
cd deepeval
```

2. Install dependencies using UV:
```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -e .
```

## Quick Start

1. Create a test file in your project:
```python
# test_llm.py
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

def test_llm_output():
    # Define your evaluation metric
    correctness_metric = GEval(
        name="Correctness",
        criteria="Check if the output matches expected behavior",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5
    )
    
    # Create a test case
    test_case = LLMTestCase(
        input="What's the return policy?",
        actual_output="You can return items within 30 days",
        expected_output="Our policy allows returns within 30 days of purchase",
        retrieval_context=["Store policy: 30-day return window on all purchases"]
    )
    
    # Run the evaluation
    assert_test(test_case, [correctness_metric])
```

2. Run your test:
```bash
uv run pytest test_llm.py -v
```

## Local Storage

All evaluation results are automatically stored in `.deepeval_results/` in your project directory. Results include:
- Test case details
- Metric scores
- Success/failure status
- Timestamps
- Input/output pairs

You can customize the storage location:
```bash
export DEEPEVAL_RESULTS_DIR="/custom/path"
```

## Local Dashboard

View your test results in an interactive dashboard:

1. Start the dashboard server:
```bash
# On Unix/macOS
cd examples/dashboard
chmod +x run_server.sh
./run_server.sh

# On Windows
cd examples\dashboard
run_server.bat
```

2. Open http://localhost:8501 in your browser

The dashboard shows:
- Success rates
- Score distributions
- Timeline views
- Detailed result tables

## Integration with Your Test Suite

Add DeepEval to your existing pytest suite:

```python
# conftest.py
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

@pytest.fixture
def llm_test_case():
    return LLMTestCase(
        input="What are your hours?",
        actual_output="We're open 9-5 Monday to Friday",
        retrieval_context=["Business hours: 9AM-5PM, Mon-Fri"]
    )

@pytest.fixture
def relevancy_metric():
    return AnswerRelevancyMetric(threshold=0.7)

def test_llm_response(llm_test_case, relevancy_metric):
    assert_test(llm_test_case, [relevancy_metric])
```

## Available Metrics

Local evaluation metrics include:
- Answer Relevancy
- Hallucination Detection
- Contextual Precision/Recall
- Task Completion
- Summarization
- And more...

Each metric runs locally using your choice of:
- Local LLMs
- Statistical methods
- NLP models

## Example Projects

Check the `examples/` directory for:
- RAG evaluation examples
- Chatbot testing
- Custom metric creation
- Bulk testing patterns

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0 - see [LICENSE.md](LICENSE.md)
