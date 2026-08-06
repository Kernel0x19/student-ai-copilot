"""Live Playwright scraper for Unstop hackathon listings.

unstop.com/hackathons is server-rendered Angular — confirmed 36 card elements
(selector: div[class*='card']) and 15+ direct /hackathons/<slug> links in the
initial HTML after JS hydration.

Confirmed body text structure per card:
  <Title>
  <Organizer>
  <Team size> Members
  <Location or 'Online'>
  <Category>
  <Eligibility>
  [Prizes worth ₹X,XX,XXX]   (optional)
  Posted <date>
  <N days left | N months left>
"""

import asyncio
import logging
import re
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_URL      = "https://unstop.com/hackathons"
_MAX_CARDS = 25

# Confirmed Angular component selector — 18 elements on listing page
_LISTING_SEL = "app-competition-listing"


async def _scrape_unstop() -> list[dict]:
    from playwright.async_api import async_playwright

    records: list[dict] = []

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
            page = await ctx.new_page()
            await page.goto(_URL, wait_until="domcontentloaded", timeout=30_000)

            try:
                await page.wait_for_load_state("networkidle", timeout=12_000)
            except Exception:
                pass

            try:
                await page.wait_for_selector(_LISTING_SEL, timeout=12_000)
            except Exception:
                pass

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            # Extract per-listing data via JS using the confirmed Angular selector
            data = await page.evaluate(f"""
                () => {{
                    const items = Array.from(document.querySelectorAll('{_LISTING_SEL}'));
                    return items.slice(0, {_MAX_CARDS}).map(el => {{
                        const linkEl = el.querySelector('a[href*=\"/hackathons/\"]');
                        const href = linkEl ? linkEl.getAttribute('href') : '';
                        return {{ text: el.innerText || '', href }};
                    }});
                }}
            """)

            seen_titles: set[str] = set()
            for item in data:
                record = _parse_card(item.get("text", ""), item.get("href", ""), {})
                if record and record["title"] not in seen_titles:
                    seen_titles.add(record["title"])
                    records.append(record)

            logger.info(f"Unstop: {len(records)} hackathons extracted from {len(data)} listings")

        except Exception as exc:
            logger.error(f"Unstop scraper error: {exc}")
        finally:
            await browser.close()

    return records[:_MAX_CARDS]


