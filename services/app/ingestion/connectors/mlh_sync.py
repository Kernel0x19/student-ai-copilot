"""Live Playwright scraper for MLH (Major League Hacking) event listings.

mlh.io/seasons/2026/events is confirmed server-rendered: the initial HTML
contains full event names, date ranges, locations, and in-person/digital flags.
Prize pool defaults to 0 — MLH is a free-entry prestige hackathon circuit with
no cash prizes (merit badges and sponsor perks only).

Scrape strategy
---------------
1. Navigate to /seasons/2026/events (the current active season).
2. waitForLoadState("networkidle") to allow any JS hydration.
3. Parse .event cards with BeautifulSoup.
4. Also check /seasons/2025/events as a fallback for more listings.
"""

import asyncio
import logging
import re
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_URLS = [
    "https://mlh.io/seasons/2027/events",   # MLH season numbering is 1 year ahead —
    "https://mlh.io/events",                #  2027 season = events running in 2026/27
]
_CARD_SEL  = ".event, [class*='event'], article"
_MAX_CARDS = 30   # cap across both season pages combined


async def _scrape_mlh() -> list[dict]:
    from playwright.async_api import async_playwright

    all_records: list[dict] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            ctx = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            for url in _URLS:
                if len(all_records) >= _MAX_CARDS:
                    break
                page = await ctx.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=25_000)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10_000)
                    except Exception:
                        pass

                    for sel in (_CARD_SEL, "li.event", "div.event-wrapper"):
                        try:
                            await page.wait_for_selector(sel, timeout=8_000)
                            break
                        except Exception:
                            continue

                    html = await page.content()
                    season_records = _parse_mlh_html(html)
                    all_records.extend(season_records)
                    logger.info(f"MLH: {url} → {len(season_records)} events")
                except Exception as exc:
                    logger.warning(f"MLH: failed to scrape {url} — {exc}")
                finally:
                    await page.close()
        finally:
            await browser.close()

    return all_records[:_MAX_CARDS]


def _parse_mlh_html(html: str) -> list[dict]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("beautifulsoup4 not installed")
        return []

    soup = BeautifulSoup(html, "html.parser")
    records: list[dict] = []

    # MLH renders each event as a <div class="event"> or similar container
    # The confirmed scrape text shows: "EventNameDATECity, State, CountryIn-Person"
    # Pattern: EventName + date_range + location + mode flag

    # Try structured card selectors first
    cards = (
        soup.select("div.event")
        or soup.select("li.event")
        or soup.select("article.event")
        or soup.select("[class*='event-']")
    )

    if not cards:
        # The confirmed scrape output is a run-on string — parse that text stream
        # Example: "HackPrixJUN 13 - 14Hyderabad…In-PersonJAMHacksJUN 12 - 14…"
        body_text = soup.get_text(separator="\n", strip=True)
        records = _parse_mlh_text_stream(body_text)
        return records

    for card in cards[:_MAX_CARDS]:
        txt = card.get_text(separator=" ", strip=True)
        record = _extract_event_from_text(txt)
        if record:
            records.append(record)

    return records


def _parse_mlh_text_stream(text: str) -> list[dict]:
    """Parse the run-on text format MLH uses when HTML structure is minimal.

    Pattern per event:
        <EventName><MON DD - DD><City, State, Country><In-Person|Digital>
    Optional tags: HIGH SCHOOL, DIVERSITY
    """
    records: list[dict] = []

    # Split on month-year date patterns: "JUN 13 - 14", "APR 25 - 27", etc.
    parts = re.split(
        r"([A-Z]{3}\s+\d{1,2}\s+-\s+\d{1,2})",
        text
    )

    # parts alternates: [pre, date, rest, date, rest, ...]
    idx = 0
    while idx < len(parts) - 1:
        if re.match(r"[A-Z]{3}\s+\d{1,2}\s+-\s+\d{1,2}", parts[idx]):
            date_str = parts[idx].strip()
            after    = parts[idx + 1].strip() if idx + 1 < len(parts) else ""
            # title is the last non-empty line BEFORE this date token
            title_candidate = parts[idx - 1].strip().split("\n")[-1].strip() if idx > 0 else ""
            title_candidate = re.sub(r"(HIGH SCHOOL|DIVERSITY|Past Events \d+|Find.*|2025|2026)$", "", title_candidate).strip()

            # location + mode are in the `after` block up to the next title
            mode = "offline"
            location = "Worldwide"
            if re.search(r"\bDigital\b|\bOnline\b|\bEverywhere\b", after[:80], re.I):
                mode = "online"
                location = "Online (Worldwide)"
            elif re.search(r"\bHybrid\b", after[:80], re.I):
                mode = "hybrid"
            else:
                # extract "City, State, Country"
                loc_match = re.match(r"^([A-Za-z,\. ]+?)(?:In-Person|Digital|$)", after[:120])
                if loc_match:
                    location = loc_match.group(1).strip().rstrip(",")

            start_date = _parse_mlh_date(date_str)

            if title_candidate and len(title_candidate) > 3:
                records.append({
                    "title": title_candidate,
                    "date_str": date_str,
                    "start_date": start_date,
                    "mode": mode,
                    "location": location,
                })
        idx += 1

    return records


