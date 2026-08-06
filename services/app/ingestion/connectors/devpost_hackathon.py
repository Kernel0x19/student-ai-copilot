# DUMMY DATA — placeholder, live scraping not feasible.
# Devpost is a pure SPA: the listing page returns only nav/header HTML.
# All hackathon cards are loaded asynchronously via internal XHR calls that
# require authenticated session cookies.  The public /api/v3/hackathons endpoint
# returns HTTP 404 from outside Devpost's own frontend.
# To enable live data: obtain Devpost Partner API credentials and replace
# this file with an authenticated API client.

from datetime import date
from app.ingestion.connectors.hackathon_base import RawHackathon

# Registration deadlines: 15 distinct dates across two non-overlapping windows.
# Aug 14–21 (existing 8) + Oct 6–12 (7 new — after hack2skill's Oct 5 cutoff).
# All dates unique across all 4 dummy connector files.
_DL = [
    # Existing 8 (Aug 14–21)
    date(2026, 8, 14),
    date(2026, 8, 15),
    date(2026, 8, 16),
    date(2026, 8, 17),
    date(2026, 8, 18),
    date(2026, 8, 19),
    date(2026, 8, 20),
    date(2026, 8, 21),
    # 7 new additions (Oct 6–12, after hack2skill's Oct 5 window)
    date(2026, 10,  6),
    date(2026, 10,  7),
    date(2026, 10,  8),
    date(2026, 10,  9),
    date(2026, 10, 10),
    date(2026, 10, 11),
    date(2026, 10, 12),
]


