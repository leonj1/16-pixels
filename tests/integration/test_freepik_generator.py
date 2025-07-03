import pytest
import os
from PIL import Image
from src.generators.freepik_generator import FreePikGenerator


class TestFreePikGenerator:
    """Integration tests for FreePik image generation."""
    
    @pytest.mark.asyncio
    async def test_generate_single_image(self):
        """Test generating a single image."""
        # Skip if no FreePik API key
        if not os.getenv('FREEPIK_API_KEY') or os.getenv('FREEPIK_API_KEY').startswith('test_'):
            pytest.skip("FreePik API key not configured")
        
        generator = FreePikGenerator()
        prompt = "a colorful pixel art gem"
        
        images = await generator.generate(prompt, variations=1)
        
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)
        # FreePik image size may vary
        assert images[0].size[0] > 0 and images[0].size[1] > 0
    
    @pytest.mark.asyncio
    async def test_generate_multiple_variations(self):
        """Test generating multiple variations."""
        # Skip if no FreePik API key
        if not os.getenv('FREEPIK_API_KEY') or os.getenv('FREEPIK_API_KEY').startswith('test_'):
            pytest.skip("FreePik API key not configured")
        
        generator = FreePikGenerator()
        prompt = "a pixel art style sword icon"
        variations = 2
        
        images = await generator.generate(prompt, variations=variations)
        
        assert len(images) == variations
        for image in images:
            assert isinstance(image, Image.Image)
    
    def test_service_name(self):
        """Test service name getter."""
        generator = FreePikGenerator(api_key="dummy_key")
        assert generator.get_service_name() == "freepik"
    
    def test_is_available_with_key(self):
        """Test availability check with API key."""
        generator = FreePikGenerator(api_key="dummy_key")
        assert generator.is_available() == True
    
    def test_is_available_without_key(self, monkeypatch):
        """Test availability check without API key."""
        monkeypatch.delenv('FREEPIK_API_KEY', raising=False)
        generator = FreePikGenerator()
        assert generator.is_available() == False
    
    @pytest.mark.asyncio
    async def test_generate_without_api_key(self, monkeypatch):
        """Test that generation fails without API key."""
        monkeypatch.delenv('FREEPIK_API_KEY', raising=False)
        generator = FreePikGenerator()
        
        with pytest.raises(ValueError, match="FreePik API key not configured"):
            await generator.generate("test prompt")