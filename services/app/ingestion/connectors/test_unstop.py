"""Unit tests for Unstop Connector

Tests the Unstop connector's API integration placeholder, configuration validation,
skip logic, schema validation, and parsing logic.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from .unstop import UnstopConnector


class TestUnstopConnector:
    """Test suite for Unstop Connector"""
    
    @pytest.fixture
    def connector_with_credentials(self):
        """Create a connector instance with API credentials configured"""
        config = {
            'unstop_api_key': 'test_api_key_12345',
            'rate_limit_delay': 0.1,  # Faster for tests
            'timeout': 5.0
        }
        return UnstopConnector(config)
    
    @pytest.fixture
    def connector_without_credentials(self):
        """Create a connector instance without API credentials (skip mode)"""
        config = {
            'rate_limit_delay': 0.1,
            'timeout': 5.0
        }
        return UnstopConnector(config)
    
    @pytest.fixture
    def sample_api_response(self):
        """Sample Unstop API response"""
        return {
            'success': True,
            'data': [
                {
                    'id': 'hack-123',
                    'name': 'AI Innovation Hackathon 2024',
                    'description': 'Build innovative AI solutions in 48 hours. Prize pool of Rs 5 lakh.',
                    'type': 'hackathon',
                    'end_date': '2024-12-31T23:59:59Z',
                    'url': 'https://unstop.com/hackathons/ai-innovation-123',
                    'apply_url': 'https://unstop.com/apply/ai-innovation-123',
                    'prize': '500000',
                    'location': 'Online',
                    'organizer': 'Tech Corp',
                    'tags': ['ai', 'machine-learning', 'innovation']
                },
                {
                    'id': 'comp-456',
                    'name': 'Data Science Challenge',
                    'description': 'Solve real-world data problems and win exciting prizes.',
                    'type': 'competition',
                    'end_date': '2025-01-15T18:00:00Z',
                    'url': 'https://unstop.com/competitions/data-science-456',
                    'prize': 'Rs 100000',
                    'eligibility': {
                        'min_year': 2,
                        'max_year': 4,
                        'streams': ['Computer Science', 'Engineering']
                    }
                }
            ],
            'meta': {
                'total': 2,
                'limit': 100,
                'offset': 0
            }
        }
    
    def test_connector_initialization_with_credentials(self, connector_with_credentials):
        """Test connector initializes correctly with API credentials"""
        assert connector_with_credentials.name == "UnstopConnector"
        assert connector_with_credentials.api_key == 'test_api_key_12345'
        assert connector_with_credentials.credentials_configured is True
        assert connector_with_credentials.rate_limit_delay == 0.1
        assert connector_with_credentials.timeout == 5.0
    
    def test_connector_initialization_without_credentials(self, connector_without_credentials):
        """Test connector initializes in skip mode without credentials"""
        assert connector_without_credentials.name == "UnstopConnector"
        assert connector_without_credentials.api_key is None
        assert connector_without_credentials.credentials_configured is False
    
    def test_opportunity_type_mapping(self, connector_with_credentials):
        """Test opportunity type mapping is correctly defined"""
        assert connector_with_credentials.OPPORTUNITY_TYPE_MAP['hackathon'] == 'hackathon'
        assert connector_with_credentials.OPPORTUNITY_TYPE_MAP['competition'] == 'competition'
        assert connector_with_credentials.OPPORTUNITY_TYPE_MAP['workshop'] == 'workshop'
        assert connector_with_credentials.OPPORTUNITY_TYPE_MAP['challenge'] == 'competition'
        assert connector_with_credentials.OPPORTUNITY_TYPE_MAP['event'] == 'event'
    
    def test_build_auth_headers_with_key(self, connector_with_credentials):
        """Test authentication headers are built correctly"""
        headers = connector_with_credentials._build_auth_headers()
        
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test_api_key_12345'
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/json'
        assert 'User-Agent' in headers
    
    def test_build_auth_headers_with_secret(self):
        """Test authentication headers include API secret when configured"""
        config = {
            'unstop_api_key': 'test_key',
            'unstop_api_secret': 'test_secret'
        }
        connector = UnstopConnector(config)
        headers = connector._build_auth_headers()
        
        assert headers['Authorization'] == 'Bearer test_key'
        assert headers['X-API-Secret'] == 'test_secret'
    
    def test_validate_response_schema_valid(self, connector_with_credentials, sample_api_response):
        """Test response schema validation accepts valid response"""
        is_valid = connector_with_credentials._validate_response_schema(sample_api_response)
        
        assert is_valid is True
    
    def test_validate_response_schema_missing_data(self, connector_with_credentials):
        """Test response schema validation rejects response missing 'data' key"""
        invalid_response = {'success': True, 'message': 'OK'}
        
        is_valid = connector_with_credentials._validate_response_schema(invalid_response)
        
        assert is_valid is False
    
    def test_validate_response_schema_data_not_list(self, connector_with_credentials):
        """Test response schema validation rejects non-list 'data'"""
        invalid_response = {'data': 'not a list'}
        
        is_valid = connector_with_credentials._validate_response_schema(invalid_response)
        
        assert is_valid is False
    
    def test_validate_response_schema_not_dict(self, connector_with_credentials):
        """Test response schema validation rejects non-dictionary response"""
        is_valid = connector_with_credentials._validate_response_schema("not a dict")
        
        assert is_valid is False
    
    def test_validate_opportunity_schema_valid(self, connector_with_credentials):
        """Test opportunity schema validation accepts valid opportunity"""
        valid_opp = {
            'id': 'test-123',
            'name': 'Test Hackathon',
            'type': 'hackathon',
            'url': 'https://example.com/test',
            'description': 'Test description',
            'end_date': '2024-12-31'
        }
        
        is_valid = connector_with_credentials._validate_opportunity_schema(valid_opp)
        
        assert is_valid is True
    
    def test_validate_opportunity_schema_missing_required(self, connector_with_credentials):
        """Test opportunity schema validation rejects opportunity missing required fields"""
        invalid_opp = {
            'id': 'test-123',
            'description': 'Missing name, type, and url'
        }
        
        is_valid = connector_with_credentials._validate_opportunity_schema(invalid_opp)
        
        assert is_valid is False
    
    def test_parse_api_date_iso_format(self, connector_with_credentials):
        """Test parsing ISO format date with time"""
        date_str = '2024-12-31T23:59:59Z'
        
        result = connector_with_credentials._parse_api_date(date_str)
        
        assert result == '2024-12-31'
    
    def test_parse_api_date_date_only(self, connector_with_credentials):
        """Test parsing date-only format"""
        date_str = '2024-12-31'
        
        result = connector_with_credentials._parse_api_date(date_str)
        
        assert result == '2024-12-31'
    
    def test_parse_api_date_none(self, connector_with_credentials):
        """Test parsing None date"""
        result = connector_with_credentials._parse_api_date(None)
        
        assert result is None
    
    def test_parse_api_date_invalid(self, connector_with_credentials):
        """Test parsing invalid date format"""
        result = connector_with_credentials._parse_api_date('invalid-date')
        
        assert result is None
    
    def test_parse_prize_amount_integer(self, connector_with_credentials):
        """Test parsing prize amount from integer"""
        result = connector_with_credentials._parse_prize_amount(50000)
        
        assert result == 50000
    
    def test_parse_prize_amount_float(self, connector_with_credentials):
        """Test parsing prize amount from float"""
        result = connector_with_credentials._parse_prize_amount(50000.0)
        
        assert result == 50000
    
    def test_parse_prize_amount_string_with_currency(self, connector_with_credentials):
        """Test parsing prize amount from string with currency symbols"""
        test_cases = [
            ('Rs 50000', 50000),
            ('₹50,000', 50000),
            ('50000', 50000),
            ('Rs. 1,00,000', 100000),
        ]
        
        for input_str, expected in test_cases:
            result = connector_with_credentials._parse_prize_amount(input_str)
            assert result == expected, f"Failed for input: {input_str}"
    
    def test_parse_prize_amount_none(self, connector_with_credentials):
        """Test parsing None prize amount"""
        result = connector_with_credentials._parse_prize_amount(None)
        
        assert result is None
    
    def test_extract_tags_basic(self, connector_with_credentials):
        """Test extracting basic tags"""
        data = {
            'tags': ['ai', 'ml'],
            'categories': ['technical']
        }
        
        result = connector_with_credentials._extract_tags(data, 'hackathon')
        
        assert 'unstop' in result
        assert 'hackathon' in result
        assert 'ai' in result
        assert 'ml' in result
        assert 'technical' in result
    
    def test_extract_tags_technical_type(self, connector_with_credentials):
        """Test technical tag added for hackathon/competition types"""
        result = connector_with_credentials._extract_tags({}, 'hackathon')
        
        assert 'technical' in result
    
    def test_parse_eligibility_dict(self, connector_with_credentials):
        """Test parsing eligibility from dictionary"""
        eligibility_data = {
            'min_year': 2,
            'max_year': 4,
            'streams': ['Computer Science']
        }
        
        result = connector_with_credentials._parse_eligibility(eligibility_data)
        
        assert result['min_year'] == 2
        assert result['max_year'] == 4
        assert result['streams'] == ['Computer Science']
    
    def test_parse_eligibility_string(self, connector_with_credentials):
        """Test parsing eligibility from string"""
        eligibility_data = 'Open to all undergraduate students'
        
        result = connector_with_credentials._parse_eligibility(eligibility_data)
        
        assert result['description'] == 'Open to all undergraduate students'
    
    @pytest.mark.asyncio
    async def test_fetch_without_credentials_raises_error(self, connector_without_credentials):
        """Test that fetch raises ValueError when credentials not configured"""
        with pytest.raises(ValueError, match="Unstop API key not configured"):
            await connector_without_credentials.fetch()
    
    @pytest.mark.asyncio
    @patch('app.ingestion.connectors.unstop.httpx.AsyncClient')
    async def test_fetch_with_credentials_success(
        self, mock_client_class, connector_with_credentials, sample_api_response
    ):
        """Test successful fetch from Unstop API with credentials"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true, "data": []}'
        mock_response.json = Mock(return_value=sample_api_response)
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        
        mock_client_class.return_value = mock_client
        
        # Override rate limit for faster test
        connector_with_credentials.rate_limit_delay = 0.01
        
        raw_data = await connector_with_credentials.fetch()
        
        assert len(raw_data) == 2
        assert raw_data[0]['data']['id'] == 'hack-123'
        assert raw_data[1]['data']['id'] == 'comp-456'
    
    @pytest.mark.asyncio
    async def test_fetch_invalid_response_schema(self, connector_with_credentials):
        """Test fetch raises error for invalid response schema"""
        # Test the _validate_response_schema method directly
        invalid_response = {'invalid': 'schema'}
        
        is_valid = connector_with_credentials._validate_response_schema(invalid_response)
        
        # Validation should fail for invalid schema
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_parse_valid_data(self, connector_with_credentials, sample_api_response):
        """Test parsing of valid API response data"""
        raw_data = [
            {
                'data': sample_api_response['data'][0],
                'api_index': 0,
                'fetched_at': datetime.utcnow().isoformat()
            }
        ]
        
        parsed = await connector_with_credentials.parse(raw_data)
        
        assert len(parsed) == 1
        record = parsed[0]
        
        # Check required fields
        assert record['title'] == 'AI Innovation Hackathon 2024'
        assert 'AI solutions' in record['description']
        assert record['deadline'] == '2024-12-31'
        assert record['source_url'] == 'https://unstop.com/hackathons/ai-innovation-123'
        assert record['application_url'] == 'https://unstop.com/apply/ai-innovation-123'
        
        # Check mapped fields
        assert record['source'] == 'Unstop'
        assert record['category'] == 'hackathon'
        assert record['amount'] == 500000
        assert record['location'] == 'Online'
        assert record['company'] == 'Tech Corp'
        assert record['external_id'] == 'hack-123'
        
        # Check tags
        assert 'unstop' in record['tags']
        assert 'hackathon' in record['tags']
        assert 'ai' in record['tags']
    
    @pytest.mark.asyncio
    async def test_parse_multiple_opportunities(self, connector_with_credentials, sample_api_response):
        """Test parsing multiple opportunities"""
        raw_data = [
            {
                'data': opp,
                'api_index': idx,
                'fetched_at': datetime.utcnow().isoformat()
            }
            for idx, opp in enumerate(sample_api_response['data'])
        ]
        
        parsed = await connector_with_credentials.parse(raw_data)
        
        assert len(parsed) == 2
        assert parsed[0]['category'] == 'hackathon'
        assert parsed[1]['category'] == 'competition'
        assert 'eligibility_rules' in parsed[1]
        assert parsed[1]['eligibility_rules']['min_year'] == 2
    
    @pytest.mark.asyncio
    async def test_parse_skips_invalid_opportunities(self, connector_with_credentials):
        """Test that parse skips opportunities with invalid schema"""
        raw_data = [
            {
                'data': {
                    'id': 'valid-1',
                    'name': 'Valid Opportunity',
                    'type': 'hackathon',
                    'url': 'https://example.com/1',
                    'description': 'Valid'
                },
                'api_index': 0,
                'fetched_at': datetime.utcnow().isoformat()
            },
            {
                'data': {
                    'id': 'invalid-2',
                    # Missing required fields
                },
                'api_index': 1,
                'fetched_at': datetime.utcnow().isoformat()
            },
            {
                'data': {
                    'id': 'valid-3',
                    'name': 'Another Valid',
                    'type': 'competition',
                    'url': 'https://example.com/3',
                    'description': 'Valid'
                },
                'api_index': 2,
                'fetched_at': datetime.utcnow().isoformat()
            }
        ]
        
        parsed = await connector_with_credentials.parse(raw_data)
        
        # Should successfully parse 2 out of 3
        assert len(parsed) == 2
        assert parsed[0]['external_id'] == 'valid-1'
        assert parsed[1]['external_id'] == 'valid-3'
    
    @pytest.mark.asyncio
    async def test_validate_complete_record(self, connector_with_credentials):
        """Test validation of complete record"""
        record = {
            'title': 'Test Hackathon',
            'description': 'Test description',
            'deadline': '2024-12-31',
            'source_url': 'https://example.com/hackathon',
            'source': 'Unstop',
            'category': 'hackathon'
        }
        
        is_valid = await connector_with_credentials.validate(record)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_missing_required_field(self, connector_with_credentials):
        """Test validation fails when required field is missing"""
        record = {
            'title': 'Test Hackathon',
            'description': 'Test description',
            # Missing 'deadline' and 'source_url'
        }
        
        is_valid = await connector_with_credentials.validate(record)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_run_without_credentials_returns_error(self, connector_without_credentials):
        """Test run method returns error result when credentials not configured"""
        result = await connector_without_credentials.run()
        
        assert result['success'] is False
        assert result['connector'] == 'UnstopConnector'
        assert 'error' in result
        assert 'API key not configured' in result['error']
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    @patch('app.ingestion.connectors.unstop.httpx.AsyncClient')
    async def test_run_complete_pipeline(
        self, mock_client_class, connector_with_credentials, sample_api_response
    ):
        """Test complete connector pipeline (fetch -> parse -> validate -> run)"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_response.json = Mock(return_value=sample_api_response)
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        
        mock_client_class.return_value = mock_client
        
        connector_with_credentials.rate_limit_delay = 0.01
        
        result = await connector_with_credentials.run()
        
        assert result['success'] is True
        assert result['connector'] == 'UnstopConnector'
        assert result['count'] == 2  # Both opportunities should be valid
        assert 'records' in result
        assert len(result['records']) == 2
        assert 'timestamp' in result
        assert 'execution_time_seconds' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
