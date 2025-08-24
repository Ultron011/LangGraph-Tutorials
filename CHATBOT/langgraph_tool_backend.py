# Core imports for LangGraph chatbot
from httpx import request
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import sqlite3
import requests
import os

# Load environment variables for API keys
load_dotenv(dotenv_path='../.env')

stock_api = os.getenv('STOCK_API_KEY')

# Initialize Groq LLM with Llama 3.3-70B model
model = ChatGroq(model="llama-3.3-70b-versatile")


# Tools
search_tool = DuckDuckGoSearchRun(region='us-en')

@tool 
def calculator(first_num: float, second_num: float, operation: str) ->dict:
    """
        Performs basic arithmetic operations on two numbers.
        Supported Operations : add, sub, mul and div
    """

    try:
        if (operation == 'add'):
            result = first_num + second_num
        elif (operation == 'sub'):
            result = first_num - second_num
        elif (operation == 'mul'):
            result = first_num * second_num
        elif (operation == 'div'):
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num" : first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) ->dict:
    """
        Fetch the latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
        using alpha vantage with API key in the url
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={stock_api}"
    r = requests.get(url)
    return r.json()

tools = [search_tool, get_stock_price, calculator]
llm_with_tools = model.bind_tools(tools)

# Define state schema - tracks conversation messages
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Main chat processing node - handles LLM responses with tools
def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = llm_with_tools.invoke(messages)  # Use LLM with tools
    return {'messages': [response]}

tool_node = ToolNode(tools)

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
# Memory saver for conversation persistence
check_pointer = SqliteSaver(conn=conn)

# Build the conversation graph
graph = StateGraph(ChatState)

# Add nodes to the graph
graph.add_node('chat_node', chat_node)
graph.add_node('tools', tool_node)  # Add the tool node

# Define flow: START -> chat_node -> conditional (tools or END)
graph.add_edge(START, 'chat_node')
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

# Compile chatbot with memory persistence
chatbot = graph.compile(checkpointer=check_pointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in check_pointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)