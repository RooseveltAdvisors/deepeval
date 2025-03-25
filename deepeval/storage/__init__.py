"""Storage backends for DeepEval results.

This module provides a clean interface for storing evaluation results
either locally or in the cloud. Users can easily switch between storage
backends by using different implementations of the StorageBackend protocol.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Union
import json
import os
import uuid
import time

from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric

class StorageBackend(Protocol):
    """Protocol defining the interface for storage backends."""
    
    @abstractmethod
    def save_results(
        self,
        test_cases: List[LLMTestCase],
        metrics: List[BaseMetric],
        results: Dict
    ) -> str:
        """Save evaluation results.
        
        Args:
            test_cases: List of test cases that were evaluated
            metrics: List of metrics used for evaluation
            results: Evaluation results to save
            
        Returns:
            str: Identifier for the saved results
        """
        pass
    
    @abstractmethod
    def load_results(self, result_id: str) -> Dict:
        """Load evaluation results.
        
        Args:
            result_id: Identifier of results to load
            
        Returns:
            Dict: The loaded results
        """
        pass

class LocalStorage(StorageBackend):
    """Store results locally in the filesystem."""
    
    def __init__(self, storage_dir: Union[str, Path] = ".deepeval_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_results(
        self,
        test_cases: List[LLMTestCase],
        metrics: List[BaseMetric],
        results: Dict
    ) -> str:
        """Save results to a local JSON file.
        
        Generates a descriptive filename including:
        - Test type (integration/unit)
        - Test file name
        - Test case name/subject
        - Timestamp for uniqueness
        
        Args:
            test_cases: List of test cases that were evaluated
            metrics: List of metrics used for evaluation
            results: Evaluation results to save
            
        Returns:
            str: Unique identifier for the saved results
        """
        timestamp = int(time.time() * 1000)
        
        # Get test type and file name from the test case
        test_type = "unknown"
        test_file = "unknown"
        test_subject = "unknown"
        
        if test_cases and hasattr(test_cases[0], 'name'):
            test_subject = test_cases[0].name or "unknown"
        
        # Try to get test file name from traceback
        import traceback
        for frame in traceback.extract_stack():
            if 'test_' in frame.filename and frame.filename.endswith('.py'):
                test_file = Path(frame.filename).stem
                test_type = "integration" if "integration" in test_file else "unit"
                break
        
        # Generate descriptive result ID
        result_id = f"{test_file}-{test_type}-{test_subject}-{timestamp}"
        file_path = self.storage_dir / f"{result_id}.json"
        
        # Convert test cases and metrics to serializable format
        serialized_data = {
            'test_cases': [tc.dict() for tc in test_cases],
            'metrics': [metric.__name__ for metric in metrics],
            'results': results,
            'timestamp': timestamp,
            'test_type': test_type,
            'test_file': test_file,
            'test_subject': test_subject
        }
        
        with open(file_path, "w") as f:
            json.dump(serialized_data, f, indent=2)
        
        return result_id
    
    def load_results(self, result_id: str) -> Dict:
        """Load results from a local JSON file."""
        file_path = self.storage_dir / f"{result_id}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"No results found for ID: {result_id}")
            
        with open(file_path) as f:
            return json.load(f)

class CloudStorage(StorageBackend):
    """Store results in the DeepEval cloud service."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPEVAL_API_KEY")
        if not self.api_key:
            raise ValueError("API key required for cloud storage")
            
        # Import cloud dependencies only when needed
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError(
                "Cloud storage requires additional dependencies. "
                "Install them with: pip install deepeval[cloud]"
            )
    
    def save_results(
        self,
        test_cases: List[LLMTestCase],
        metrics: List[BaseMetric],
        results: Dict
    ) -> str:
        """Save results to the cloud service."""
        serialized_data = {
            'test_cases': [tc.dict() for tc in test_cases],
            'metrics': [metric.__name__ for metric in metrics],
            'results': results,
            'timestamp': int(time.time() * 1000)
        }
        
        response = self.requests.post(
            "https://api.confident-ai.com/v1/results",
            json=serialized_data,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()['result_id']
    
    def load_results(self, result_id: str) -> Dict:
        """Load results from the cloud service."""
        response = self.requests.get(
            f"https://api.confident-ai.com/v1/results/{result_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()

# Default storage backend
default_storage = LocalStorage() 