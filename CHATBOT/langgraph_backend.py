# Core imports for LangGraph chatbot
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv(dotenv_path='../.env')

# Initialize Groq LLM with Llama 3.3-70B model
model = ChatGroq(model="llama-3.3-70b-versatile")

# Define state schema - tracks conversation messages
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Main chat processing node - handles LLM responses
def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages' : [response]}

# Memory saver for conversation persistence
check_pointer = InMemorySaver()

# Build the conversation graph
graph = StateGraph(ChatState)

# Add single processing node
graph.add_node('chat_node', chat_node)

# Define flow: START -> chat_node -> END
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# Compile chatbot with memory persistence
chatbot = graph.compile(checkpointer=check_pointer)