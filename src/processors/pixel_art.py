from PIL import Image
import numpy as np
from typing import Optional, Tuple


def convert_to_pixel_art(
    image: Image.Image, 
    size: int = 16,
    color_palette_size: int = 32,
    dithering: bool = True
) -> Image.Image:
    """
    Convert an image to pixel art style with specified dimensions.
    
    Args:
        image: Input PIL Image
        size: Target size (will create size x size image)
        color_palette_size: Number of colors in the final palette
        dithering: Whether to apply dithering for smoother color transitions
        
    Returns:
        PIL Image in pixel art style
    """
    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Step 1: Resize to target size using nearest neighbor for sharp pixels
    resized = image.resize((size, size), Image.Resampling.NEAREST)
    
    # Step 2: Reduce color palette
    if dithering:
        # Convert to P mode with dithering for better color distribution
        quantized = resized.convert('P', palette=Image.ADAPTIVE, colors=color_palette_size, dither=Image.FLOYDSTEINBERG)
    else:
        # Simple color quantization without dithering
        quantized = resized.convert('P', palette=Image.ADAPTIVE, colors=color_palette_size, dither=Image.NONE)
    
    # Convert back to RGB for consistency
    final_image = quantized.convert('RGB')
    
    return final_image


def enhance_pixel_art_prompt(prompt: str) -> str:
    """
    Enhance a prompt to better generate pixel art style images.
    
    Args:
        prompt: Original user prompt
        
    Returns:
        Enhanced prompt optimized for pixel art generation
    """
    pixel_art_keywords = [
        "pixel art style",
        "8-bit",
        "16-bit", 
        "retro game sprite",
        "low resolution",
        "pixelated",
        "simple shapes",
        "limited color palette"
    ]
    
    # Add pixel art keywords if not already present
    enhanced = prompt
    if not any(keyword in prompt.lower() for keyword in ["pixel", "8-bit", "16-bit", "sprite"]):
        enhanced = f"{prompt}, {', '.join(pixel_art_keywords[:3])}"
    
    return enhanced


def create_pixel_grid(
    image: Image.Image,
    pixel_size: int = 20,
    grid_color: Tuple[int, int, int] = (128, 128, 128),
    grid_width: int = 1
) -> Image.Image:
    """
    Create a larger preview image with visible pixel grid for better visualization.
    
    Args:
        image: 16x16 pixel art image
        pixel_size: Size of each pixel in the preview
        grid_color: RGB color for the grid lines
        grid_width: Width of grid lines
        
    Returns:
        Enlarged image with pixel grid
    """
    # Get original dimensions
    width, height = image.size
    
    # Calculate new dimensions
    new_width = width * pixel_size + (width + 1) * grid_width
    new_height = height * pixel_size + (height + 1) * grid_width
    
    # Create new image with grid color background
    preview = Image.new('RGB', (new_width, new_height), grid_color)
    
    # Place each pixel
    for y in range(height):
        for x in range(width):
            pixel_color = image.getpixel((x, y))
            
            # Calculate position in preview
            px = x * (pixel_size + grid_width) + grid_width
            py = y * (pixel_size + grid_width) + grid_width
            
            # Draw the pixel
            for dy in range(pixel_size):
                for dx in range(pixel_size):
                    preview.putpixel((px + dx, py + dy), pixel_color)
    
    return preview


def analyze_pixel_art(image: Image.Image) -> dict:
    """
    Analyze a pixel art image and return statistics.
    
    Args:
        image: Pixel art image to analyze
        
    Returns:
        Dictionary with analysis results
    """
    # Convert to numpy array for analysis
    img_array = np.array(image)
    
    # Get unique colors
    unique_colors = len(np.unique(img_array.reshape(-1, 3), axis=0))
    
    # Calculate color distribution
    colors, counts = np.unique(img_array.reshape(-1, 3), axis=0, return_counts=True)
    
    # Find dominant colors
    sorted_indices = np.argsort(counts)[::-1]
    dominant_colors = [tuple(colors[i]) for i in sorted_indices[:5]]
    
    return {
        'dimensions': image.size,
        'total_pixels': image.size[0] * image.size[1],
        'unique_colors': unique_colors,
        'dominant_colors': dominant_colors,
        'mode': image.mode
    }