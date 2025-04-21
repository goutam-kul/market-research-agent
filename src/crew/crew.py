from crewai import Crew, Process
from crew.agents import researcher, use_case_generator, resource_collector, proposal_synthesizer
from crew.tasks import research_task, use_case_generation_task, resource_collection_task, proposal_synthesis_task

# Define the crew
market_research_crew = Crew(
    agents=[researcher, use_case_generator, resource_collector, proposal_synthesizer],
    tasks=[research_task, use_case_generation_task, resource_collection_task, proposal_synthesis_task],
    process=Process.sequential,
    verbose=True
)