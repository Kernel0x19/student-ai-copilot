# DUMMY DATA — placeholder, live scraping not feasible.
# HackerEarth challenges page returns only ~300 bytes of shell HTML (filter UI labels).
# All challenge data loads via authenticated internal API calls that redirect
# to a login page when accessed externally.
# To enable live data: use HackerEarth's official Developer API (api.hackerearth.com)
# with an API key, then replace this file with an authenticated API client.

from datetime import date
from app.ingestion.connectors.hackathon_base import RawHackathon

# Registration deadlines: 15 distinct dates in August 2026 (Aug 22 – Sep 5)
# Each date is unique across all 4 dummy connector files.
_DL = [
    date(2026, 8, 22),   # 001
    date(2026, 8, 23),   # 002
    date(2026, 8, 24),   # 003
    date(2026, 8, 25),   # 004
    date(2026, 8, 26),   # 005
    date(2026, 8, 27),   # 006
    date(2026, 8, 28),   # 007
    date(2026, 8, 29),   # 008
    date(2026, 8, 30),   # 009
    date(2026, 8, 31),   # 010
    date(2026, 9,  1),   # 011
    date(2026, 9,  2),   # 012
    date(2026, 9,  3),   # 013
    date(2026, 9,  4),   # 014
    date(2026, 9,  5),   # 015
]


