"""Unit tests for TEE Abstraction Layer.

Tests cover:
- TEEService abstract base class interface
- MockTEEService implementation for development
- AWSNitroTEEService placeholder validation
- AzureConfidentialTEEService placeholder validation
- TEE mode configuration and factory function
- Error handling for invalid modes and initialization failures
"""

import pytest
import logging
from app.security.tee import (
    TEEService,
    TEEMode,
    MockTEEService,
    AWSNitroTEEService,
    AzureConfidentialTEEService,
    create_tee_service,
    get_tee_processor,
)


class TestTEEMode:
    """Test TEE mode enumeration."""

    def test_tee_mode_values(self):
        """Test that TEEMode enum has correct values."""
        assert TEEMode.MOCK.value == "mock"
        assert TEEMode.AWS_NITRO.value == "aws_nitro"
        assert TEEMode.AZURE_CONFIDENTIAL.value == "azure_confidential"

    def test_tee_mode_from_string(self):
        """Test creating TEEMode from string values."""
        assert TEEMode("mock") == TEEMode.MOCK
        assert TEEMode("aws_nitro") == TEEMode.AWS_NITRO
        assert TEEMode("azure_confidential") == TEEMode.AZURE_CONFIDENTIAL

    def test_tee_mode_invalid_value(self):
        """Test that invalid mode value raises ValueError."""
        with pytest.raises(ValueError):
            TEEMode("invalid_mode")


class TestMockTEEService:
    """Test MockTEEService implementation."""

    @pytest.fixture
    def mock_tee(self):
        """Create MockTEEService instance."""
        return MockTEEService()

    @pytest.mark.asyncio
    async def test_process_secure_decrypt(self, mock_tee):
        """Test process_secure with decrypt operation.
        
        Note: In mock implementation, process_secure uses a fixed purpose for decryption.
        For real TEE implementations, the purpose/key would be managed securely.
        """
        test_data = b"sensitive document content"
        # Encrypt with the same purpose that process_secure uses for decryption
        encrypted = mock_tee.encrypt_sensitive(test_data, "document")
        
        result = await mock_tee.process_secure(encrypted, "decrypt")
        
        assert result == test_data
        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_process_secure_extract(self, mock_tee):
        """Test process_secure with extract operation."""
        test_data = b"document to extract"
        
        result = await mock_tee.process_secure(test_data, "extract")
        
        assert result == test_data

    @pytest.mark.asyncio
    async def test_process_secure_unknown_operation(self, mock_tee, caplog):
        """Test process_secure with unknown operation logs warning and returns data."""
        test_data = b"test data"
        
        with caplog.at_level(logging.WARNING):
            result = await mock_tee.process_secure(test_data, "unknown_op")
        
        assert result == test_data
        assert "Unknown operation 'unknown_op'" in caplog.text

    def test_encrypt_decrypt_symmetric(self, mock_tee):
        """Test that encrypt and decrypt are symmetric operations."""
        original = b"secret data"
        purpose = "test_purpose"
        
        encrypted = mock_tee.encrypt_sensitive(original, purpose)
        decrypted = mock_tee.decrypt_sensitive(encrypted, purpose, "test_actor")
        
        assert decrypted == original

    def test_encrypt_different_purposes(self, mock_tee):
        """Test that encryption with different purposes produces different results."""
        data = b"same data"
        
        encrypted1 = mock_tee.encrypt_sensitive(data, "purpose1")
        encrypted2 = mock_tee.encrypt_sensitive(data, "purpose2")
        
        assert encrypted1 != encrypted2

    def test_decrypt_logs_audit_info(self, mock_tee, caplog):
        """Test that decrypt_sensitive logs audit information."""
        data = b"sensitive"
        encrypted = mock_tee.encrypt_sensitive(data, "docs")
        
        with caplog.at_level(logging.INFO):
            mock_tee.decrypt_sensitive(encrypted, "docs", "user123")
        
        assert "TEE decrypt audit" in caplog.text
        assert "purpose=docs" in caplog.text
        assert "actor=user123" in caplog.text

    def test_process_in_enclave(self, mock_tee):
        """Test process_in_enclave returns expected structure."""
        payload = {"field1": "value1", "field2": "value2"}
        
        result = mock_tee.process_in_enclave("verify", payload)
        
        assert result["status"] == "processed"
        assert result["operation"] == "verify"
        assert result["verified"] is True


