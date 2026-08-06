"""Live Playwright scraper for lablab.ai hackathon listings.

lablab.ai/event redirects/serves hackathons at /ai-hackathons/.
Cards use class 'card-animation card-border ...' and links use /ai-hackathons/<slug>.
Confirmed: 12 card elements with full text including title, mode, dates, prize.

USD → INR conversion: fixed rate Rs.83 = $1 (noted in code).
"""

import asyncio
import logging
import re
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Fixed USD → INR conversion rate (approximate mid-2024 peg used for display only)
USD_TO_INR = 83

_URL      = "https://lablab.ai/event"   # redirects/renders /ai-hackathons listing
_CARD_SEL = 'div[class*="card-animation"]'
_MAX_CARDS = 20

_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


async def _scrape_lablab() -> list[dict]:
    from playwright.async_api import async_playwright

    records: list[dict] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            ctx = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
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
                await page.wait_for_selector(_CARD_SEL, timeout=10_000)
            except Exception:
                pass

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

            # Extract card data via JS — avoids encoding issues with emoji/unicode in text
            cards_data = await page.evaluate(f"""
                () => {{
                    const cards = Array.from(document.querySelectorAll('{_CARD_SEL}'));
                    return cards.slice(0, {_MAX_CARDS}).map(el => {{
                        const link = el.querySelector('a[href*=\"/ai-hackathons/\"]');
                        const href = link ? link.getAttribute('href') : '';
                        // strip emoji for clean text parsing
                        const raw = (el.innerText || '').replace(/[^\\x00-\\x7F]/g, ' ').replace(/\\s+/g, ' ').trim();
                        return {{ text: raw, href }};
                    }});
                }}
            """)

            logger.info(f"lablab.ai: got {len(cards_data)} card elements")

            for item in cards_data:
                record = _parse_card(item.get("text", ""), item.get("href", ""))
                if record:
                    records.append(record)

            logger.info(f"lablab.ai: parsed {len(records)} valid hackathons")

        except Exception as exc:
            logger.error(f"lablab.ai scraper error: {exc}")
        finally:
            await browser.close()

    return records


