from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime, timedelta
from crewai_tools import SerperDevTool
 
end_date = datetime.today().strftime("%Y-%m-%d")
start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

# Initialize the tool for internet searching capabilities with filters for credible sources
tool = SerperDevTool(
    api_key=os.getenv('SERPER_API_KEY'),
    filters={
        "domains": [
            "official company websites",
            "reputable news outlets like Reuters, Bloomberg, The New York Times, etc."
        ],
        "exclude": ["reddit.com", "quora.com", "similar sites"],
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }
)
