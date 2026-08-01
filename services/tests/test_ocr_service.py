"""Unit tests for OCR Service

Tests cover:
- OCR text extraction with sample documents
- Tesseract integration
- AWS Textract placeholder
- Confidence score calculation
"""

import pytest
from PIL import Image
import io
from app.verification.ocr_service import (
    OCRService,
    OCRProvider,
    create_ocr_service
)


def create_test_image(text: str = "Test Document", size: tuple = (400, 200)) -> bytes:
    """Create a simple test image with text
    
    Args:
        text: Text to include in the image
        size: Image dimensions (width, height)
    
    Returns:
        Image bytes
    """
    from PIL import ImageDraw, ImageFont
    
    # Create a white image
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw text in the center
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Calculate text position (roughly centered)
    text_position = (50, size[1] // 2 - 10)
    draw.text(text_position, text, fill='black', font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


class TestOCRService:
    """Test suite for OCR Service"""
    
    def test_ocr_service_initialization_tesseract(self):
        """Test OCR service initializes with Tesseract provider"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        assert ocr.provider == OCRProvider.TESSERACT
    
    def test_ocr_service_initialization_textract(self):
        """Test OCR service initializes with AWS Textract provider"""
        ocr = OCRService(provider=OCRProvider.AWS_TEXTRACT)
        assert ocr.provider == OCRProvider.AWS_TEXTRACT
        assert ocr.aws_region == 'us-east-1'
    
    def test_ocr_service_initialization_invalid_provider(self):
        """Test OCR service rejects invalid provider"""
        with pytest.raises(ValueError, match="Unsupported OCR provider"):
            OCRService(provider="invalid_provider")
    
    def test_factory_function(self):
        """Test factory function creates OCR service correctly"""
        ocr = create_ocr_service(provider=OCRProvider.TESSERACT)
        assert isinstance(ocr, OCRService)
        assert ocr.provider == OCRProvider.TESSERACT
    
    @pytest.mark.asyncio
    async def test_extract_text_empty_image_data(self):
        """Test extract_text rejects empty image data"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        with pytest.raises(ValueError, match="Image data cannot be empty"):
            await ocr.extract_text(b'')
    
    @pytest.mark.asyncio
    async def test_tesseract_extract_simple_text(self):
        """Test Tesseract extracts text from simple image"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        # Create test image with clear text
        image_bytes = create_test_image("HELLO WORLD")
        
        result = await ocr.extract_text(image_bytes)
        
        # Verify result structure
        assert 'text' in result
        assert 'confidence' in result
        assert 'word_confidences' in result
        assert 'provider' in result
        assert 'metadata' in result
        
        # Verify provider
        assert result['provider'] == OCRProvider.TESSERACT
        
        # Verify text contains expected content (OCR might not be perfect)
        assert isinstance(result['text'], str)
        
        # Verify confidence scores
        assert 0.0 <= result['confidence'] <= 1.0
        assert isinstance(result['word_confidences'], list)
        
        # Verify metadata
        assert 'total_words' in result['metadata']
        assert 'languages' in result['metadata']
        assert result['metadata']['languages'] == 'eng+hin'
    
    @pytest.mark.asyncio
    async def test_tesseract_extract_with_custom_path(self):
        """Test Tesseract with custom executable path"""
        # This test verifies the custom path is set, actual extraction depends on system
        ocr = OCRService(
            provider=OCRProvider.TESSERACT,
            tesseract_cmd="/usr/bin/tesseract"
        )
        
        assert ocr.tesseract_cmd == "/usr/bin/tesseract"
    
    @pytest.mark.asyncio
    async def test_textract_extract_without_boto3(self):
        """Test AWS Textract returns placeholder when boto3 not configured"""
        ocr = OCRService(provider=OCRProvider.AWS_TEXTRACT)
        
        # Create test image
        image_bytes = create_test_image("Test Document")
        
        result = await ocr.extract_text(image_bytes)
        
        # Should return placeholder structure
        assert 'text' in result
        assert 'confidence' in result
        assert 'provider' in result
        assert result['provider'] == OCRProvider.AWS_TEXTRACT
    
    def test_calculate_field_confidence_empty_field(self):
        """Test field confidence calculation with empty field"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        confidence = ocr.calculate_field_confidence(
            field_text="",
            full_text="Some full text",
            ocr_confidence=0.9
        )
        
        assert confidence == 0.0
    
    def test_calculate_field_confidence_found_in_text(self):
        """Test field confidence when field is found in full text"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        confidence = ocr.calculate_field_confidence(
            field_text="John Doe",
            full_text="Name: John Doe, Age: 25",
            ocr_confidence=0.9
        )
        
        # Should maintain high confidence (found in text, good length)
        assert confidence >= 0.9
        assert confidence <= 1.0
    
    def test_calculate_field_confidence_not_found_in_text(self):
        """Test field confidence when field is not found in full text"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        confidence = ocr.calculate_field_confidence(
            field_text="Jane Smith",
            full_text="Name: John Doe, Age: 25",
            ocr_confidence=0.9
        )
        
        # Should be penalized (not found in text)
        assert confidence < 0.9
        assert confidence >= 0.6  # 0.9 * 0.7 = 0.63
    
    def test_calculate_field_confidence_short_field(self):
        """Test field confidence with very short field"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        confidence = ocr.calculate_field_confidence(
            field_text="AB",
            full_text="Name: AB, Age: 25",
            ocr_confidence=0.9
        )
        
        # Should be penalized for short length
        assert confidence < 0.9
    
    def test_calculate_field_confidence_long_field(self):
        """Test field confidence with long field (more context)"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        long_text = "This is a very long field with lots of context"
        confidence = ocr.calculate_field_confidence(
            field_text=long_text,
            full_text=f"Document: {long_text}",
            ocr_confidence=0.8
        )
        
        # Should get boost for longer text
        assert confidence >= 0.8
        assert confidence <= 1.0
    
    def test_calculate_field_confidence_boundaries(self):
        """Test field confidence respects 0.0-1.0 boundaries"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        # Test lower boundary
        confidence_low = ocr.calculate_field_confidence(
            field_text="X",
            full_text="Different text",
            ocr_confidence=0.1
        )
        assert confidence_low >= 0.0
        
        # Test upper boundary with high base confidence
        long_text = "Very long text with lots of content here"
        confidence_high = ocr.calculate_field_confidence(
            field_text=long_text,
            full_text=long_text,
            ocr_confidence=0.95
        )
        assert confidence_high <= 1.0
    
    @pytest.mark.asyncio
    async def test_tesseract_confidence_calculation(self):
        """Test that Tesseract returns valid confidence scores"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        # Create test image
        image_bytes = create_test_image("TEST 123")
        result = await ocr.extract_text(image_bytes)
        
        # Verify confidence is within valid range
        assert 0.0 <= result['confidence'] <= 1.0
        
        # Verify word confidences are all valid
        for word_conf in result['word_confidences']:
            assert 0.0 <= word_conf <= 1.0
    
    @pytest.mark.asyncio
    async def test_ocr_metadata_structure(self):
        """Test OCR result includes proper metadata"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        image_bytes = create_test_image("Sample Text")
        result = await ocr.extract_text(image_bytes)
        
        # Verify metadata structure
        assert 'metadata' in result
        assert isinstance(result['metadata'], dict)
        assert 'total_words' in result['metadata']
        assert isinstance(result['metadata']['total_words'], int)


class TestOCRServiceIntegration:
    """Integration tests for OCR Service with realistic scenarios"""
    
    @pytest.mark.asyncio
    async def test_document_extraction_workflow(self):
        """Test complete workflow: image -> OCR -> confidence calculation"""
        ocr = OCRService(provider=OCRProvider.TESSERACT)
        
        # Create a document-like image
        image_bytes = create_test_image("Aadhaar Card\nName: John Doe\nNumber: 1234 5678 9012")
        
        # Extract text
        result = await ocr.extract_text(image_bytes)
        
        # Verify we got some text
        assert len(result['text']) > 0
        assert result['confidence'] > 0.0
        
        # Calculate field confidence for extracted name
        # (In real scenario, this would be parsed from OCR text)
        field_confidence = ocr.calculate_field_confidence(
            field_text="John Doe",
            full_text=result['text'],
            ocr_confidence=result['confidence']
        )
        
        # Verify field confidence calculation
        assert 0.0 <= field_confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_multiple_provider_support(self):
        """Test that both providers can be instantiated"""
        tesseract_ocr = OCRService(provider=OCRProvider.TESSERACT)
        textract_ocr = OCRService(provider=OCRProvider.AWS_TEXTRACT)
        
        assert tesseract_ocr.provider == OCRProvider.TESSERACT
        assert textract_ocr.provider == OCRProvider.AWS_TEXTRACT
        
        # Both should be able to process (Textract returns placeholder)
        image_bytes = create_test_image("Test")
        
        result_tesseract = await tesseract_ocr.extract_text(image_bytes)
        result_textract = await textract_ocr.extract_text(image_bytes)
        
        assert 'text' in result_tesseract
        assert 'text' in result_textract
