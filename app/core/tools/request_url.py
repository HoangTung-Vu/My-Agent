import requests
from app.utils.html_process import process_html_content
from langchain_core.tools import Tool

def fetch_webpage_content(url: str):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            string_results = "URL :" + str(url) + "\n\n" + process_html_content(response.text)
            
            return string_results
        except Exception as e:
            return {"error": str(e)}
        

fetch_web = Tool(
    name="fetch_web",
    description="Fetches the content of a webpage given its URL.",
    func=fetch_webpage_content,
)