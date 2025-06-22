"""
Configuration file for Promptsmith Chart Optimizer

This file handles API keys, model configurations, and other settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")  # Default to GPT-4 Turbo
    
    # Optimization settings
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "5"))
    CONTINUE_THRESHOLD: float = float(os.getenv("CONTINUE_THRESHOLD", "8.5"))
    
    # Scoring weights
    HEURISTIC_WEIGHT: float = float(os.getenv("HEURISTIC_WEIGHT", "0.4"))
    LLM_WEIGHT: float = float(os.getenv("LLM_WEIGHT", "0.6"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
            print("   Create a .env file with: OPENAI_API_KEY=your-api-key-here")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration."""
        print("🔧 Current Configuration:")
        print(f"   Model: {cls.OPENAI_MODEL}")
        print(f"   Max Iterations: {cls.MAX_ITERATIONS}")
        print(f"   Continue Threshold: {cls.CONTINUE_THRESHOLD}")
        print(f"   Heuristic Weight: {cls.HEURISTIC_WEIGHT}")
        print(f"   LLM Weight: {cls.LLM_WEIGHT}")
        print(f"   API Key: {'✅ Set' if cls.OPENAI_API_KEY else '❌ Not set'}")


# Example .env file content:
ENV_EXAMPLE = """
# Create a .env file in the project root with:
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4.1
MAX_ITERATIONS=5
CONTINUE_THRESHOLD=8.5
HEURISTIC_WEIGHT=0.4
LLM_WEIGHT=0.6
""" 