import json
import random
import asyncio
import pokebase

from showdown import utils
from config import username
from battle.decisions import *

async def reconnectToBattle(msg, websocket):
    """If the bot was in a battle but it was disconnected from the server,
    he will join to the battle again.

    websocket.send("|/cancelsearch"): This ensures that at least two '|updatesearch|' will be received.
    """
    while msg[0:14] != "|updatesearch|":
        msg = await websocket.recv()
    await websocket.send("|/cancelsearch")
    msg = await websocket.recv()
    while msg[0:14] != "|updatesearch|":
        msg = await websocket.recv()
    games = json.loads(msg.replace("|updatesearch|", ""))['games']
    if games:
        for game in games:
            await websocket.send(f"|/join {game}")

class on_battle():
    def __init__(self, msg, websocket) -> None:
        self.msg = msg
        self.websocket = websocket
        self.pokemons = {}
        self.pokemonlist = {}
        self.alliesHP = {}
        self.moves_available = []
        self.pokemonHP = None
        self.playerID = None
        self.foePokemon = None
        self.foePokemonHP = None
        self.foeID = None
        self.newTurn = False
        self.active = None
        self.jsonData = None
        self.allies = []
        self.battleID = self.msg.splitlines()[0][1:]

    async def message(self, msg):
        self.battleEnd = False

        splitmsg = msg.splitlines()
        for line in splitmsg:
            if line[:10] == "|request|{":
                contentJson = line[9:]
                self.jsonData = json.loads(contentJson)
                setjsonData = set(self.jsonData)
                if 'forceSwitch' in setjsonData:
                    await self.switch()

                if 'active' in setjsonData:
                    self.allies = []
                    self.newTurn = True
                    pokemons = self.jsonData["side"]["pokemon"]
                    self.active = str(pokemons[0]["details"]).lower()
                    for pokemon in pokemons:
                        if pokemon["active"] == False:
                            pokemonID = str(pokemon['details']).lower()
                            pokemonHP = str(pokemon['condition'].split("/")[0])
                            if pokemonHP == "0 fnt": pokemonHP = 0
                            else: pokemonHP = int(pokemonHP)
                            if pokemonHP:
                                self.allies.append(pokebase.pokemon(pokemonID))
                                self.alliesHP[pokemonID] = pokemonHP
                    self.updatePokemons()

            if line[:8] == "|player|" and line.count("|") == 5:
                if utils.name_to_id(line.split("|")[3]) != utils.name_to_id(username):
                    self.foeID = line.split("|")[2]

            if line[:5] == "|win|":
                self.battleEnd = True

            if line[:8] == "|switch|":
                if line.split("|")[2].split(":")[0].strip() == f"{self.foeID}a":
                    self.foePokemon = line.split("|")[2].split(":")[1].strip()
                    self.foePokemon = pokebase.pokemon(utils.name_to_id(self.foePokemon))
                self.updateHP(line)
            if line[:9] == "|-damage|" or line[:7] == "|-heal|":
                self.updateHP(line)

        if msg == f'>{self.battleID}\n|request|':
            await self.timeron()
            await self.motto()

        if self.battleEnd:
            if line[5:] == username:
                await self.win()
            else:
                await self.lose()
            return await self.leave()
        if self.newTurn and self.foePokemon:
            requestMoves = self.jsonData["active"][0]["moves"]
            self.movementsAvailable(requestMoves)
            if "recharge" not in self.moves_available:
                pokemon = pokebase.pokemon(self.active)
                decisionMove: decision = decision(self.websocket, self.battleID, self.moves_available, self.foePokemon, pokemon, self.allies, self.pokemonHP, self.foePokemonHP, self.alliesHP)
                asyncio.create_task(decisionMove._decisionByLogic())
            else:
                await self.choosemove('recharge')
            #self.clearMovementsAvailable()
            self.newTurn = False

    def updatePokemons(self):
        pokemons = self.jsonData["side"]["pokemon"]
        self.playerID = self.jsonData["side"]["id"]
        for number, pokemon in enumerate(pokemons):
            self.pokemonlist[str(pokemon['details']).split(",")[0]] = number + 1
        for pokemon in pokemons:
            if pokemon['condition'] == '0 fnt':
                self.pokemonlist.pop(str(pokemon['details']).split(",")[0])
    
    def updateHP(self, data):
        hp = data.split("|")[-1].split("/")[0]
        player = data.split("|")[2].split(":")[0][:2]
        if hp == "0 fnt": hp = 0
        else: hp = int(hp)
        if player == self.playerID:
            self.pokemonHP = hp - 60
        else:
            self.foePokemonHP = hp

    def movementsAvailable(self, moves):
        self.moves_available = []
        for move in moves:
            attributesMoves = set(move)
            if 'disabled' in attributesMoves:
                if move['disabled']:
                    continue
            self.moves_available.append(move['move'].lower())
    
    def clearMovementsAvailable(self):
        return self.moves_available.clear()

    async def switch(self):
        self.updatePokemons()
        pokemonSwitch = random.choice(list(self.pokemonlist))
        await self.websocket.send(f"{self.battleID}|/choose switch {self.pokemonlist[pokemonSwitch]}")
    
    async def choosemove(self, move):
        return await self.websocket.send(f'{self.battleID}|/choose move {move}')

    async def timeron(self):
        """Start the timer on a Metronome Battle.
        """
        return await self.websocket.send(f'{self.battleID}|/timer on')

    async def leave(self):
        """Leaves from a battle.
        """
        return await self.websocket.send(f'/noreply |/leave {self.battleID}')

    async def motto(self):
        await self.websocket.send(f'{self.battleID}|♪ Jessie: Prepare for trouble!\nJames: Make it double!\nJessie: To protect the world from devastation!')
        await asyncio.sleep(2)
        await self.websocket.send(f'{self.battleID}|James: To unite all peoples within our nation!\nJessie: To denounce the evils of truth and love! \nJames: To extend our reach to the stars above!')
        await asyncio.sleep(2)
        await self.websocket.send(f'{self.battleID}|Jessie: Jessie! James: James!\nJessie: Team Rocket blasts off at the speed of light!\nJames: Surrender now or prepare to fight!')
        await asyncio.sleep(1.5)
        await self.websocket.send(f"{self.battleID}|Meowth: Meowth! That's right! ♪ ♪ ♪")

    async def lose(self):
        return await self.websocket.send(f"{self.battleID}|AHHHHHH!~ Team Rocket's blasting off again!!! . . . ting")

    async def win(self):
        return await self.websocket.send(f"{self.battleID}|Jessie: We've won! We've finally won!\nJames: I hope the Boss will be proud of me!\nMeowth: and the Boss will finally make me da top cat!")