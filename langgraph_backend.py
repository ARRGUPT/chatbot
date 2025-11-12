from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests
import streamlit as st

# -------------------
# 1. LLM
# -------------------
load_dotenv()
groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
api_key = st.secrets.get("ALPHAVANTAGE_API_KEY") or os.getenv("ALPHAVANTAGE_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model="llama-3.3-70b-versatile")

# -------------------
# 2. Tools
# -------------------
search_tool = DuckDuckGoSearchRun()

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation=="add":
            result = first_num+second_num
        elif operation=="sub":
            result = first_num-second_num
        elif operation=="mul":
            result = first_num*second_num
        elif operation=="div":
            if second_num==0:
                return {"error":"Division by zero is not allowed"}
            result = first_num/second_num
        else:
            return {"error":f"Unsupported operation '{operation}'"}
        
        return {"first_num":first_num, "second_num":second_num, "operation":operation, "result":result}
    except Exception as e:
        return {"error":str(e)}


@tool
def get_stock_price(symbol:str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    return r.json()


tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)


# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    
    messages : Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state['messages']

    response = llm_with_tools.invoke(messages)
    
    return {"messages" : [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
# setting up connection with sqlite3 database
# conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# SqliteSaver Checkpointer
# checkpointer = SqliteSaver(conn=conn)

try:
    # from langgraph.checkpoint.sqlite import SqliteSaver
    conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    print("Warning: Using MemorySaver instead of SqliteSaver")

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, 'chat_node')

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')
# graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_all_threads(): 
    try:
        all_threads = set()
        for checkpoint in checkpointer.list(None):
            all_threads.add(checkpoint.config['configurable']['thread_id'])
        return list(all_threads)
    except Exception as e:
        print(f"Error retrieving threads: {e}")
        return []
