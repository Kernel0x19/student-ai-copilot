"""AICTE Connector - Web scraper for AICTE scholarship portal

This connector fetches scholarship listings from the AICTE (All India Council for
Technical Education) scholarship portal using web scraping with BeautifulSoup.

Requirements satisfied:
- Requirement 1.1: Retrieve scholarship listings from AICTE portal
- Requirement 1.2: Log parsing failures with diagnostic context
- Requirement 1.3: Extract required fields (title, description, eligibility, amount, deadline, URLs)
- Requirement 1.4: Normalize data into standard Opportunity_Record schema
- Requirement 1.6: Rate limiting with 2-second delays between requests
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

import httpx
from bs4 import BeautifulSoup

from .base import BaseConnector

logger = logging.getLogger(__name__)


class AICTEConnector(BaseConnector):
    """Scraper for AICTE scholarship portal with rate limiting and error handling
    
    This connector implements web scraping for the AICTE scholarship portal,
    extracting scholarship information including titles, descriptions, amounts,
    deadlines, eligibility rules, and URLs.
    """
    
    # AICTE portal URL (using a typical scholarship listing page)
    BASE_URL = "https://www.aicte-india.org/schemes"
    
    # Rate limiting delay between requests (Requirement 1.6)
    RATE_LIMIT_DELAY = 2.0  # seconds
    
    # Request timeout
    TIMEOUT = 30.0  # seconds
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize AICTE connector
        
        Args:
            config: Configuration dictionary with optional keys:
                - base_url: Override default AICTE URL
                - rate_limit_delay: Override default 2-second delay
                - timeout: Override default 30-second timeout
        """
        super().__init__(config)
        
        # Allow configuration overrides
        self.base_url = config.get('base_url', self.BASE_URL)
        self.rate_limit_delay = config.get('rate_limit_delay', self.RATE_LIMIT_DELAY)
        self.timeout = config.get('timeout', self.TIMEOUT)
        
        logger.info(
            f"AICTEConnector initialized: base_url={self.base_url}, "
            f"rate_limit={self.rate_limit_delay}s"
        )
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw scholarship data from AICTE portal
        
        Implements web scraping with rate limiting to retrieve scholarship
        listings from the AICTE portal. Each scholarship card is extracted
        as raw HTML along with its URL.
        
        Returns:
            List of dictionaries with 'html' and 'url' keys containing
            raw scholarship data
            
        Raises:
            httpx.HTTPError: If HTTP request fails
            Exception: For other network or parsing errors
        """
        logger.info(f"Fetching scholarships from AICTE portal: {self.base_url}")
        
        raw_data = []
        
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; EduPilot/1.0; +https://edupilot.com/bot)'
                }
            ) as client:
                # Fetch the main scholarships listing page
                logger.debug(f"Requesting {self.base_url}")
                response = await client.get(self.base_url)
                response.raise_for_status()
                
                logger.debug(f"Received response: {response.status_code}, size={len(response.text)} bytes")
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find scholarship cards/items on the page
                # Note: These selectors may need adjustment based on actual AICTE portal structure
                scholarship_cards = soup.select('.scholarship-card, .scheme-card, article.scholarship, div.opportunity-card')
                
                if not scholarship_cards:
                    # Try alternative selectors if primary ones don't match
                    logger.warning("Primary selectors found no matches, trying alternatives")
                    scholarship_cards = soup.select('[class*="scholarship"], [class*="scheme"]')
                
                logger.info(f"Found {len(scholarship_cards)} scholarship cards on page")
                
                if len(scholarship_cards) == 0:
                    logger.warning(
                        "No scholarship cards found. Portal structure may have changed. "
                        "HTML snippet: " + response.text[:500]
                    )
                
                # Extract each scholarship card
                for idx, card in enumerate(scholarship_cards):
                    try:
                        # Extract the link from the card
                        link_elem = card.select_one('a[href], a')
                        if link_elem and link_elem.get('href'):
                            url = link_elem['href']
                            
                            # Convert relative URLs to absolute
                            if url.startswith('/'):
                                url = f"https://www.aicte-india.org{url}"
                            elif not url.startswith('http'):
                                url = f"https://www.aicte-india.org/{url}"
                        else:
                            # No link found, use base URL as fallback
                            url = self.base_url
                            logger.debug(f"Card {idx}: No link found, using base URL")
                        
                        raw_data.append({
                            'html': str(card),
                            'url': url,
                            'card_index': idx
                        })
                        
                        # Rate limiting between processing cards (Requirement 1.6)
                        if idx < len(scholarship_cards) - 1:  # Don't delay after last item
                            await asyncio.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        # Log parsing errors with diagnostic context (Requirement 1.2)
                        logger.error(
                            f"Failed to extract card {idx}: {str(e)}. "
                            f"Card HTML: {str(card)[:200]}"
                        )
                        continue
                
                logger.info(f"Successfully extracted {len(raw_data)} scholarship cards")
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching AICTE portal: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching AICTE data: {str(e)}", exc_info=True)
            raise
        
        return raw_data
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse raw HTML data into standard opportunity schema
        
        Extracts structured information from raw scholarship HTML cards,
        normalizing into the platform's standard opportunity format.
        
        Args:
            raw_data: List of dictionaries with 'html' and 'url' keys
            
        Returns:
            List of dictionaries conforming to standard opportunity schema
            with fields: title, description, amount, deadline, eligibility_rules,
            application_url, source_url, source, category
        """
        logger.info(f"Parsing {len(raw_data)} scholarship cards")
        
        parsed = []
        
        for idx, item in enumerate(raw_data):
            try:
                soup = BeautifulSoup(item['html'], 'html.parser')
                
                # Extract title (Requirement 1.3)
                title = self._extract_title(soup)
                
                # Extract description (Requirement 1.3)
                description = self._extract_description(soup)
                
                # Extract amount (Requirement 1.3)
                amount_min, amount_max = self._extract_amount(soup)
                
                # Extract deadline (Requirement 1.3)
                deadline = self._extract_deadline(soup)
                
                # Extract eligibility rules (Requirement 1.3)
                eligibility_rules = self._extract_eligibility(soup)
                
                # Build normalized record (Requirement 1.4)
                record = {
                    'title': title,
                    'description': description,
                    'deadline': deadline,
                    'source_url': item['url'],
                    'application_url': item['url'],
                    'source': 'AICTE',
                    'category': 'scholarship',
                    'eligibility_rules': eligibility_rules,
                    'tags': ['technical', 'engineering', 'aicte']
                }
                
                # Add amount fields if extracted
                if amount_min is not None:
                    record['amount_min'] = amount_min
                if amount_max is not None:
                    record['amount_max'] = amount_max
                if amount_min is not None and amount_min == amount_max:
                    record['amount'] = amount_min
                
                parsed.append(record)
                
            except Exception as e:
                # Log parsing failures with diagnostic context (Requirement 1.2)
                html_snippet = item.get('html', '')
                if html_snippet is None:
                    html_snippet = 'None'
                else:
                    html_snippet = str(html_snippet)[:300]
                
                logger.error(
                    f"Failed to parse card {idx}: {str(e)}. "
                    f"URL: {item.get('url', 'N/A')}. "
                    f"HTML snippet: {html_snippet}"
                )
                continue
        
        logger.info(f"Successfully parsed {len(parsed)} out of {len(raw_data)} cards")
        
        return parsed
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract scholarship title from HTML
        
        Args:
            soup: BeautifulSoup object of scholarship card
            
        Returns:
            Scholarship title string, or "Untitled Scholarship" if not found
        """
        # Try multiple possible selectors for title
        title_selectors = [
            '.title', '.scholarship-title', '.scheme-title',
            'h2', 'h3', 'h4',
            '[class*="title"]', '[class*="heading"]'
        ]
        
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                return elem.text.strip()
        
        # Fallback
        logger.debug("Could not find title, using default")
        return "Untitled AICTE Scholarship"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract scholarship description from HTML
        
        Args:
            soup: BeautifulSoup object of scholarship card
            
        Returns:
            Scholarship description string, or default if not found
        """
        # Try multiple possible selectors for description
        desc_selectors = [
            '.description', '.desc', '.content', '.scholarship-description',
            '.scheme-description', 'p', '[class*="description"]'
        ]
        
        descriptions = []
        for selector in desc_selectors:
            elems = soup.select(selector)
            for elem in elems:
                text = elem.text.strip()
                if text and len(text) > 20:  # Meaningful description
                    descriptions.append(text)
        
        if descriptions:
            # Join all descriptions or use the longest one
            return ' '.join(descriptions[:3]) if len(descriptions) > 1 else descriptions[0]
        
        # Fallback: use all text from the card
        all_text = soup.get_text(separator=' ', strip=True)
        if len(all_text) > 50:
            return all_text[:500]  # Truncate to reasonable length
        
        return "AICTE scholarship opportunity. Please visit the official portal for complete details."
    
    def _extract_amount(self, soup: BeautifulSoup) -> tuple[Optional[int], Optional[int]]:
        """Extract scholarship amount from HTML
        
        Looks for patterns like:
        - Rs. 50,000
        - ₹50000 - ₹100000
        - Up to 1 Lakh
        
        Args:
            soup: BeautifulSoup object of scholarship card
            
        Returns:
            Tuple of (amount_min, amount_max) as integers, or (None, None) if not found
        """
        # Look for amount-related elements
        amount_selectors = [
            '.amount', '.scholarship-amount', '.prize', '.stipend',
            '[class*="amount"]', '[class*="prize"]'
        ]
        
        text_to_search = soup.get_text(separator=' ', strip=True)
        
        # Try to find amount patterns
        # Pattern 1: Rs. 50,000 or ₹50,000
        pattern1 = r'(?:Rs\.?|₹)\s*([\d,]+)'
        
        # Pattern 2: Range - Rs. 50,000 - Rs. 100,000
        pattern2 = r'(?:Rs\.?|₹)\s*([\d,]+)\s*(?:to|-)\s*(?:Rs\.?|₹)?\s*([\d,]+)'
        
        # Pattern 3: Up to X Lakh
        pattern3 = r'up\s+to\s+([\d.]+)\s*lakh'
        
        # Try range pattern first
        match = re.search(pattern2, text_to_search, re.IGNORECASE)
        if match:
            try:
                amount_min = int(match.group(1).replace(',', ''))
                amount_max = int(match.group(2).replace(',', ''))
                return amount_min, amount_max
            except (ValueError, IndexError):
                pass
        
        # Try lakh pattern
        match = re.search(pattern3, text_to_search, re.IGNORECASE)
        if match:
            try:
                lakhs = float(match.group(1))
                amount = int(lakhs * 100000)
                return amount, amount
            except (ValueError, IndexError):
                pass
        
        # Try single amount pattern
        match = re.search(pattern1, text_to_search, re.IGNORECASE)
        if match:
            try:
                amount = int(match.group(1).replace(',', ''))
                return amount, amount
            except (ValueError, IndexError):
                pass
        
        return None, None
    
    def _extract_deadline(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract application deadline from HTML
        
        Looks for date patterns in various formats and normalizes to ISO format.
        
        Args:
            soup: BeautifulSoup object of scholarship card
            
        Returns:
            Deadline in ISO format (YYYY-MM-DD) or None if not found
        """
        text = soup.get_text(separator=' ', strip=True)
        
        # Look for deadline keywords
        deadline_patterns = [
            r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'last\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'apply\s+by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # Any date pattern
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try to parse and normalize the date
                normalized = self._normalize_date(date_str)
                if normalized:
                    return normalized
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to ISO format (YYYY-MM-DD)
        
        Args:
            date_str: Date string in various formats (DD/MM/YYYY, DD-MM-YYYY, etc.)
            
        Returns:
            ISO format date string or None if parsing fails
        """
        # Try common date formats
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%d/%m/%y', '%d-%m-%y', '%d.%m.%y',
            '%Y-%m-%d', '%Y/%m/%d',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _extract_eligibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract eligibility criteria from HTML
        
        Attempts to parse structured eligibility rules from the description.
        
        Args:
            soup: BeautifulSoup object of scholarship card
            
        Returns:
            Dictionary with eligibility rules (may be empty if not parseable)
        """
        text = soup.get_text(separator=' ', strip=True).lower()
        
        eligibility = {}
        
        # Try to extract CGPA/percentage requirements
        # Pattern: "cgpa of 7.0" or "cgpa: 7.0" or "minimum cgpa 7.0"
        cgpa_match = re.search(r'(?:cgpa|gpa)[\s:of]+(\d+\.?\d*)', text)
        if cgpa_match:
            try:
                eligibility['min_cgpa'] = float(cgpa_match.group(1))
            except ValueError:
                pass
        
        percentage_match = re.search(r'(\d+)%?\s*(?:percentage|marks)', text)
        if percentage_match:
            try:
                eligibility['min_percentage'] = int(percentage_match.group(1))
            except ValueError:
                pass
        
        # Try to extract category requirements
        if any(cat in text for cat in ['sc', 'st', 'obc', 'ews', 'general']):
            categories = []
            if 'sc' in text:
                categories.append('SC')
            if 'st' in text:
                categories.append('ST')
            if 'obc' in text:
                categories.append('OBC')
            if 'ews' in text:
                categories.append('EWS')
            if 'general' in text or 'all' in text:
                categories.append('General')
            
            if categories:
                eligibility['category'] = categories
        
        # Try to extract stream/course requirements
        streams = []
        if any(s in text for s in ['engineering', 'b.tech', 'btech', 'b.e.', 'technical']):
            streams.append('Engineering')
        if any(s in text for s in ['diploma', 'polytechnic']):
            streams.append('Diploma')
        
        if streams:
            eligibility['streams'] = streams
        
        return eligibility
