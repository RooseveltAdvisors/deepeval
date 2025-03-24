"""Tests for DeepEval storage functionality when used as a library."""

import json
import tempfile
from pathlib import Path
import pytest

from deepeval import evaluate
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval.storage import LocalStorage

@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for test storage."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_test_case():
    """Create a sample test case for testing."""
    return LLMTestCase(
        input="What is DeepEval?",
        actual_output="DeepEval is an LLM evaluation framework",
        expected_output="DeepEval helps evaluate LLM performance",
        context=["DeepEval is a comprehensive evaluation framework for LLMs"]
    )

@pytest.fixture
def sample_metrics():
    """Create sample metrics for testing."""
    return [
        HallucinationMetric(threshold=0.7),
        AnswerRelevancyMetric(threshold=0.7)
    ]

def test_local_storage_creation(temp_storage_dir):
    """Test creating local storage with custom directory."""
    storage = LocalStorage(storage_dir=temp_storage_dir)
    assert storage.storage_dir == temp_storage_dir
    assert temp_storage_dir.exists()

def test_local_storage_save_results(temp_storage_dir, sample_test_case, sample_metrics):
    """Test saving results to local storage."""
    storage = LocalStorage(storage_dir=temp_storage_dir)
    test_results = {
        "hallucination": [{"score": 0.95, "success": True, "reason": "No hallucination detected"}],
        "answer_relevancy": [{"score": 0.85, "success": True, "reason": "Answer is relevant"}]
    }
    
    result_id = storage.save_results([sample_test_case], sample_metrics, test_results)
    assert result_id is not None
    
    # Check if file was created
    result_file = temp_storage_dir / f"{result_id}.json"
    assert result_file.exists()
    
    # Verify content
    with open(result_file) as f:
        saved_data = json.load(f)
    assert saved_data["results"] == test_results
    assert "test_cases" in saved_data
    assert "metrics" in saved_data
    assert "timestamp" in saved_data

def test_local_storage_load_results(temp_storage_dir, sample_test_case, sample_metrics):
    """Test loading results from local storage."""
    storage = LocalStorage(storage_dir=temp_storage_dir)
    test_results = {
        "hallucination": [{"score": 0.95, "success": True, "reason": "No hallucination detected"}],
        "answer_relevancy": [{"score": 0.85, "success": True, "reason": "Answer is relevant"}]
    }
    
    # Save and then load results
    result_id = storage.save_results([sample_test_case], sample_metrics, test_results)
    loaded_results = storage.load_results(result_id)
    
    assert loaded_results["results"] == test_results
    assert "test_cases" in loaded_results
    assert "metrics" in loaded_results
    assert "timestamp" in loaded_results

def test_local_storage_missing_results(temp_storage_dir):
    """Test handling of missing results."""
    storage = LocalStorage(storage_dir=temp_storage_dir)
    
    with pytest.raises(FileNotFoundError):
        storage.load_results("nonexistent_id")

def test_evaluation_with_local_storage(temp_storage_dir, sample_test_case, sample_metrics):
    """Test full evaluation workflow with local storage."""
    storage = LocalStorage(storage_dir=temp_storage_dir)
    
    # Run evaluation
    results = evaluate([sample_test_case], sample_metrics, storage=storage)
    
    # Verify results were saved
    assert len(list(temp_storage_dir.glob("*.json"))) > 0
    
    # Verify results structure
    assert isinstance(results, dict)
    assert "hallucination" in results
    assert "answer_relevancy" in results
    assert "result_id" in results
    
    # Check metric results
    for metric_name in ["hallucination", "answer_relevancy"]:
        metric_results = results[metric_name]
        assert isinstance(metric_results, list)
        assert len(metric_results) == 1
        result = metric_results[0]
        assert "score" in result
        assert "success" in result
        assert isinstance(result["score"], float)
        assert isinstance(result["success"], bool)

def test_multiple_test_cases(temp_storage_dir, sample_metrics):
    """Test evaluation with multiple test cases."""
    storage = LocalStorage(storage_dir=temp_storage_dir)
    
    # Create multiple test cases
    test_cases = [
        LLMTestCase(
            input=f"Question {i}",
            actual_output=f"Answer {i}",
            expected_output=f"Expected {i}",
            context=[f"Context {i}"]
        )
        for i in range(3)
    ]
    
    # Run evaluation
    results = evaluate(test_cases, sample_metrics, storage=storage)
    
    # Verify results structure
    assert isinstance(results, dict)
    assert "hallucination" in results
    assert "answer_relevancy" in results
    assert "result_id" in results
    
    # Check metric results
    for metric_name in ["hallucination", "answer_relevancy"]:
        metric_results = results[metric_name]
        assert isinstance(metric_results, list)
        assert len(metric_results) == len(test_cases)
        for result in metric_results:
            assert "score" in result
            assert "success" in result
            assert isinstance(result["score"], float)
            assert isinstance(result["success"], bool)

def test_storage_directory_creation():
    """Test storage directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        storage_dir = Path(tmpdirname) / "nonexistent" / "deepeval_results"
        storage = LocalStorage(storage_dir=storage_dir)
        assert storage_dir.exists()

def test_result_id_generation():
    """Test uniqueness of result IDs."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        storage = LocalStorage(storage_dir=tmpdirname)
        test_results = {
            "hallucination": [{"score": 0.95, "success": True, "reason": "No hallucination detected"}],
            "answer_relevancy": [{"score": 0.85, "success": True, "reason": "Answer is relevant"}]
        }
        
        # Generate multiple result IDs
        result_ids = set()
        for _ in range(10):
            result_id = storage.save_results(
                [LLMTestCase(input="test", actual_output="test")],
                [HallucinationMetric()],
                test_results
            )
            result_ids.add(result_id)
        
        # All IDs should be unique
        assert len(result_ids) == 10 