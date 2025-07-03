import os
from typing import List, Optional
from PIL import Image
import io
import httpx
import replicate
from .base import ImageGenerator


class ReplicateGenerator(ImageGenerator):
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('REPLICATE_API_TOKEN')
        super().__init__(api_key)
        
        if self.api_key:
            os.environ['REPLICATE_API_TOKEN'] = self.api_key
    
    def get_service_name(self) -> str:
        return "replicate"
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def generate(self, prompt: str, variations: int = 1) -> List[Image.Image]:
        if not self.is_available():
            raise ValueError("Replicate API token not configured")
        
        images = []
        
        # Add pixel art style to the prompt
        enhanced_prompt = f"{prompt}, pixel art style, 16-bit, retro game sprite, low resolution"
        
        try:
            # Using Stable Diffusion through Replicate
            model = replicate.models.get("stability-ai/stable-diffusion")
            version = model.versions.get("db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf")
            
            for i in range(variations):
                # Run the model
                output = version.predict(
                    prompt=enhanced_prompt,
                    width=512,
                    height=512,
                    num_outputs=1,
                    num_inference_steps=50,
                    guidance_scale=7.5
                )
                
                # Download the generated image
                if output and len(output) > 0:
                    image_url = output[0]
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_url)
                        image = Image.open(io.BytesIO(response.content))
                        images.append(image)
                        
        except Exception as e:
            self.logger.error(f"Failed to generate image with Replicate: {e}")
            raise
            
        return images