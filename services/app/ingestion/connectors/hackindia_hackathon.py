# DUMMY DATA — placeholder, live scraping not feasible.
# hackindia.com is a parked domain currently for sale on HugeDomains.com
# (listed at $4,995 as of August 2026 — the site returns a domain-for-sale page).
# The original HackIndia platform no longer operates at this URL.
# To re-enable: verify a new official domain for HackIndia and build a fresh
# scraper or API connector against that URL.

from datetime import date
from app.ingestion.connectors.hackathon_base import RawHackathon

# Registration deadlines: 15 distinct dates (Sep 6–20, 2026)
# Each date is unique across all 4 dummy connector files.
_DL = [
    date(2026, 9,  6),   # 001
    date(2026, 9,  7),   # 002
    date(2026, 9,  8),   # 003
    date(2026, 9,  9),   # 004
    date(2026, 9, 10),   # 005
    date(2026, 9, 11),   # 006
    date(2026, 9, 12),   # 007
    date(2026, 9, 13),   # 008
    date(2026, 9, 14),   # 009
    date(2026, 9, 15),   # 010
    date(2026, 9, 16),   # 011
    date(2026, 9, 17),   # 012
    date(2026, 9, 18),   # 013
    date(2026, 9, 19),   # 014
    date(2026, 9, 20),   # 015
]


