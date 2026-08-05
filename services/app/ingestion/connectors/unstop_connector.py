# DUMMY DATA — placeholder until real Unstop API integration is added.
# Unstop's public API does not expose internship-specific listings reliably.
# To integrate live data: use their partner API or authenticated scraping,
# then remove this comment block.

from datetime import date, timedelta
from app.ingestion.base import RawOpportunity

_YR = {"min": 1, "max": 4}   # matches any year including year_of_study=1


class UnstopConnector:
    """Static dummy internship listings representing Unstop (15 listings).

    No network calls are made. Returns instantly.
    """

    source_id = "unstop"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="unstop-strategy-bain-panindia", source="unstop",
                title="Strategy & Consulting Intern",
                description="Work on live client engagements across FMCG, tech, and healthcare. Build frameworks and present insights to senior partners.",
                amount_min=20000, amount_max=35000, deadline=date.today() + timedelta(days=28),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "computer science"], "year_of_study": _YR, "skills": ["Excel", "Communication", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "consulting", "strategy"],
                raw_data={"company": "Bain & Company", "location": "Pan India", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="unstop-research-kpmg-delhi", source="unstop",
                title="Research Analyst Intern",
                description="Conduct market research, competitor benchmarking, and consumer behaviour analysis for KPMG advisory practice.",
                amount_min=10000, amount_max=18000, deadline=date.today() + timedelta(days=22),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "computer science"], "year_of_study": _YR, "skills": ["Excel", "Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "research", "analytics"],
                raw_data={"company": "KPMG India", "location": "Delhi / Hybrid", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="unstop-iot-bosch-hyd", source="unstop",
                title="Embedded Systems / IoT Intern",
                description="Design and validate firmware for IoT devices at Bosch India R&D. Work with MQTT protocols and Azure IoT dashboards.",
                amount_min=10000, amount_max=16000, deadline=date.today() + timedelta(days=32),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "JavaScript", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "iot", "embedded"],
                raw_data={"company": "Bosch India", "location": "Hyderabad", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="unstop-hr-analytics-swiggy-remote", source="unstop",
                title="HR Analytics Intern",
                description="Build people analytics dashboards in Power BI and model attrition risks. Support talent acquisition with data insights.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=20),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "computer science"], "year_of_study": _YR, "skills": ["Excel", "Python", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "hr", "analytics", "remote"],
                raw_data={"company": "Swiggy", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="unstop-supply-chain-flipkart-blr", source="unstop",
                title="Supply Chain & Logistics Intern",
                description="Analyse supply chain efficiency metrics and model inventory optimisation scenarios for Flipkart operations.",
                amount_min=15000, amount_max=22000, deadline=date.today() + timedelta(days=38),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "computer science"], "year_of_study": _YR, "skills": ["Excel", "Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "supply-chain", "operations"],
                raw_data={"company": "Flipkart", "location": "Bangalore", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="unstop-product-intern-meesho-blr", source="unstop",
                title="Product Management Intern",
                description="Define and prioritise features for Meesho seller onboarding. Write user stories and analyse funnel data.",
                amount_min=20000, amount_max=30000, deadline=date.today() + timedelta(days=25),
                eligibility_rules={"streams": ["Engineering", "computer science", "Management / MBA"], "year_of_study": _YR, "skills": ["Communication", "Excel", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "product-management", "ecommerce"],
                raw_data={"company": "Meesho", "location": "Bangalore", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="unstop-finance-deloitte-mumbai", source="unstop",
                title="Financial Advisory Intern",
                description="Support financial due diligence and valuation models for M&A transactions at Deloitte Financial Advisory practice.",
                amount_min=18000, amount_max=28000, deadline=date.today() + timedelta(days=15),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Excel", "Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "finance", "advisory"],
                raw_data={"company": "Deloitte Financial Advisory", "location": "Mumbai", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="unstop-brand-intern-pune", source="unstop",
                title="Brand Management Intern",
                description="Develop brand campaigns and competitive analysis for a leading Indian FMCG brand. MBA Marketing preferred.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=33),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Excel", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "brand-management", "marketing"],
                raw_data={"company": "Dabur India", "location": "Pune / Hybrid", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="unstop-data-science-intern-chennai", source="unstop",
                title="Data Science Intern",
                description="Build and evaluate classification models for a lending platform credit-risk scoring engine.",
                amount_min=16000, amount_max=24000, deadline=date.today() + timedelta(days=44),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "Machine Learning", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "data-science", "fintech"],
                raw_data={"company": "Credit Mantri", "location": "Chennai", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="unstop-social-impact-intern-remote", source="unstop",
                title="Social Impact & CSR Intern",
                description="Research CSR programme outcomes and draft impact reports for a large conglomerate's foundation.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=18),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Arts & Humanities"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "csr", "remote"],
                raw_data={"company": "Tata Trusts", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="unstop-ux-intern-myntra-blr", source="unstop",
                title="UX Design Intern",
                description="Design intuitive shopping experiences for Myntra mobile app. Run usability studies and create Figma prototypes.",
                amount_min=15000, amount_max=22000, deadline=date.today() + timedelta(days=37),
                eligibility_rules={"streams": ["Engineering", "Design", "computer science"], "year_of_study": _YR, "skills": ["Python", "Communication", "JavaScript"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "ux-design", "fashion-tech"],
                raw_data={"company": "Myntra", "location": "Bangalore", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="unstop-legal-intern-mumbai", source="unstop",
                title="Corporate Legal Intern",
                description="Assist in-house legal team with contract drafting, SEBI compliance, and regulatory filings.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=21),
                eligibility_rules={"streams": ["Engineering", "Law / LLB", "Management / MBA"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "legal", "compliance"],
                raw_data={"company": "HDFC Bank Legal", "location": "Mumbai", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="unstop-ml-vision-intern-remote", source="unstop",
                title="Computer Vision Intern",
                description="Train and optimise object detection models (YOLOv8) for a smart-manufacturing quality inspection platform.",
                amount_min=18000, amount_max=28000, deadline=date.today() + timedelta(days=48),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "Machine Learning"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "computer-vision", "ml", "remote"],
                raw_data={"company": "Detect Technologies", "location": "Remote", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="unstop-journalism-intern-delhi", source="unstop",
                title="Business Journalism Intern",
                description="Research and write business news articles and sector analysis for a leading Indian financial media publication.",
                amount_min=7000, amount_max=11000, deadline=date.today() + timedelta(days=14),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Arts & Humanities"], "year_of_study": _YR, "skills": ["Communication", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "journalism", "media"],
                raw_data={"company": "Mint (HT Media)", "location": "Delhi", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="unstop-renewable-energy-intern-remote", source="unstop",
                title="Renewable Energy Analyst Intern",
                description="Model solar and wind project financials, conduct site feasibility analysis, and prepare investor presentations.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=30),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "computer science"], "year_of_study": _YR, "skills": ["Excel", "Python", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://unstop.com",
                state_filter=["ALL"], tags=["unstop", "renewable-energy", "remote"],
                raw_data={"company": "Greenko Group", "location": "Remote", "duration": "3 months"},
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