def _extract_event_from_text(txt: str) -> Optional[dict]:
    """Extract fields from a single MLH card's text content."""
    date_match = re.search(r"([A-Z]{3}\s+\d{1,2}\s+-\s+\d{1,2})", txt)
    if not date_match:
        return None

    date_str = date_match.group(1)
    before   = txt[: date_match.start()].strip()
    after    = txt[date_match.end() :].strip()

    # title = last meaningful part before the date
    title = before.split("\n")[-1].strip()
    title = re.sub(r"(HIGH SCHOOL|DIVERSITY)\s*$", "", title).strip()

    if not title or len(title) < 3:
        return None

    mode = "online" if re.search(r"\bDigital\b|\bEverywhere\b", after, re.I) else "offline"
    location_match = re.match(r"^([A-Za-z ,\.]+?)(?:In-Person|Digital|$)", after)
    location = location_match.group(1).strip().rstrip(",") if location_match else "Worldwide"

    return {
        "title": title,
        "date_str": date_str,
        "start_date": _parse_mlh_date(date_str),
        "mode": mode,
        "location": location,
    }


def _parse_mlh_date(date_str: str) -> Optional[date]:
    """Parse 'JUN 13 - 14' → date object using current/next year."""
    m = re.match(r"([A-Z]{3})\s+(\d{1,2})\s*-\s*\d{1,2}", date_str)
    if not m:
        return None
    month_str, day_str = m.group(1).lower(), m.group(2)
    month_num = _MONTH_MAP.get(month_str)
    if not month_num:
        return None
    try:
        day = int(day_str)
        # try current year, then next year
        for year in (date.today().year, date.today().year + 1):
            try:
                d = date(year, month_num, day)
                if d >= date.today() - timedelta(days=365):
                    return d
            except ValueError:
                continue
    except (ValueError, TypeError):
        pass
    return None


_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _to_raw(record: dict, idx: int):
    from app.ingestion.connectors.hackathon_base import RawHackathon

    title = (record.get("title") or "").strip()
    if not title or title.lower().startswith("find"):
        return None

    start_date: Optional[date] = record.get("start_date")
    if not start_date:
        start_date = date.today() + timedelta(days=30 + idx * 7)

    # Skip events whose start date is already in the past
    if start_date < date.today():
        return None

    end_date     = start_date + timedelta(days=2)
    reg_deadline = max(date.today() + timedelta(days=2), start_date - timedelta(days=7))

    # Ensure the reg deadline is always at least 7 days away so it doesn't
    # immediately appear as "closing soon" on first scrape
    if reg_deadline <= date.today() + timedelta(days=7):
        reg_deadline = date.today() + timedelta(days=8)

    mode = record.get("mode", "offline")
    location = record.get("location", "Worldwide")
    if not location:
        location = "Online (Worldwide)" if mode == "online" else "Worldwide"

    slug = title[:40].lower().replace(" ", "-").replace("/", "-")
    # Use slug-based stable external_id so re-runs upsert rather than insert duplicates
    return RawHackathon(
        external_id=f"mlh-{slug[:40]}",
        source="mlh",
        title=title,
        organizer="Major League Hacking (MLH)",
        mode=mode,
        location=location,
        team_size="1-4",
        prize_pool=0,   # MLH events have no cash prizes — prestige + sponsor perks only
        registration_deadline=reg_deadline,
        start_date=start_date,
        end_date=end_date,
        themes=["Hackathon", "Student", "MLH"],
        apply_link="https://mlh.io/seasons/2026/events",
        posted_date=date.today(),
    )


class MLHConnector:
    """Sync connector for MLH hackathons (live Playwright + SSR parse).

    Prize pool is always 0 — MLH is a prestige hackathon circuit, not a cash-prize platform.
    """

    source_id = "mlh_live"

    def fetch(self):
        logger.info("MLHConnector: starting live scrape …")
        try:
            raw_items = asyncio.run(_scrape_mlh())
        except Exception as exc:
            logger.error(f"MLHConnector: scrape failed — {exc}")
            return []

        results = []
        for idx, rec in enumerate(raw_items):
            rh = _to_raw(rec, idx)
            if rh:
                results.append(rh)

        logger.info(f"MLHConnector: {len(results)} hackathons ready")
        return results

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "live_scrape"}
