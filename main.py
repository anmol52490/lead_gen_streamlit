from src.lead_flow.crews.lead_gen import LeadGen
from src.lead_flow.crews.company_lead_gen import CompanyLeadGen
def analyze_lead(profile_type: str, profile_url: str):
    processor = LeadGen()
    processor1 = CompanyLeadGen()
    HIDEVS_VISION= """
HiDevs is a community-driven AI upskilling platform focused on building the next generation of talent in Generative AI and related technologies. Its core mission is to empower individuals—especially students and early-career engineers—through personalized learning paths, real-world projects, and industry mentorship to ensure successful transitions from academia to industry.

Vision & Mission:
HiDevs envisions creating a specialized global workforce equipped to meet the demands of rapidly evolving AI ecosystems. The mission is to upskill and reskill individuals, unlocking job opportunities and fostering career growth. By 2030, HiDevs aims to develop a global community of over 10 million Generative AI developers.

What HiDevs Offers:
- Structured 5-Step Upskilling Journey:
  1. Foundations – Start with an AI-driven skill assessment.
  2. Personalized Roadmap – Get tailored learning paths with curated resources.
  3. Real-World Projects – Work on industry PoCs from global companies.
  4. AI-Driven Feedback – Receive dynamic, level-based feedback.
  5. Job Assistance – End-to-end placement support including resume building, LinkedIn optimization, and mock interviews.

- Tools & Utilities:
  - AI-Powered Resume Builder
  - Interview Prep & JD Matching System

Community & Reach:
- 1K+ students mentored
- 500+ member community
- 10+ seminars & workshops
- 150+ active users

Achievements:
- $2000 in cloud credits from Google & AWS
- MoU with NMIT Bangalore to develop 1000+ GenAI talents

Founders:
- Deepak Chawla (Founder)
- Himanshu Somani (Co-Founder)
"""
    if profile_type == "user":
        username = profile_url.split("/in/")[-1].strip("/")
        api_data = processor.fetch_linkedin_data(username)
        if not api_data or not isinstance(api_data, dict) or "data" not in api_data:
            return None, f"Invalid or empty data for user: {username}"

        inputs = processor.extract_fields(api_data)
        inputs["hidevs_vision"] = HIDEVS_VISION
        result = processor.crew().kickoff(inputs=inputs)

    elif profile_type == "company":
        company_id = profile_url.split("/company/")[-1].strip("/")
        company_details = processor.fetch_company_details(company_id)
        company_post = processor.fetch_company_posts(company_id)
        if not company_details or not company_post:
            return None, f"Invalid or empty data for user: {username}"
        #if not api_data or not isinstance(api_data, dict) or "data" not in api_data:
            

        inputs = processor.extract_fields1(company_details, company_post)
        inputs["hidevs_vision"] = HIDEVS_VISION
        result = processor1.crew().kickoff(inputs=inputs)

    return result, None
