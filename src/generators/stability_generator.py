import os
from typing import List, Optional
from PIL import Image
import io
import base64
import httpx
from .base import ImageGenerator


class StabilityGenerator(ImageGenerator):
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('STABILITY_API_KEY')
        super().__init__(api_key)
        self.base_url = "https://api.stability.ai/v1"
    
    def get_service_name(self) -> str:
        return "stability"
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def generate(self, prompt: str, variations: int = 1) -> List[Image.Image]:
        if not self.is_available():
            raise ValueError("Stability API key not configured")
        
        images = []
        
        # Add pixel art style to the prompt
        enhanced_prompt = f"{prompt}, pixel art style, 16-bit, retro game sprite, pixelated"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                for i in range(variations):
                    payload = {
                        "text_prompts": [
                            {
                                "text": enhanced_prompt,
                                "weight": 1.0
                            }
                        ],
                        "cfg_scale": 7,
                        "height": 512,
                        "width": 512,
                        "samples": 1,
                        "steps": 30,
                        "style_preset": "digital-art"
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/generation/stable-diffusion-v1-6/text-to-image",
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    
                    if response.status_code != 200:
                        self.logger.error(f"Stability API error: {response.status_code} - {response.text}")
                        raise Exception(f"Stability API returned status {response.status_code}")
                    
                    result = response.json()
                    
                    # Extract image from base64
                    if "artifacts" in result and len(result["artifacts"]) > 0:
                        for artifact in result["artifacts"]:
                            if artifact.get("finishReason") == "SUCCESS":
                                image_data = base64.b64decode(artifact["base64"])
                                image = Image.open(io.BytesIO(image_data))
                                images.append(image)
                                break
                        
            except Exception as e:
                self.logger.error(f"Failed to generate image with Stability: {e}")
                raise
            
        return images