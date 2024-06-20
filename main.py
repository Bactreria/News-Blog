import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_news_researcher, create_news_summarizer
from tasks import create_news_research_task, create_news_summarize_task
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
news_summarizer = create_news_summarizer(llm)

# Calculate the date range for the last 7 days
end_date = datetime.today().date()
start_date = end_date - timedelta(days=7)

# Generate a timestamped output file name
output_file_date = datetime.now().strftime("%Y%m%d")
output_file = f'competitors_weekly_news_{output_file_date}.md'

# List of billing companies
companies = [
    "Amdocs"
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

# Execute task process for each company
summarized_news = ["# Weekly News Digest\n\n"]

for company in companies:
    try:
        # Create unique tasks for each company
        research_task = create_news_research_task(news_researcher, company, start_date, end_date)
        summarize_task = create_news_summarize_task(news_summarizer, company)

        # Create the crew with unique tasks
        crew = Crew(
            agents=[news_researcher, news_summarizer],
            tasks=[research_task, summarize_task],
            process=Process.sequential
        )

        # Execute the crew tasks
        result = kickoff_with_retry(crew, {'company': company})
        summarized_news.append(f"## {company}\n{result}\n\n")
    except Exception as e:
        print(f"Failed to execute tasks for {company}: {e}")

# Write all summarized news to a single file
with open(output_file, 'w') as file:
    file.writelines(summarized_news)

print(f"Summarized news has been written to {output_file}")

# Convert Markdown to HTML
html_content = markdown2.markdown("\n".join(summarized_news))

# Clean the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Remove any unwanted <br> tags or fix invalid CSS
for br in soup.find_all("br"):
    br.decompose()

# Convert back to cleaned HTML
cleaned_html_content = str(soup)

# Create an HTML email template
email_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weekly Blog Digest</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #444;
        }}
        .article {{
            margin-bottom: 20px;
        }}
        .source {{
            font-size: 0.9em;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        {cleaned_html_content}
    </div>
</body>
</html>
"""

# Get the current date for email subject
email_subject_date = datetime.now().strftime("%Y-%m-%d")
email_subject = f"Weekly Blog Digest - {email_subject_date}"

# Send the email using yagmail
yag = yagmail.SMTP(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))

yag.send(
    to=(your email),
    subject=email_subject,
    contents=email_content
)

print("Email sent successfully")
