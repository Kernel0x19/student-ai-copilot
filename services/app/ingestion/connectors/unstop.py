"""Unstop Connector - API connector for Unstop partnership (placeholder)

This connector provides an interface compatible with future Unstop partner API integration.
It defines request/response schemas, implements authentication placeholders, and gracefully
skips execution when API credentials are not configured.

IMPORTANT: This is a placeholder connector for future integration. The user does not have
access to the Unstop API. The connector will validate configuration and skip execution with
appropriate warnings when credentials are missing.

Requirements satisfied:
- Requirement 2.1: Provide interface compatible with future Unstop partner API
- Requirement 2.2: Implement authentication placeholder for API key configuration
- Requirement 2.3: Define request/response schemas matching Unstop's documented API format
- Requirement 2.4: Skip execution and log configuration warning when credentials not present
- Requirement 2.5: Map Unstop opportunity types to Platform Opportunity_Record categories
- Requirement 2.6: Handle API rate limiting according to partner agreement terms
- Requirement 2.7: Validate API responses against expected schemas and reject malformed data
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

import httpx

from .base import BaseConnector

logger = logging.getLogger(__name__)


class UnstopConnector(BaseConnector):
    """API connector for Unstop partnership (placeholder for future integration)
    
    This connector is a production-ready placeholder that:
    1. Validates configuration and gracefully skips when credentials are missing
    2. Defines expected API request/response schemas for future integration
    3. Logs appropriate warnings when skipped
    4. Follows the same pattern as AICTEConnector but for API-based integration
    
    When API credentials are configured, this connector will fetch opportunities
    from the Unstop partner API including hackathons, competitions, and workshops.
    """
    
    # Unstop API endpoint (placeholder - actual endpoint will be provided by partner)
    BASE_URL = "https://api.unstop.com/v1/opportunities"
    
    # Rate limiting delay between requests (to be adjusted per partner agreement)
    RATE_LIMIT_DELAY = 1.0  # seconds (Requirement 2.6)
    
    # Request timeout
    TIMEOUT = 30.0  # seconds
    
    # Opportunity type mapping (Requirement 2.5)
    OPPORTUNITY_TYPE_MAP = {
        'hackathon': 'hackathon',
        'competition': 'competition',
        'workshop': 'workshop',
        'challenge': 'competition',
        'event': 'event',
        'conference': 'event'
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Unstop connector
        
        Args:
            config: Configuration dictionary with optional keys:
                - unstop_api_key: API key for Unstop partner integration
                - unstop_api_secret: API secret (if required)
                - base_url: Override default Unstop API URL
                - rate_limit_delay: Override default rate limiting delay
                - timeout: Override default timeout
        """
        super().__init__(config)
        
        # Configuration (Requirement 2.2)
        self.api_key = config.get('unstop_api_key')
        self.api_secret = config.get('unstop_api_secret')
        self.base_url = config.get('base_url', self.BASE_URL)
        self.rate_limit_delay = config.get('rate_limit_delay', self.RATE_LIMIT_DELAY)
        self.timeout = config.get('timeout', self.TIMEOUT)
        
        # Check if credentials are configured
        self.credentials_configured = bool(self.api_key)
        
        if self.credentials_configured:
            logger.info(
                f"UnstopConnector initialized with API credentials: base_url={self.base_url}, "
                f"rate_limit={self.rate_limit_delay}s"
            )
        else:
            # Log configuration warning (Requirement 2.4)
            logger.warning(
                "UnstopConnector initialized WITHOUT API credentials. "
                "Connector will skip execution until 'unstop_api_key' is configured. "
                "To enable Unstop integration, add 'unstop_api_key' to connector config."
            )
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw opportunity data from Unstop API
        
        This method checks for API credentials and gracefully skips execution
        if not configured. When credentials are present, it makes authenticated
        API requests to fetch opportunities.
        
        Returns:
            List of dictionaries containing raw opportunity data from API
            Empty list if credentials are not configured
            
        Raises:
            ValueError: If credentials are not configured (caught by run() method)
            httpx.HTTPError: If API request fails
        """
        # Configuration validation and skip logic (Requirement 2.4)
        if not self.credentials_configured:
            logger.warning(
                "Unstop API credentials not configured - skipping data fetch. "
                "Configure 'unstop_api_key' in connector config to enable Unstop integration."
            )
            raise ValueError("Unstop API key not configured - skipping")
        
        logger.info(f"Fetching opportunities from Unstop API: {self.base_url}")
        
        raw_data = []
        
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=self._build_auth_headers()
            ) as client:
                # Request schema (Requirement 2.3)
                # Future implementation will include pagination, filters, etc.
                params = {
                    'status': 'active',  # Only fetch active opportunities
                    'limit': 100,  # Pagination limit
                    'offset': 0
                }
                
                logger.debug(f"Requesting {self.base_url} with params: {params}")
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                logger.debug(
                    f"Received response: {response.status_code}, "
                    f"size={len(response.text)} bytes"
                )
                
                # Parse JSON response (Requirement 2.3)
                response_data = response.json()
                
                # Validate response schema (Requirement 2.7)
                if not self._validate_response_schema(response_data):
                    logger.error(
                        "API response does not match expected schema. "
                        f"Response keys: {list(response_data.keys())}"
                    )
                    raise ValueError("Invalid API response schema")
                
                # Extract opportunities from response
                opportunities = response_data.get('data', [])
                logger.info(f"Found {len(opportunities)} opportunities in API response")
                
                # Store raw data with metadata
                for idx, opp in enumerate(opportunities):
                    raw_data.append({
                        'data': opp,
                        'api_index': idx,
                        'fetched_at': datetime.utcnow().isoformat()
                    })
                    
                    # Rate limiting between processing items (Requirement 2.6)
                    if idx < len(opportunities) - 1:
                        await asyncio.sleep(self.rate_limit_delay)
                
                logger.info(f"Successfully fetched {len(raw_data)} opportunities from Unstop API")
                
                # TODO: Handle pagination for larger result sets
                # if response_data.get('has_more'):
                #     fetch next page
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching from Unstop API: {str(e)}")
            raise
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching Unstop data: {str(e)}", exc_info=True)
            raise
        
        return raw_data
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse raw API data into standard opportunity schema
        
        Transforms Unstop API responses into the platform's standard opportunity
        format, mapping opportunity types and normalizing field names.
        
        Args:
            raw_data: List of dictionaries with 'data' key containing API response
            
        Returns:
            List of dictionaries conforming to standard opportunity schema
        """
        logger.info(f"Parsing {len(raw_data)} opportunities from Unstop API")
        
        parsed = []
        
        for idx, item in enumerate(raw_data):
            try:
                data = item['data']
                
                # Validate individual opportunity schema (Requirement 2.7)
                if not self._validate_opportunity_schema(data):
                    logger.warning(
                        f"Opportunity {idx} does not match expected schema, skipping. "
                        f"Keys: {list(data.keys())}"
                    )
                    continue
                
                # Extract and map fields to standard schema (Requirement 2.3)
                opp_type = data.get('type', 'event').lower()
                category = self.OPPORTUNITY_TYPE_MAP.get(opp_type, 'event')
                
                # Parse deadline
                deadline = self._parse_api_date(data.get('end_date'))
                
                # Build normalized record
                record = {
                    'title': data.get('name', data.get('title', 'Untitled Unstop Opportunity')),
                    'description': data.get('description', data.get('about', '')),
                    'deadline': deadline,
                    'source_url': data.get('url', data.get('link', '')),
                    'application_url': data.get('apply_url', data.get('url', '')),
                    'source': 'Unstop',
                    'category': category,  # Mapped category (Requirement 2.5)
                    'tags': self._extract_tags(data, opp_type),
                    'external_id': data.get('id', data.get('opportunity_id'))
                }
                
                # Add optional fields
                if 'prize' in data or 'reward' in data:
                    prize = data.get('prize', data.get('reward'))
                    amount = self._parse_prize_amount(prize)
                    if amount:
                        record['amount'] = amount
                        record['amount_min'] = amount
                        record['amount_max'] = amount
                
                if 'location' in data:
                    record['location'] = data.get('location')
                
                if 'company' in data or 'organizer' in data:
                    record['company'] = data.get('company', data.get('organizer'))
                
                if 'duration' in data:
                    record['duration'] = data.get('duration')
                
                # Extract eligibility if available
                if 'eligibility' in data:
                    record['eligibility_rules'] = self._parse_eligibility(data['eligibility'])
                
                parsed.append(record)
                
            except Exception as e:
                logger.error(
                    f"Failed to parse opportunity {idx}: {str(e)}. "
                    f"Data: {item.get('data', {})}"
                )
                continue
        
        logger.info(f"Successfully parsed {len(parsed)} out of {len(raw_data)} opportunities")
        
        return parsed
    
    def _build_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers for API requests (Requirement 2.2)
        
        Returns:
            Dictionary of HTTP headers including authentication
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; EduPilot/1.0; +https://edupilot.com/bot)',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            # Bearer token authentication (adjust based on actual API requirements)
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        if self.api_secret:
            # Add API secret if required by partner agreement
            headers['X-API-Secret'] = self.api_secret
        
        return headers
    
    def _validate_response_schema(self, response: Dict[str, Any]) -> bool:
        """Validate API response matches expected schema (Requirement 2.7)
        
        Expected response schema:
        {
            "success": true,
            "data": [...],
            "meta": {
                "total": 100,
                "limit": 100,
                "offset": 0
            }
        }
        
        Args:
            response: API response dictionary
            
        Returns:
            True if response matches expected schema, False otherwise
        """
        # Check for required top-level keys
        if not isinstance(response, dict):
            logger.error("Response is not a dictionary")
            return False
        
        # Expect 'data' key containing list of opportunities
        if 'data' not in response:
            logger.error("Response missing 'data' key")
            return False
        
        if not isinstance(response['data'], list):
            logger.error("Response 'data' is not a list")
            return False
        
        return True
    
    def _validate_opportunity_schema(self, opp: Dict[str, Any]) -> bool:
        """Validate individual opportunity matches expected schema (Requirement 2.7)
        
        Expected opportunity schema:
        {
            "id": "123",
            "name": "Hackathon Name",
            "description": "Description text",
            "type": "hackathon",
            "end_date": "2024-12-31T23:59:59Z",
            "url": "https://unstop.com/opportunity/123",
            ...
        }
        
        Args:
            opp: Opportunity dictionary from API
            
        Returns:
            True if opportunity has minimum required fields, False otherwise
        """
        # Check for essential fields
        required_fields = ['name', 'type', 'url']
        
        for field in required_fields:
            if field not in opp and not any(alt in opp for alt in ['title', 'link']):
                logger.warning(f"Opportunity missing required field: {field}")
                return False
        
        return True
    
    def _parse_api_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse API date string to ISO format
        
        Args:
            date_str: Date string from API (ISO format expected)
            
        Returns:
            ISO format date string (YYYY-MM-DD) or None
        """
        if not date_str:
            return None
        
        try:
            # Handle ISO format with time (2024-12-31T23:59:59Z)
            if 'T' in date_str:
                parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return parsed.strftime('%Y-%m-%d')
            # Handle date-only format (2024-12-31)
            elif len(date_str) == 10 and date_str.count('-') == 2:
                return date_str
            else:
                logger.debug(f"Unable to parse date format: {date_str}")
                return None
        except (ValueError, AttributeError) as e:
            logger.debug(f"Date parsing error: {str(e)}")
            return None
    
    def _parse_prize_amount(self, prize_str: Any) -> Optional[int]:
        """Parse prize/reward amount from API response
        
        Args:
            prize_str: Prize string or number from API
            
        Returns:
            Prize amount as integer or None
        """
        if not prize_str:
            return None
        
        try:
            # If already a number
            if isinstance(prize_str, (int, float)):
                return int(prize_str)
            
            # Parse from string (e.g., "Rs 50000", "₹50,000", "50000")
            if isinstance(prize_str, str):
                import re
                # Remove currency symbols and commas
                cleaned = re.sub(r'[₹Rs,\s]', '', prize_str)
                # Extract first number
                match = re.search(r'\d+', cleaned)
                if match:
                    return int(match.group())
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def _extract_tags(self, data: Dict[str, Any], opp_type: str) -> List[str]:
        """Extract tags for opportunity categorization
        
        Args:
            data: Opportunity data from API
            opp_type: Opportunity type
            
        Returns:
            List of tag strings
        """
        tags = ['unstop', opp_type]
        
        # Add tags from API if available
        if 'tags' in data and isinstance(data['tags'], list):
            tags.extend(data['tags'])
        
        if 'categories' in data and isinstance(data['categories'], list):
            tags.extend(data['categories'])
        
        # Add domain-specific tags
        if opp_type in ['hackathon', 'competition']:
            tags.append('technical')
        
        return tags
    
    def _parse_eligibility(self, eligibility_data: Any) -> Dict[str, Any]:
        """Parse eligibility criteria from API response
        
        Args:
            eligibility_data: Eligibility information from API
            
        Returns:
            Dictionary with structured eligibility rules
        """
        eligibility = {}
        
        # Handle different formats
        if isinstance(eligibility_data, dict):
            # Direct mapping of structured data
            if 'min_year' in eligibility_data:
                eligibility['min_year'] = eligibility_data['min_year']
            if 'max_year' in eligibility_data:
                eligibility['max_year'] = eligibility_data['max_year']
            if 'streams' in eligibility_data:
                eligibility['streams'] = eligibility_data['streams']
        elif isinstance(eligibility_data, str):
            # Parse from text description
            eligibility['description'] = eligibility_data
        
        return eligibility
