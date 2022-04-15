import asyncio
import websockets
from utils.login import user

uri = 'ws://sim.smogon.com/showdown/websocket'

async def run():
    async with websockets.connect(uri) as websocket:
        bot: user = user(websocket)
        await bot.login()

if __name__ == "__main__":
    eventLoop = asyncio.get_event_loop()
    eventLoop.run_until_complete(run())