class TestAWSNitroTEEService:
    """Test AWSNitroTEEService placeholder."""

    @pytest.fixture
    def aws_tee(self):
        """Create AWSNitroTEEService instance."""
        return AWSNitroTEEService()

    @pytest.mark.asyncio
    async def test_process_secure_not_implemented(self, aws_tee):
        """Test that process_secure raises NotImplementedError with helpful message."""
        with pytest.raises(NotImplementedError) as exc_info:
            await aws_tee.process_secure(b"data", "decrypt")
        
        assert "AWS Nitro Enclaves integration not yet implemented" in str(exc_info.value)
        assert "deployment guide" in str(exc_info.value)

    def test_encrypt_sensitive_not_implemented(self, aws_tee):
        """Test that encrypt_sensitive raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            aws_tee.encrypt_sensitive(b"data", "purpose")
        
        assert "AWS Nitro Enclave SDK" in str(exc_info.value)

    def test_decrypt_sensitive_not_implemented(self, aws_tee):
        """Test that decrypt_sensitive raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            aws_tee.decrypt_sensitive(b"token", "purpose", "actor")
        
        assert "AWS Nitro Enclave SDK" in str(exc_info.value)

    def test_process_in_enclave_not_implemented(self, aws_tee):
        """Test that process_in_enclave raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            aws_tee.process_in_enclave("operation", {})
        
        assert "AWS Nitro Enclave SDK" in str(exc_info.value)

    def test_initialization_logs(self, caplog):
        """Test that initialization logs appropriate message."""
        with caplog.at_level(logging.INFO):
            AWSNitroTEEService()
        
        assert "Initializing AWS Nitro TEE Service" in caplog.text


class TestAzureConfidentialTEEService:
    """Test AzureConfidentialTEEService placeholder."""

    @pytest.fixture
    def azure_tee(self):
        """Create AzureConfidentialTEEService instance."""
        return AzureConfidentialTEEService()

    @pytest.mark.asyncio
    async def test_process_secure_not_implemented(self, azure_tee):
        """Test that process_secure raises NotImplementedError with helpful message."""
        with pytest.raises(NotImplementedError) as exc_info:
            await azure_tee.process_secure(b"data", "decrypt")
        
        assert "Azure Confidential Computing integration not yet implemented" in str(exc_info.value)
        assert "deployment guide" in str(exc_info.value)

    def test_encrypt_sensitive_not_implemented(self, azure_tee):
        """Test that encrypt_sensitive raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            azure_tee.encrypt_sensitive(b"data", "purpose")
        
        assert "Azure Confidential Computing SDK" in str(exc_info.value)

    def test_decrypt_sensitive_not_implemented(self, azure_tee):
        """Test that decrypt_sensitive raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            azure_tee.decrypt_sensitive(b"token", "purpose", "actor")
        
        assert "Azure Confidential Computing SDK" in str(exc_info.value)

    def test_process_in_enclave_not_implemented(self, azure_tee):
        """Test that process_in_enclave raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            azure_tee.process_in_enclave("operation", {})
        
        assert "Azure Confidential Computing SDK" in str(exc_info.value)

    def test_initialization_logs(self, caplog):
        """Test that initialization logs appropriate message."""
        with caplog.at_level(logging.INFO):
            AzureConfidentialTEEService()
        
        assert "Initializing Azure Confidential TEE Service" in caplog.text


