import asyncio

from langchain_core.messages import HumanMessage

from graph import build_graph


async def main():

    graph = await build_graph()

    print("Agent Started!")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        response = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ]
            }
        )

        messages = response["messages"]

        print("\nAssistant:")
        print(messages[-1].content)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())