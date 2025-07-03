import pytest
from PIL import Image
import numpy as np
from src.processors.pixel_art import (
    convert_to_pixel_art, 
    enhance_pixel_art_prompt,
    create_pixel_grid,
    analyze_pixel_art
)


class TestPixelArtProcessor:
    """Integration tests for pixel art processing functions."""
    
    def test_convert_to_pixel_art_basic(self):
        """Test basic pixel art conversion."""
        # Create a test image
        test_image = Image.new('RGB', (512, 512), color='red')
        
        # Convert to pixel art
        pixel_art = convert_to_pixel_art(test_image, size=16)
        
        assert pixel_art.size == (16, 16)
        assert pixel_art.mode == 'RGB'
    
    def test_convert_with_color_reduction(self):
        """Test pixel art conversion with color palette reduction."""
        # Create a gradient image with many colors
        width, height = 256, 256
        test_image = Image.new('RGB', (width, height))
        pixels = test_image.load()
        
        for x in range(width):
            for y in range(height):
                pixels[x, y] = (x, y, 128)
        
        # Convert with limited palette
        pixel_art = convert_to_pixel_art(test_image, size=16, color_palette_size=8)
        
        # Analyze the result
        analysis = analyze_pixel_art(pixel_art)
        
        assert pixel_art.size == (16, 16)
        assert analysis['unique_colors'] <= 8
    
    def test_convert_without_dithering(self):
        """Test pixel art conversion without dithering."""
        test_image = Image.new('RGB', (100, 100), color='blue')
        
        pixel_art = convert_to_pixel_art(test_image, size=16, dithering=False)
        
        assert pixel_art.size == (16, 16)
    
    def test_enhance_pixel_art_prompt(self):
        """Test prompt enhancement for pixel art."""
        # Test with prompt that doesn't mention pixel art
        prompt1 = "a cute cat"
        enhanced1 = enhance_pixel_art_prompt(prompt1)
        assert "pixel art" in enhanced1.lower()
        assert "8-bit" in enhanced1 or "16-bit" in enhanced1
        
        # Test with prompt that already mentions pixel art
        prompt2 = "a pixel art dragon sprite"
        enhanced2 = enhance_pixel_art_prompt(prompt2)
        assert enhanced2 == prompt2  # Should not add redundant keywords
    
    def test_create_pixel_grid(self):
        """Test pixel grid preview creation."""
        # Create a small test image
        test_image = Image.new('RGB', (4, 4), color='green')
        
        # Create grid preview
        preview = create_pixel_grid(test_image, pixel_size=10, grid_width=1)
        
        # Expected size: 4 pixels * 10 size + 5 grid lines * 1 width = 45x45
        expected_size = 4 * 10 + 5 * 1
        assert preview.size == (expected_size, expected_size)
    
    def test_analyze_pixel_art(self):
        """Test pixel art analysis."""
        # Create a test image with known properties
        test_image = Image.new('RGB', (8, 8))
        pixels = test_image.load()
        
        # Fill with 4 different colors
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for x in range(8):
            for y in range(8):
                color_index = (x // 4) * 2 + (y // 4)
                pixels[x, y] = colors[color_index]
        
        analysis = analyze_pixel_art(test_image)
        
        assert analysis['dimensions'] == (8, 8)
        assert analysis['total_pixels'] == 64
        assert analysis['unique_colors'] == 4
        assert len(analysis['dominant_colors']) <= 5
        assert analysis['mode'] == 'RGB'
    
    def test_convert_non_rgb_image(self):
        """Test conversion of non-RGB images."""
        # Create RGBA image
        test_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        
        pixel_art = convert_to_pixel_art(test_image, size=16)
        
        assert pixel_art.mode == 'RGB'
        assert pixel_art.size == (16, 16)