from datetime import date, timedelta

from app.ingestion.base import BaseConnector, RawOpportunity


class NSPConnector(BaseConnector):
    """National Scholarship Portal — seed/sample data for MVP; production uses Playwright scraper."""

    source_id = "nsp"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="nsp-pm-yasasvi",
                source="nsp",
                title="PM Yasasvi Scholarship for OBC, EBC and DNT Students",
                description="Central sector scheme for OBC, EBC and DNT category students in Class 9-12.",
                amount_min=75000,
                amount_max=125000,
                deadline=date.today() + timedelta(days=45),
                eligibility_rules={
                    "category": ["OBC", "EBC", "DNT"],
                    "max_income": 250000,
                    "min_percentage_12th": 60,
                    "states": ["ALL"],
                },
                documents_required=["income_certificate", "caste_certificate", "aadhaar", "bank_passbook"],
                application_url="https://scholarships.gov.in/",
                state_filter=["ALL"],
                tags=["central", "obc", "pre-matric"],
            ),
            RawOpportunity(
                external_id="nsp-post-matric-sc",
                source="nsp",
                title="Post Matric Scholarship for SC Students",
                description="Financial assistance to SC students pursuing post-matriculation courses.",
                amount_min=10000,
                amount_max=50000,
                deadline=date.today() + timedelta(days=60),
                eligibility_rules={
                    "category": ["SC"],
                    "max_income": 250000,
                    "min_cgpa": 5.0,
                    "year_of_study": {"min": 1, "max": 4},
                    "states": ["ALL"],
                },
                documents_required=["caste_certificate", "income_certificate", "fee_receipt", "aadhaar"],
                application_url="https://scholarships.gov.in/",
                state_filter=["ALL"],
                tags=["central", "sc", "post-matric"],
            ),
            RawOpportunity(
                external_id="nsp-merit-cum-means",
                source="nsp",
                title="Merit-cum-Means Scholarship for Professional Courses",
                description="For students pursuing professional/technical courses with family income below threshold.",
                amount_min=20000,
                amount_max=30000,
                deadline=date.today() + timedelta(days=30),
                eligibility_rules={
                    "category": ["General", "OBC", "SC", "ST", "EWS"],
                    "max_income": 600000,
                    "min_cgpa": 6.0,
                    "streams": ["Engineering", "Medical", "Law", "Management"],
                    "states": ["ALL"],
                },
                documents_required=["income_certificate", "marksheet", "admission_letter", "aadhaar"],
                application_url="https://scholarships.gov.in/",
                state_filter=["ALL"],
                tags=["central", "merit", "professional"],
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "seed_data"}


class MahaDBTConnector(BaseConnector):
    source_id = "mahadbt"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="mahadbt-rajarshi-shahu",
                source="mahadbt",
                title="Rajarshi Shahu Maharaj Scholarship (Maharashtra)",
                description="State scholarship for economically backward class students in Maharashtra.",
                amount_min=5000,
                amount_max=25000,
                deadline=date.today() + timedelta(days=40),
                eligibility_rules={
                    "category": ["OBC", "SEBC", "VJNT"],
                    "max_income": 800000,
                    "min_cgpa": 5.5,
                    "states": ["Maharashtra"],
                },
                documents_required=["domicile_certificate", "income_certificate", "caste_certificate"],
                application_url="https://mahadbt.maharashtra.gov.in/",
                state_filter=["Maharashtra"],
                tags=["state", "maharashtra", "obc"],
            ),
            RawOpportunity(
                external_id="mahadbt-ebc-scholarship",
                source="mahadbt",
                title="EBC Scholarship for Professional Courses (Maharashtra)",
                description="For EBC category students in professional degree programs within Maharashtra.",
                amount_min=15000,
                amount_max=40000,
                deadline=date.today() + timedelta(days=55),
                eligibility_rules={
                    "category": ["EBC"],
                    "max_income": 600000,
                    "min_cgpa": 6.0,
                    "streams": ["Engineering", "Pharmacy", "Architecture"],
                    "states": ["Maharashtra"],
                },
                documents_required=["fee_receipt", "income_certificate", "aadhaar", "bank_passbook"],
                application_url="https://mahadbt.maharashtra.gov.in/",
                state_filter=["Maharashtra"],
                tags=["state", "maharashtra", "ebc", "professional"],
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "seed_data"}


class MySchemeConnector(BaseConnector):
    source_id = "myscheme"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="myscheme-nsp-bridge",
                source="myscheme",
                title="National Means-cum-Merit Scholarship (NMMS)",
                description="Encourages meritorious students from economically weaker sections to continue studies.",
                amount_min=12000,
                amount_max=12000,
                deadline=date.today() + timedelta(days=90),
                eligibility_rules={
                    "category": ["General", "OBC", "SC", "ST", "EWS"],
                    "max_income": 350000,
                    "min_percentage_12th": 55,
                    "year_of_study": {"min": 8, "max": 12},
                    "states": ["ALL"],
                },
                documents_required=["income_certificate", "marksheet", "school_certificate"],
                application_url="https://www.myscheme.gov.in/schemes/nmms",
                state_filter=["ALL"],
                tags=["central", "merit", "school"],
            ),
            RawOpportunity(
                external_id="myscheme-girls-scholarship",
                source="myscheme",
                title="Pragati Scholarship for Girl Students (Technical)",
                description="AICTE scheme for girl students in degree/diploma technical programs.",
                amount_min=50000,
                amount_max=50000,
                deadline=date.today() + timedelta(days=35),
                eligibility_rules={
                    "gender": ["Female"],
                    "max_income": 800000,
                    "min_cgpa": 6.5,
                    "streams": ["Engineering", "Technology"],
                    "states": ["ALL"],
                },
                documents_required=["admission_letter", "income_certificate", "aadhaar", "bank_passbook"],
                application_url="https://www.myscheme.gov.in/",
                state_filter=["ALL"],
                tags=["central", "girls", "technical", "aicte"],
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "seed_data"}
