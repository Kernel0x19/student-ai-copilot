"""Base connector interface for data source connectors with async support"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

# Configure logger for connectors
logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class for all data source connectors
    
    This class provides a standardized interface for fetching, parsing, validating,
    and running data connectors with built-in error handling and logging.
    
    Requirements satisfied:
    - Requirement 1.1: Base connector interface with fetch/parse/validate/run methods
    - Requirement 1.4: Error handling and logging framework
    - Requirement 1.7: Standard opportunity schema validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the connector with configuration
        
        Args:
            config: Configuration dictionary containing connector-specific settings
        """
        self.config = config
        self.name = self.__class__.__name__
        self.last_run: Optional[datetime] = None
        self.last_error: Optional[str] = None
        
        logger.info(f"Initialized {self.name} connector")
    
    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw data from source
        
        This method should be implemented by each specific connector to retrieve
        data from their respective sources (web scraping, API calls, etc.)
        
        Returns:
            List of dictionaries containing raw opportunity data
            
        Raises:
            Exception: Any errors during data fetching should be raised and will
                      be caught by the run() method
        """
        pass
    
    @abstractmethod
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse and normalize raw data into standard schema
        
        This method transforms raw data from the source into the platform's
        standard opportunity schema format.
        
        Args:
            raw_data: List of raw data dictionaries from fetch()
            
        Returns:
            List of dictionaries conforming to standard opportunity schema
            
        Raises:
            Exception: Any errors during parsing should be raised and will
                      be caught by the run() method
        """
        pass
    
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate parsed data against standard opportunity schema
        
        Checks that all required fields are present in the opportunity record.
        Can be overridden by subclasses for additional validation logic.
        
        Args:
            data: A single parsed opportunity dictionary
            
        Returns:
            True if data is valid, False otherwise
        """
        required_fields = ['title', 'description', 'deadline', 'source_url']
        
        is_valid = all(field in data for field in required_fields)
        
        if not is_valid:
            missing_fields = [field for field in required_fields if field not in data]
            logger.warning(
                f"{self.name}: Validation failed - missing fields: {missing_fields}"
            )
        
        return is_valid
    
    async def run(self) -> Dict[str, Any]:
        """Execute full connector pipeline with error handling
        
        This method orchestrates the complete connector workflow:
        1. Fetch raw data from source
        2. Parse data into standard schema
        3. Validate each record
        4. Return results with metadata
        
        Returns:
            Dictionary containing:
                - connector (str): Name of the connector
                - success (bool): Whether execution succeeded
                - records (List[Dict]): Valid opportunity records (on success)
                - count (int): Number of valid records (on success)
                - error (str): Error message (on failure)
                - timestamp (str): Execution timestamp
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"{self.name}: Starting connector run")
            
            # Fetch raw data
            logger.debug(f"{self.name}: Fetching raw data")
            raw = await self.fetch()
            logger.info(f"{self.name}: Fetched {len(raw)} raw records")
            
            # Parse data into standard schema
            logger.debug(f"{self.name}: Parsing data")
            parsed = await self.parse(raw)
            logger.info(f"{self.name}: Parsed {len(parsed)} records")
            
            # Validate each record
            logger.debug(f"{self.name}: Validating records")
            validated = []
            for record in parsed:
                if await self.validate(record):
                    validated.append(record)
            
            logger.info(f"{self.name}: {len(validated)} valid records out of {len(parsed)} parsed")
            
            # Update success metadata
            self.last_run = datetime.utcnow()
            self.last_error = None
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"{self.name}: Completed successfully in {execution_time:.2f}s - "
                f"{len(validated)} valid records"
            )
            
            return {
                'connector': self.name,
                'success': True,
                'records': validated,
                'count': len(validated),
                'timestamp': start_time.isoformat(),
                'execution_time_seconds': execution_time
            }
            
        except Exception as e:
            # Log and store error information
            error_msg = str(e)
            self.last_error = error_msg
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error(
                f"{self.name}: Execution failed after {execution_time:.2f}s - {error_msg}",
                exc_info=True
            )
            
            return {
                'connector': self.name,
                'success': False,
                'error': error_msg,
                'timestamp': start_time.isoformat(),
                'execution_time_seconds': execution_time
            }


# Standard Opportunity Schema Definition
STANDARD_OPPORTUNITY_SCHEMA = {
    # Required fields
    'title': 'str',                      # Opportunity title
    'description': 'str',                # Detailed description
    'deadline': 'str|datetime|None',     # Application deadline (ISO format string or datetime)
    'source_url': 'str',                 # URL to original opportunity posting
    
    # Optional but recommended fields
    'source': 'str',                     # Data source identifier (e.g., 'AICTE', 'Unstop')
    'category': 'str',                   # Opportunity category (e.g., 'scholarship', 'internship', 'competition')
    'amount': 'int|None',               # Financial amount (single value)
    'amount_min': 'int|None',           # Minimum amount (range)
    'amount_max': 'int|None',           # Maximum amount (range)
    'application_url': 'str|None',      # Direct application link
    'eligibility_rules': 'dict',        # Structured eligibility criteria
    'documents_required': 'list',       # List of required documents
    'state_filter': 'list',             # Geographic restrictions
    'tags': 'list',                     # Additional categorization tags
    'external_id': 'str|None',          # Source's unique identifier
    'location': 'str|None',             # Location/city (for internships)
    'company': 'str|None',              # Company name (for internships)
    'duration': 'str|None',             # Duration/period
    'stipend': 'str|int|None',          # Stipend information
}


def get_schema_documentation() -> str:
    """Return human-readable documentation of the standard opportunity schema"""
    return """
Standard Opportunity Schema
============================

Required Fields:
- title (str): The name/title of the opportunity
- description (str): Full description of the opportunity
- deadline (str|datetime|None): Application deadline in ISO format or datetime object
- source_url (str): URL to the original opportunity posting

Optional Fields:
- source (str): Identifier for the data source (e.g., 'AICTE', 'Unstop', 'Internshala')
- category (str): Type of opportunity ('scholarship', 'internship', 'competition', 'hackathon')
- amount (int): Financial benefit amount (for single value)
- amount_min (int): Minimum amount (for range)
- amount_max (int): Maximum amount (for range)
- application_url (str): Direct link to application form
- eligibility_rules (dict): Structured eligibility criteria (e.g., {'min_cgpa': 6.0, 'category': ['SC', 'ST']})
- documents_required (list): List of required document types
- state_filter (list): Geographic restrictions (state names or ['ALL'])
- tags (list): Additional tags for categorization
- external_id (str): Unique identifier from source system
- location (str): City/location (primarily for internships)
- company (str): Company/organization name (primarily for internships)
- duration (str): Time period/duration
- stipend (str|int): Stipend/compensation information

Notes:
- All connectors should normalize their data into this schema
- Use None for missing optional fields rather than empty strings
- Dates should be in ISO format (YYYY-MM-DD) or datetime objects
- Eligibility rules should use consistent key names across connectors
"""
