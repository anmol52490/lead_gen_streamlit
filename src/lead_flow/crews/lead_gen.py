# Updated lead_gen.py with GCP-Safe Caching

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from src.lead_flow.typesx import Activity_Analyser, Profile_Analyser, Content_Analyst, Alignment
import http.client
import json
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Load the LLM
gemini_llm = LLM(
    model="gemini/gemini-1.5-pro",
    temperature=0.1,
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Use /tmp/cache for GCP safe caching
CACHE_DIR = Path("/tmp/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

@CrewBase
class LeadGen():
    """LeadGen crew"""

    agents_config = os.path.join(os.getcwd(), "config/agent_user.yaml")
    tasks_config = os.path.join(os.getcwd(), "config/task_user.yaml")

    @agent
    def activity_analyser(self) -> Agent:
        return Agent(config=self.agents_config['activity_analyser'], llm=gemini_llm)

    @agent
    def profile_summarizer(self) -> Agent:
        return Agent(config=self.agents_config['profile_summarizer'], llm=gemini_llm)

    @agent
    def content_analyst(self) -> Agent:
        return Agent(config=self.agents_config['content_analyst'], llm=gemini_llm)

    @agent
    def vision_aligner(self) -> Agent:
        return Agent(config=self.agents_config['vision_aligner'], llm=gemini_llm)

    @task
    def analyze_activity_task(self) -> Task:
        return Task(config=self.tasks_config['analyze_activity'], output_pydantic=Activity_Analyser)

    @task
    def summarize_profile_task(self) -> Task:
        return Task(config=self.tasks_config['summarize_profile'], output_pydantic=Profile_Analyser)

    @task
    def analyze_content_task(self) -> Task:
        return Task(config=self.tasks_config['analyze_content'], output_pydantic=Content_Analyst)

    @task
    def assess_alignment_task(self) -> Task:
        return Task(config=self.tasks_config['assess_alignment'], output_pydantic=Alignment)

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def _get_cache_file(self, filename: str) -> Path:
        return CACHE_DIR / filename

    def fetch_linkedin_data(self, username):
        cache_file = self._get_cache_file(f"extracted_data_{username}.json")
        if cache_file.exists():
            try:
                print(f"Loading cached data from {cache_file}")
                with cache_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Cache error (read): {e}")

        try:
            print(f"Fetching data from API for {username}")
            conn = http.client.HTTPSConnection("linkedin-api8.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
                'x-rapidapi-host': "linkedin-api8.p.rapidapi.com"
            }
            conn.request("GET", f"/profile-data-connection-count-posts?username={username}", headers=headers)
            res = conn.getresponse()
            if res.status != 200:
                print(f"API Error: {res.status} {res.reason}")
                return None

            raw_data = res.read()
            with cache_file.open('w', encoding='utf-8') as f:
                f.write(raw_data.decode('utf-8'))

            return json.loads(raw_data)

        except Exception as e:
            print(f"API Error (fetch_linkedin_data): {e}")
            return None
        finally:
            conn.close()

    def fetch_company_details(self, company_id):
        cache_file = self._get_cache_file(f"extracted_data_{company_id}.json")
        if cache_file.exists():
            try:
                print(f"Loading cached company details from {cache_file}")
                with cache_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Cache error (read company): {e}")

        try:
            print(f"Fetching company details from API for {company_id}")
            conn = http.client.HTTPSConnection("linkedin-api8.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
                'x-rapidapi-host': "linkedin-api8.p.rapidapi.com"
            }
            conn.request("GET", f"/get-company-details?username={company_id}", headers=headers)
            res = conn.getresponse()
            if res.status != 200:
                print(f"API Error: {res.status} {res.reason}")
                return None

            raw_data = res.read()
            with cache_file.open('w', encoding='utf-8') as f:
                f.write(raw_data.decode('utf-8'))

            return json.loads(raw_data)

        except Exception as e:
            print(f"API Error (fetch_company_details): {e}")
            return None
        finally:
            conn.close()

    def fetch_company_posts(self, company_id):
        cache_file = self._get_cache_file(f"extracted_data_posts_{company_id}.json")
        if cache_file.exists():
            try:
                print(f"Loading cached company posts from {cache_file}")
                with cache_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Cache error (read company posts): {e}")

        try:
            print(f"Fetching company's posts from API for {company_id}")
            conn = http.client.HTTPSConnection("linkedin-api8.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
                'x-rapidapi-host': "linkedin-api8.p.rapidapi.com"
            }
            conn.request("GET", f"/get-company-posts?username={company_id}&start=0", headers=headers)
            res = conn.getresponse()
            if res.status != 200:
                print(f"API Error: {res.status} {res.reason}")
                return None

            raw_data = res.read()
            with cache_file.open('w', encoding='utf-8') as f:
                f.write(raw_data.decode('utf-8'))

            return json.loads(raw_data)

        except Exception as e:
            print(f"API Error (fetch_company_posts): {e}")
            return None
        finally:
            conn.close()

    def extract_fields(self, data):
        return {
            'posts_data': [post.get('text', 'No post text available') for post in data.get('posts', [])[:10]],
            'summary': data.get('data', {}).get('summary', 'No summary available'),
            'post_times': [post.get('postedDate', 'No date available') for post in data.get('posts', [])[:10]],
            'educations_data': [e.get('schoolName', 'Unknown school') for e in data.get('data', {}).get('educations', [])],
            'positions_data': [p.get('description', 'No position description') for p in data.get('data', {}).get('fullPositions', [])],
            'skills_data': [s.get('name', 'Unnamed skill') for s in data.get('data', {}).get('skills', [])],
            'headline': data.get('data', {}).get('headline', 'No headline available'),
            'education_data': [e.get('degree', 'Degree not specified') for e in data.get('data', {}).get('educations', [])]
        }

    def extract_fields1(self, company_details, company_posts):
        company_data = company_details.get('data', {})
        posts_data = company_posts.get('data', []) if company_posts else []
        return {
            'company_description': company_data.get('description', 'No company description available'),
            'company_type': company_data.get('type', 'Company type not specified'),
            'company_tagline': company_data.get('tagline', 'No tagline available'),
            'company_name': company_data.get('name', 'Unnamed company'),
            'post_times': [post.get('postedDate', 'No date') for post in posts_data[:10]],
            'specialities': company_data.get('specialities', []),
            'industries': company_data.get('industries', []),
            'staff_count': company_data.get('staffCount', 'Unknown'),
            'company_posts': [post.get('text', 'No post text available') for post in posts_data[:10]],
            'post_dates': [post.get('postedDate', 'No date available') for post in posts_data[:10]],
            'post_links': [post.get('postUrl', 'No post link available') for post in posts_data[:10]],
            'post_engagements': [{
                'likes': post.get('likeCount', 0),
                'comments': post.get('commentsCount', 0),
                'reactions': post.get('totalReactionCount', 0)
            } for post in posts_data[:10]],
            'media_images': [post.get('image', [{}])[0].get('url', 'No image') if post.get('image') else 'No image' for post in posts_data[:10]]
        }