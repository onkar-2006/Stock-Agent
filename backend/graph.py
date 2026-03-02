from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph import START ,END
from typing_extensions import TypedDict , List ,Annotated, Literal
from langchain_core.messages import HumanMessage , AIMessage ,BaseMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode ,tool_node  , tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from prompt import PROMPT
from langchain_tavily import TavilySearch
import os
from tools import Tools
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")



class AgentState(TypedDict):
  messages:Annotated[List[BaseMessage] , add_messages]




model = ChatGroq(model ="openai/gpt-oss-120b" , temperature=0.7 , max_tokens=1000, api_key = GROQ_API_KEY)
llm_with_tools = model.bind_tools(Tools)


def call_agent_node(state: AgentState):
    """The node the answer the user."""

    system_prompt = SystemMessage(content=PROMPT)
    messages = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}



graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent_node" ,call_agent_node)
graph_builder.add_edge(START , "agent_node")


tool_node = ToolNode(Tools)
graph_builder.add_node("tools", tool_node)


graph_builder.add_conditional_edges(
    "agent_node",
    tools_condition,
    {"tools": "tools", "__end__": END} 
)

graph_builder.add_edge("tools", "agent_node")

memory = InMemorySaver()

agent = graph_builder.compile(memory)





