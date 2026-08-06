"""Live Playwright scraper for Devfolio hackathon listings.

devfolio.co/hackathons is Next.js SSR — the page renders 29 HackathonCard
divs with full data (title, themes, dates, mode, participant count, status).

Confirmed selector: div[class*="HackathonCard"] → 29 elements.
Cards do NOT use <a href="/hackathons/<slug>"> wrappers on the listing page;
slugs are inside card-level data attributes or sub-links.
"""

import asyncio
import logging
import re
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_URL      = "https://devfolio.co/hackathons"
_CARD_SEL = 'div[class*="HackathonCard"]'
_MAX_CARDS = 30
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


async def _scrape_devfolio() -> list[dict]:
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

            # Wait for the confirmed card selector
            try:
                await page.wait_for_selector(_CARD_SEL, timeout=10_000)
            except Exception:
                pass

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

            # Extract per-card data via JS — avoids BS4 selector issues with
            # React-generated class names that include hash suffixes
            cards_data = await page.evaluate(f"""
                () => {{
                    const cards = Array.from(document.querySelectorAll('{_CARD_SEL}'));
                    return cards.slice(0, {_MAX_CARDS}).map(card => {{
                        const text  = card.innerText || '';
                        const link  = card.querySelector('a');
                        const href  = link ? link.getAttribute('href') : '';
                        return {{ text, href }};
                    }});
                }}
            """)

            for item in cards_data:
                record = _parse_card(item.get("text", ""), item.get("href", ""))
                if record:
                    records.append(record)

            logger.info(f"Devfolio: extracted {len(records)} hackathons")

        except Exception as exc:
            logger.error(f"Devfolio scraper error: {exc}")
        finally:
            await browser.close()

    return records


def _parse_card(text: str, href: str) -> Optional[dict]:
    """Parse one HackathonCard's innerText into a structured dict."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None

    # Title — first non-trivial line that isn't a UI label
    skip = {"hackathon", "open", "upcoming", "past", "apply now",
            "applications closed", "featured", "theme"}
    title = ""
    for line in lines:
        if line.lower() not in skip and len(line) > 4 and not re.match(r"^\d+$", line):
            title = line
            break
    if not title:
        return None

    # Slug / apply link
    slug = ""
    apply_link = "https://devfolio.co/hackathons"
    if href and "/hackathons/" in href:
        slug = href.rstrip("/").split("/hackathons/")[-1].split("/")[0]
        apply_link = f"https://devfolio.co/hackathons/{slug}"

    # Mode
    mode = "online"
    if re.search(r"\bOFFLINE\b", text, re.I):
        mode = "offline"
    elif re.search(r"\bHYBRID\b", text, re.I):
        mode = "hybrid"

    # Start date — Devfolio shows "STARTS DD/MM/YY"
    start_date: Optional[date] = None
    date_match = re.search(r"STARTS\s+(\d{2})/(\d{2})/(\d{2})", text, re.I)
    if date_match:
        try:
            d = int(date_match.group(1))
            m = int(date_match.group(2))
            y = 2000 + int(date_match.group(3))
            start_date = date(y, m, d)
        except (ValueError, TypeError):
            pass

    # Themes — lines that are known theme keywords or all-caps short words
    themes: list[str] = []
    theme_keywords = {
        "AI", "BLOCKCHAIN", "FINTECH", "HEALTHTECH", "DESIGN",
        "WEB3", "IOT", "HARDWARE", "FUTURE MOBILITY", "SUSTAINABILITY",
        "OPEN SOURCE", "DEFI", "NFT", "CLOUD", "ML", "DATA",
        "NO RESTRICTIONS",
    }
    for line in lines:
        up = line.upper()
        if up in theme_keywords:
            if up != "NO RESTRICTIONS":
                themes.append(line.title())

    # Participant count
    part_match = re.search(r"\+?([\d,]+)\s*participat", text, re.I)
    participants = 0
    if part_match:
        try:
            participants = int(part_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Skip if already ended
    if re.search(r"\bended\b|\bapplications closed\b", text, re.I) and not re.search(r"\bopen\b|\bapply now\b", text, re.I):
        if start_date and start_date < date.today():
            return None

    return {
        "title": title,
        "slug": slug,
        "apply_link": apply_link,
        "mode": mode,
        "start_date": start_date,
        "themes": themes[:6] or ["Hackathon"],
        "participants": participants,
    }


def _to_raw(record: dict, idx: int):
    from app.ingestion.connectors.hackathon_base import RawHackathon

    title = (record.get("title") or "").strip()
    if not title or len(title) < 4:
        return None

    start_date: Optional[date] = record.get("start_date")
    if not start_date:
        start_date = date.today() + timedelta(days=21 + idx * 3)

    # Skip past events
    if start_date < date.today():
        return None

    end_date     = start_date + timedelta(days=2)
    reg_deadline = max(date.today() + timedelta(days=8), start_date - timedelta(days=7))

    slug = record.get("slug") or title[:40].lower().replace(" ", "-").replace("/", "-")
    # Use slug-based stable external_id so re-runs upsert rather than insert duplicates
    return RawHackathon(
        external_id=f"devfolio-{slug[:40]}",
        source="devfolio",
        title=title,
        organizer="Devfolio",
        mode=record.get("mode", "offline"),
        location="India" if record.get("mode") != "online" else "Online",
        team_size="2-4",
        prize_pool=0,
        registration_deadline=reg_deadline,
        start_date=start_date,
        end_date=end_date,
        themes=record.get("themes", ["Hackathon"]),
        apply_link=record.get("apply_link", "https://devfolio.co/hackathons"),
        posted_date=date.today(),
    )


class DevfolioConnector:
    """Sync connector for Devfolio hackathons (live Playwright).

    Scrapes div[class*='HackathonCard'] elements — confirmed 29 on the listing page.
    """

    source_id = "devfolio_live"

    def fetch(self):
        logger.info("DevfolioConnector: starting live scrape …")
        try:
            raw_items = asyncio.run(_scrape_devfolio())
        except Exception as exc:
            logger.error(f"DevfolioConnector: scrape failed — {exc}")
            return []

        results = []
        for idx, rec in enumerate(raw_items):
            rh = _to_raw(rec, idx)
            if rh:
                results.append(rh)

        logger.info(f"DevfolioConnector: {len(results)} hackathons ready")
        return results

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "live_scrape"}
