from deepeval import evaluate
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from config import config

def run_evaluation(save_mode: str = "local") -> None:
    """Run evaluation with specified save mode.
    
    Args:
        save_mode (str): Where to save results ('local' or 'cloud')
    """
    # Update configuration
    config.save_mode = save_mode
    config.validate()

    # Sample context and test data
    context = [
        """DeepEval is a comprehensive evaluation framework for LLMs. It provides:
1. Multiple evaluation metrics (hallucination, relevancy, etc.)
2. A dashboard for visualizing results
3. Easy integration with existing LLM applications
4. Detailed scoring and analysis"""
    ]

    actual_output = "DeepEval is a framework for evaluating LLMs. It offers multiple metrics like hallucination detection and provides a dashboard for visualization."
    expected_output = "DeepEval is an evaluation framework that helps assess LLM performance through various metrics and includes a dashboard."
    query = "What is DeepEval and what features does it offer?"

    # Create test case
    test_case = LLMTestCase(
        input=query,
        actual_output=actual_output,
        expected_output=expected_output,
        context=context
    )

    # Define metrics
    metrics = [
        HallucinationMetric(threshold=0.7),
        AnswerRelevancyMetric(threshold=0.7)
    ]

    # Run evaluation
    results = evaluate([test_case], metrics)

    # Print results
    for metric_name, metric_result in results.items():
        print(f"{metric_name}: {'Passed' if metric_result.passed else 'Failed'} (Score: {metric_result.score})")

if __name__ == "__main__":
    # Get save mode from environment or use default
    save_mode = config.save_mode
    run_evaluation(save_mode) 