import os
import asyncio
from typing import Dict, List, Any
from PIL import Image
import logging
from .base import ImageGenerator
from .openai_generator import OpenAIGenerator
from .freepik_generator import FreePikGenerator
from .replicate_generator import ReplicateGenerator
from .stability_generator import StabilityGenerator
from ..utils.logger import setup_logger


class GeneratorRegistry:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.generators: Dict[str, ImageGenerator] = {}
        self._register_all_generators()
    
    def _register_all_generators(self):
        """Register all available generators based on configured API keys."""
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.generators['openai'] = OpenAIGenerator()
                self.logger.info("Registered OpenAI generator")
            except Exception as e:
                self.logger.error(f"Failed to register OpenAI generator: {e}")
        
        # FreePik
        if os.getenv('FREEPIK_API_KEY'):
            try:
                self.generators['freepik'] = FreePikGenerator()
                self.logger.info("Registered FreePik generator")
            except Exception as e:
                self.logger.error(f"Failed to register FreePik generator: {e}")
        
        # Replicate
        if os.getenv('REPLICATE_API_TOKEN'):
            try:
                self.generators['replicate'] = ReplicateGenerator()
                self.logger.info("Registered Replicate generator")
            except Exception as e:
                self.logger.error(f"Failed to register Replicate generator: {e}")
        
        # Stability AI
        if os.getenv('STABILITY_API_KEY'):
            try:
                self.generators['stability'] = StabilityGenerator()
                self.logger.info("Registered Stability AI generator")
            except Exception as e:
                self.logger.error(f"Failed to register Stability AI generator: {e}")
        
        # TODO: Add other generators as they are implemented
        # - RunwayML
        # - KreaAI  
        # - LeonardoAI
        # - HuggingFace
        
        if not self.generators:
            self.logger.warning("No image generators registered. Please configure API keys.")
    
    def get_available_generators(self) -> List[str]:
        """Get list of available generator names."""
        return list(self.generators.keys())
    
    async def generate_all(self, prompt: str, variations: int = 1) -> Dict[str, Dict[str, Any]]:
        """
        Generate images from all available providers in parallel.
        
        Args:
            prompt: Image generation prompt
            variations: Number of variations per provider (1-4)
            
        Returns:
            Dictionary mapping provider names to their results
        """
        if not self.generators:
            raise ValueError("No image generators available. Please configure API keys.")
        
        results = {}
        tasks = []
        
        # Create tasks for parallel generation
        for name, generator in self.generators.items():
            task = self._generate_with_provider(name, generator, prompt, variations)
            tasks.append(task)
        
        # Execute all tasks in parallel
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, (name, _) in enumerate(self.generators.items()):
            if isinstance(completed[i], Exception):
                self.logger.error(f"Generator {name} failed: {completed[i]}")
                results[name] = {
                    'service': name,
                    'prompt': prompt,
                    'variations_requested': variations,
                    'variations_generated': 0,
                    'images': [],
                    'errors': [str(completed[i])]
                }
            else:
                results[name] = completed[i]
        
        return results
    
    async def _generate_with_provider(
        self, 
        name: str, 
        generator: ImageGenerator, 
        prompt: str, 
        variations: int
    ) -> Dict[str, Any]:
        """Generate images with a specific provider."""
        self.logger.info(f"Generating {variations} images with {name}...")
        
        try:
            result = await generator.generate_with_metadata(prompt, variations)
            self.logger.info(f"{name} generated {result['variations_generated']} images successfully")
            return result
        except Exception as e:
            self.logger.error(f"{name} generation failed: {e}")
            raise