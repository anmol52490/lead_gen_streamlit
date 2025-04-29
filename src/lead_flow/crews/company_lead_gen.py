from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from dotenv import load_dotenv
load_dotenv()
from src.lead_flow.typesx import Activity_Analyser, Profile_Analyser, Content_Analyst, Alignment
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
gemini_llm  = LLM(
    model="gemini/gemini-1.5-pro",
    temperature=0.1,
    api_key=os.getenv("GEMINI_API_KEY"),
    )
@CrewBase
class CompanyLeadGen():
    """CompanyLeadGen crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = os.path.join(os.getcwd(), "config/agent_company.yaml")
    tasks_config = os.path.join(os.getcwd(), "config/task_company.yaml")

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def company_activity_analyser(self) -> Agent:
        return Agent(
            config=self.agents_config['company_activity_analyser'],
            verbose=True,
            llm=gemini_llm,
        )

    @agent
    def company_profile_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['company_profile_summarizer'],
            verbose=True,
            llm=gemini_llm,
        )

    @agent
    def company_content_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['company_content_analyst'],
            verbose=True,llm=gemini_llm,
        )
    @agent
    def strategic_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['strategic_analyzer'],
            verbose=True,llm=gemini_llm,
        )
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def analyze_company_activity(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_company_activity'],
            output_pydantic=Activity_Analyser
        )
    
    @task
    def summarize_company_profile(self) -> Task:
        return Task(
            config=self.tasks_config['summarize_company_profile'],
            output_pydantic=Profile_Analyser,
        )

    @task
    def analyze_company_content(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_company_content'],
            output_pydantic=Content_Analyst,
            
        )
    @task
    def assess_alignment(self) -> Task:
        return Task(
            config=self.tasks_config['assess_alignment'],
            output_pydantic=Alignment,
            
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CompanyLeadGen crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