class HackIndiaConnector:
    """15 realistic HackIndia-style hackathon listings (dummy data)."""

    source_id = "hackindia"

    def fetch(self) -> list[RawHackathon]:
        return [
            RawHackathon(
                external_id="hi-dummy-001", source="hackindia",
                title="HackIndia: Delhi Web3 Sprint",
                organizer="HackIndia", mode="offline",
                location="New Delhi",
                team_size="2-4", prize_pool=500000,
                registration_deadline=_DL[0],
                start_date=date(2026, 9, 13), end_date=date(2026, 9, 15),
                themes=["Web3", "Blockchain", "DeFi", "NFT"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="hi-dummy-002", source="hackindia",
                title="HackIndia: Bengaluru AI Edition",
                organizer="HackIndia", mode="offline",
                location="Bengaluru",
                team_size="2-4", prize_pool=500000,
                registration_deadline=_DL[1],
                start_date=date(2026, 9, 14), end_date=date(2026, 9, 16),
                themes=["AI", "ML", "LLM", "Startups"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="hi-dummy-003", source="hackindia",
                title="HackIndia: Mumbai FinTech Hackathon",
                organizer="HackIndia", mode="offline",
                location="Mumbai",
                team_size="2-4", prize_pool=500000,
                registration_deadline=_DL[2],
                start_date=date(2026, 9, 15), end_date=date(2026, 9, 17),
                themes=["FinTech", "Blockchain", "Payments", "AI"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="hi-dummy-004", source="hackindia",
                title="HackIndia: Hyderabad Build Week",
                organizer="HackIndia", mode="hybrid",
                location="Hyderabad / Online",
                team_size="2-5", prize_pool=300000,
                registration_deadline=_DL[3],
                start_date=date(2026, 9, 16), end_date=date(2026, 9, 18),
                themes=["Full Stack", "Cloud", "DevOps", "AI"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="hi-dummy-005", source="hackindia",
                title="HackIndia: Pune Startup Sprint",
                organizer="HackIndia", mode="offline",
                location="Pune",
                team_size="2-4", prize_pool=400000,
                registration_deadline=_DL[4],
                start_date=date(2026, 9, 17), end_date=date(2026, 9, 19),
                themes=["Startups", "SaaS", "B2B", "AI"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="hi-dummy-006", source="hackindia",
                title="HackIndia: Chennai IoT Challenge",
                organizer="HackIndia", mode="offline",
                location="Chennai",
                team_size="2-4", prize_pool=300000,
                registration_deadline=_DL[5],
                start_date=date(2026, 9, 18), end_date=date(2026, 9, 20),
                themes=["IoT", "Hardware", "Embedded", "Smart Cities"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="hi-dummy-007", source="hackindia",
                title="HackIndia: Kolkata Open Innovation",
                organizer="HackIndia", mode="offline",
                location="Kolkata",
                team_size="2-4", prize_pool=250000,
                registration_deadline=_DL[6],
                start_date=date(2026, 9, 19), end_date=date(2026, 9, 21),
                themes=["Open Innovation", "Social Impact", "AI", "EdTech"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="hi-dummy-008", source="hackindia",
                title="HackIndia: Jaipur AgriTech Hack",
                organizer="HackIndia", mode="offline",
                location="Jaipur",
                team_size="2-4", prize_pool=300000,
                registration_deadline=_DL[7],
                start_date=date(2026, 9, 20), end_date=date(2026, 9, 22),
                themes=["AgriTech", "Rural India", "IoT", "Sustainability"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="hi-dummy-009", source="hackindia",
                title="HackIndia: Virtual Web3 Global",
                organizer="HackIndia", mode="online",
                location="Online",
                team_size="1-4", prize_pool=500000,
                registration_deadline=_DL[8],
                start_date=date(2026, 9, 17), end_date=date(2026, 10, 17),
                themes=["Web3", "Solana", "Ethereum", "DeFi"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="hi-dummy-010", source="hackindia",
                title="HackIndia: Chandigarh ClimaTech",
                organizer="HackIndia", mode="offline",
                location="Chandigarh",
                team_size="2-4", prize_pool=250000,
                registration_deadline=_DL[9],
                start_date=date(2026, 9, 22), end_date=date(2026, 9, 24),
                themes=["Climate", "GreenTech", "Sustainability", "AI"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="hi-dummy-011", source="hackindia",
                title="HackIndia: Ahmedabad HealthTech",
                organizer="HackIndia", mode="offline",
                location="Ahmedabad",
                team_size="2-4", prize_pool=350000,
                registration_deadline=_DL[10],
                start_date=date(2026, 9, 23), end_date=date(2026, 9, 25),
                themes=["HealthTech", "MedTech", "AI", "Diagnostics"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="hi-dummy-012", source="hackindia",
                title="HackIndia: Bhopal GovTech Hackathon",
                organizer="HackIndia + NASSCOM", mode="offline",
                location="Bhopal",
                team_size="2-5", prize_pool=300000,
                registration_deadline=_DL[11],
                start_date=date(2026, 9, 24), end_date=date(2026, 9, 26),
                themes=["GovTech", "e-Governance", "AI", "Social Impact"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="hi-dummy-013", source="hackindia",
                title="HackIndia: Kochi Web3 Edition",
                organizer="HackIndia", mode="offline",
                location="Kochi",
                team_size="2-4", prize_pool=400000,
                registration_deadline=_DL[12],
                start_date=date(2026, 9, 25), end_date=date(2026, 9, 27),
                themes=["Web3", "Blockchain", "DeFi", "Kerala Tech"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="hi-dummy-014", source="hackindia",
                title="HackIndia: Lucknow EdTech Sprint",
                organizer="HackIndia", mode="offline",
                location="Lucknow",
                team_size="2-4", prize_pool=200000,
                registration_deadline=_DL[13],
                start_date=date(2026, 9, 26), end_date=date(2026, 9, 28),
                themes=["EdTech", "AI", "Vernacular", "Social Impact"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="hi-dummy-015", source="hackindia",
                title="HackIndia: Coimbatore Manufacturing Hack",
                organizer="HackIndia", mode="offline",
                location="Coimbatore",
                team_size="2-4", prize_pool=300000,
                registration_deadline=_DL[14],
                start_date=date(2026, 9, 27), end_date=date(2026, 9, 29),
                themes=["Manufacturing", "Industry 4.0", "IoT", "AI"],
                apply_link="https://hackindia.com",
                posted_date=date(2026, 7, 31),
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
