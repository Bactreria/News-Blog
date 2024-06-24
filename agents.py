from crewai import Agent
from tools import tool

def create_news_researcher(llm):
    return Agent(
        role="Researcher",
        goal="Discover and summarize key information about the latest weekly news for {company} from reputable sources.",
        verbose=True,
        memory=True,
        backstory=(
            "A seasoned analyst who excels in digging deep to uncover valuable insights about various companies."
        ),
        tools=[tool],
        llm=llm,
        allow_delegation=True,
        max_iter=5   
    )

def create_news_summarizer(llm):
    return Agent(
        role="Summarizer",
        goal="Create a summary of the latest weekly news for {company}.",
        verbose=True,
        memory=True,
        backstory=(
            "An experienced writer with a knack for turning complex business details into compelling stories."
        ),
        tools=[tool],
        llm=llm,
        allow_delegation=False,
        max_iter=5   
    )

def create_date_verifier(llm):
    return Agent(
        role="Date Verifier",
        goal="Verify that each article is within the specified date range and filter out those that are not.",
        verbose=True,
        memory=True,
        backstory=(
            "An expert in date verification, ensuring all news articles fall within the required timeframe."
        ),
        tools=[tool],
        llm=llm,
        allow_delegation=False,
        max_iter=7   
    )
