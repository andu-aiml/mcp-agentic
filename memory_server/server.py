import logging

from mcp.server.fastmcp import FastMCP

from sqlalchemy import select

from db import AsyncSessionLocal
from db import init_db

from models import Memory


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


mcp = FastMCP("memory-server")


@mcp.tool()
async def save_memory(
    user_id: str,
    memory: str
) -> dict:
    """
    Save a memory into PostgreSQL.

    Use this when:
    - user asks to remember something
    - storing long-term information
    - saving research notes
    - storing preferences
    """

    try:

        async with AsyncSessionLocal() as session:

            new_memory = Memory(
                user_id=user_id,
                memory=memory
            )

            session.add(new_memory)

            await session.commit()
            await session.refresh(new_memory)

            logger.info(
                f"Memory saved for user: {user_id}"
            )

            return {
                "status": "success",
                "memory_id": new_memory.id,
                "message": "Memory saved successfully"
            }

    except Exception as e:

        logger.error(f"Save memory error: {e}")

        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
async def get_memories(
    user_id: str
) -> dict:
    """
    Retrieve all memories for a user.

    Use this when:
    - recalling previous information
    - retrieving saved notes
    - restoring context
    """

    try:

        async with AsyncSessionLocal() as session:

            query = select(Memory).where(
                Memory.user_id == user_id
            )

            result = await session.execute(query)

            memories = result.scalars().all()

            formatted_memories = []

            for memory in memories:
                formatted_memories.append({
                    "id": memory.id,
                    "memory": memory.memory,
                    "created_at": str(memory.created_at)
                })

            return {
                "status": "success",
                "count": len(formatted_memories),
                "memories": formatted_memories
            }

    except Exception as e:

        logger.error(f"Get memories error: {e}")

        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
async def search_memories(
    user_id: str,
    query_text: str
) -> dict:
    """
    Search memories using keyword matching.

    Use this when:
    - finding related memories
    - contextual recall
    - searching historical data
    """

    try:

        async with AsyncSessionLocal() as session:

            query = select(Memory).where(
                Memory.user_id == user_id,
                Memory.memory.ilike(f"%{query_text}%")
            )

            result = await session.execute(query)

            memories = result.scalars().all()

            formatted_memories = []

            for memory in memories:
                formatted_memories.append({
                    "id": memory.id,
                    "memory": memory.memory,
                    "created_at": str(memory.created_at)
                })

            return {
                "status": "success",
                "count": len(formatted_memories),
                "memories": formatted_memories
            }

    except Exception as e:

        logger.error(f"Search memory error: {e}")

        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
async def delete_memory(
    memory_id: int
) -> dict:
    """
    Delete a memory by ID.
    """

    try:

        async with AsyncSessionLocal() as session:

            query = select(Memory).where(
                Memory.id == memory_id
            )

            result = await session.execute(query)

            memory = result.scalar_one_or_none()

            if not memory:
                return {
                    "status": "error",
                    "message": "Memory not found"
                }

            await session.delete(memory)
            await session.commit()

            return {
                "status": "success",
                "message": "Memory deleted"
            }

    except Exception as e:

        logger.error(f"Delete memory error: {e}")

        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":

    import asyncio

    logger.info("Initializing database...")

    asyncio.run(init_db())

    logger.info("Starting Memory MCP Server...")

    mcp.run(transport="stdio")