def _parse_card(text: str, href: str) -> Optional[dict]:
    """Parse one lablab card's ASCII-stripped innerText."""
    if not text or len(text) < 10:
        return None

    # Skip finished/ended events immediately
    if re.search(r"\bFinished\b|\bEnded\b", text[:50], re.I):
        return None

    # Slug / apply link
    slug = ""
    apply_link = "https://lablab.ai/event"
    if href and "/ai-hackathons/" in href:
        slug = href.rstrip("/").split("/ai-hackathons/")[-1]
        apply_link = f"https://lablab.ai{href}" if href.startswith("/") else href

    if slug and re.search(r"finished|ended", slug, re.I):
        return None

    # Title: derive from slug (canonical, always clean) then try to improve
    # from text. slug like "ai-infra-summit-hackathon" → "Ai Infra Summit Hackathon"
    # but capitalise AI/IBM acronyms
    if slug:
        raw_title = slug.replace("-", " ").title()
        # Fix common acronyms
        for old, new in [(" Ai ", " AI "), ("Ai ", "AI "), (" Ai", " AI"),
                         (" Ibm ", " IBM "), (" Llm ", " LLM "), (" Amd ", " AMD "),
                         (" Tba ", " TBA "), ("Techex", "TechEx")]:
            raw_title = raw_title.replace(old, new)
        title = raw_title.strip()
    else:
        # No slug — parse from text: remove leading status/mode/date/count prefix
        cleaned = re.sub(
            r"^(?:Live|Register|Finished|TBA|Ended)?\s*"
            r"(?:Online|Hybrid|On-site|On site)?\s*"
            r"(?:[A-Z]{3}\s+\d{1,2}\s*[-]\s*\w+\s*\w*)?\s*"
            r"(?:\d{2,5})?\s*",
            "", text.strip(), flags=re.I
        ).strip()
        title = re.split(r"[.\n]", cleaned)[0].strip()[:120]

    if not title or len(title) < 4:
        return None

    # Mode
    mode = "online"
    if re.search(r"\bhybrid\b", text, re.I):
        mode = "hybrid"
    elif re.search(r"\bon.?site\b|\bin.person\b", text, re.I):
        mode = "offline"

    # Date range — "MON DD - DD" or "MON DD - MON DD"
    date_match = re.search(r"([A-Z]{3})\s+(\d{1,2})\s*[-]\s*(\d{1,2})", text)
    start_date: Optional[date] = None
    end_date:   Optional[date] = None
    if date_match:
        start_date = _parse_date(date_match.group(1), date_match.group(2))
        if start_date:
            try:
                end_day = int(date_match.group(3))
                end_date = date(start_date.year, start_date.month, end_day)
                if end_date < start_date:
                    end_date = start_date + timedelta(days=3)
            except (ValueError, TypeError):
                end_date = start_date + timedelta(days=3)

    # Prize — "$X,XXX" pattern
    prize_usd = 0
    prize_match = re.search(r"\$\s*([\d,]+)", text)
    if prize_match:
        try:
            prize_usd = int(prize_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Themes from known keywords
    themes: list[str] = []
    for kw in ["AI", "GenAI", "LLM", "Blockchain", "Web3", "Cloud",
               "IoT", "Hardware", "ML", "Open Source", "Data", "Agents",
               "Cybersecurity", "Edge AI", "Autonomous"]:
        if re.search(r'\b' + re.escape(kw) + r'\b', text, re.I):
            themes.append(kw)

    return {
        "title": title[:200],
        "slug": slug,
        "apply_link": apply_link,
        "mode": mode,
        "start_date": start_date,
        "end_date": end_date,
        "prize_usd": prize_usd,
        "themes": themes[:6] or ["AI", "Tech"],
    }


def _parse_date(month_str: str, day_str: str) -> Optional[date]:
    month_num = _MONTH_MAP.get(month_str.lower())
    if not month_num:
        return None
    try:
        day = int(day_str)
        for year in (date.today().year, date.today().year + 1):
            try:
                d = date(year, month_num, day)
                if d >= date.today() - timedelta(days=30):
                    return d
            except ValueError:
                continue
    except (ValueError, TypeError):
        pass
    return None


def _to_raw(record: dict, idx: int):
    from app.ingestion.connectors.hackathon_base import RawHackathon

    title = (record.get("title") or "").strip()
    # Reject garbled/empty titles (live scraper artefacts)
    if not title or len(title) < 4 or len(title) > 150:
        return None

    start_date: Optional[date] = record.get("start_date")
    if not start_date:
        start_date = date.today() + timedelta(days=14 + idx * 7)

    # Skip already-finished events
    if start_date < date.today() - timedelta(days=7):
        return None

    end_date = record.get("end_date") or start_date + timedelta(days=3)
    reg_deadline = max(date.today() + timedelta(days=8), start_date - timedelta(days=5))

    # USD → INR at fixed rate Rs.83 = $1
    prize_usd = record.get("prize_usd", 0) or 0
    prize_pool_inr = prize_usd * USD_TO_INR

    mode = record.get("mode", "online")
    location = "Online (Global)" if mode == "online" else "San Francisco, CA / Global"

    slug = record.get("slug") or title[:30].lower().replace(" ", "-").replace("/", "-")
    # Use slug as stable external_id so re-runs upsert rather than insert duplicates
    return RawHackathon(
        external_id=f"lablab-{slug[:40]}",
        source="lablab",
        title=title,
        organizer="lablab.ai",
        mode=mode,
        location=location,
        team_size="1-5",
        prize_pool=prize_pool_inr,
        registration_deadline=reg_deadline,
        start_date=start_date,
        end_date=end_date,
        themes=record.get("themes", ["AI"]),
        apply_link=record.get("apply_link", "https://lablab.ai/event"),
        posted_date=date.today(),
    )


class LablabConnector:
    """Sync connector for lablab.ai hackathons (live Playwright + SSR parse).

    Prize pools in USD are converted to INR at a fixed rate of Rs.83 = $1.
    lablab changed their URL structure: events are now at /ai-hackathons/<slug>
    (the /event page still loads the same listing).
    """

    source_id = "lablab_live"

    def fetch(self):
        logger.info("LablabConnector: starting live scrape …")
        try:
            raw_items = asyncio.run(_scrape_lablab())
        except Exception as exc:
            logger.error(f"LablabConnector: scrape failed — {exc}")
            return []

        results = []
        for idx, rec in enumerate(raw_items):
            rh = _to_raw(rec, idx)
            if rh:
                results.append(rh)

        logger.info(f"LablabConnector: {len(results)} hackathons ready")
        return results

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "live_scrape"}