class HackerEarthHackathonConnector:
    """15 realistic HackerEarth hackathon listings (dummy data)."""

    source_id = "hackerearth"

    def fetch(self) -> list[RawHackathon]:
        return [
            RawHackathon(
                external_id="he-dummy-001", source="hackerearth",
                title="HackerEarth AI Challenge: Build with LLMs",
                organizer="HackerEarth", mode="online",
                location="Online", team_size="1-3", prize_pool=500000,
                registration_deadline=_DL[0],
                start_date=date(2026, 8, 24), end_date=date(2026, 9, 24),
                themes=["AI", "LLM", "NLP", "GenAI"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="he-dummy-002", source="hackerearth",
                title="Infosys InfyTQ Hackathon 2026",
                organizer="Infosys", mode="online",
                location="Online", team_size="1-4", prize_pool=300000,
                registration_deadline=_DL[1],
                start_date=date(2026, 8, 25), end_date=date(2026, 9, 25),
                themes=["Full Stack", "Cloud", "AI", "Microservices"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="he-dummy-003", source="hackerearth",
                title="Wipro HackZen: Campus Edition",
                organizer="Wipro", mode="online",
                location="Online", team_size="2-4", prize_pool=200000,
                registration_deadline=_DL[2],
                start_date=date(2026, 8, 26), end_date=date(2026, 9, 26),
                themes=["AI", "Cybersecurity", "IoT", "Cloud"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="he-dummy-004", source="hackerearth",
                title="Zomato HungerHack: FoodTech Innovation",
                organizer="Zomato", mode="online",
                location="Online", team_size="1-4", prize_pool=400000,
                registration_deadline=_DL[3],
                start_date=date(2026, 8, 27), end_date=date(2026, 9, 27),
                themes=["FoodTech", "AI", "Logistics", "ML"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="he-dummy-005", source="hackerearth",
                title="HackerEarth HealthTech Challenge",
                organizer="HackerEarth", mode="online",
                location="Online", team_size="1-3", prize_pool=350000,
                registration_deadline=_DL[4],
                start_date=date(2026, 8, 28), end_date=date(2026, 9, 28),
                themes=["HealthTech", "AI", "Data Science", "ML"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 7, 30),
            ),
            RawHackathon(
                external_id="he-dummy-006", source="hackerearth",
                title="Accenture Innovation Challenge",
                organizer="Accenture", mode="hybrid",
                location="Bangalore / Online",
                team_size="2-5", prize_pool=500000,
                registration_deadline=_DL[5],
                start_date=date(2026, 9, 10), end_date=date(2026, 9, 12),
                themes=["AI", "Sustainability", "Cloud", "Digital Transformation"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="he-dummy-007", source="hackerearth",
                title="HDFC Bank FinHack 2026",
                organizer="HDFC Bank", mode="online",
                location="Online", team_size="1-4", prize_pool=600000,
                registration_deadline=_DL[6],
                start_date=date(2026, 8, 30), end_date=date(2026, 9, 30),
                themes=["FinTech", "Banking", "AI", "Blockchain"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="he-dummy-008", source="hackerearth",
                title="TCS CodeVita Season 14",
                organizer="Tata Consultancy Services", mode="online",
                location="Online", team_size="1-2", prize_pool=200000,
                registration_deadline=_DL[7],
                start_date=date(2026, 9, 3), end_date=date(2026, 9, 5),
                themes=["Competitive Coding", "Algorithms", "Problem Solving"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 7, 29),
            ),
            RawHackathon(
                external_id="he-dummy-009", source="hackerearth",
                title="Juspay DevSprint: Payments Innovation",
                organizer="Juspay", mode="online",
                location="Online", team_size="1-4", prize_pool=300000,
                registration_deadline=_DL[8],
                start_date=date(2026, 9, 1), end_date=date(2026, 10, 1),
                themes=["Payments", "FinTech", "API", "UPI"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="he-dummy-010", source="hackerearth",
                title="ClimaTech Hackathon: Sustainable Solutions",
                organizer="HackerEarth + NASSCOM", mode="online",
                location="Online", team_size="2-4", prize_pool=450000,
                registration_deadline=_DL[9],
                start_date=date(2026, 9, 2), end_date=date(2026, 10, 2),
                themes=["Climate", "Sustainability", "AI", "IoT"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="he-dummy-011", source="hackerearth",
                title="Samsung Solve for Tomorrow",
                organizer="Samsung India", mode="hybrid",
                location="Seoul / India Hubs",
                team_size="2-4", prize_pool=500000,
                registration_deadline=_DL[10],
                start_date=date(2026, 9, 15), end_date=date(2026, 9, 17),
                themes=["Hardware", "AI", "IoT", "Smart Cities"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 7, 28),
            ),
            RawHackathon(
                external_id="he-dummy-012", source="hackerearth",
                title="ShareChat Creator Tech Hack",
                organizer="ShareChat / Moj", mode="online",
                location="Online", team_size="1-3", prize_pool=250000,
                registration_deadline=_DL[11],
                start_date=date(2026, 9, 4), end_date=date(2026, 10, 4),
                themes=["Social Media", "AI", "Video Tech", "Vernacular NLP"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="he-dummy-013", source="hackerearth",
                title="L&T Technology DevSprint",
                organizer="L&T Technology Services", mode="online",
                location="Online", team_size="2-4", prize_pool=300000,
                registration_deadline=_DL[12],
                start_date=date(2026, 9, 5), end_date=date(2026, 10, 5),
                themes=["Engineering", "IoT", "Digital Twin", "AI"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="he-dummy-014", source="hackerearth",
                title="Razorpay HackRPay",
                organizer="Razorpay", mode="online",
                location="Online", team_size="1-4", prize_pool=400000,
                registration_deadline=_DL[13],
                start_date=date(2026, 9, 6), end_date=date(2026, 10, 6),
                themes=["Payments", "FinTech", "API", "AI"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="he-dummy-015", source="hackerearth",
                title="HackerEarth Data Science League",
                organizer="HackerEarth", mode="online",
                location="Online", team_size="1-2", prize_pool=200000,
                registration_deadline=_DL[14],
                start_date=date(2026, 9, 7), end_date=date(2026, 10, 7),
                themes=["Data Science", "ML", "Statistics", "Kaggle-style"],
                apply_link="https://www.hackerearth.com/challenges/hackathon/",
                posted_date=date(2026, 8, 1),
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
