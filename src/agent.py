import os
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

# Import LangGraph components for state management
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

# Import Gemini LLM
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env
load_dotenv()

# --- 1. DEFINE AGENT STATE ---
# This dictionary will hold all data for the conversation
class AgentState(TypedDict):
    # 'messages' will store the conversation history (User + AI)
    # Annotated[..., add_messages] tells LangGraph to append new messages to the list
    messages: Annotated[List[AnyMessage], add_messages]
    
    # Store extracted user details for the Lead Capture tool
    user_name: str
    user_email: str
    user_platform: str
    
    # Store the detected intent (Greeting, Pricing, High-Intent)
    current_intent: str

# --- 2. INITIALIZE GEMINI LLM ---
# The assignment allows Gemini 1.5 Flash.
# We set temperature=0 to make the agent factual and consistent.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

print("✅ State defined and Gemini LLM initialized.")