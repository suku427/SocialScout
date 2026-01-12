from src.agent import graph
from langchain_core.messages import HumanMessage

def run_chat():
    print("🤖 AutoStream Agent (Type 'q' to quit)")
    print("---------------------------------------")
    
    # Initialize chat history
    messages = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'q':
            break
            
        # Add user message to history
        messages.append(HumanMessage(content=user_input))
        
        # Run the graph
        # The graph handles state, so we just pass the latest inputs
        for event in graph.stream({"messages": messages}):
            for value in event.values():
                if "messages" in value:
                    last_msg = value["messages"][-1]
                    # Only print the AI's final response, not the tool calls
                    if last_msg.content:
                        print(f"Agent: {last_msg.content}")

if __name__ == "__main__":
    run_chat()