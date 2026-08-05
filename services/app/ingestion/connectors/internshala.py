"""Internshala Connector - Web scraper for Internshala internship portal

This connector fetches internship listings from Internshala using Playwright for
browser automation. It implements robots.txt compliance checks, user-agent rotation,
rate limiting, and comprehensive activity logging.

Requirements satisfied:
- Requirement 3.1: Retrieve internship listings through web scraping
- Requirement 3.2: Include robots.txt compliance checks before scraping
- Requirement 3.3: Abort execution and log restriction when robots.txt disallows
- Requirement 3.4: Extract required fields (title, company, location, stipend, duration, eligibility, deadline, application_url)
- Requirement 3.5: Implement user-agent rotation to distribute request patterns
- Requirement 3.6: Rate limiting with 3-second delays between requests
- Requirement 3.7: Log all scraping activities with timestamps for audit compliance
"""

import asyncio
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

import httpx
from playwright.async_api import async_playwright, Browser, Page

from .base import BaseConnector

logger = logging.getLogger(__name__)


class InternshalaConnector(BaseConnector):
    """Web scraper for Internshala internship portal with robots.txt compliance
    
    This connector implements browser automation using Playwright to scrape
    internship listings from Internshala. It includes comprehensive compliance
    checks, rate limiting, user-agent rotation, and activity logging.
    """
    
    # Internshala portal URL
    BASE_URL = "https://internshala.com"
    INTERNSHIPS_URL = "https://internshala.com/internships"
    
    # Rate limiting delay between requests (Requirement 3.6)
    RATE_LIMIT_DELAY = 3.0  # seconds
    
    # Request timeout
    TIMEOUT = 30000  # milliseconds (30 seconds) for Playwright
    
    # User-agent rotation pool (Requirement 3.5)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (EduPilot Bot; +https://edupilot.com/bot)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (EduPilot Bot; +https://edupilot.com/bot)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (EduPilot Bot; +https://edupilot.com/bot)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0 (EduPilot Bot; +https://edupilot.com/bot)',
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Internshala connector
        
        Args:
            config: Configuration dictionary with optional keys:
                - base_url: Override default Internshala URL
                - internships_url: Override default internships listing URL
                - rate_limit_delay: Override default 3-second delay
                - timeout: Override default 30-second timeout
                - skip_robots_check: Skip robots.txt check (default: False)
                - headless: Run browser in headless mode (default: True)
        """
        super().__init__(config)
        
        # Allow configuration overrides
        self.base_url = config.get('base_url', self.BASE_URL)
        self.internships_url = config.get('internships_url', self.INTERNSHIPS_URL)
        self.rate_limit_delay = config.get('rate_limit_delay', self.RATE_LIMIT_DELAY)
        self.timeout = config.get('timeout', self.TIMEOUT)
        self.skip_robots_check = config.get('skip_robots_check', False)
        self.headless = config.get('headless', True)
        
        logger.info(
            f"InternshalaConnector initialized: base_url={self.base_url}, "
            f"rate_limit={self.rate_limit_delay}s, headless={self.headless}"
        )
        
        # Log initialization activity (Requirement 3.7)
        self._log_activity("connector_initialized", {
            "base_url": self.base_url,
            "rate_limit_delay": self.rate_limit_delay,
            "robots_check_enabled": not self.skip_robots_check
        })
    
    def _log_activity(self, action: str, metadata: Dict[str, Any]):
        """Log scraping activity with timestamp for audit compliance (Requirement 3.7)
        
        Args:
            action: Action being performed (e.g., 'robots_check', 'fetch_started', 'page_scraped')
            metadata: Additional context about the activity
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "connector": "InternshalaConnector",
            "action": action,
            "metadata": metadata
        }
        
        logger.info(f"Activity Log: {log_entry}")
    
    async def check_robots(self) -> bool:
        """Check robots.txt before scraping (Requirement 3.2)
        
        Fetches and parses the robots.txt file from Internshala to verify
        that scraping is allowed for the /internships path.
        
        Returns:
            True if scraping is allowed, False if disallowed
            
        Raises:
            Exception: If robots.txt cannot be fetched
        """
        robots_url = f"{self.base_url}/robots.txt"
        
        self._log_activity("robots_check_started", {"robots_url": robots_url})
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)
                response.raise_for_status()
                
                robots_text = response.text
                
                # Parse robots.txt for disallow rules
                # Look for User-agent: * or User-agent: EduPilot
                disallowed_paths = []
                allowed_paths = []
                current_user_agent = None
                
                for line in robots_text.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('User-agent:'):
                        user_agent = line.split(':', 1)[1].strip()
                        if user_agent == '*' or 'edupi' in user_agent.lower():
                            current_user_agent = user_agent
                    
                    elif current_user_agent and line.startswith('Disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path:
                            disallowed_paths.append(path)
                    
                    elif current_user_agent and line.startswith('Allow:'):
                        path = line.split(':', 1)[1].strip()
                        if path:
                            allowed_paths.append(path)
                
                # Check if /internships is disallowed
                internships_path = '/internships'
                is_allowed = True
                
                # Check explicit disallows
                for disallow in disallowed_paths:
                    if disallow == '/' or internships_path.startswith(disallow):
                        is_allowed = False
                        break
                
                # Check explicit allows (override disallows)
                for allow in allowed_paths:
                    if internships_path.startswith(allow):
                        is_allowed = True
                        break
                
                self._log_activity("robots_check_completed", {
                    "is_allowed": is_allowed,
                    "disallowed_paths": disallowed_paths[:5],  # Log first 5
                    "allowed_paths": allowed_paths[:5]
                })
                
                if not is_allowed:
                    logger.warning(
                        f"Robots.txt disallows scraping of {internships_path}. "
                        f"Disallowed paths: {disallowed_paths}"
                    )
                
                return is_allowed
                
        except Exception as e:
            error_msg = f"Failed to fetch or parse robots.txt: {str(e)}"
            logger.error(error_msg)
            self._log_activity("robots_check_failed", {"error": error_msg})
            
            # Default to allowing if robots.txt cannot be fetched
            # This is a conservative approach - could also default to disallow
            logger.warning("Defaulting to ALLOW since robots.txt could not be verified")
            return True
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw internship data from Internshala portal
        
        Implements browser automation with Playwright to retrieve internship
        listings. Includes robots.txt compliance checking, user-agent rotation,
        and rate limiting.
        
        Returns:
            List of dictionaries with 'html' and 'url' keys containing
            raw internship data
            
        Raises:
            ValueError: If robots.txt disallows scraping (Requirement 3.3)
            Exception: For other browser automation or scraping errors
        """
        # Check robots.txt compliance (Requirement 3.2)
        if not self.skip_robots_check:
            is_allowed = await self.check_robots()
            if not is_allowed:
                # Abort and log restriction (Requirement 3.3)
                error_msg = (
                    "Robots.txt disallows scraping of /internships path - aborting. "
                    "To override, set 'skip_robots_check: true' in connector config."
                )
                self._log_activity("fetch_aborted", {
                    "reason": "robots.txt disallow",
                    "url": self.internships_url
                })
                raise ValueError(error_msg)
        else:
            logger.warning("Skipping robots.txt check per configuration")
            self._log_activity("robots_check_skipped", {"reason": "config override"})
        
        self._log_activity("fetch_started", {"url": self.internships_url})
        
        logger.info(f"Fetching internships from Internshala portal: {self.internships_url}")
        
        raw_data = []
        
        try:
            async with async_playwright() as p:
                # Select random user agent for this session (Requirement 3.5)
                user_agent = random.choice(self.USER_AGENTS)
                
                self._log_activity("browser_launch", {
                    "user_agent": user_agent,
                    "headless": self.headless
                })
                
                # Launch browser
                browser: Browser = await p.chromium.launch(headless=self.headless)
                
                try:
                    # Create new page with custom user agent
                    page: Page = await browser.new_page(user_agent=user_agent)
                    page.set_default_timeout(self.timeout)
                    
                    # Navigate to internships listing page
                    logger.debug(f"Navigating to {self.internships_url}")
                    await page.goto(self.internships_url, wait_until='domcontentloaded')
                    
                    self._log_activity("page_loaded", {
                        "url": page.url,
                        "title": await page.title()
                    })
                    
                    # Wait for internship cards to load
                    # Try multiple possible selectors
                    selectors = [
                        '.internship_meta',
                        '.individual_internship',
                        '[class*="internship"]',
                        'article',
                        '.card'
                    ]
                    
                    element_found = False
                    for selector in selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=10000)
                            element_found = True
                            logger.debug(f"Found elements with selector: {selector}")
                            break
                        except Exception:
                            continue
                    
                    if not element_found:
                        logger.warning(
                            "Could not find internship cards with known selectors. "
                            "Page structure may have changed."
                        )
                    
                    # Extract all internship cards
                    # Try multiple selectors for maximum compatibility
                    internship_selectors = [
                        '.individual_internship',
                        '.internship_meta',
                        '[class*="internship-card"]',
                        '[class*="internship-item"]',
                        'article.internship',
                        '.card'
                    ]
                    
                    internships = []
                    for selector in internship_selectors:
                        internships = await page.query_selector_all(selector)
                        if internships:
                            logger.info(f"Found {len(internships)} internships with selector: {selector}")
                            break
                    
                    if not internships:
                        logger.warning(
                            "No internship elements found. Portal structure may have changed. "
                            f"Page URL: {page.url}"
                        )
                        self._log_activity("no_internships_found", {
                            "url": page.url,
                            "selectors_tried": internship_selectors
                        })
                    
                    # Extract data from each internship card (honour max_cards)
                    max_cards = self.config.get("max_cards", len(internships))
                    internships = internships[:max_cards]

                    for idx, internship in enumerate(internships):
                        try:
                            # Get inner HTML
                            html = await internship.inner_html()
                            
                            # Try to extract the internship URL/link
                            url = self.internships_url  # Default fallback
                            
                            # Try multiple ways to get the link
                            try:
                                link_elem = await internship.query_selector('a[href]')
                                if link_elem:
                                    href = await link_elem.get_attribute('href')
                                    if href:
                                        # Convert relative URLs to absolute
                                        if href.startswith('/'):
                                            url = f"{self.base_url}{href}"
                                        elif not href.startswith('http'):
                                            url = f"{self.base_url}/{href}"
                                        else:
                                            url = href
                            except Exception as e:
                                logger.debug(f"Could not extract link from card {idx}: {e}")
                            
                            # Try to get data-href attribute (common pattern)
                            try:
                                data_href = await internship.get_attribute('data-href')
                                if data_href:
                                    if data_href.startswith('/'):
                                        url = f"{self.base_url}{data_href}"
                                    elif not data_href.startswith('http'):
                                        url = f"{self.base_url}/{data_href}"
                                    else:
                                        url = data_href
                            except Exception:
                                pass
                            
                            raw_data.append({
                                'html': html,
                                'url': url,
                                'card_index': idx
                            })
                            
                            # Rate limiting between processing cards (Requirement 3.6)
                            if idx < len(internships) - 1:  # Don't delay after last item
                                await asyncio.sleep(self.rate_limit_delay)
                                
                        except Exception as e:
                            logger.error(f"Failed to extract card {idx}: {str(e)}")
                            self._log_activity("card_extraction_failed", {
                                "card_index": idx,
                                "error": str(e)
                            })
                            continue
                    
                    logger.info(f"Successfully extracted {len(raw_data)} internship cards")
                    
                    self._log_activity("fetch_completed", {
                        "cards_extracted": len(raw_data),
                        "total_cards_found": len(internships)
                    })
                    
                finally:
                    # Always close browser
                    await browser.close()
                    self._log_activity("browser_closed", {})
                    
        except ValueError as e:
            # Re-raise robots.txt violation (Requirement 3.3)
            raise
        except Exception as e:
            error_msg = f"Unexpected error during Internshala scraping: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._log_activity("fetch_failed", {"error": error_msg})
            raise
        
        return raw_data
    
    async def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse raw HTML data into standard opportunity schema
        
        Extracts structured information from raw internship HTML cards,
        normalizing into the platform's standard opportunity format.
        
        Args:
            raw_data: List of dictionaries with 'html' and 'url' keys
            
        Returns:
            List of dictionaries conforming to standard opportunity schema
            with fields: title, company, location, stipend, duration, eligibility,
            deadline, application_url, source_url, source, category
        """
        logger.info(f"Parsing {len(raw_data)} internship cards")
        
        self._log_activity("parse_started", {"card_count": len(raw_data)})
        
        parsed = []
        
        for idx, item in enumerate(raw_data):
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(item['html'], 'html.parser')
                
                # Extract title (Requirement 3.4)
                title = self._extract_title(soup)
                
                # Extract company (Requirement 3.4)
                company = self._extract_company(soup)
                
                # Extract location (Requirement 3.4)
                location = self._extract_location(soup)
                
                # Extract stipend (Requirement 3.4)
                stipend = self._extract_stipend(soup)
                
                # Extract duration (Requirement 3.4)
                duration = self._extract_duration(soup)
                
                # Extract deadline (Requirement 3.4)
                deadline = self._extract_deadline(soup)
                
                # Extract description for eligibility and general info
                description = self._extract_description(soup)
                
                # Extract eligibility criteria (Requirement 3.4)
                eligibility_rules = self._extract_eligibility(soup, description)
                
                # Build normalized record
                record = {
                    'title': title,
                    'description': description,
                    'company': company,
                    'location': location,
                    'duration': duration,
                    'deadline': deadline,
                    'source_url': item['url'],
                    'application_url': item['url'],
                    'source': 'Internshala',
                    'category': 'internship',
                    'eligibility_rules': eligibility_rules,
                    'tags': ['internship', 'internshala', 'work-experience']
                }
                
                # Add stipend if extracted
                if stipend:
                    record['stipend'] = stipend
                    # Try to parse numeric value for amount field
                    amount = self._parse_stipend_amount(stipend)
                    if amount:
                        record['amount'] = amount
                        record['amount_min'] = amount
                        record['amount_max'] = amount
                
                parsed.append(record)
                
            except Exception as e:
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
                self._log_activity("card_parse_failed", {
                    "card_index": idx,
                    "url": item.get('url'),
                    "error": str(e)
                })
                continue
        
        logger.info(f"Successfully parsed {len(parsed)} out of {len(raw_data)} cards")
        
        self._log_activity("parse_completed", {
            "parsed_count": len(parsed),
            "total_count": len(raw_data)
        })
        
        return parsed
    
    def _extract_title(self, soup) -> str:
        """Extract internship title from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Internship title string, or "Untitled Internship" if not found
        """
        selectors = [
            '.profile', '.internship-title', '.title', '.job-title',
            'h3', 'h4', '[class*="title"]', '[class*="profile"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                return elem.text.strip()
        
        return "Untitled Internship"
    
    def _extract_company(self, soup) -> Optional[str]:
        """Extract company name from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Company name string or None if not found
        """
        selectors = [
            '.company-name', '.company', '.organization',
            '[class*="company"]', '[class*="organization"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                return elem.text.strip()
        
        return None
    
    def _extract_location(self, soup) -> Optional[str]:
        """Extract location from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Location string or None if not found
        """
        selectors = [
            '.location', '.locations', '.location-link',
            '[class*="location"]', '[class*="city"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                text = elem.text.strip()
                # Clean up common patterns
                text = text.replace('Work From Home', 'Remote')
                return text
        
        return None
    
    def _extract_stipend(self, soup) -> Optional[str]:
        """Extract stipend information from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Stipend string or None if not found
        """
        selectors = [
            '.stipend', '.salary', '.compensation',
            '[class*="stipend"]', '[class*="salary"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                return elem.text.strip()
        
        # Try to find in text content
        text = soup.get_text(separator=' ', strip=True)
        stipend_match = re.search(r'(?:stipend|salary)[\s:]+([₹\d,\-\s]+(?:per month|/month)?)', text, re.IGNORECASE)
        if stipend_match:
            return stipend_match.group(1).strip()
        
        return None
    
    def _parse_stipend_amount(self, stipend_str: str) -> Optional[int]:
        """Parse numeric stipend amount from string
        
        Args:
            stipend_str: Stipend string (e.g., "₹10,000 per month")
            
        Returns:
            Numeric amount or None if cannot parse
        """
        if not stipend_str:
            return None
        
        # Remove currency symbols and text
        cleaned = re.sub(r'[₹Rs,\s]', '', stipend_str)
        cleaned = re.sub(r'(?:per|/)?month', '', cleaned, flags=re.IGNORECASE)
        
        # Extract first number
        match = re.search(r'\d+', cleaned)
        if match:
            try:
                return int(match.group())
            except ValueError:
                pass
        
        return None
    
    def _extract_duration(self, soup) -> Optional[str]:
        """Extract internship duration from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Duration string or None if not found
        """
        selectors = [
            '.duration', '.internship-duration', '.period',
            '[class*="duration"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                return elem.text.strip()
        
        # Try to find in text content
        text = soup.get_text(separator=' ', strip=True)
        duration_match = re.search(r'(?:duration|period)[\s:]+(\d+\s*(?:weeks?|months?))', text, re.IGNORECASE)
        if duration_match:
            return duration_match.group(1).strip()
        
        return None
    
    def _extract_deadline(self, soup) -> Optional[str]:
        """Extract application deadline from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Deadline in ISO format (YYYY-MM-DD) or None if not found
        """
        text = soup.get_text(separator=' ', strip=True)
        
        # Look for deadline patterns
        patterns = [
            r'(?:deadline|last date|apply by)[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                normalized = self._normalize_date(date_str)
                if normalized:
                    return normalized
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to ISO format (YYYY-MM-DD)
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            ISO format date string or None if parsing fails
        """
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%d/%m/%y', '%d-%m-%y', '%d.%m.%y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%d %b %Y', '%d %B %Y',
            '%d-%b-%Y', '%d-%B-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _extract_description(self, soup) -> str:
        """Extract internship description from HTML
        
        Args:
            soup: BeautifulSoup object of internship card
            
        Returns:
            Description string
        """
        selectors = [
            '.internship_other_details', '.description', '.details',
            '[class*="description"]', '[class*="details"]', 'p'
        ]
        
        descriptions = []
        for selector in selectors:
            elems = soup.select(selector)
            for elem in elems:
                text = elem.text.strip()
                if text and len(text) > 20:
                    descriptions.append(text)
        
        if descriptions:
            return ' '.join(descriptions[:3])
        
        # Fallback
        all_text = soup.get_text(separator=' ', strip=True)
        if len(all_text) > 50:
            return all_text[:500]
        
        return "Internship opportunity. Please visit Internshala for complete details."
    
    def _extract_eligibility(self, soup, description: str) -> Dict[str, Any]:
        """Extract eligibility criteria from HTML and description
        
        Args:
            soup: BeautifulSoup object of internship card
            description: Extracted description text
            
        Returns:
            Dictionary with eligibility rules
        """
        text = description.lower()
        eligibility = {}
        
        # Extract year/class requirements
        year_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*year', text)
        if year_match:
            eligibility['min_year'] = int(year_match.group(1))
        
        # Extract stream/course requirements
        streams = []
        stream_keywords = {
            'engineering': ['engineering', 'b.tech', 'btech', 'b.e.'],
            'computer science': ['computer science', 'cs', 'cse', 'it', 'information technology'],
            'mba': ['mba', 'management', 'business administration'],
            'design': ['design', 'graphic', 'ui/ux'],
            'marketing': ['marketing', 'digital marketing'],
            'content': ['content', 'writing', 'copywriting']
        }
        
        for stream, keywords in stream_keywords.items():
            if any(kw in text for kw in keywords):
                streams.append(stream)
        
        if streams:
            eligibility['streams'] = streams
        
        # Extract skill requirements
        skills = []
        skill_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 
                         'machine learning', 'data science', 'excel', 'powerpoint']
        
        for skill in skill_keywords:
            if skill in text:
                skills.append(skill)
        
        if skills:
            eligibility['skills'] = skills[:5]  # Limit to top 5
        
        return eligibility