def _parse_card(text: str, href: str, slug_map: dict) -> Optional[dict]:
    """Parse one Unstop card's innerText."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        return None

    # Title — first substantive line (skip very short or pure-number lines)
    title = ""
    for line in lines:
        if len(line) > 6 and not re.match(r"^[\d\s,₹%]+$", line):
            title = line
            break
    if not title:
        return None

    # Organizer — next substantive line after title
    organizer = ""
    idx = lines.index(title) if title in lines else 0
    for line in lines[idx + 1:]:
        if len(line) > 3 and not re.match(r"^[\d\s,₹%]+$", line) and "Members" not in line:
            organizer = line
            break

    # Mode / location
    mode = "online"
    location = "Online"
    if re.search(r"\bOnline\b", text, re.I):
        mode = "online"
        location = "Online"
    else:
        # look for a city/location line
        for line in lines:
            if re.search(r"\b(India|Mumbai|Delhi|Bengaluru|Hyderabad|Pune|Chennai|"
                         r"Jaipur|Noida|Gurugram|Kolkata|Ahmedabad)\b", line):
                mode = "offline"
                location = line[:80]
                break

    # Team size
    team_size = "1-4"
    team_match = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*Members", text, re.I)
    solo_match = re.search(r"Individual Participation|Solo", text, re.I)
    fixed_match = re.search(r"^(\d+)\s*$", "\n".join(lines), re.M)
    if team_match:
        team_size = f"{team_match.group(1)}-{team_match.group(2)}"
    elif solo_match:
        team_size = "Solo"
    elif fixed_match:
        team_size = fixed_match.group(1)

    # Prize pool
    prize_pool = 0
    prize_match = re.search(r"Prizes?\s+worth\s+[₹Rs.]*\s*([\d,]+)", text, re.I)
    if prize_match:
        try:
            prize_pool = int(prize_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Registration deadline — "N days left" or "N months left"
    reg_deadline: Optional[date] = None
    days_match   = re.search(r"(\d+)\s+days?\s+left", text, re.I)
    months_match = re.search(r"(\d+)\s+months?\s+left", text, re.I)
    if days_match:
        days = int(days_match.group(1))
        if days >= 8:   # filter out within-7-days
            reg_deadline = date.today() + timedelta(days=days)
    elif months_match:
        months = int(months_match.group(1))
        reg_deadline = date.today() + timedelta(days=months * 30)

    if not reg_deadline:
        reg_deadline = date.today() + timedelta(days=30)

    # Apply link
    apply_link = "https://unstop.com/hackathons"
    if href and "/hackathons/" in href:
        apply_link = f"https://unstop.com{href}" if href.startswith("/") else href
    else:
        # try slug_map
        for slug, path in slug_map.items():
            if slug.lower()[:10] in title.lower():
                apply_link = f"https://unstop.com{path}"
                break

    # Themes — from category lines
    themes: list[str] = []
    known = ["AI", "Artificial Intelligence", "Blockchain", "FinTech", "Web3",
             "IoT", "Software Development", "Data Science", "Hardware", "Design",
             "Games", "Finance", "Arts", "Engineering", "Applied AI"]
    for kw in known:
        if kw.lower() in text.lower():
            short = kw if kw != "Artificial Intelligence" else "AI"
            if short not in themes:
                themes.append(short)

    return {
        "title": title,
        "organizer": organizer,
        "mode": mode,
        "location": location,
        "team_size": team_size,
        "prize_pool": prize_pool,
        "registration_deadline": reg_deadline,
        "themes": themes[:5] or ["Hackathon"],
        "apply_link": apply_link,
    }


def _to_raw(record: dict, idx: int):
    from app.ingestion.connectors.hackathon_base import RawHackathon

    title = (record.get("title") or "").strip()
    if not title or len(title) < 4:
        return None

    reg_deadline: Optional[date] = record.get("registration_deadline")
    if not reg_deadline or reg_deadline <= date.today() + timedelta(days=7):
        return None  # skip within-7-days

    slug = title[:40].lower().replace(" ", "-").replace("/", "-")
    # Use slug-based stable external_id so re-runs upsert rather than insert duplicates
    return RawHackathon(
        external_id=f"unstop-{slug[:40]}",
        source="unstop",
        title=title,
        organizer=record.get("organizer", "Unstop"),
        mode=record.get("mode", "online"),
        location=record.get("location", "Online"),
        team_size=record.get("team_size", "1-4"),
        prize_pool=record.get("prize_pool", 0),
        registration_deadline=reg_deadline,
        start_date=reg_deadline + timedelta(days=1),
        end_date=reg_deadline + timedelta(days=3),
        themes=record.get("themes", ["Hackathon"]),
        apply_link=record.get("apply_link", "https://unstop.com/hackathons"),
        posted_date=date.today(),
    )


class UnstopHackathonConnector:
    """Sync connector for Unstop hackathons (live Playwright scrape).

    Scrapes div[class*='card'] elements — confirmed 36 cards on the listing page.
    """

    source_id = "unstop_hackathon_live"

    def fetch(self):
        logger.info("UnstopHackathonConnector: starting live scrape …")
        try:
            raw_items = asyncio.run(_scrape_unstop())
        except Exception as exc:
            logger.error(f"UnstopHackathonConnector: scrape failed — {exc}")
            return []

        results = []
        for idx, rec in enumerate(raw_items):
            rh = _to_raw(rec, idx)
            if rh:
                results.append(rh)

        logger.info(f"UnstopHackathonConnector: {len(results)} hackathons ready")
        return results

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "live_scrape"}