class DevpostHackathonConnector:
    """15 realistic Devpost hackathon listings (dummy data).

    8 entries with Aug 14–21 deadlines (original after near-expiry cleanup)
    + 7 new entries with Oct 6–12 deadlines, reaching the target of 15.
    """

    source_id = "devpost"

    def fetch(self) -> list[RawHackathon]:
        return [
            RawHackathon(
                external_id="devpost-dummy-008", source="devpost",
                title="HackMIT: Innovation Challenge",
                organizer="MIT", mode="offline",
                location="Cambridge, MA, USA",
                team_size="2-4", prize_pool=166000,
                registration_deadline=_DL[0],
                start_date=date(2026, 8, 28), end_date=date(2026, 8, 30),
                themes=["AI", "Biotech", "Climate", "Hardware"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 7, 29),
            ),
            RawHackathon(
                external_id="devpost-dummy-009", source="devpost",
                title="Polygon Build It: Web3 Hackathon",
                organizer="Polygon Labs", mode="online",
                location="Online", team_size="1-5", prize_pool=1245000,
                registration_deadline=_DL[1],
                start_date=date(2026, 8, 17), end_date=date(2026, 9, 17),
                themes=["Blockchain", "Web3", "DeFi", "NFT"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="devpost-dummy-010", source="devpost",
                title="Snap AR Lens Hackathon",
                organizer="Snap Inc.", mode="online",
                location="Online", team_size="1-3", prize_pool=166000,
                registration_deadline=_DL[2],
                start_date=date(2026, 8, 18), end_date=date(2026, 9, 18),
                themes=["AR/VR", "Mobile", "Design", "AI"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="devpost-dummy-011", source="devpost",
                title="Anthropic AI Safety Hackathon",
                organizer="Anthropic", mode="online",
                location="Online", team_size="1-4", prize_pool=332000,
                registration_deadline=_DL[3],
                start_date=date(2026, 8, 19), end_date=date(2026, 9, 19),
                themes=["AI Safety", "LLM", "Ethics", "Research"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="devpost-dummy-012", source="devpost",
                title="Stripe Financial Infrastructure Hack",
                organizer="Stripe", mode="online",
                location="Online", team_size="1-4", prize_pool=498000,
                registration_deadline=_DL[4],
                start_date=date(2026, 8, 20), end_date=date(2026, 9, 20),
                themes=["FinTech", "Payments", "API", "SaaS"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="devpost-dummy-013", source="devpost",
                title="Microsoft Imagine Cup 2026",
                organizer="Microsoft", mode="hybrid",
                location="Seattle, WA / Online",
                team_size="1-4", prize_pool=1328000,
                registration_deadline=_DL[5],
                start_date=date(2026, 9, 3), end_date=date(2026, 9, 5),
                themes=["AI", "Sustainability", "Accessibility", "Cloud"],
                apply_link="https://imaginecup.microsoft.com/",
                posted_date=date(2026, 7, 27),
            ),
            RawHackathon(
                external_id="devpost-dummy-014", source="devpost",
                title="OpenAI Developer Showcase",
                organizer="OpenAI", mode="online",
                location="Online", team_size="1-5", prize_pool=830000,
                registration_deadline=_DL[6],
                start_date=date(2026, 8, 22), end_date=date(2026, 9, 22),
                themes=["LLM", "AI", "GenAI", "GPT", "Agents"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="devpost-dummy-015", source="devpost",
                title="HealthTech Innovation Hackathon",
                organizer="WHO Digital Health", mode="online",
                location="Online", team_size="2-5", prize_pool=415000,
                registration_deadline=_DL[7],
                start_date=date(2026, 8, 23), end_date=date(2026, 9, 23),
                themes=["HealthTech", "AI", "Data", "Social Impact"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 8, 2),
            ),
            # ── 7 new entries (Oct 6–12 deadlines) ──────────────────────────
            RawHackathon(
                external_id="devpost-dummy-016", source="devpost",
                title="Cloudflare Workers AI Hackathon",
                organizer="Cloudflare", mode="online",
                location="Online", team_size="1-4", prize_pool=415000,
                registration_deadline=_DL[8],
                start_date=date(2026, 10, 8), end_date=date(2026, 11, 8),
                themes=["Cloud", "AI", "Edge Computing", "Serverless"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 1),
            ),
            RawHackathon(
                external_id="devpost-dummy-017", source="devpost",
                title="Meta Llama Innovation Challenge",
                organizer="Meta AI", mode="online",
                location="Online", team_size="1-5", prize_pool=664000,
                registration_deadline=_DL[9],
                start_date=date(2026, 10, 9), end_date=date(2026, 11, 9),
                themes=["LLM", "AI", "Open Source", "Agents"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 2),
            ),
            RawHackathon(
                external_id="devpost-dummy-018", source="devpost",
                title="Solana Grizzlython",
                organizer="Solana Foundation", mode="online",
                location="Online", team_size="1-5", prize_pool=1660000,
                registration_deadline=_DL[10],
                start_date=date(2026, 10, 10), end_date=date(2026, 11, 10),
                themes=["Blockchain", "Web3", "Solana", "DeFi"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 3),
            ),
            RawHackathon(
                external_id="devpost-dummy-019", source="devpost",
                title="Intel AI PC Developer Challenge",
                organizer="Intel", mode="online",
                location="Online", team_size="1-3", prize_pool=249000,
                registration_deadline=_DL[11],
                start_date=date(2026, 10, 11), end_date=date(2026, 11, 11),
                themes=["AI", "Hardware", "Edge AI", "PC"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 4),
            ),
            RawHackathon(
                external_id="devpost-dummy-020", source="devpost",
                title="Twilio Quest: The AI Chronicles",
                organizer="Twilio", mode="online",
                location="Online", team_size="1-4", prize_pool=332000,
                registration_deadline=_DL[12],
                start_date=date(2026, 10, 12), end_date=date(2026, 11, 12),
                themes=["AI", "API", "Communication", "Telecom"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 5),
            ),
            RawHackathon(
                external_id="devpost-dummy-021", source="devpost",
                title="Vercel AI SDK Hackathon",
                organizer="Vercel", mode="online",
                location="Online", team_size="1-4", prize_pool=249000,
                registration_deadline=_DL[13],
                start_date=date(2026, 10, 13), end_date=date(2026, 11, 13),
                themes=["AI", "Web Dev", "Serverless", "Frontend"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 6),
            ),
            RawHackathon(
                external_id="devpost-dummy-022", source="devpost",
                title="Supabase Launch Week Hackathon",
                organizer="Supabase", mode="online",
                location="Online", team_size="1-4", prize_pool=166000,
                registration_deadline=_DL[14],
                start_date=date(2026, 10, 14), end_date=date(2026, 11, 14),
                themes=["Database", "Open Source", "Web Dev", "AI"],
                apply_link="https://devpost.com/hackathons",
                posted_date=date(2026, 9, 7),
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
