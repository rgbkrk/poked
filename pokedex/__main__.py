import poked.client as client
import asyncio


async def main():
    df = await client.list_pokemon()

    print(df)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
