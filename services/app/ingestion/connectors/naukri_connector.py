# DUMMY DATA — placeholder until real Naukri Campus API integration is added.
# To integrate live data: replace the fetch() method with httpx scraping of
# campus.naukri.com and remove this comment block.

from datetime import date, timedelta
from app.ingestion.base import RawOpportunity

_YR = {"min": 1, "max": 4}   # matches any year including year_of_study=1


class NaukriConnector:
    """Static dummy internship listings representing Naukri Campus (15 listings).

    No network calls are made. Returns instantly.
    """

    source_id = "naukri"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="naukri-java-backend-pune", source="naukri",
                title="Java Backend Intern",
                description="Develop and maintain microservices using Spring Boot and Java at Infosys BPM. B.Tech CS/IT students with solid Java fundamentals preferred.",
                amount_min=12000, amount_max=20000, deadline=date.today() + timedelta(days=30),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "JavaScript", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "java", "backend"],
                raw_data={"company": "Infosys BPM", "location": "Pune", "duration": "6 months"},
            ),
            RawOpportunity(
                external_id="naukri-digital-marketing-blr", source="naukri",
                title="Digital Marketing Intern",
                description="Run paid campaigns on Google & Meta, manage social handles, and track ROI analytics.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=21),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "marketing"], "year_of_study": _YR, "skills": ["Excel", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "digital-marketing"],
                raw_data={"company": "Razorpay", "location": "Bangalore", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="naukri-cloud-devops-remote", source="naukri",
                title="Cloud & DevOps Intern",
                description="Assist the SRE team with CI/CD pipelines, Kubernetes cluster management, and monitoring dashboards on AWS.",
                amount_min=18000, amount_max=28000, deadline=date.today() + timedelta(days=35),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "JavaScript"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "cloud", "devops", "remote"],
                raw_data={"company": "Wipro Limited", "location": "Remote", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="naukri-bda-noida", source="naukri",
                title="Business Development Associate Intern",
                description="Identify and qualify B2B leads, support the sales team with cold outreach.",
                amount_min=7000, amount_max=11000, deadline=date.today() + timedelta(days=18),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "sales", "business-development"],
                raw_data={"company": "Paytm", "location": "Noida", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="naukri-data-analyst-mumbai", source="naukri",
                title="Data Analyst Intern",
                description="Build MIS dashboards in Power BI, clean large datasets, and assist with A/B test reporting.",
                amount_min=10000, amount_max=15000, deadline=date.today() + timedelta(days=27),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Excel", "SQL", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "data", "analytics"],
                raw_data={"company": "Reliance Jio", "location": "Mumbai", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="naukri-python-intern-chennai", source="naukri",
                title="Python Developer Intern",
                description="Build automation scripts and internal tooling using Python, Django, and PostgreSQL.",
                amount_min=10000, amount_max=16000, deadline=date.today() + timedelta(days=24),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "SQL", "JavaScript"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "python", "django"],
                raw_data={"company": "Cognizant Technology Solutions", "location": "Chennai", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="naukri-ui-angular-intern-hyd", source="naukri",
                title="Frontend Engineer Intern",
                description="Develop feature modules for an enterprise HR software product using React and TypeScript.",
                amount_min=11000, amount_max=17000, deadline=date.today() + timedelta(days=33),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["React", "JavaScript", "TypeScript"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "react", "frontend"],
                raw_data={"company": "Mphasis", "location": "Hyderabad", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="naukri-content-intern-remote", source="naukri",
                title="Technical Content Writer Intern",
                description="Write developer-focused blog posts and API documentation for a cloud infrastructure product.",
                amount_min=7000, amount_max=10000, deadline=date.today() + timedelta(days=16),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Communication", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "content", "remote"],
                raw_data={"company": "Freshworks", "location": "Remote", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="naukri-hr-intern-gurgaon", source="naukri",
                title="Human Resources Intern",
                description="Support campus recruitment coordination, offer letter processing, and employee onboarding.",
                amount_min=8000, amount_max=12000, deadline=date.today() + timedelta(days=20),
                eligibility_rules={"streams": ["Engineering", "Management / MBA", "Commerce"], "year_of_study": _YR, "skills": ["Communication", "Excel"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "hr", "recruitment"],
                raw_data={"company": "Genpact", "location": "Gurgaon", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="naukri-embedded-intern-pune", source="naukri",
                title="Embedded Systems Intern",
                description="Write and test firmware for automotive ECUs using Embedded C and Python on STM32 microcontrollers.",
                amount_min=12000, amount_max=18000, deadline=date.today() + timedelta(days=40),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["Python", "JavaScript", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "embedded", "firmware"],
                raw_data={"company": "Bosch Engineering", "location": "Pune", "duration": "6 months"},
            ),
            RawOpportunity(
                external_id="naukri-accounts-intern-jaipur", source="naukri",
                title="Accounts & Taxation Intern",
                description="Assist the accounts team with TDS computation, GST return filing, and bank reconciliation.",
                amount_min=6000, amount_max=9000, deadline=date.today() + timedelta(days=14),
                eligibility_rules={"streams": ["Engineering", "Commerce", "Management / MBA"], "year_of_study": _YR, "skills": ["Excel", "Communication"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "accounts", "finance"],
                raw_data={"company": "Jaipur Rugs", "location": "Jaipur", "duration": "2 months"},
            ),
            RawOpportunity(
                external_id="naukri-ml-ops-intern-remote", source="naukri",
                title="MLOps / AI Intern",
                description="Deploy and monitor ML models using MLflow. Set up CI/CD pipelines for model deployment using Python.",
                amount_min=16000, amount_max=24000, deadline=date.today() + timedelta(days=45),
                eligibility_rules={"streams": ["Engineering", "computer science", "Data Science"], "year_of_study": _YR, "skills": ["Python", "Machine Learning", "SQL"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "mlops", "ml", "remote"],
                raw_data={"company": "Hexaware Technologies", "location": "Remote", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="naukri-supply-chain-intern-mumbai", source="naukri",
                title="Supply Chain Planning Intern",
                description="Support inventory planning, demand forecasting, and supplier coordination for an FMCG brand.",
                amount_min=10000, amount_max=14000, deadline=date.today() + timedelta(days=22),
                eligibility_rules={"streams": ["Engineering", "Management / MBA"], "year_of_study": _YR, "skills": ["Excel", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "supply-chain", "operations"],
                raw_data={"company": "Godrej Consumer Products", "location": "Mumbai", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="naukri-react-native-intern-blr", source="naukri",
                title="React / Mobile Developer Intern",
                description="Build cross-platform mobile features using React Native. Work with REST APIs and Firebase.",
                amount_min=13000, amount_max=19000, deadline=date.today() + timedelta(days=38),
                eligibility_rules={"streams": ["Engineering", "computer science"], "year_of_study": _YR, "skills": ["React", "JavaScript", "Node.js"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "react", "mobile"],
                raw_data={"company": "PharmEasy", "location": "Bangalore", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="naukri-ux-research-intern-remote", source="naukri",
                title="UX / Product Research Intern",
                description="Plan and conduct user interviews and usability tests for a B2B SaaS product. Synthesise findings into insights.",
                amount_min=9000, amount_max=13000, deadline=date.today() + timedelta(days=29),
                eligibility_rules={"streams": ["Engineering", "computer science", "Design"], "year_of_study": _YR, "skills": ["Communication", "Python"], "states": ["ALL"]},
                documents_required=["resume"], application_url="https://www.naukri.com",
                state_filter=["ALL"], tags=["naukri", "ux-research", "remote"],
                raw_data={"company": "Zoho Corporation", "location": "Remote", "duration": "3 months"},
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "dummy_data"}
