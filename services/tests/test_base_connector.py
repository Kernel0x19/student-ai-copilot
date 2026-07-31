"""Unit tests for BaseConnector class

Tests the base connector interface including fetch, parse, validate, and run methods,
as well as error handling and logging functionality.
"""

import pytest
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

from app.ingestion.connectors.base import (
    BaseConnector,
    STANDARD_OPPORTUNITY_SCHEMA,
    get_schema_documentation
)


class MockSuccessConnector(BaseConnector):
    """Mock connector that succeeds"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Return mock raw data"""
        return [
            {'raw_title': 'Scholarship 1', 'raw_desc': 'Description 1'},
            {'raw_title': 'Scholarship 2', 'raw_desc': 'Description 2'},
        ]
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform raw data into standard schema"""
        return [
            {
                'title': item['raw_title'],
                'description': item['raw_desc'],
                'deadline': '2024-12-31',
                'source_url': 'https://example.com/opportunity',
                'source': 'MockSource',
                'category': 'scholarship'
            }
            for item in raw_data
        ]


class MockFailingFetchConnector(BaseConnector):
    """Mock connector that fails during fetch"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Raise an exception"""
        raise ConnectionError("Failed to connect to data source")
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Should not be called"""
        return []


class MockFailingParseConnector(BaseConnector):
    """Mock connector that fails during parse"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Return raw data"""
        return [{'raw': 'data'}]
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Raise an exception"""
        raise ValueError("Failed to parse data")


class MockInvalidDataConnector(BaseConnector):
    """Mock connector that returns invalid data"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Return raw data"""
        return [
            {'raw_title': 'Valid Item'},
            {'raw_title': 'Invalid Item'},
        ]
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return mix of valid and invalid records"""
        return [
            {
                'title': 'Valid Scholarship',
                'description': 'A valid scholarship',
                'deadline': '2024-12-31',
                'source_url': 'https://example.com/valid'
            },
            {
                'title': 'Invalid Scholarship',
                # Missing description, deadline, and source_url
            }
        ]


@pytest.mark.asyncio
class TestBaseConnector:
    """Test suite for BaseConnector class"""
    
    async def test_initialization(self):
        """Test connector initialization with config"""
        config = {'api_key': 'test123', 'timeout': 30}
        connector = MockSuccessConnector(config)
        
        assert connector.config == config
        assert connector.name == 'MockSuccessConnector'
        assert connector.last_run is None
        assert connector.last_error is None
    
    async def test_successful_run(self):
        """Test successful connector execution"""
        connector = MockSuccessConnector({})
        result = await connector.run()
        
        assert result['success'] is True
        assert result['connector'] == 'MockSuccessConnector'
        assert result['count'] == 2
        assert len(result['records']) == 2
        assert 'timestamp' in result
        assert 'execution_time_seconds' in result
        
        # Check that records have expected fields
        for record in result['records']:
            assert 'title' in record
            assert 'description' in record
            assert 'deadline' in record
            assert 'source_url' in record
        
        # Check metadata updated
        assert connector.last_run is not None
        assert connector.last_error is None
    
    async def test_fetch_failure(self):
        """Test connector handles fetch failures gracefully"""
        connector = MockFailingFetchConnector({})
        result = await connector.run()
        
        assert result['success'] is False
        assert result['connector'] == 'MockFailingFetchConnector'
        assert 'error' in result
        assert 'Failed to connect' in result['error']
        assert 'records' not in result
        
        # Check metadata updated
        assert connector.last_error is not None
        assert 'Failed to connect' in connector.last_error
    
    async def test_parse_failure(self):
        """Test connector handles parse failures gracefully"""
        connector = MockFailingParseConnector({})
        result = await connector.run()
        
        assert result['success'] is False
        assert result['connector'] == 'MockFailingParseConnector'
        assert 'error' in result
        assert 'Failed to parse' in result['error']
        
        # Check metadata updated
        assert connector.last_error is not None
        assert 'Failed to parse' in connector.last_error
    
    async def test_validation_filters_invalid_records(self):
        """Test that validation filters out invalid records"""
        connector = MockInvalidDataConnector({})
        result = await connector.run()
        
        assert result['success'] is True
        assert result['count'] == 1  # Only 1 valid record
        assert len(result['records']) == 1
        
        # Check that the valid record is present
        assert result['records'][0]['title'] == 'Valid Scholarship'
    
    async def test_validate_required_fields(self):
        """Test validation checks required fields"""
        connector = MockSuccessConnector({})
        
        # Valid record
        valid_data = {
            'title': 'Test',
            'description': 'Test desc',
            'deadline': '2024-12-31',
            'source_url': 'https://example.com'
        }
        assert await connector.validate(valid_data) is True
        
        # Invalid records - missing required fields
        invalid_data_no_title = {
            'description': 'Test desc',
            'deadline': '2024-12-31',
            'source_url': 'https://example.com'
        }
        assert await connector.validate(invalid_data_no_title) is False
        
        invalid_data_no_deadline = {
            'title': 'Test',
            'description': 'Test desc',
            'source_url': 'https://example.com'
        }
        assert await connector.validate(invalid_data_no_deadline) is False
    
    async def test_multiple_runs_update_metadata(self):
        """Test that multiple runs update last_run correctly"""
        connector = MockSuccessConnector({})
        
        # First run
        result1 = await connector.run()
        first_run_time = connector.last_run
        
        assert result1['success'] is True
        assert first_run_time is not None
        
        # Wait a bit (in real scenario)
        # Second run should update last_run
        result2 = await connector.run()
        second_run_time = connector.last_run
        
        assert result2['success'] is True
        assert second_run_time is not None
        assert second_run_time >= first_run_time
    
    @patch('app.ingestion.connectors.base.logger')
    async def test_logging_on_success(self, mock_logger):
        """Test that successful runs generate appropriate log messages"""
        connector = MockSuccessConnector({})
        await connector.run()
        
        # Check that info logs were called
        mock_logger.info.assert_called()
        
        # Check for specific log messages
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Starting connector run' in str(call) for call in log_calls)
        assert any('Completed successfully' in str(call) for call in log_calls)
    
    @patch('app.ingestion.connectors.base.logger')
    async def test_logging_on_failure(self, mock_logger):
        """Test that failed runs generate error log messages"""
        connector = MockFailingFetchConnector({})
        await connector.run()
        
        # Check that error log was called
        mock_logger.error.assert_called()
        
        # Check error message content
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any('Execution failed' in str(call) for call in error_calls)
    
    async def test_execution_time_tracking(self):
        """Test that execution time is tracked"""
        connector = MockSuccessConnector({})
        result = await connector.run()
        
        assert 'execution_time_seconds' in result
        assert isinstance(result['execution_time_seconds'], float)
        assert result['execution_time_seconds'] >= 0


class TestSchemaDocumentation:
    """Test suite for schema documentation"""
    
    def test_schema_constant_exists(self):
        """Test that STANDARD_OPPORTUNITY_SCHEMA is defined"""
        assert STANDARD_OPPORTUNITY_SCHEMA is not None
        assert isinstance(STANDARD_OPPORTUNITY_SCHEMA, dict)
    
    def test_schema_has_required_fields(self):
        """Test that schema defines required fields"""
        required_fields = ['title', 'description', 'deadline', 'source_url']
        
        for field in required_fields:
            assert field in STANDARD_OPPORTUNITY_SCHEMA
    
    def test_schema_documentation_function(self):
        """Test that schema documentation function returns string"""
        doc = get_schema_documentation()
        
        assert isinstance(doc, str)
        assert len(doc) > 0
        assert 'Standard Opportunity Schema' in doc
        assert 'Required Fields' in doc
        assert 'Optional Fields' in doc


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    async def test_empty_fetch_result(self):
        """Test connector handles empty fetch results"""
        class EmptyConnector(BaseConnector):
            async def fetch(self) -> List[Dict[str, Any]]:
                return []
            
            async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                return []
        
        connector = EmptyConnector({})
        result = await connector.run()
        
        assert result['success'] is True
        assert result['count'] == 0
        assert result['records'] == []
    
    async def test_empty_config(self):
        """Test connector works with empty config"""
        connector = MockSuccessConnector({})
        result = await connector.run()
        
        assert result['success'] is True
    
    async def test_config_with_various_types(self):
        """Test connector handles various config types"""
        config = {
            'string': 'value',
            'number': 123,
            'boolean': True,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'none': None
        }
        
        connector = MockSuccessConnector(config)
        
        assert connector.config == config
        result = await connector.run()
        assert result['success'] is True
