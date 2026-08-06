# DUMMY DATA — placeholder, live scraping not feasible.
# Hack2Skill (hack2skill.com) loads entirely client-side.
# Both hack2skill.com/hackathons and hack2skill.com/allevents return no
# extractable content — the content extractor returns only 53 bytes of
# boilerplate.  No public API endpoints were found.
# To enable live data: use Playwright with deep wait-for-selector targeting
# specific event card class names, or obtain Hack2Skill's official API.

from datetime import date
from app.ingestion.connectors.hackathon_base import RawHackathon

# Registration deadlines: 15 distinct dates (Sep 21 – Oct 5, 2026)
# Each date is unique across all 4 dummy connector files.
_DL = [
    date(2026, 9, 21),   # 001
    date(2026, 9, 22),   # 002
    date(2026, 9, 23),   # 003
    date(2026, 9, 24),   # 004
    date(2026, 9, 25),   # 005
    date(2026, 9, 26),   # 006
    date(2026, 9, 27),   # 007
    date(2026, 9, 28),   # 008
    date(2026, 9, 29),   # 009
    date(2026, 9, 30),   # 010
    date(2026, 10,  1),  # 011
    date(2026, 10,  2),  # 012
    date(2026, 10,  3),  # 013
    date(2026, 10,  4),  # 014
    date(2026, 10,  5),  # 015
]


