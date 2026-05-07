
from langchain_openai import ChatOpenAI


def create_llm():
    """
    Create the LLM.
    """

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )

    # If using OpenAI instead:
    #
    # llm = ChatOpenAI(
    #     model="gpt-4o"
    # )

    return llm


def bind_tools(llm, tools):
    """
    Bind MCP tools to the LLM.
    """

    return llm.bind_tools(tools)