from .doc_retriever import doc_retriever
from .get_weather import get_weather
from .google_search import google_search
from .request_url import fetch_web

# Scalable 
all_tools = {
    "doc_retriever": doc_retriever,
    "get_weather": get_weather,
    "google_search": google_search,
    "fetch_web": fetch_web
}
