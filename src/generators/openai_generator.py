import os
from typing import List, Optional
from PIL import Image
import io
import httpx
from openai import AsyncOpenAI
from .base import ImageGenerator


class OpenAIGenerator(ImageGenerator):
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        super().__init__(api_key)
        
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def get_service_name(self) -> str:
        return "openai"
    
    def is_available(self) -> bool:
        return self.api_key is not None and self.client is not None
    
    async def generate(self, prompt: str, variations: int = 1) -> List[Image.Image]:
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")
        
        images = []
        
        # Add pixel art style to the prompt for better results
        enhanced_prompt = f"{prompt}, pixel art style, 16-bit, retro game art"
        
        try:
            # Generate multiple images in parallel
            for i in range(variations):
                response = await self.client.images.generate(
                    model="dall-e-2",  # Using DALL-E 2 as it supports smaller sizes
                    prompt=enhanced_prompt,
                    size="256x256",  # Smallest available size
                    n=1,
                    response_format="url"
                )
                
                # Download the image
                image_url = response.data[0].url
                async with httpx.AsyncClient() as http_client:
                    image_response = await http_client.get(image_url)
                    image = Image.open(io.BytesIO(image_response.content))
                    images.append(image)
                    
        except Exception as e:
            self.logger.error(f"Failed to generate image with OpenAI: {e}")
            raise
            
        return images