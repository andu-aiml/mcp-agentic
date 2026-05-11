import asyncio

from server import save_memory
from server import get_memories
from server import search_memories


async def main():

    print("\n--- SAVING MEMORY ---")

    result = await save_memory(
        user_id="andu",
        memory="User is building an AI agent using MCP and LangGraph"
    )

    print(result)

    print("\n--- GET ALL MEMORIES ---")

    memories = await get_memories(
        user_id="andu"
    )

    print(memories)

    print("\n--- SEARCH MEMORIES ---")

    search_result = await search_memories(
        user_id="andu",
        query_text="LangGraph"
    )

    print(search_result)


if __name__ == "__main__":
    asyncio.run(main())
