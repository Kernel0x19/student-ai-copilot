# DUMMY DATA — placeholder until real Wellfound API integration is added.
# Wellfound's GraphQL endpoint returns 403 from server environments.
# To integrate live data: use their official Talent API (requires partner access),
# then remove this comment block.

from datetime import date, timedelta
from app.ingestion.base import RawOpportunity

_YR = {"min": 1, "max": 4}   # matches any year including year_of_study=1


class WellfoundConnector:
    """Static dummy internship listings representing Wellfound (15 listings).

    No network calls are made. Returns instantly.
    """

    source_id = "wellfound"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="wellfound-fullstack-zluri-remote", source="wellfound",
                title="Full-Stack Engineer Intern",
                description="Join a Series-A B2B SaaS startup to build features in Next.js + FastAPI. Ship real production code in week 1. Fully remote.",
                amount_min=20000, amount_max=35000, deadline=date.today() + timedelta(days=45),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["React", "Python", "Node.js"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "saas", "remote"],
                raw_data={"company": "Zluri", "location": "Remote", "duration": "3-6 months"},
            ),
            RawOpportunity(
                external_id="wellfound-product-slintel-blr", source="wellfound",
                title="Product Management Intern",
                description="Work with the founding team to define roadmap, write PRDs, and run user research. Technical background preferred.",
                amount_min=15000, amount_max=25000, deadline=date.today() + timedelta(days=40),
                eligibility_rules={"streams": ["Engineering", "computer science", "Management / MBA"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "product-management"],
                raw_data={"company": "Slintel (6sense)", "location": "Bangalore (Hybrid)", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="wellfound-design-jupiter-remote", source="wellfound",
                title="Product Designer Intern",
                description="Design end-to-end product flows for a Series-C fintech consumer app (2M+ users). Figma proficiency required.",
                amount_min=12000, amount_max=20000, deadline=date.today() + timedelta(days=35),
                eligibility_rules={"streams": ["Engineering", "Design", "computer science"], "year_of_study": _YR, "skills": ["Communication", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "design", "remote"],
                raw_data={"company": "Jupiter Money", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-llm-sarvam-remote", source="wellfound",
                title="Machine Learning Intern (LLMs)",
                description="Fine-tune open-source LLMs for Indic language tasks and build production-grade RAG pipelines.",
                amount_min=25000, amount_max=40000, deadline=date.today() + timedelta(days=50),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "Machine Learning", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "llm", "ai", "remote"],
                raw_data={"company": "Sarvam AI", "location": "Remote", "duration": "6 months"},
            ),
            RawOpportunity(
                external_id="wellfound-growth-khatabook-blr", source="wellfound",
                title="Growth & Marketing Intern",
                description="Own user acquisition experiments across channels for a Series-D SME fintech. Run A/B tests and analyse cohort data.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=22),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "computer science"], "year_of_study": _YR, "skills": ["Excel", "Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "growth"],
                raw_data={"company": "Khatabook", "location": "Bangalore", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-backend-go-remote", source="wellfound",
                title="Backend Engineer Intern",
                description="Build high-throughput microservices for a Series-B payments infrastructure startup. Work on low-latency transaction pipelines.",
                amount_min=22000, amount_max=32000, deadline=date.today() + timedelta(days=42),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "Node.js", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "backend", "remote"],
                raw_data={"company": "Cashfree Payments", "location": "Remote", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="wellfound-data-eng-blr", source="wellfound",
                title="Data Engineering Intern",
                description="Build and optimise ETL pipelines using Apache Spark and dbt on a Snowflake data warehouse.",
                amount_min=18000, amount_max=28000, deadline=date.today() + timedelta(days=36),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "data-engineering"],
                raw_data={"company": "Hasura", "location": "Bangalore (Hybrid)", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="wellfound-bizdev-remote", source="wellfound",
                title="Business Development Intern",
                description="Research enterprise sales leads, prepare outreach sequences for a Series-A B2B SaaS startup.",
                amount_min=10000, amount_max=15000, deadline=date.today() + timedelta(days=19),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "sales", "remote"],
                raw_data={"company": "Suprsend", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-devrel-intern-remote", source="wellfound",
                title="Developer Relations Intern",
                description="Create technical tutorials and demo apps to grow the developer community around an open-source API platform.",
                amount_min=15000, amount_max=22000, deadline=date.today() + timedelta(days=55),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["JavaScript", "Python", "Node.js"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "devrel", "remote"],
                raw_data={"company": "Ory (India Remote)", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-ios-swift-mumbai", source="wellfound",
                title="iOS Engineer Intern",
                description="Build native iOS features for a Series-B consumer fintech app using Swift and SwiftUI.",
                amount_min=18000, amount_max=28000, deadline=date.today() + timedelta(days=30),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "JavaScript", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "ios", "fintech"],
                raw_data={"company": "OneCard", "location": "Mumbai (Hybrid)", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="wellfound-security-intern-remote", source="wellfound",
                title="Application Security Intern",
                description="Conduct code reviews and penetration tests on a cloud-native SaaS product. OWASP Top 10 knowledge preferred.",
                amount_min=16000, amount_max=24000, deadline=date.today() + timedelta(days=38),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "security", "remote"],
                raw_data={"company": "Razorpay Security", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-content-strategy-remote", source="wellfound",
                title="Content Strategy Intern",
                description="Build and execute a content calendar and write SEO-driven long-form articles for a seed-stage B2B startup.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=17),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Arts & Humanities"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "content", "remote"],
                raw_data={"company": "Springworks", "location": "Remote", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="wellfound-analytics-mixpanel-blr", source="wellfound",
                title="Product Analytics Intern",
                description="Instrument product event tracking, build funnel dashboards, and provide weekly user-behaviour reports to the PM team.",
                amount_min=14000, amount_max=20000, deadline=date.today() + timedelta(days=27),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "SQL", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "analytics"],
                raw_data={"company": "Learnyst", "location": "Bangalore", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-operations-intern-delhi", source="wellfound",
                title="Operations Intern (Startup)",
                description="Assist the COO with process documentation and vendor management for a quick-commerce startup.",
                amount_min=10000, amount_max=15000, deadline=date.today() + timedelta(days=20),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Excel", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "operations"],
                raw_data={"company": "Blinkit Alumni Venture", "location": "Delhi / Hybrid", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="wellfound-flutter-intern-remote", source="wellfound",
                title="Flutter / Mobile Developer Intern",
                description="Build cross-platform mobile features in Flutter/Dart for a seed-stage edtech app targeting rural students.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=44),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["JavaScript", "Python", "Node.js"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://wellfound.com",
                state_filter=["ALL"], tags=["wellfound", "startup", "mobile", "remote"],
                raw_data={"company": "Rocket Learning", "location": "Remote", "duration": "3 months"},
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
