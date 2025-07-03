from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import json
import logging


class OutputManager:
    def __init__(self, base_dir: str = "./output"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.current_session: Optional[Path] = None
    
    def create_session_folder(self) -> Path:
        """Create a new timestamped session folder."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_path = self.base_dir / timestamp
        session_path.mkdir(parents=True, exist_ok=True)
        self.current_session = session_path
        self.logger.info(f"Created session folder: {session_path}")
        return session_path
    
    def save_image(
        self, 
        image: Image.Image, 
        provider: str, 
        variation_num: int,
        session_path: Optional[Path] = None
    ) -> Path:
        """
        Save an image to the appropriate provider folder.
        
        Args:
            image: PIL Image to save
            provider: Name of the image generation provider
            variation_num: Variation number (1-based)
            session_path: Optional session path (uses current if not provided)
            
        Returns:
            Path to the saved image
        """
        if session_path is None:
            session_path = self.current_session
            
        if session_path is None:
            raise ValueError("No session folder created. Call create_session_folder first.")
        
        # Create provider subdirectory
        provider_path = session_path / provider
        provider_path.mkdir(exist_ok=True)
        
        # Save the image
        image_filename = f"variation_{variation_num}.png"
        image_path = provider_path / image_filename
        image.save(image_path, "PNG")
        
        # Also save a preview with pixel grid
        from ..processors.pixel_art import create_pixel_grid
        preview = create_pixel_grid(image)
        preview_path = provider_path / f"variation_{variation_num}_preview.png"
        preview.save(preview_path, "PNG")
        
        self.logger.info(f"Saved image: {image_path}")
        return image_path
    
    def save_metadata(
        self,
        query: str,
        classification: Dict[str, Any],
        results: Dict[str, Any],
        session_path: Optional[Path] = None
    ) -> Path:
        """
        Save session metadata to JSON file.
        
        Args:
            query: Original user query
            classification: Query classification results
            results: Generation results from all providers
            session_path: Optional session path (uses current if not provided)
            
        Returns:
            Path to the metadata file
        """
        if session_path is None:
            session_path = self.current_session
            
        if session_path is None:
            raise ValueError("No session folder created.")
        
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'classification': classification,
            'providers': {},
            'total_images_generated': 0,
            'session_folder': str(session_path)
        }
        
        # Process results from each provider
        for provider, provider_results in results.items():
            metadata['providers'][provider] = {
                'variations_requested': provider_results.get('variations_requested', 0),
                'variations_generated': provider_results.get('variations_generated', 0),
                'errors': provider_results.get('errors', []),
                'success': len(provider_results.get('errors', [])) == 0
            }
            metadata['total_images_generated'] += provider_results.get('variations_generated', 0)
        
        # Save metadata
        metadata_path = session_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Saved metadata: {metadata_path}")
        return metadata_path
    
    def create_session_summary(self, session_path: Optional[Path] = None) -> str:
        """
        Create a text summary of the session.
        
        Args:
            session_path: Optional session path (uses current if not provided)
            
        Returns:
            Summary text
        """
        if session_path is None:
            session_path = self.current_session
            
        if session_path is None:
            return "No session available."
        
        # Count images per provider
        summary_lines = [f"Session: {session_path.name}"]
        summary_lines.append("-" * 40)
        
        total_images = 0
        for provider_dir in session_path.iterdir():
            if provider_dir.is_dir() and provider_dir.name != "__pycache__":
                image_count = len(list(provider_dir.glob("variation_*.png")))
                if image_count > 0:
                    summary_lines.append(f"{provider_dir.name}: {image_count} images")
                    total_images += image_count
        
        summary_lines.append("-" * 40)
        summary_lines.append(f"Total: {total_images} images")
        
        return "\n".join(summary_lines)