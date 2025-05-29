import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "your_default_api_key")

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.8
)

tools_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1
)