import random
import pokebase
from pokemon_set import *

pokemonsSet = pokemonsSet[0]

class decision():
    def __init__(self, moves_available, foePokemon, pokemon, allies, pokemonHP, foePokemonHP, alliesHP) -> None:
        self.moves_available = moves_available
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

    def _decisionByLogic(self):
        self.defPokemonStats()
        self.check_moves_available()
        choice = self.checkMovesDamage()
        return choice


    def defPokemonStats(self):
        for stat in self.pokemon.stats:
            statBase = stat.base_stat
            finalStat = (statBase + 15) * 2 + 252 / 4 * 100 / 100 + 5
            self.pokemonStats[str(stat.stat)] = finalStat
        for stat in self.foePokemon.stats:
            statBase = stat.base_stat
            finalStat = (statBase + 15) * 2 + 252 / 4 * 100 / 100 + 5
            self.foePokemonStats[str(stat.stat)] = finalStat
        for ally in self.allies:
            stats = {}
            for stat in ally.stats:
                statBase = stat.base_stat
                finalStat = (statBase + 15) * 2 + 252 / 4 * 100 / 100 + 5
                stats[str(stat.stat)] = finalStat
            self.alliesStats[ally] = stats

    def check_moves_available(self):
        for move in self.moves_available:
            move = self.moves_available[0]
            self.moves_available.remove(move)
            if " " in move:
                move = move.replace(" ", "-")
            self.moves_available.append(move)

        if not self.foePokemon.past_types:
            types = self.foePokemon.types
            for type_ in types:
                self.foePokemonType.append(type_.type.name)
        else:
            typesGenOne = self.foePokemon.past_types[0].types
            for type_ in typesGenOne:
                self.foePokemonType.append(type_.type.name)

        if not self.pokemon.past_types:
            types = self.pokemon.types
            for type_ in types:
                self.pokemonType.append(type_.type.name)
        else:
            typesGenOne = self.foePokemon.past_types[0].types
            for type_ in typesGenOne:
                self.foePokemonType.append(type_.type.name)
        
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
        move = pokebase.move(move)
        print(move)
        moveDamageClass = {}
        movePower = 2 * 100 / 5 + 2
        print(movePower)
        if len(move.past_values) > 1: movePower *= move.past_values[1].power if move.past_values[1].power else 0
        else: movePower *= move.power if move.power else 0
        print(movePower, 2)
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
                atkPokemon = pokemonStats['special-attack']
                defFoePokemon = foePokemonStats['special-attack']
        movePower *= atkPokemon / defFoePokemon / 52
        print(movePower, 3)
        if str(move.type) in pokemonType:
            movePower *= 1.5
        for type_ in foePokemonType:
            moveType = moveType.capitalize()
            movePower *= self.typechart(type_, moveType, movePower)
        print(movePower, 4)
        movePower *= 217 / 255
        return movePower

    def checkMovesDamage(self):
        statusMove = []
        if self.foePokemon.name in pokemonsSet:
            moves = pokemonsSet[self.foePokemon.name]
            for move in moves:
                movePower = self.setMovesPower(move, self.foePokemonStats, self.pokemonStats, self.foePokemonType, self.pokemonType)
                if self.pokemonHP - movePower <= 0:
                    choice = self.checkSecurePokemons()
                    return choice

        for move in self.moves_available:
            movePower = self.setMovesPower(move, self.pokemonStats, self.foePokemonStats, self.pokemonType, self.foePokemonType)
            if self.foePokemonHP - movePower <= 0:
                return f"move {move}"
            if not movePower:
                statusMove.append(move)
        
        return f"move {random.choice(statusMove)}"

    def checkSecurePokemons(self):
        damagesPerAllies = {}
        for ally in self.allies:
            if self.foePokemon.name in pokemonsSet:
                moves = pokemonsSet[self.foePokemon.name]
                for move in moves:
                    movePower = self.setMovesPower(move, self.foePokemonStats, self.alliesStats[ally], self.foePokemonType, self.alliesType[ally])
                    damagesPerAllies[ally.name] = self.alliesHP[ally.name] - movePower

        if damagesPerAllies:
            security = {allyKey: damage for allyKey, damage in sorted(damagesPerAllies.items(), key=lambda item: item[1])}
            return f'switch {list(security)[0]}'
        else:
            statusMove = []
            movesByPower = {}
            for move in self.moves_available:
                movePower = self.setMovesPower(move, self.foePokemonStats, self.pokemonStats, self.foePokemonType, self.pokemonType)
                movesByPower[move] = movePower
                if not movePower:
                    statusMove.append(move)
            movesByPowerOrdered = {move: damage for move, damage in sorted(movesByPower.items(), key=lambda item: item[1], reverse=True)}
            if not list(movesByPowerOrdered)[0]:
                return f'move {random.choice(statusMove)}'
            else:
                return f"move {list(movesByPowerOrdered)[0]}"


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
            damage = 2
        elif damageTaken == 3:
            damage = 0
        return damage