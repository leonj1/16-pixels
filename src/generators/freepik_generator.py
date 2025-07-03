import os
from typing import List, Optional, Dict, Any
from PIL import Image
import io
import httpx
import asyncio
from .base import ImageGenerator


class FreePikGenerator(ImageGenerator):
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('FREEPIK_API_KEY')
        super().__init__(api_key)
        self.base_url = "https://api.freepik.com/v1"
    
    def get_service_name(self) -> str:
        return "freepik"
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def generate(self, prompt: str, variations: int = 1) -> List[Image.Image]:
        if not self.is_available():
            raise ValueError("FreePik API key not configured")
        
        images = []
        
        # Add pixel art style to the prompt
        enhanced_prompt = f"{prompt}, pixel art style, 16-bit, retro game sprite"
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Generate images
                for i in range(variations):
                    payload = {
                        "prompt": enhanced_prompt,
                        "num_images": 1,
                        "image": {
                            "size": "square"  # FreePik's closest to 1:1 aspect ratio
                        },
                        "styling": {
                            "style": "digital-art"
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/ai/text-to-image",
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    
                    if response.status_code != 200:
                        self.logger.error(f"FreePik API error: {response.status_code} - {response.text}")
                        raise Exception(f"FreePik API returned status {response.status_code}")
                    
                    result = response.json()
                    
                    # Extract image URL from response
                    if "data" in result and len(result["data"]) > 0:
                        image_url = result["data"][0].get("url")
                        if image_url:
                            # Download the image
                            image_response = await client.get(image_url)
                            image = Image.open(io.BytesIO(image_response.content))
                            images.append(image)
                    
                    # Add small delay between requests to avoid rate limiting
                    if i < variations - 1:
                        await asyncio.sleep(1)
                        
            except Exception as e:
                self.logger.error(f"Failed to generate image with FreePik: {e}")
                raise
            
        return images