class Hack2SkillConnector:
    """15 realistic Hack2Skill hackathon listings (dummy data)."""

    source_id = "hack2skill"

    def fetch(self) -> list[RawHackathon]:
        return [
            RawHackathon(
                external_id="h2s-dummy-001", source="hack2skill",
                title="Smart India Hackathon 2026",
                organizer="Ministry of Education / AICTE", mode="offline",
                location="Multiple IIT / NIT Campuses",
                team_size="6", prize_pool=1000000,
                registration_deadline=_DL[0],
                start_date=date(2026, 10, 6), end_date=date(2026, 10, 8),
                themes=["GovTech", "AI", "Healthcare", "Agriculture", "Smart Cities"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="h2s-dummy-002", source="hack2skill",
                title="IIT Bombay Techfest Hackathon",
                organizer="IIT Bombay Techfest", mode="offline",
                location="IIT Bombay, Mumbai",
                team_size="2-4", prize_pool=500000,
                registration_deadline=_DL[1],
                start_date=date(2026, 10, 7), end_date=date(2026, 10, 9),
                themes=["AI", "Robotics", "Space Tech", "Clean Energy"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="h2s-dummy-003", source="hack2skill",
                title="Agentic AI World Record Hackathon 2026",
                organizer="Hack2Skill", mode="offline",
                location="Bengaluru",
                team_size="1-4", prize_pool=2000000,
                registration_deadline=_DL[2],
                start_date=date(2026, 10, 4), end_date=date(2026, 10, 5),
                themes=["AI Agents", "LLM", "Agentic AI", "Automation"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="h2s-dummy-004", source="hack2skill",
                title="DRDO Defence Tech Hackathon",
                organizer="DRDO / Hack2Skill", mode="offline",
                location="New Delhi",
                team_size="4-6", prize_pool=1500000,
                registration_deadline=_DL[3],
                start_date=date(2026, 10, 9), end_date=date(2026, 10, 11),
                themes=["Defence Tech", "AI", "Cybersecurity", "Drones"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="h2s-dummy-005", source="hack2skill",
                title="Indian Railways Innovation Challenge",
                organizer="Ministry of Railways / Hack2Skill", mode="hybrid",
                location="New Delhi / Online",
                team_size="3-5", prize_pool=1000000,
                registration_deadline=_DL[4],
                start_date=date(2026, 10, 10), end_date=date(2026, 10, 12),
                themes=["Railways", "Smart Transport", "IoT", "Safety AI"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="h2s-dummy-006", source="hack2skill",
                title="ISRO Space Tech Hackathon",
                organizer="ISRO / Hack2Skill", mode="offline",
                location="Bengaluru",
                team_size="2-5", prize_pool=750000,
                registration_deadline=_DL[5],
                start_date=date(2026, 10, 11), end_date=date(2026, 10, 13),
                themes=["Space Tech", "Satellite", "Remote Sensing", "AI"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="h2s-dummy-007", source="hack2skill",
                title="National Water Hackathon",
                organizer="Ministry of Jal Shakti / Hack2Skill", mode="hybrid",
                location="Multiple State Capitals / Online",
                team_size="3-5", prize_pool=500000,
                registration_deadline=_DL[6],
                start_date=date(2026, 10, 12), end_date=date(2026, 10, 14),
                themes=["Water Tech", "Sustainability", "IoT", "AI"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="h2s-dummy-008", source="hack2skill",
                title="IIT Delhi Rendezvous Hack",
                organizer="IIT Delhi", mode="offline",
                location="IIT Delhi, New Delhi",
                team_size="2-4", prize_pool=400000,
                registration_deadline=_DL[7],
                start_date=date(2026, 10, 13), end_date=date(2026, 10, 15),
                themes=["AI", "Fintech", "Climate", "Open Innovation"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="h2s-dummy-009", source="hack2skill",
                title="NASSCOM FutureSkills AI Hack",
                organizer="NASSCOM / Hack2Skill", mode="online",
                location="Online",
                team_size="1-4", prize_pool=300000,
                registration_deadline=_DL[8],
                start_date=date(2026, 10, 1), end_date=date(2026, 10, 31),
                themes=["AI", "Upskilling", "Future of Work", "EdTech"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="h2s-dummy-010", source="hack2skill",
                title="Startup India Innovation Challenge",
                organizer="DPIIT / Startup India / Hack2Skill", mode="hybrid",
                location="New Delhi / Online",
                team_size="2-5", prize_pool=1000000,
                registration_deadline=_DL[9],
                start_date=date(2026, 10, 15), end_date=date(2026, 10, 17),
                themes=["Startups", "Deep Tech", "Social Impact", "Scale-up"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 1),
            ),
            RawHackathon(
                external_id="h2s-dummy-011", source="hack2skill",
                title="Healthcare Innovation Hackathon by AIIMS",
                organizer="AIIMS / Hack2Skill", mode="offline",
                location="New Delhi",
                team_size="2-5", prize_pool=500000,
                registration_deadline=_DL[10],
                start_date=date(2026, 10, 16), end_date=date(2026, 10, 18),
                themes=["HealthTech", "MedTech", "AI Diagnostics", "Telemedicine"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 5),
            ),
            RawHackathon(
                external_id="h2s-dummy-012", source="hack2skill",
                title="India Energy Hackathon",
                organizer="Ministry of Power / Hack2Skill", mode="hybrid",
                location="New Delhi / Online",
                team_size="3-5", prize_pool=750000,
                registration_deadline=_DL[11],
                start_date=date(2026, 10, 17), end_date=date(2026, 10, 19),
                themes=["Renewable Energy", "Grid Tech", "EV", "Solar"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 3),
            ),
            RawHackathon(
                external_id="h2s-dummy-013", source="hack2skill",
                title="NIT Trichy Pragyan Hackathon",
                organizer="NIT Trichy", mode="offline",
                location="NIT Trichy, Tamil Nadu",
                team_size="2-4", prize_pool=300000,
                registration_deadline=_DL[12],
                start_date=date(2026, 10, 18), end_date=date(2026, 10, 20),
                themes=["AI", "IoT", "Robotics", "Open Innovation"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 2),
            ),
            RawHackathon(
                external_id="h2s-dummy-014", source="hack2skill",
                title="Cyber Suraksha Hackathon",
                organizer="CERT-In / MeitY / Hack2Skill", mode="offline",
                location="New Delhi",
                team_size="2-4", prize_pool=600000,
                registration_deadline=_DL[13],
                start_date=date(2026, 10, 19), end_date=date(2026, 10, 21),
                themes=["Cybersecurity", "AI", "Threat Intelligence", "GovTech"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 4),
            ),
            RawHackathon(
                external_id="h2s-dummy-015", source="hack2skill",
                title="UrbanTech City Challenge",
                organizer="Smart Cities Mission / Hack2Skill", mode="hybrid",
                location="Multiple Smart Cities / Online",
                team_size="3-5", prize_pool=750000,
                registration_deadline=_DL[14],
                start_date=date(2026, 10, 20), end_date=date(2026, 10, 22),
                themes=["Smart Cities", "Urban Planning", "Mobility", "IoT"],
                apply_link="https://hack2skill.com",
                posted_date=date(2026, 8, 1),
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
