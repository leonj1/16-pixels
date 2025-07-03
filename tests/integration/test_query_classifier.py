import pytest
import asyncio
import os
from src.agent.query_classifier import QueryClassifier


class TestQueryClassifier:
    """Integration tests for the Pydantic AI query classifier."""
    
    @pytest.mark.asyncio
    async def test_valid_image_queries(self, sample_prompts):
        """Test that valid image generation queries are correctly classified."""
        # Skip if no Google API key
        if not os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY').startswith('test_'):
            pytest.skip("Google API key not configured")
        
        classifier = QueryClassifier()
        
        for prompt in sample_prompts['valid_image_prompts']:
            result = await classifier.classify(prompt)
            
            assert result.is_image_request == True, f"Failed to classify as image request: {prompt}"
            assert result.confidence >= 0.7, f"Low confidence for valid prompt: {prompt}"
            assert result.image_description is not None, f"No image description extracted: {prompt}"
            assert result.rejection_reason is None, f"Unexpected rejection reason: {prompt}"
    
    @pytest.mark.asyncio
    async def test_invalid_queries(self, sample_prompts):
        """Test that non-image queries are correctly rejected."""
        # Skip if no Google API key
        if not os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY').startswith('test_'):
            pytest.skip("Google API key not configured")
        
        classifier = QueryClassifier()
        
        for prompt in sample_prompts['invalid_prompts']:
            result = await classifier.classify(prompt)
            
            assert result.is_image_request == False, f"Incorrectly classified as image request: {prompt}"
            assert result.rejection_reason is not None, f"No rejection reason provided: {prompt}"
            assert result.image_description is None, f"Unexpected image description: {prompt}"
    
    def test_sync_classification(self, sample_prompts):
        """Test synchronous classification method."""
        # Skip if no Google API key
        if not os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY').startswith('test_'):
            pytest.skip("Google API key not configured")
        
        classifier = QueryClassifier()
        
        # Test with a valid image prompt
        prompt = sample_prompts['valid_image_prompts'][0]
        result = classifier.classify_sync(prompt)
        
        assert result.is_image_request == True
        assert result.confidence > 0
        assert result.image_description is not None
    
    def test_missing_api_key(self, monkeypatch):
        """Test that missing API key raises appropriate error."""
        # Remove API key
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        with pytest.raises(ValueError, match="Google API key is required"):
            QueryClassifier()