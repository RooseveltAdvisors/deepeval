"""Configuration management for DeepEval.

This module handles configuration loading from environment variables and .env files.
It follows a hierarchical configuration pattern:
1. Environment variables (highest priority)
2. .env file values
3. Default values (lowest priority)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

@dataclass
class DeepEvalConfig:
    """Configuration for DeepEval evaluation modes.
    
    Attributes:
        save_mode (str): Where to save evaluation results ('local' or 'cloud')
        local_save_dir (Path): Directory for local result storage
        api_key (Optional[str]): DeepEval API key for cloud storage
        api_url (str): DeepEval API URL for cloud storage
        api_version (str): DeepEval API version
        metric_thresholds (Dict[str, float]): Thresholds for different metrics
    """
    save_mode: str = "local"
    local_save_dir: Path = Path(".deepeval_results")
    api_key: Optional[str] = None
    api_url: str = "https://api.confident-ai.com"
    api_version: str = "v1"
    metric_thresholds: Dict[str, float] = None

    def __post_init__(self):
        """Initialize metric thresholds after dataclass initialization."""
        self.metric_thresholds = {
            "hallucination": float(os.getenv("DEEPEVAL_HALLUCINATION_THRESHOLD", "0.7")),
            "relevancy": float(os.getenv("DEEPEVAL_RELEVANCY_THRESHOLD", "0.7"))
        }

    @classmethod
    def from_env(cls) -> "DeepEvalConfig":
        """Create config from environment variables.
        
        Environment variables take precedence over .env file values.
        Returns:
            DeepEvalConfig: Configuration instance with loaded values
        """
        return cls(
            save_mode=os.getenv("DEEPEVAL_SAVE_MODE", "local"),
            local_save_dir=Path(os.getenv("DEEPEVAL_RESULTS_DIR", ".deepeval_results")),
            api_key=os.getenv("DEEPEVAL_API_KEY"),
            api_url=os.getenv("DEEPEVAL_API_URL", "https://api.confident-ai.com"),
            api_version=os.getenv("DEEPEVAL_API_VERSION", "v1")
        )

    def validate(self) -> None:
        """Validate configuration settings.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if self.save_mode not in ["local", "cloud"]:
            raise ValueError("save_mode must be either 'local' or 'cloud'")
        
        if self.save_mode == "cloud" and not self.api_key:
            raise ValueError("API key required for cloud save mode")

        if self.save_mode == "local":
            self.local_save_dir.mkdir(exist_ok=True)

    def get_metric_threshold(self, metric_name: str) -> float:
        """Get threshold for a specific metric.
        
        Args:
            metric_name (str): Name of the metric
            
        Returns:
            float: Threshold value for the metric
        """
        return self.metric_thresholds.get(metric_name, 0.7)

# Default configuration instance
config = DeepEvalConfig.from_env() 