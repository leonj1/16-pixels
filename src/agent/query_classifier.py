import os
from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from .models import ImageQueryClassification


class QueryClassifier:
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        self.model = GeminiModel('gemini-2.5-flash')
        
        self.agent = Agent(
            self.model,
            result_type=ImageQueryClassification,
            system_prompt="""You are a query classifier that determines if a user's request is asking for image generation.

Image generation requests typically:
- Ask to create, generate, draw, design, or visualize something
- Request artwork, illustrations, pictures, or images
- Describe visual elements they want to see
- Use phrases like "show me", "create an image of", "generate a picture"

Non-image requests include:
- Questions seeking information or explanations
- Text analysis or processing tasks
- Calculations or data analysis
- Code generation or debugging
- General conversation or chat

Analyze the query and return:
- is_image_request: true if it's an image generation request
- confidence: your confidence level (0.0 to 1.0)
- image_description: a clear description of what image should be generated (if applicable)
- rejection_reason: explanation of why it's not an image request (if applicable)"""
        )
    
    async def classify(self, query: str) -> ImageQueryClassification:
        result = await self.agent.run(query)
        return result.data
    
    def classify_sync(self, query: str) -> ImageQueryClassification:
        result = self.agent.run_sync(query)
        return result.data