class TestCreateTEEService:
    """Test TEE service factory function."""

    def test_create_mock_service(self):
        """Test creating mock TEE service."""
        service = create_tee_service("mock")
        
        assert isinstance(service, MockTEEService)
        assert isinstance(service, TEEService)

    def test_create_aws_nitro_service(self):
        """Test creating AWS Nitro TEE service."""
        service = create_tee_service("aws_nitro")
        
        assert isinstance(service, AWSNitroTEEService)
        assert isinstance(service, TEEService)

    def test_create_azure_confidential_service(self):
        """Test creating Azure Confidential TEE service."""
        service = create_tee_service("azure_confidential")
        
        assert isinstance(service, AzureConfidentialTEEService)
        assert isinstance(service, TEEService)

    def test_create_with_invalid_mode(self):
        """Test that invalid mode raises ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            create_tee_service("invalid_mode")
        
        assert "Invalid TEE mode: invalid_mode" in str(exc_info.value)
        assert "mock, aws_nitro, azure_confidential" in str(exc_info.value)

    def test_default_mode_is_mock(self):
        """Test that default mode creates mock service."""
        service = create_tee_service()
        
        assert isinstance(service, MockTEEService)

    def test_factory_logs_service_creation(self, caplog):
        """Test that factory logs service creation."""
        with caplog.at_level(logging.INFO):
            create_tee_service("mock")
        
        assert "Creating TEE service: MockTEEService" in caplog.text


class TestBackwardCompatibility:
    """Test backward compatibility aliases."""

    def test_get_tee_processor_creates_mock_service(self):
        """Test legacy get_tee_processor function."""
        service = get_tee_processor("mock")
        
        assert isinstance(service, MockTEEService)

    def test_get_tee_processor_default(self):
        """Test legacy get_tee_processor with default argument."""
        service = get_tee_processor()
        
        assert isinstance(service, MockTEEService)

    def test_get_tee_processor_aws_nitro(self):
        """Test legacy get_tee_processor with aws_nitro mode."""
        service = get_tee_processor("aws_nitro")
        
        assert isinstance(service, AWSNitroTEEService)


class TestTEEServiceInterface:
    """Test that all implementations conform to TEEService interface."""

    @pytest.mark.parametrize("service_class", [
        MockTEEService,
        AWSNitroTEEService,
        AzureConfidentialTEEService,
    ])
    def test_service_has_process_secure(self, service_class):
        """Test that all services implement process_secure method."""
        service = service_class()
        assert hasattr(service, 'process_secure')
        assert callable(getattr(service, 'process_secure'))

    @pytest.mark.parametrize("service_class", [
        MockTEEService,
        AWSNitroTEEService,
        AzureConfidentialTEEService,
    ])
    def test_service_has_encrypt_sensitive(self, service_class):
        """Test that all services implement encrypt_sensitive method."""
        service = service_class()
        assert hasattr(service, 'encrypt_sensitive')
        assert callable(getattr(service, 'encrypt_sensitive'))

    @pytest.mark.parametrize("service_class", [
        MockTEEService,
        AWSNitroTEEService,
        AzureConfidentialTEEService,
    ])
    def test_service_has_decrypt_sensitive(self, service_class):
        """Test that all services implement decrypt_sensitive method."""
        service = service_class()
        assert hasattr(service, 'decrypt_sensitive')
        assert callable(getattr(service, 'decrypt_sensitive'))

    @pytest.mark.parametrize("service_class", [
        MockTEEService,
        AWSNitroTEEService,
        AzureConfidentialTEEService,
    ])
    def test_service_has_process_in_enclave(self, service_class):
        """Test that all services implement process_in_enclave method."""
        service = service_class()
        assert hasattr(service, 'process_in_enclave')
        assert callable(getattr(service, 'process_in_enclave'))

    @pytest.mark.parametrize("service_class", [
        MockTEEService,
        AWSNitroTEEService,
        AzureConfidentialTEEService,
    ])
    def test_service_is_tee_service(self, service_class):
        """Test that all services inherit from TEEService."""
        service = service_class()
        assert isinstance(service, TEEService)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def mock_tee(self):
        return MockTEEService()

    @pytest.mark.asyncio
    async def test_process_secure_empty_data(self, mock_tee):
        """Test processing empty data."""
        result = await mock_tee.process_secure(b"", "decrypt")
        assert result == b""

    @pytest.mark.asyncio
    async def test_process_secure_large_data(self, mock_tee):
        """Test processing large data payload.
        
        Note: Using the same purpose ('document') that process_secure uses internally.
        """
        large_data = b"x" * 10000
        encrypted = mock_tee.encrypt_sensitive(large_data, "document")
        
        result = await mock_tee.process_secure(encrypted, "decrypt")
        
        assert result == large_data
        assert len(result) == 10000

    def test_encrypt_empty_data(self, mock_tee):
        """Test encrypting empty data."""
        encrypted = mock_tee.encrypt_sensitive(b"", "purpose")
        assert isinstance(encrypted, bytes)
        assert encrypted == b""

    def test_process_in_enclave_empty_payload(self, mock_tee):
        """Test process_in_enclave with empty payload."""
        result = mock_tee.process_in_enclave("test", {})
        
        assert result["status"] == "processed"
        assert result["operation"] == "test"
