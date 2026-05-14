from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agent import create_llm, bind_tools
from tools import load_mcp_tools
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


async def build_graph():

    # Load tools from MCP server
    tools = await load_mcp_tools()

    # Create LLM
    llm = create_llm()

    # Bind tools
    llm_with_tools = bind_tools(llm, tools)

    # Assistant node
    async def assistant(state: State):

        system_prompt = SystemMessage(
            content="""
            You are an AI assistant with memory capabilities.

            IMPORTANT RULES:

            1. When the user shares personal information such as:
            - name
            - preferences
            - goals
            - background
            - projects
            - interests

            Use the save_memory tool.

            2. When the user asks about previous information or memory:
            - "What is my name?"
            - "What do you know about me?"
            - "What project am I working on?"

            Use the get_memories tool.

            3. Be proactive in using tools whenever memory is useful.
            """
            )

        response = await llm_with_tools.ainvoke(
            [system_prompt] + state["messages"]
        )

        return {
            "messages": [response]
        }

    # Tool execution node
    tool_node = ToolNode(tools)

    # Build graph
    builder = StateGraph(State)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", tool_node)

    builder.set_entry_point("assistant")

    # Conditional routing
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        }
    )

    # After tools -> go back to assistant
    builder.add_edge("tools", "assistant")

    graph = builder.compile()

    return graph