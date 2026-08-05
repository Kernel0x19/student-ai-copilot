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


class InternshalaSeeder(BaseConnector):
    """Seed internship data for MVP; production uses the Playwright-based InternshalaConnector."""

    source_id = "internshala"

    def fetch(self) -> list[RawOpportunity]:
        return [
            RawOpportunity(
                external_id="internshala-sde-intern-blr",
                source="internshala",
                title="Software Development Intern (Full-Stack)",
                description="Work with a fast-growing fintech startup building React + Node.js features. Own end-to-end feature delivery and code reviews. Ideal for 2nd/3rd-year CS/IT students.",
                amount_min=10000, amount_max=15000,
                deadline=date.today() + timedelta(days=20),
                eligibility_rules={"streams": ["Engineering", "Computer Science", "IT"], "year_of_study": {"min": 2, "max": 4}, "skills": ["HTML", "CSS", "JavaScript"], "states": ["ALL"]},
                documents_required=["resume", "college_id"],
                application_url="https://internshala.com/internship/detail/software-development-intern",
                state_filter=["ALL"], tags=["web", "react", "node", "full-stack"],
                raw_data={"company": "FinPay Technologies", "location": "Bengaluru (Remote)", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="internshala-ml-intern-pune",
                source="internshala",
                title="Machine Learning Intern",
                description="Join our AI lab to build NLP models for document classification using Python and HuggingFace transformers. Open to 3rd/4th-year B.Tech students with CGPA ≥ 7.0.",
                amount_min=12000, amount_max=20000,
                deadline=date.today() + timedelta(days=30),
                eligibility_rules={"streams": ["Engineering", "Computer Science", "Data Science"], "min_cgpa": 7.0, "year_of_study": {"min": 3, "max": 4}, "skills": ["Python", "Machine Learning"], "states": ["ALL"]},
                documents_required=["resume", "college_id"],
                application_url="https://internshala.com/internship/detail/machine-learning-intern",
                state_filter=["ALL"], tags=["ml", "ai", "python", "nlp"],
                raw_data={"company": "DocuAI Labs", "location": "Pune / Remote", "duration": "6 months"},
            ),
            RawOpportunity(
                external_id="internshala-ux-intern-remote",
                source="internshala",
                title="UI/UX Design Intern",
                description="Design mobile-first interfaces for our EdTech platform. Proficiency in Figma required. Portfolio submission mandatory.",
                amount_min=6000, amount_max=10000,
                deadline=date.today() + timedelta(days=35),
                eligibility_rules={"streams": ["Design", "Engineering", "Arts"], "year_of_study": {"min": 1, "max": 4}, "skills": ["Figma", "UI Design"], "states": ["ALL"]},
                documents_required=["resume", "portfolio_link"],
                application_url="https://internshala.com/internship/detail/ui-ux-design-intern",
                state_filter=["ALL"], tags=["design", "figma", "ux", "edtech", "remote"],
                raw_data={"company": "LearnSpark", "location": "Remote", "duration": "3 months"},
            ),
            RawOpportunity(
                external_id="internshala-android-intern-hyd",
                source="internshala",
                title="Android Development Intern",
                description="Build features for a consumer app (2M+ downloads) using Kotlin and Jetpack Compose. CS/IT students in 3rd or final year preferred.",
                amount_min=15000, amount_max=25000,
                deadline=date.today() + timedelta(days=22),
                eligibility_rules={"streams": ["Engineering", "Computer Science", "IT"], "min_cgpa": 6.5, "year_of_study": {"min": 3, "max": 4}, "skills": ["Kotlin", "Android", "Java"], "states": ["ALL"]},
                documents_required=["resume", "college_id"],
                application_url="https://internshala.com/internship/detail/android-development-intern",
                state_filter=["ALL"], tags=["android", "kotlin", "mobile"],
                raw_data={"company": "ShopNow App", "location": "Hyderabad", "duration": "4 months"},
            ),
            RawOpportunity(
                external_id="internshala-hr-intern-chennai",
                source="internshala",
                title="HR & Talent Acquisition Intern",
                description="Support campus hiring drives, screen CVs, schedule interviews, and onboard new hires. MBA/BBA or any stream with strong communication skills welcome.",
                amount_min=7000, amount_max=10000,
                deadline=date.today() + timedelta(days=18),
                eligibility_rules={"streams": ["Management", "Commerce", "Arts", "Engineering"], "year_of_study": {"min": 2, "max": 4}, "states": ["ALL"]},
                documents_required=["resume"],
                application_url="https://internshala.com/internship/detail/hr-talent-acquisition-intern",
                state_filter=["ALL"], tags=["hr", "recruitment", "management"],
                raw_data={"company": "HireHub Solutions", "location": "Chennai / Remote", "duration": "3 months"},
            ),
        ]

    def health_check(self) -> dict:
        return {"source": self.source_id, "status": "ok", "mode": "seed_data"}
