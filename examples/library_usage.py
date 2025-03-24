"""Example of using DeepEval as a library in your project."""

from pathlib import Path
from typing import List, Dict, Any
from deepeval import evaluate
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval.storage import LocalStorage

class MyLLMEvaluator:
    """Example class showing how to integrate DeepEval into your application."""
    
    def __init__(self, storage_dir: str = ".my_app_results"):
        """Initialize evaluator with custom storage location."""
        self.storage = LocalStorage(storage_dir=storage_dir)
        self.metrics = [
            HallucinationMetric(threshold=0.7),
            AnswerRelevancyMetric(threshold=0.7)
        ]
    
    def evaluate_response(
        self,
        question: str,
        actual_response: str,
        expected_response: str,
        context: List[str]
    ) -> Dict[str, Any]:
        """Evaluate a single LLM response."""
        test_case = LLMTestCase(
            input=question,
            actual_output=actual_response,
            expected_output=expected_response,
            context=context
        )
        
        return evaluate([test_case], self.metrics, storage=self.storage)
    
    def evaluate_batch(
        self,
        questions: List[str],
        actual_responses: List[str],
        expected_responses: List[str],
        contexts: List[List[str]]
    ) -> Dict[str, Any]:
        """Evaluate multiple LLM responses."""
        test_cases = [
            LLMTestCase(
                input=q,
                actual_output=a,
                expected_output=e,
                context=c
            )
            for q, a, e, c in zip(
                questions,
                actual_responses,
                expected_responses,
                contexts
            )
        ]
        
        return evaluate(test_cases, self.metrics, storage=self.storage)

def main():
    """Example usage of the MyLLMEvaluator class."""
    # Initialize evaluator
    evaluator = MyLLMEvaluator(storage_dir="example_results")
    
    # Single evaluation example
    results = evaluator.evaluate_response(
        question="What is DeepEval?",
        actual_response="DeepEval is an LLM evaluation framework",
        expected_response="DeepEval helps evaluate LLM performance",
        context=["DeepEval is a comprehensive evaluation framework for LLMs"]
    )
    
    print("\nSingle Evaluation Results:")
    for metric_name, metric_result in results.items():
        print(f"{metric_name}: Score = {metric_result.score}, Passed = {metric_result.passed}")
    
    # Batch evaluation example
    batch_results = evaluator.evaluate_batch(
        questions=[
            "What is Python?",
            "What is an LLM?"
        ],
        actual_responses=[
            "Python is a programming language",
            "LLM is a large language model"
        ],
        expected_responses=[
            "Python is a high-level programming language",
            "An LLM is an AI model for processing language"
        ],
        contexts=[
            ["Python is a popular high-level programming language"],
            ["Large Language Models (LLMs) are AI systems for text processing"]
        ]
    )
    
    print("\nBatch Evaluation Results:")
    for metric_name, metric_result in batch_results.items():
        print(f"{metric_name}: Score = {metric_result.score}, Passed = {metric_result.passed}")

if __name__ == "__main__":
    main() 