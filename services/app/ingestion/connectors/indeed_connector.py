# DUMMY DATA — placeholder until real Indeed India API integration is added.
# Indeed's public job API was shut down in 2022. To integrate live data:
# implement an approved partner API or replace with an alternative jobs API,
# then remove this comment block.

from datetime import date, timedelta
from app.ingestion.base import RawOpportunity

_YR = {"min": 1, "max": 4}   # matches any year including year_of_study=1


class IndeedConnector:
    """Static dummy internship listings representing Indeed India (15 listings).

    No network calls are made. Returns instantly.
    """

    source_id = "indeed"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="indeed-frontend-blr-remote", source="indeed",
                title="Frontend Developer Intern",
                description="Build responsive web interfaces using React and TypeScript for a high-growth B2B SaaS platform. Remote-first culture with strong engineering mentorship.",
                amount_min=10000, amount_max=18000, deadline=date.today() + timedelta(days=25),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["React", "JavaScript", "TypeScript"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "frontend", "react", "remote"],
                raw_data={"company": "Clarisights", "location": "Bangalore (Remote)", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="indeed-finance-mumbai", source="indeed",
                title="Finance & Accounts Intern",
                description="Assist the finance team with MIS reporting, account reconciliation, and GST filing. B.Com / MBA Finance preferred. Tally and Excel mandatory.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=20),
                eligibility_rules={"streams": ["Engineering", "Commerce", "Management / MBA"], "year_of_study": _YR, "skills": ["Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "finance", "accounts"],
                raw_data={"company": "Mahindra Finance", "location": "Mumbai", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="indeed-content-seo-delhi", source="indeed",
                title="Content & SEO Intern",
                description="Write SEO-optimised blog posts, product descriptions, and social copy for a D2C brand. Strong written English mandatory. Fully remote.",
                amount_min=6000, amount_max=9000, deadline=date.today() + timedelta(days=15),
                eligibility_rules={"streams": ["Engineering", "Arts & Humanities", "Management / MBA"], "year_of_study": _YR, "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "content", "seo", "remote"],
                raw_data={"company": "Mamaearth", "location": "Delhi / Remote", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="indeed-data-science-hyd", source="indeed",
                title="Data Science Intern",
                description="Work on real customer datasets to build churn prediction models. Strong Python and SQL skills needed.",
                amount_min=15000, amount_max=25000, deadline=date.today() + timedelta(days=28),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "SQL", "Machine Learning"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "data-science", "python"],
                raw_data={"company": "Deloitte USI", "location": "Hyderabad", "duration": "6 months"},
            ),
            RawOpportunity(
                external_id="indeed-ios-intern-chennai", source="indeed",
                title="iOS Development Intern",
                description="Develop and ship features for a consumer iOS app (1M+ users) using Swift and SwiftUI.",
                amount_min=14000, amount_max=22000, deadline=date.today() + timedelta(days=32),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["JavaScript", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "ios", "mobile"],
                raw_data={"company": "Zomato", "location": "Chennai / Hybrid", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="indeed-cybersecurity-intern-pune", source="indeed",
                title="Cybersecurity Analyst Intern",
                description="Assist the security operations team with vulnerability scanning, log analysis, and incident response.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=22),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "cybersecurity", "security"],
                raw_data={"company": "Accenture Security", "location": "Pune", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="indeed-operations-intern-ahmedabad", source="indeed",
                title="Operations & Logistics Intern",
                description="Support route optimisation, vendor coordination, and daily dispatch tracking.",
                amount_min=7000, amount_max=10000, deadline=date.today() + timedelta(days=18),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Excel", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "operations", "logistics"],
                raw_data={"company": "Delhivery", "location": "Ahmedabad", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="indeed-graphic-design-intern-remote", source="indeed",
                title="Graphic Design Intern",
                description="Create visual assets for social media campaigns, email newsletters, and product pages. Portfolio mandatory.",
                amount_min=6000, amount_max=10000, deadline=date.today() + timedelta(days=40),
                eligibility_rules={"streams": ["Engineering", "Design", "Arts & Humanities"], "year_of_study": _YR, "states": ["ALL"]},
                documents_required=["resume", "portfolio_link"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "design", "remote"],
                raw_data={"company": "UrbanCompany", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="indeed-backend-nodejs-intern-blr", source="indeed",
                title="Backend Developer Intern (Node.js)",
                description="Build and maintain RESTful APIs using Node.js and Express. Work with PostgreSQL and Redis.",
                amount_min=12000, amount_max=20000, deadline=date.today() + timedelta(days=35),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Node.js", "JavaScript", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "backend", "nodejs"],
                raw_data={"company": "MindTree", "location": "Bangalore", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="indeed-market-research-intern-remote", source="indeed",
                title="Market Research Intern",
                description="Conduct research on consumer trends and competitive landscapes for the FMCG sector.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=23),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Economics"], "year_of_study": _YR, "skills": ["Excel", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "market-research", "remote"],
                raw_data={"company": "Hindustan Unilever", "location": "Remote", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="indeed-qa-intern-bengaluru", source="indeed",
                title="QA / Test Automation Intern",
                description="Write and execute test cases for web and mobile applications. Identify bugs and work with dev team.",
                amount_min=10000, amount_max=15000, deadline=date.today() + timedelta(days=30),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "JavaScript"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "qa", "testing"],
                raw_data={"company": "Wipro Digital", "location": "Bengaluru", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="indeed-social-media-intern-kolkata", source="indeed",
                title="Social Media Marketing Intern",
                description="Manage Instagram and LinkedIn content calendars and analyse post performance metrics.",
                amount_min=5000, amount_max=8000, deadline=date.today() + timedelta(days=12),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Arts & Humanities"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "social-media", "marketing"],
                raw_data={"company": "Licious", "location": "Kolkata / Remote", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="indeed-cloud-aws-intern-noida", source="indeed",
                title="AWS Cloud Infrastructure Intern",
                description="Assist in provisioning AWS resources (EC2, S3, Lambda) and support DevOps deployment pipelines.",
                amount_min=15000, amount_max=22000, deadline=date.today() + timedelta(days=38),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "aws", "cloud"],
                raw_data={"company": "HCL Technologies", "location": "Noida", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="indeed-legal-intern-delhi", source="indeed",
                title="Legal & Compliance Intern",
                description="Support the legal team with contract review, compliance documentation, and regulatory research.",
                amount_min=10000, amount_max=15000, deadline=date.today() + timedelta(days=17),
                eligibility_rules={"streams": ["Engineering", "Law / LLB", "Management / MBA"], "year_of_study": _YR, "skills": ["Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "legal", "compliance"],
                raw_data={"company": "Nykaa", "location": "Delhi", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="indeed-product-design-intern-remote", source="indeed",
                title="Product Design Intern",
                description="Design intuitive user flows for a B2C edtech app. Conduct usability tests and iterate on prototypes.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=45),
                eligibility_rules={"streams": ["Engineering", "Design", "computer science"], "year_of_study": _YR, "skills": ["Python", "React"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.indeed.com",
                state_filter=["ALL"], tags=["indeed", "product-design", "remote"],
                raw_data={"company": "BYJU'S", "location": "Remote", "duration": "3 months"},
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
