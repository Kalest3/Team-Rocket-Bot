import random
import pokebase
import asyncio
from pokemon_set import *

pokemonsSet = pokemonsSet[0]

class decision():
    def __init__(self, websocket, battleID, moves_available, foePokemon, pokemon, allies, pokemonHP, foePokemonHP, alliesHP) -> None:
        self.websocket = websocket
        self.battleID = battleID
        self.moves_available = moves_available
        self.moves_availableClass = {}
        self.foe_moves_availableClass = {}
        self.pokemon = pokemon
        self.pokemonType = []
        self.pokemonHP = pokemonHP
        self.pokemonStats = {}
        self.allies = allies
        self.alliesHP = alliesHP
        self.alliesStats = {}
        self.alliesType = {}
        self.foePokemon = foePokemon
        self.foePokemonType = []
        self.foePokemonHP = foePokemonHP
        self.foePokemonStats = {}
        self.types = {}
        self.movesDamageClass = {}

    async def _decisionByLogic(self):
        self.defAllPokemonStats()
        self.check_moves_available()
        self.defPokemonType()
        self.defFoePokemonType()
        self.defAlliesType()
        choice = self.checkMovesDamage()
        await self.websocket.send(f"{self.battleID}|/choose {choice}")

    def defAllPokemonStats(self):
        self.defPokemonStats()
        self.defFoePokemonStats()
        self.defAlliesStats()
    
    def defPokemonStats(self):
        for stat in self.pokemon.stats:
            statBase = stat.base_stat
            finalStat = (statBase + 15) * 2 * 100 / 100 + 5
            self.pokemonStats[str(stat.stat)] = finalStat
    
    def defFoePokemonStats(self):
        for stat in self.foePokemon.stats:
            statBase = stat.base_stat
            finalStat = (statBase + 15) * 2 + 252 / 4 * 100 / 100 + 5
            self.foePokemonStats[str(stat.stat)] = finalStat
    
    def defAlliesStats(self):
        for ally in self.allies:
            stats = {}
            for stat in ally.stats:
                statBase = stat.base_stat
                finalStat = (statBase + 15) * 2 * 100 / 100 + 5
                stats[str(stat.stat)] = finalStat
            self.alliesStats[ally] = stats

    def check_moves_available(self):
        for move in self.moves_available:
            move = self.moves_available[0]
            self.moves_available.remove(move)
            if " " in move:
                move = move.replace(" ", "-")
            self.moves_available.append(move)
            self.moves_availableClass[move] = pokebase.move(move)

        if self.foePokemon.name in pokemonsSet:
            moves = pokemonsSet[self.foePokemon.name]
            for move in moves:
                self.foe_moves_availableClass[move] = pokebase.move(move)
    
    def defPokemonType(self):
        if not self.pokemon.past_types:
            types = self.pokemon.types
            for type_ in types:
                self.pokemonType.append(type_.type.name)
        else:
            typesGenOne = self.foePokemon.past_types[0].types
            for type_ in typesGenOne:
                self.foePokemonType.append(type_.type.name)
    
    def defFoePokemonType(self):
        if not self.foePokemon.past_types:
            types = self.foePokemon.types
            for type_ in types:
                self.foePokemonType.append(type_.type.name)
        else:
            typesGenOne = self.foePokemon.past_types[0].types
            for type_ in typesGenOne:
                self.foePokemonType.append(type_.type.name)

    def defAlliesType(self):
        for ally in self.allies:
            typeList = []
            if not ally.past_types:
                types = ally.types
                for type_ in types:
                    typeList.append(type_.type.name)
                self.alliesType[ally] = typeList
            else:
                typesGenOne = ally.past_types[0].types
                for type_ in typesGenOne:
                    typeList.append(type_.type.name)
                self.alliesType[ally] = typeList

    def setMovesPower(self, move, pokemonStats, foePokemonStats, pokemonType, foePokemonType):
        moveDamageClass = {}
        movePower = 2 * 100 / 5 + 2
        if len(move.past_values) > 1: movePower *= move.past_values[1].power if move.past_values[1].power else 0
        else: movePower *= move.power if move.power else 0
        moveType = str(move.type)
        if not movePower:
            movePower = 0
            return movePower
        else:
            if self.damageClassLogic(moveType) == 'ph':
                moveDamageClass[move] = 'physical'
                atkPokemon = pokemonStats['attack']
                defFoePokemon = foePokemonStats['defense']
            else:
                moveDamageClass[move] = 'special'
                atkPokemon = pokemonStats['special-defense']
                defFoePokemon = foePokemonStats['special-defense']
        movePower *= atkPokemon / defFoePokemon / 50
        movePower += 2
        if str(move.type) in pokemonType:
            movePower *= 1.5
        for type_ in foePokemonType:
            moveType = moveType.capitalize()
            movePower *= self.typechart(type_, moveType, movePower)
        movePower *= 217 / 255
        return movePower

    def checkMovesDamage(self):
        statusMove = []
        if self.foePokemon.name in pokemonsSet:
            for move in self.foe_moves_availableClass.values():
                movePower = self.setMovesPower(move, self.foePokemonStats, self.pokemonStats, self.foePokemonType, self.pokemonType)
                if self.pokemonHP - movePower <= 0:
                    choice = self.checkSecureChoice()
                    return choice

        for move in self.moves_available:
            moveClass = self.moves_availableClass[move]
            movePower = self.setMovesPower(moveClass, self.pokemonStats, self.foePokemonStats, self.pokemonType, self.foePokemonType)
            if self.foePokemonHP - movePower <= 0:
                return f"move {move}"
            if not movePower:
                statusMove.append(move)
        
        if "hyper-beam" in self.moves_available: 
            self.moves_available.remove("hyper-beam")
            self.moves_availableClass.pop("hyper-beam")
        if "explosion" in self.moves_available: 
            self.moves_available.remove("explosion")
            self.moves_availableClass.pop("explosion")

        if statusMove:
            return f"move {random.choice(statusMove)}"
        else:
            return f"move {random.choice(self.moves_available)}"

    def checkSecureChoice(self):
        securePokemon = self.checkSecureSwitch(False)
        if not securePokemon:
            statusMove = []
            movesByPower = {}
            for move in self.moves_available:
                moveClass = self.moves_availableClass[move]
                movePower = self.setMovesPower(moveClass, self.foePokemonStats, self.pokemonStats, self.foePokemonType, self.pokemonType)
                movesByPower[move] = movePower
                if not movePower:
                    statusMove.append(move)
            movesByPowerOrdered = {move: damage for move, damage in sorted(movesByPower.items(), key=lambda item: item[1], reverse=True)}
            if not list(movesByPowerOrdered)[0]:
                return f'move {random.choice(statusMove)}'
            else:
                return f"move {list(movesByPowerOrdered)[0]}"
        return securePokemon

    def checkSecureSwitch(self, forceSwitch):
        damagesPerAllies = {}
        for ally in self.allies:
            if self.foePokemon.name in pokemonsSet:
                for move in self.foe_moves_availableClass:
                    moveClass = self.foe_moves_availableClass[move]
                    movePower = self.setMovesPower(moveClass, self.foePokemonStats, self.alliesStats[ally], self.foePokemonType, self.alliesType[ally])
                    damagesPerAllies[ally.name] = self.alliesHP[ally.name]
                    if not forceSwitch: damagesPerAllies[ally.name] -= movePower * 2 
                    else: damagesPerAllies[ally.name] -= movePower
                    if damagesPerAllies[ally.name] <= 0: break

        security = {allyKey: damage for allyKey, damage in sorted(damagesPerAllies.items(), key=lambda item: item[1], reverse=True)}

        if security:
            if list(security.values())[0] > 0: return f'switch {list(security)[0]}'
            else: return

    def damageClassLogic(self, typeMove):
        movesSpecial = ['fire', 'grass', 'water', 'ice', 'electric', 'psychic', 'dragon']
        movesPhysical = ['poison', 'normal', 'ground', 'rock', 'fighting', 'bug', 'ghost', 'flying']
        if typeMove in movesSpecial:
            return 'sp'
        elif typeMove in movesPhysical:
            return 'ph'
    
    def checkTypeVantagem(self):
        vantagem = 1
        for type_ in self.foePokemonType:
            typeFoePokemon = type_
            for type_ in self.pokemon:
                typePokemon = type_.type.capitalize()
                vantagem += self.typechart(typePokemon, typeFoePokemon, vantagem)
        if vantagem >= 2:
            return True

    def typechart(self, type_, moveType, damage):
        self.types = {"bug": {
            "damageTaken": {
                "Bug": 0,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 2,
                "Fire": 1,
                "Flying": 1,
                "Ghost": 0,
                "Grass": 2,
                "Ground": 2,
                "Ice": 0,
                "Normal": 0,
                "Poison": 1,
                "Psychic": 0,
                "Rock": 1,
                "Water": 0,
            },
        },
        "dragon": {
            "damageTaken": {
                "Bug": 0,
                "Dragon": 1,
                "Electric": 2,
                "Fighting": 0,
                "Fire": 2,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 2,
                "Ground": 0,
                "Ice": 1,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 0,
                "Water": 2,
            },
        },
        "electric": {
            "damageTaken": {
                "Bug": 0,
                "Dragon": 0,
                "Electric": 2,
                "Fighting": 0,
                "Fire": 0,
                "Flying": 2,
                "Ghost": 0,
                "Grass": 0,
                "Ground": 1,
                "Ice": 0,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 0,
                "Water": 0,
            },
        },
        "fighting": {
            "damageTaken": {
                "Bug": 2,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 0,
                "Fire": 0,
                "Flying": 1,
                "Ghost": 0,
                "Grass": 0,
                "Ground": 0,
                "Ice": 0,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 1,
                "Rock": 2,
                "Water": 0,
            },
        },
        "fire": {
            "damageTaken": {
                "Bug": 2,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 0,
                "Fire": 2,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 2,
                "Ground": 1,
                "Ice": 0,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 1,
                "Water": 1,
            },
        },
        "flying": {
            "damageTaken": {
                "Bug": 2,
                "Dragon": 0,
                "Electric": 1,
                "Fighting": 2,
                "Fire": 0,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 2,
                "Ground": 3,
                "Ice": 1,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 1,
                "Water": 0,
            },
        },
        "ghost": {
            "damageTaken": {
                "Bug": 2,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 3,
                "Fire": 0,
                "Flying": 0,
                "Ghost": 1,
                "Grass": 0,
                "Ground": 0,
                "Ice": 0,
                "Normal": 3,
                "Poison": 2,
                "Psychic": 0,
                "Rock": 0,
                "Water": 0,
            },
        },
        "grass": {
            "damageTaken": {
                "Bug": 1,
                "Dragon": 0,
                "Electric": 2,
                "Fighting": 0,
                "Fire": 1,
                "Flying": 1,
                "Ghost": 0,
                "Grass": 2,
                "Ground": 2,
                "Ice": 1,
                "Normal": 0,
                "Poison": 1,
                "Psychic": 0,
                "Rock": 0,
                "Water": 2,
            },
        },
        "ground": {
            "damageTaken": {
                "sandstorm": 3,
                "Bug": 0,
                "Dragon": 0,
                "Electric": 3,
                "Fighting": 0,
                "Fire": 0,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 1,
                "Ground": 0,
                "Ice": 1,
                "Normal": 0,
                "Poison": 2,
                "Psychic": 0,
                "Rock": 2,
                "Water": 1,
            },
        },
        "ice": {
            "damageTaken": {
                "Bug": 0,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 1,
                "Fire": 1,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 0,
                "Ground": 0,
                "Ice": 2,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 1,
                "Water": 0,
            },
        },
        "normal": {
            "damageTaken": {
                "Bug": 0,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 1,
                "Fire": 0,
                "Flying": 0,
                "Ghost": 3,
                "Grass": 0,
                "Ground": 0,
                "Ice": 0,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 0,
                "Water": 0,
            },
        },
        "poison": {
            "damageTaken": {
                "tox": 3,
                "Bug": 2,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 2,
                "Fire": 0,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 2,
                "Ground": 1,
                "Ice": 0,
                "Normal": 0,
                "Poison": 2,
                "Psychic": 1,
                "Rock": 0,
                "Water": 0,
            },
        },
        "psychic": {
            "damageTaken": {
                "Bug": 1,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 2,
                "Fire": 0,
                "Flying": 0,
                "Ghost": 3,
                "Grass": 0,
                "Ground": 0,
                "Ice": 0,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 2,
                "Rock": 0,
                "Water": 0,
            },
        },
        "rock": {
            "damageTaken": {
                "sandstorm": 3,
                "Bug": 0,
                "Dragon": 0,
                "Electric": 0,
                "Fighting": 1,
                "Fire": 2,
                "Flying": 2,
                "Ghost": 0,
                "Grass": 1,
                "Ground": 1,
                "Ice": 0,
                "Normal": 2,
                "Poison": 2,
                "Psychic": 0,
                "Rock": 0,
                "Water": 1,
            },
        },
       "water": {
            "damageTaken": {
                "Bug": 0,
                "Dragon": 0,
                "Electric": 1,
                "Fighting": 0,
                "Fire": 2,
                "Flying": 0,
                "Ghost": 0,
                "Grass": 1,
                "Ground": 0,
                "Ice": 2,
                "Normal": 0,
                "Poison": 0,
                "Psychic": 0,
                "Rock": 0,
                "Water": 2,
            },
        }
        }
        damageTaken = self.types[type_]['damageTaken'][moveType]
        if damageTaken == 0:
            damage = 1
        elif damageTaken == 1:
            damage = 2
        elif damageTaken == 2:
            damage = 0.5
        elif damageTaken == 3:
            damage = 0
        return damage