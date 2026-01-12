import os
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

# LangGraph & LangChain imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, AnyMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Import our RAG retriever
from src.rag import get_retriever

load_dotenv()

# --- 1. DEFINE TOOLS ---
@tool
def lookup_policy_pricing(query: str):
    """
    Useful for answering questions about AutoStream's subscription plans, 
    pricing, video limits, resolutions, and company policies (refunds/support).
    ALWAYS use this tool for pricing or feature questions.
    """
    retriever = get_retriever()
    # Retrieve top 2 chunks to ensure we get relevant info
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def mock_lead_capture(name: str, email: str, platform: str):
    """
    Use this tool ONLY when the user explicitly provides their Name, Email, and Platform 
    indicating they want to sign up or join. Do NOT call this if data is missing.
    """
    return f"Lead captured successfully: {name}, {email}, {platform}"

# --- 2. DEFINE STATE ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# --- 3. INITIALIZE AGENT ---
# CHANGED: Using 'gemini-pro' which is the most stable free-tier model
# --- 3. INITIALIZE AGENT ---
# CHANGED: Using "gemini-2.0-flash" as confirmed by your check_models.py list
# --- 3. INITIALIZE AGENT ---
# CHANGED: Using "gemini-2.0-flash-lite-preview-02-05" to FIX the 429 Error
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

tools = [lookup_policy_pricing, mock_lead_capture]
llm_with_tools = llm.bind_tools(tools)

# --- 4. SYSTEM PROMPT (THE BRAIN) ---
SYSTEM_PROMPT = """You are an intelligent support agent for AutoStream, a SaaS platform for automated video editing.

YOUR GOALS:
1. Intent Detection:
   - Casual Greeting -> Respond politely.
   - Pricing/Product Inquiry -> ALWAYS use the 'lookup_policy_pricing' tool to find the answer.
   - High-Intent (Ready to sign up) -> Ask for Name, Email, and Creator Platform.

2. Lead Capture Rules:
   - If a user says they want to sign up (High Intent), check if you have Name, Email, and Platform.
   - If ANY detail is missing, ASK for it. Do NOT make up data.
   - ONLY when you have all 3, call the 'mock_lead_capture' tool.

3. Tone:
   - Be helpful, professional, and concise.
"""

# --- 5. DEFINE GRAPH NODES ---
def agent_node(state: AgentState):
    """The node where the LLM thinks and generates a response."""
    messages = state["messages"]
    
    # Ensure system prompt is always at the start
    if not isinstance(messages[0], SystemMessage):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# --- 6. BUILD THE GRAPH ---
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools)) 

builder.set_entry_point("agent")

builder.add_conditional_edges(
    "agent",
    tools_condition,
)
builder.add_edge("tools", "agent")

graph = builder.compile()

print("✅ Agent Graph Built Successfully.")