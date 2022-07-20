import requests
import json
import logging
from config import *
from team import teamPacked
import battle.battle as battle

logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG,
        )

class user():
    def __init__(self, websocket, pokemonlist):
        self.loginDone = False
        self.msg = None
        self.websocket = websocket
        self.battles = {}
        self.pokemonlist = pokemonlist

    async def login(self):
        while True:
            self.msg = str(await self.websocket.recv())
            if self.msg[0:10] == '|challstr|':
                challstr = self.msg[10:]
                postlogin = requests.post('https://play.pokemonshowdown.com/~~showdown/action.php', data={'act':'login','name':username,'pass':password,'challstr':challstr})
                assertion = json.loads(postlogin.text[1:])["assertion"]
                await self.websocket.send(f'|/trn {username},0,{assertion}')
                await self.websocket.send(f'|/avatar {avatar}')
                await self.websocket.send(f'|/status {status}')
                for room in rooms:
                    await self.websocket.send(f"|/j {room}")
                await battle.reconnectToBattle(self.msg, self.websocket)
                self.loginDone = True
            if self.loginDone:
                await self.on_login()

    async def on_login(self):
        if self.msg[0:4] == "|pm|":
            user = self.msg.split("|")[2]
            contentPM = self.msg.split("|")[4]
            if contentPM == "/challenge gen1ou":
                await self.utm(teamPacked)
                await self.websocket.send(f"|/accept {user}")
        if self.msg[0:15] == ">battle-gen1ou-":
            splitLines = self.msg.splitlines()
            battleID = splitLines[0][1:]
            for line in splitLines:
                if line == "|init|battle":
                    self.battleActive: battle.on_battle = battle.on_battle(self.msg, self.websocket, self.pokemonlist)
                    self.battles[self.battleActive.battleID] = self.battleActive
                    break
            await self.battles[battleID].message(self.msg)

    async def utm(self, team):
        """Uses a specified team to battle.
        """
        return await self.websocket.send(f'|/utm {team}')