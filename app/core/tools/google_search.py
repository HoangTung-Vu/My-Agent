from langchain_core.tools import Tool

import os
from dotenv import load_dotenv
load_dotenv()

cse_id = os.getenv('GOOGLE_CSE_ID', 'your-google-cse-id-here')
search_key = os.getenv("GOOGLE_SEARCH_API_KEY", "your-google-api-key-here")

print(f"Using CSE ID: {cse_id}")
print(f"Using Search API Key: {search_key}")

from langchain_google_community import GoogleSearchAPIWrapper
from app.core.tools.request_url import fetch_webpage_content

search = GoogleSearchAPIWrapper(google_cse_id=cse_id,google_api_key=search_key)
def search_top3(query : str):
    return search.results(query = query, num_results = 3)

def search_and_fetch_content(query : str):
    search_res = search_top3(query)

    for page in search_res : 
        if 'link' in page:
            page['content'] = fetch_webpage_content(page['link'])
    
    semantic_result = "\n\n".join([f"Link: {page['link']}\n {page['content']}" for page in search_res])
    return semantic_result 

google_search = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search_and_fetch_content,
)

