import asyncio
import websockets
from loadAPI import setPokemonList
from utils.login import user

pokemonlist = setPokemonList().copy()

uri = 'ws://sim.smogon.com/showdown/websocket'

async def run():
    async with websockets.connect(uri) as websocket:
        bot: user = user(websocket, pokemonlist)
        await bot.login()

if __name__ == "__main__":
    asyncio.run(run())