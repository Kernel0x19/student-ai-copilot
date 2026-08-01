"""Unit tests for Internshala Connector

Tests the Internshala connector's robots.txt compliance, Playwright-based scraping,
parsing logic, rate limiting, user-agent rotation, and activity logging.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

from .internshala import InternshalaConnector


class TestInternshalaConnector:
    """Test suite for Internshala Connector"""
    
    @pytest.fixture
    def connector(self):
        """Create a connector instance for testing"""
        config = {
            'rate_limit_delay': 0.1,  # Faster for tests
            'timeout': 5000,  # 5 seconds for tests
            'headless': True,
            'skip_robots_check': True  # Skip by default in tests
        }
        return InternshalaConnector(config)
    
    @pytest.fixture
    def sample_html(self):
        """Sample Internshala internship card HTML"""
        return """
        <div class="individual_internship">
            <h3 class="profile">Software Development Intern</h3>
            <div class="company-name">Tech Corp India</div>
            <div class="location">Bangalore, Remote</div>
            <div class="stipend">₹15,000 per month</div>
            <div class="duration">6 months</div>
            <div class="internship_other_details">
                Looking for 3rd year Computer Science students with knowledge of 
                Python, Django, and React. Should have good problem-solving skills.
                Deadline: 31/12/2024
            </div>
            <a href="/internship/detail/software-development-intern-123">View Details</a>
        </div>
        """
    
    def test_connector_initialization(self, connector):
        """Test connector initializes with correct configuration"""
        assert connector.name == "InternshalaConnector"
        assert connector.rate_limit_delay == 0.1
        assert connector.timeout == 5000
        assert connector.headless is True
        assert connector.base_url == "https://internshala.com"
        assert len(connector.USER_AGENTS) == 4
    
    @pytest.mark.asyncio
    async def test_check_robots_allowed(self, connector):
        """Test robots.txt check when scraping is allowed"""
        robots_text = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /internships
        """
        
        with patch('app.ingestion.connectors.internshala.httpx.AsyncClient') as mock_client_class:
            mock_response = Mock()
            mock_response.text = robots_text
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            is_allowed = await connector.check_robots()
            
            assert is_allowed is True
    
    @pytest.mark.asyncio
    async def test_check_robots_disallowed(self, connector):
        """Test robots.txt check when scraping is disallowed"""
        robots_text = """
User-agent: *
Disallow: /internships
        """
        
        with patch('app.ingestion.connectors.internshala.httpx.AsyncClient') as mock_client_class:
            mock_response = Mock()
            mock_response.text = robots_text
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            is_allowed = await connector.check_robots()
            
            assert is_allowed is False
    
    @pytest.mark.asyncio
    async def test_check_robots_fetch_failure_defaults_to_allow(self, connector):
        """Test robots.txt check defaults to allowing when fetch fails"""
        with patch('app.ingestion.connectors.internshala.httpx.AsyncClient') as mock_client_class:
            # Mock the async context manager and its methods
            mock_client = AsyncMock()
            
            # The get method should raise an exception
            async def mock_get(*args, **kwargs):
                raise Exception("Network error")
            
            mock_client.get = mock_get
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_class.return_value = mock_client
            
            is_allowed = await connector.check_robots()
            
            # Should default to allowing when robots.txt cannot be fetched
            assert is_allowed is True
    
    def test_log_activity(self, connector):
        """Test activity logging functionality"""
        # Activity logging should not raise exceptions
        connector._log_activity("test_action", {"key": "value"})
        
        # Verify it logs properly (check via logging mock if needed)
        # For now, just verify it doesn't crash
        assert True
    
    def test_extract_title(self, connector, sample_html):
        """Test title extraction from HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        title = connector._extract_title(soup)
        
        assert title == "Software Development Intern"
    
    def test_extract_title_missing(self, connector):
        """Test title extraction when element is missing"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<div></div>", 'html.parser')
        
        title = connector._extract_title(soup)
        
        assert title == "Untitled Internship"
    
    def test_extract_company(self, connector, sample_html):
        """Test company name extraction from HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        company = connector._extract_company(soup)
        
        assert company == "Tech Corp India"
    
    def test_extract_company_missing(self, connector):
        """Test company extraction when element is missing"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<div></div>", 'html.parser')
        
        company = connector._extract_company(soup)
        
        assert company is None
    
    def test_extract_location(self, connector, sample_html):
        """Test location extraction from HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        location = connector._extract_location(soup)
        
        assert location == "Bangalore, Remote"
    
    def test_extract_location_work_from_home(self, connector):
        """Test location extraction converts Work From Home to Remote"""
        from bs4 import BeautifulSoup
        html = '<div class="location">Work From Home</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        location = connector._extract_location(soup)
        
        assert location == "Remote"
    
    def test_extract_stipend(self, connector, sample_html):
        """Test stipend extraction from HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        stipend = connector._extract_stipend(soup)
        
        assert stipend == "₹15,000 per month"
    
    def test_parse_stipend_amount(self, connector):
        """Test numeric stipend amount parsing"""
        test_cases = [
            ('₹15,000 per month', 15000),
            ('Rs 10000/month', 10000),
            ('₹5,000', 5000),
            ('Unpaid', None),
        ]
        
        for input_str, expected in test_cases:
            result = connector._parse_stipend_amount(input_str)
            assert result == expected, f"Failed for {input_str}"
    
    def test_extract_duration(self, connector, sample_html):
        """Test duration extraction from HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        duration = connector._extract_duration(soup)
        
        assert duration == "6 months"
    
    def test_extract_deadline(self, connector, sample_html):
        """Test deadline extraction and normalization"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        deadline = connector._extract_deadline(soup)
        
        assert deadline == "2024-12-31"
    
    def test_normalize_date_various_formats(self, connector):
        """Test date normalization with different formats"""
        test_cases = [
            ('31/12/2024', '2024-12-31'),
            ('31-12-2024', '2024-12-31'),
            ('01/01/24', '2024-01-01'),
            ('2024-12-31', '2024-12-31'),
            ('31 Dec 2024', '2024-12-31'),
            ('31-Dec-2024', '2024-12-31'),
        ]
        
        for input_date, expected in test_cases:
            result = connector._normalize_date(input_date)
            assert result == expected, f"Failed for {input_date}"
    
    def test_extract_description(self, connector, sample_html):
        """Test description extraction from HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        description = connector._extract_description(soup)
        
        assert 'computer science' in description.lower()
        assert 'python' in description.lower()
        assert 'django' in description.lower()
    
    def test_extract_eligibility(self, connector, sample_html):
        """Test eligibility criteria extraction"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, 'html.parser')
        description = connector._extract_description(soup)
        
        eligibility = connector._extract_eligibility(soup, description)
        
        assert 'min_year' in eligibility
        assert eligibility['min_year'] == 3
        assert 'streams' in eligibility
        assert 'computer science' in eligibility['streams']
        assert 'skills' in eligibility
        assert 'python' in eligibility['skills']
    
    @pytest.mark.asyncio
    async def test_parse_valid_data(self, connector, sample_html):
        """Test parsing of valid raw data"""
        raw_data = [{
            'html': sample_html,
            'url': 'https://internshala.com/internship/detail/software-development-intern-123',
            'card_index': 0
        }]
        
        parsed = await connector.parse(raw_data)
        
        assert len(parsed) == 1
        record = parsed[0]
        
        # Check required fields
        assert record['title'] == "Software Development Intern"
        assert record['company'] == "Tech Corp India"
        assert record['location'] == "Bangalore, Remote"
        assert record['stipend'] == "₹15,000 per month"
        assert record['duration'] == "6 months"
        assert record['deadline'] == "2024-12-31"
        assert record['source_url'] == 'https://internshala.com/internship/detail/software-development-intern-123'
        
        # Check standard fields
        assert record['source'] == 'Internshala'
        assert record['category'] == 'internship'
        assert 'description' in record
        assert 'eligibility_rules' in record
        assert 'tags' in record
        assert 'internshala' in record['tags']
        
        # Check parsed amount
        assert record['amount'] == 15000
        assert record['amount_min'] == 15000
        assert record['amount_max'] == 15000
    
    @pytest.mark.asyncio
    async def test_parse_multiple_cards(self, connector):
        """Test parsing multiple internship cards"""
        raw_data = [
            {
                'html': '<div class="profile">Internship 1</div><div class="company-name">Company A</div>',
                'url': 'https://internshala.com/i1',
                'card_index': 0
            },
            {
                'html': '<div class="profile">Internship 2</div><div class="company-name">Company B</div>',
                'url': 'https://internshala.com/i2',
                'card_index': 1
            }
        ]
        
        parsed = await connector.parse(raw_data)
        
        assert len(parsed) == 2
        assert parsed[0]['title'] == "Internship 1"
        assert parsed[0]['company'] == "Company A"
        assert parsed[1]['title'] == "Internship 2"
        assert parsed[1]['company'] == "Company B"
    
    @pytest.mark.asyncio
    async def test_parse_with_errors(self, connector):
        """Test that parse continues after individual card errors"""
        raw_data = [
            {
                'html': '<div class="profile">Valid Internship</div>',
                'url': 'https://internshala.com/i1',
                'card_index': 0
            },
            {
                'html': None,  # This will cause an error
                'url': 'https://internshala.com/i2',
                'card_index': 1
            },
            {
                'html': '<div class="profile">Another Valid</div>',
                'url': 'https://internshala.com/i3',
                'card_index': 2
            }
        ]
        
        parsed = await connector.parse(raw_data)
        
        # Should successfully parse 2 out of 3
        assert len(parsed) == 2
    
    @pytest.mark.asyncio
    async def test_validate_complete_record(self, connector):
        """Test validation of complete record"""
        record = {
            'title': 'Test Internship',
            'description': 'Test description',
            'deadline': '2024-12-31',
            'source_url': 'https://internshala.com/internship/123',
            'source': 'Internshala'
        }
        
        is_valid = await connector.validate(record)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_missing_required_field(self, connector):
        """Test validation fails when required field is missing"""
        record = {
            'title': 'Test Internship',
            'description': 'Test description',
            # Missing 'deadline' and 'source_url'
        }
        
        is_valid = await connector.validate(record)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_fetch_aborts_when_robots_disallowed(self):
        """Test fetch aborts when robots.txt disallows scraping"""
        # Create connector WITH robots check enabled
        connector = InternshalaConnector({
            'skip_robots_check': False,
            'rate_limit_delay': 0.1
        })
        
        # Mock robots.txt to disallow
        robots_text = "User-agent: *\nDisallow: /internships"
        
        with patch('app.ingestion.connectors.internshala.httpx.AsyncClient') as mock_client_class:
            mock_response = Mock()
            mock_response.text = robots_text
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            # Should raise ValueError when robots.txt disallows
            with pytest.raises(ValueError, match="Robots.txt disallows"):
                await connector.fetch()
    
    @pytest.mark.asyncio
    @patch('app.ingestion.connectors.internshala.async_playwright')
    async def test_fetch_success(self, mock_playwright, connector):
        """Test successful fetch from Internshala portal using Playwright"""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        
        # Configure page mock
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.title = AsyncMock(return_value="Internships - Internshala")
        mock_page.url = "https://internshala.com/internships"
        mock_page.set_default_timeout = Mock()
        
        # Configure element mocks
        mock_element1 = AsyncMock()
        mock_element1.inner_html = AsyncMock(return_value='<div class="profile">Internship 1</div>')
        mock_element1.query_selector = AsyncMock(return_value=None)
        mock_element1.get_attribute = AsyncMock(return_value='/internship/1')
        
        mock_element2 = AsyncMock()
        mock_element2.inner_html = AsyncMock(return_value='<div class="profile">Internship 2</div>')
        mock_element2.query_selector = AsyncMock(return_value=None)
        mock_element2.get_attribute = AsyncMock(return_value='/internship/2')
        
        mock_page.query_selector_all = AsyncMock(return_value=[mock_element1, mock_element2])
        
        # Configure browser mock
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        # Configure playwright mock
        mock_p = AsyncMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
        
        mock_playwright_context = AsyncMock()
        mock_playwright_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_playwright_context.__aexit__ = AsyncMock()
        
        mock_playwright.return_value = mock_playwright_context
        
        # Override rate limit for faster test
        connector.rate_limit_delay = 0.01
        
        raw_data = await connector.fetch()
        
        assert len(raw_data) == 2
        assert raw_data[0]['url'] == 'https://internshala.com/internship/1'
        assert raw_data[1]['url'] == 'https://internshala.com/internship/2'
    
    @pytest.mark.asyncio
    @patch('app.ingestion.connectors.internshala.async_playwright')
    async def test_run_complete_pipeline(self, mock_playwright, connector, sample_html):
        """Test complete connector pipeline (fetch -> parse -> validate -> run)"""
        # Mock Playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.title = AsyncMock(return_value="Internships")
        mock_page.url = "https://internshala.com/internships"
        mock_page.set_default_timeout = Mock()
        
        mock_element = AsyncMock()
        mock_element.inner_html = AsyncMock(return_value=sample_html)
        mock_element.query_selector = AsyncMock(return_value=None)
        mock_element.get_attribute = AsyncMock(return_value='/internship/123')
        
        mock_page.query_selector_all = AsyncMock(return_value=[mock_element])
        
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_p = AsyncMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
        
        mock_playwright_context = AsyncMock()
        mock_playwright_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_playwright_context.__aexit__ = AsyncMock()
        
        mock_playwright.return_value = mock_playwright_context
        
        connector.rate_limit_delay = 0.01
        
        result = await connector.run()
        
        assert result['success'] is True
        assert result['connector'] == 'InternshalaConnector'
        assert result['count'] >= 0
        assert 'records' in result
        assert 'timestamp' in result
        assert 'execution_time_seconds' in result
    
    @pytest.mark.asyncio
    async def test_run_handles_errors(self, connector):
        """Test run method handles errors gracefully"""
        with patch.object(connector, 'fetch', side_effect=Exception("Fetch failed")):
            result = await connector.run()
        
        # The run() method should catch exceptions and return success=False
        assert result['success'] is False
        assert result['connector'] == 'InternshalaConnector'
        assert 'error' in result
        assert 'timestamp' in result
    
    def test_user_agent_rotation(self, connector):
        """Test that connector has multiple user agents for rotation"""
        assert len(connector.USER_AGENTS) == 4
        
        # Verify all user agents include bot identifier
        for ua in connector.USER_AGENTS:
            assert 'EduPilot' in ua
            assert 'edupilot.com/bot' in ua.lower()
    
    def test_rate_limit_configuration(self, connector):
        """Test rate limiting is properly configured"""
        assert connector.rate_limit_delay == 0.1  # From test fixture
        
        # Test with default configuration
        default_connector = InternshalaConnector({})
        assert default_connector.rate_limit_delay == 3.0  # Default from class


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
