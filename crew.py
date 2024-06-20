from crewai import Crew, Process

def create_crew(research_agent, summarizer_agent, research_task, summarize_task):
    return Crew(
        agents=[research_agent, summarizer_agent],
        tasks=[research_task, summarize_task],
        process=Process.sequential
    )
