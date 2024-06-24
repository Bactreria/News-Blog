from crewai import Task
from tools import tool

def create_news_research_task(agent, company, start_date, end_date):
    return Task(
        description=(
            f"Identify the latest weekly news about {company} billing company from their official site and other reputable news sources. "
            f"Collect news from {start_date} to {end_date}. Avoid sources like Reddit, Quora, and similar sites."
        ),
        expected_output=f'A list of headlines and  links with complete url  to the news articles about {company} billing company from {start_date} to {end_date}.',
        tools=[tool],
        agent=agent
    )

def create_news_summarize_task(agent, company):
    return Task(
        description=(
            f"Summarize the latest weekly news articles about {company} billing company collected by the news researcher. "
            "Provide a concise summary for each article including the headline, a 4-5 line summary and the source(named as readme and url must be complete). "
            "Ensure each 'Read more' link directs to the actual article on the official or reputable news site."
        ),
        expected_output=f'A summarized report of the weekly news about {company} billing company in markdown format with headlines,comprehensive summaries of 5-6 lines  and read more(which has the complete source link).',
        tools=[tool],
        agent=agent,
        async_execution=False   
    )

def create_date_verification_task(agent, company, start_date, end_date):
    return Task(
        description=(
            f"Verify that the dates of all articles about {company} are within the range {start_date} to {end_date}. "
            "Filter out any articles that are not within this range."
            "Ensure URLs are complete and direct to the actual article on click."
        ),
        expected_output=f'Filtered list of articles about {company} strictly within {start_date} to {end_date}.',
        tools=[tool],
        agent=agent
    )
