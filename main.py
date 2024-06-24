import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_news_researcher, create_news_summarizer, create_date_verifier
from tasks import create_news_research_task, create_news_summarize_task, create_date_verification_task
import markdown2
import yagmail
from google.api_core.exceptions import ServiceUnavailable
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Initialize the Google Generative AI (Gemini) API
def initialize_llm():
    from langchain_google_genai import ChatGoogleGenerativeAI
    google_api_key = os.getenv("GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        verbose=True,
        temperature=0.5,
        google_api_key=google_api_key
    )

# Initialize LLM
llm = initialize_llm()

# Create agents with the LLM
news_researcher = create_news_researcher(llm)
date_verifier = create_date_verifier(llm)
news_summarizer = create_news_summarizer(llm)

# Calculate the date range for the last 7 days (strictly between 1 week)
end_date = datetime.today().date()
start_date = end_date - timedelta(days=6)

# Generate a timestamped output file name
output_file_date = datetime.now().strftime("%Y%m%d")
output_file = f'competitors_weekly_news_{output_file_date}.md'

# List of companies
companies = [
    "Amdocs", "BillingPlatform", "Binary Stream", "BluLogix", "Aptitude",
    "Chargebee", "ChargeOver", "Cleeng", "CSG", "Evergen",
    "Gotransverse", "LogiSense", "Maxio", "MonetizeNow", "OneBill",
    "Opencell", "NetSuite", "Recurly", "RecVue", "Rev.io",
    "Intacct", "Stax", "Stripe Billing", "Vindicia", "Workday",
    "Zoho", "Zone & Co", "Zuora", "Aria", "Amberflo",
    "IDI Billing Solutions", "Billwerk", "Cerillion", "m3ter", "Metronome",
    "Octane", "Orb", "Ordway Labs", "Paddle", "Piano.io",
    "Subskribe", "Wingback", "SAP BRIM", "Oracle BRM", "Moesif",
    "Cacheflow"
]


# Retry mechanism for kickoff
def kickoff_with_retry(crew, inputs, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            return crew.kickoff(inputs=inputs)
        except ServiceUnavailable as e:
            attempt += 1
            wait_time = 2 ** attempt
            print(f"Attempt {attempt} failed: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    raise Exception("Maximum retry attempts reached. The service may be down.")

# Function to process each company sequentially
def process_company(company):
    try:
        # Create unique tasks for each company
        research_task = create_news_research_task(news_researcher, company, start_date, end_date)
        date_verification_task = create_date_verification_task(date_verifier, company, start_date, end_date)
        summarize_task = create_news_summarize_task(news_summarizer, company)

        # Create the crew with unique tasks, including date verification
        crew = Crew(
            agents=[news_researcher, date_verifier, news_summarizer],
            tasks=[research_task, date_verification_task, summarize_task],
            process=Process.sequential
        )

        # Create context for the company
        context = {
            "company": company + "billing company",
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        }

        # Execute the crew tasks
        result = kickoff_with_retry(crew, {'company': company, 'context': context})
        return f"## {company}\n{result}\n\n"
    except Exception as e:
        print(f"Failed to execute tasks for {company}: {e}")
        return f"## {company}\nFailed to retrieve news.\n\n"

# Execute task process for each company sequentially
summarized_news = ["# Weekly News Digest\n\n"]

for company in companies:
    summarized_news.append(process_company(company))

# Write all summarized news to a single file
with open(output_file, 'w') as file:
    file.writelines(summarized_news)

print(f"Summarized news has been written to {output_file}")

# Convert Markdown to HTML
html_content = markdown2.markdown("\n".join(summarized_news))

# Clean the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Remove unwanted <br> tags
for br in soup.find_all("br"):
    br.decompose()

# Convert back to cleaned HTML
cleaned_html_content = str(soup)

# Create an HTML email template without styling
email_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weekly Blog Digest</title>
</head>
<body>
    {cleaned_html_content}
</body>
</html>
"""

# Get the current date for email subject
email_subject_date = datetime.now().strftime("%Y-%m-%d")
email_subject = f"Weekly Blog Digest - {email_subject_date}"

# Send the email using yagmail
yag = yagmail.SMTP(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))

yag.send(
    to="pavanusha0019@gmail.com",
    subject=email_subject,
    contents=email_content
)

print("Email sent successfully")
