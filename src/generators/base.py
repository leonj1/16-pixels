from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PIL import Image
import logging


class ImageGenerator(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def generate(self, prompt: str, variations: int = 1) -> List[Image.Image]:
        """
        Generate images based on the prompt.
        
        Args:
            prompt: The image description/prompt
            variations: Number of variations to generate (1-4)
            
        Returns:
            List of PIL Image objects
        """
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Return the name of the image generation service."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available (API key configured, etc.)."""
        pass
    
    async def generate_with_metadata(self, prompt: str, variations: int = 1) -> Dict[str, Any]:
        """
        Generate images with metadata about the generation process.
        
        Returns:
            Dictionary containing:
            - 'images': List of PIL Image objects
            - 'service': Service name
            - 'prompt': Original prompt
            - 'variations_requested': Number of variations requested
            - 'variations_generated': Actual number generated
            - 'errors': Any errors encountered
        """
        metadata = {
            'service': self.get_service_name(),
            'prompt': prompt,
            'variations_requested': variations,
            'variations_generated': 0,
            'images': [],
            'errors': []
        }
        
        try:
            images = await self.generate(prompt, variations)
            metadata['images'] = images
            metadata['variations_generated'] = len(images)
        except Exception as e:
            self.logger.error(f"Error generating images: {e}")
            metadata['errors'].append(str(e))
            
        return metadata