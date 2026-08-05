"""Sync wrapper around the async InternshalaConnector.

The original InternshalaConnector uses async Playwright + BeautifulSoup to scrape
internshala.com.  The ingestion pipeline is synchronous, so this module:

1. Runs the async scraper in a fresh event loop via asyncio.run()
2. Converts the parsed records (dicts) into RawOpportunity objects
3. Exposes a plain .fetch() that the sync pipeline can call directly

Usage in pipeline.py:
    from app.ingestion.connectors.internshala_sync import InternshalaLiveConnector
    connector = InternshalaLiveConnector()
    raw_items = connector.fetch()          # list[RawOpportunity]
"""

import asyncio
import logging
from datetime import date, timedelta
from typing import Optional

from app.ingestion.connectors.internshala import InternshalaConnector
from app.ingestion.connectors.seed_connectors import RawOpportunity

logger = logging.getLogger(__name__)

# Default scraper config — headless, 0.5-second rate limit, robots.txt respected
# Rate limit reduced from 3.0s to 0.5s for faster ingestion (20 cards ≈ 30s total)
_DEFAULT_CONFIG = {
    "headless": True,
    "rate_limit_delay": 0.5,
    "skip_robots_check": False,
    "max_cards": 20,  # cap how many cards to process per run
}


def _parse_stipend(raw: dict) -> tuple[Optional[int], Optional[int]]:
    """Return (amount_min, amount_max) from a scraped record."""
    amount = raw.get("amount") or raw.get("amount_min")
    if amount:
        try:
            v = int(amount)
            return v, v
        except (ValueError, TypeError):
            pass
    return None, None


def _parse_deadline(raw: dict) -> Optional[date]:
    """Return a date object from ISO deadline string, or 60 days from now."""
    dl = raw.get("deadline")
    if dl:
        from datetime import datetime
        try:
            return datetime.strptime(str(dl), "%Y-%m-%d").date()
        except ValueError:
            pass
    return date.today() + timedelta(days=60)


def _to_raw_opportunity(record: dict, idx: int) -> Optional[RawOpportunity]:
    """Convert one parsed Internshala record dict to a RawOpportunity."""
    title = (record.get("title") or "").strip()
    if not title or title == "Untitled Internship":
        logger.debug(f"Skipping card {idx}: no title")
        return None

    amount_min, amount_max = _parse_stipend(record)
    eligibility = record.get("eligibility_rules") or {}

    return RawOpportunity(
        external_id=f"internshala-live-{idx}-{title[:30].replace(' ', '-').lower()}",
        source="internshala",
        title=title,
        description=(record.get("description") or "Visit Internshala for full details.").strip(),
        amount_min=amount_min,
        amount_max=amount_max,
        deadline=_parse_deadline(record),
        eligibility_rules={
            "streams": eligibility.get("streams", []),
            "skills": eligibility.get("skills", []),
            "year_of_study": (
                {"min": eligibility["min_year"]} if "min_year" in eligibility else {"min": 1, "max": 4}
            ),
            "states": ["ALL"],
        },
        documents_required=["resume"],
        application_url=record.get("application_url") or record.get("source_url"),
        state_filter=["ALL"],
        tags=record.get("tags", []) + ["internshala", "live"],
        raw_data={
            "company": record.get("company"),
            "location": record.get("location"),
            "duration": record.get("duration"),
        },
    )


class InternshalaLiveConnector:
    """Sync connector that drives the async InternshalaConnector.

    Call .fetch() to get a list[RawOpportunity] ready for normalize_internship().
    Gracefully returns an empty list if scraping fails (e.g. robots.txt block,
    network error) so the pipeline continues with seed data as fallback.
    """

    source_id = "internshala_live"

    def __init__(self, config: dict | None = None):
        self._config = {**_DEFAULT_CONFIG, **(config or {})}

    def fetch(self) -> list[RawOpportunity]:
        logger.info("InternshalaLiveConnector: starting live scrape …")
        try:
            raw_items = asyncio.run(self._async_fetch())
        except Exception as exc:
            logger.error(f"InternshalaLiveConnector: async scrape failed — {exc}")
            return []

        results: list[RawOpportunity] = []
        for idx, record in enumerate(raw_items):
            ro = _to_raw_opportunity(record, idx)
            if ro:
                results.append(ro)

        logger.info(f"InternshalaLiveConnector: got {len(results)} usable internships")
        return results

    async def _async_fetch(self) -> list[dict]:
        """Run fetch() + parse() on the underlying async connector."""
        connector = InternshalaConnector(self._config)
        raw_html = await connector.fetch()          # list[{html, url}]
        parsed   = await connector.parse(raw_html)  # list[dict]
        return parsed

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "live_scrape"}
