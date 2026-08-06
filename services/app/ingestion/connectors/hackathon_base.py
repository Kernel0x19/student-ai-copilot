"""Shared base types for hackathon connectors.

All 8 hackathon connectors (4 live + 4 dummy) use RawHackathon as the
transfer object.  The hackathon ingestion pipeline converts these into
Hackathon ORM rows.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class RawHackathon:
    """Transfer object for one scraped/dummy hackathon listing.

    Field contract (matches the Hackathon DB model exactly):
      - external_id  : stable unique key per source  (e.g. "unstop-live-42")
      - source       : platform slug                  (e.g. "unstop", "devfolio")
      - title        : event name
      - organizer    : host org / company
      - mode         : "online" | "offline" | "hybrid"
      - location     : city/venue or "Online" for online-only
      - team_size    : e.g. "1-4", "2-5", "Solo"  (string, free-form)
      - prize_pool   : integer rupees (0 if none / unknown)
      - registration_deadline : YYYY-MM-DD or None
      - start_date   : YYYY-MM-DD or None
      - end_date     : YYYY-MM-DD or None
      - themes       : list of tag strings e.g. ["AI", "Blockchain"]
      - apply_link   : canonical registration URL
      - posted_date  : YYYY-MM-DD (today if unknown)
    """

    external_id: str
    source: str
    title: str
    organizer: str = ""
    mode: str = "online"          # online | offline | hybrid
    location: str = "Online"
    team_size: str = "1-4"
    prize_pool: int = 0           # integer rupees
    registration_deadline: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    themes: list[str] = field(default_factory=list)
    apply_link: str = ""
    posted_date: Optional[date] = None
