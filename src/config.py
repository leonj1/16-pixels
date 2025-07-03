import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict


class Config:
    """Configuration management for the 16-pixels application."""
    
    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Optional path to .env file
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Required API keys
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # Optional API keys for image generation
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.freepik_api_key = os.getenv('FREEPIK_API_KEY')
        self.runway_api_key = os.getenv('RUNWAY_API_KEY')
        self.leonardo_api_key = os.getenv('LEONARDO_API_KEY')
        self.replicate_api_token = os.getenv('REPLICATE_API_TOKEN')
        self.huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
        self.stability_api_key = os.getenv('STABILITY_API_KEY')
        
        # Application settings
        self.default_output_dir = os.getenv('OUTPUT_DIR', './output')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def validate(self) -> None:
        """Validate required configuration."""
        if not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required for query classification. "
                "Please set it in your environment or .env file."
            )
    
    def get_available_services(self) -> Dict[str, bool]:
        """Get dictionary of available services based on configured API keys."""
        return {
            'openai': bool(self.openai_api_key),
            'freepik': bool(self.freepik_api_key),
            'runway': bool(self.runway_api_key),
            'leonardo': bool(self.leonardo_api_key),
            'replicate': bool(self.replicate_api_token),
            'huggingface': bool(self.huggingface_token),
            'stability': bool(self.stability_api_key),
        }
    
    def count_available_services(self) -> int:
        """Count number of available image generation services."""
        return sum(self.get_available_services().values())
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        services = self.get_available_services()
        available = [name for name, is_available in services.items() if is_available]
        
        return (
            f"Config(google_api_key={'✓' if self.google_api_key else '✗'}, "
            f"services={len(available)}/{len(services)} "
            f"[{', '.join(available)}])"
        )


# Global configuration instance
config = Config()