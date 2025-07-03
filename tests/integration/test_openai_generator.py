import pytest
import os
from PIL import Image
from src.generators.openai_generator import OpenAIGenerator


class TestOpenAIGenerator:
    """Integration tests for OpenAI DALL-E image generation."""
    
    @pytest.mark.asyncio
    async def test_generate_single_image(self):
        """Test generating a single image."""
        # Skip if no OpenAI API key
        if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY').startswith('test_'):
            pytest.skip("OpenAI API key not configured")
        
        generator = OpenAIGenerator()
        prompt = "a simple pixel art heart icon"
        
        images = await generator.generate(prompt, variations=1)
        
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)
        assert images[0].size == (256, 256)  # DALL-E 2 smallest size
    
    @pytest.mark.asyncio
    async def test_generate_multiple_variations(self):
        """Test generating multiple variations."""
        # Skip if no OpenAI API key
        if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY').startswith('test_'):
            pytest.skip("OpenAI API key not configured")
        
        generator = OpenAIGenerator()
        prompt = "a pixel art style game coin"
        variations = 3
        
        images = await generator.generate(prompt, variations=variations)
        
        assert len(images) == variations
        for image in images:
            assert isinstance(image, Image.Image)
            assert image.size == (256, 256)
    
    @pytest.mark.asyncio
    async def test_generate_with_metadata(self):
        """Test generation with metadata."""
        # Skip if no OpenAI API key
        if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY').startswith('test_'):
            pytest.skip("OpenAI API key not configured")
        
        generator = OpenAIGenerator()
        prompt = "a tiny pixel art tree"
        
        result = await generator.generate_with_metadata(prompt, variations=2)
        
        assert result['service'] == 'openai'
        assert result['prompt'] == prompt
        assert result['variations_requested'] == 2
        assert result['variations_generated'] == 2
        assert len(result['images']) == 2
        assert len(result['errors']) == 0
    
    def test_service_name(self):
        """Test service name getter."""
        generator = OpenAIGenerator(api_key="dummy_key")
        assert generator.get_service_name() == "openai"
    
    def test_is_available_with_key(self):
        """Test availability check with API key."""
        generator = OpenAIGenerator(api_key="dummy_key")
        assert generator.is_available() == True
    
    def test_is_available_without_key(self, monkeypatch):
        """Test availability check without API key."""
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        generator = OpenAIGenerator()
        assert generator.is_available() == False
    
    @pytest.mark.asyncio
    async def test_generate_without_api_key(self, monkeypatch):
        """Test that generation fails without API key."""
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        generator = OpenAIGenerator()
        
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            await generator.generate("test prompt")