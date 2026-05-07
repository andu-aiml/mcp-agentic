from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agent import create_llm, bind_tools
from tools import load_mcp_tools
from dotenv import load_dotenv

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

        response = await llm_with_tools.ainvoke(
            state["messages"]
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