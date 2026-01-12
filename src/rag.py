import json
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# --- 1. LOAD DATA ---
def load_knowledge_base():
    """Reads the JSON file and converts it into LangChain Documents."""
    file_path = os.path.join("data", "knowledge_base.json")
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    # Convert JSON structure into a readable string format for the LLM
    text_content = (
        f"Company: {data['company_name']}\n"
        f"Product: {data['product']}\n\n"
        "PLANS:\n"
    )
    
    for plan in data['plans']:
        text_content += (
            f"- {plan['name']}: {plan['price']}\n"
            f"  Features: {', '.join(plan['features'])}\n"
        )
        
    text_content += "\nPOLICIES:\n"
    text_content += f"- Refunds: {data['policies']['refund_policy']}\n"
    text_content += f"- Support: {data['policies']['support_policy']}\n"

    return [Document(page_content=text_content)]

# --- 2. CREATE RETRIEVER ---
def get_retriever():
    """Builds the Vector Store and returns a retriever object."""
    docs = load_knowledge_base()
    
    # CHANGED: Initialize Local Embedding Model
    # This runs on your CPU, is free, and has NO rate limits.
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create a local vector store (Chroma) in memory
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="autostream_knowledge"
    )
    
    # Return a retriever
    return vectorstore.as_retriever(search_kwargs={"k": 1})

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("🔄 Indexing knowledge base (this may take a moment first time)...")
    retriever = get_retriever()
    
    # Test query
    query = "How much does the Basic Plan cost?"
    result = retriever.invoke(query)
    
    print("\n✅ RAG Test Results:")
    print(f"Query: {query}")
    print(f"Retrieved Context: \n{result[0].page_content}")