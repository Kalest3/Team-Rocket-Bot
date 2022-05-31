from typing import final
import pokebase
from pokemon_set import *

class decision():
    def __init__(self, moves_available, foePokemon, pokemon) -> None:
        self.moves_available = moves_available
        self.pokemon = pokemon
        self.foePokemon = foePokemon
        self.foePokemonType = []
        self.types = {}
        self.movesPower = {}
        self.movesDamageClass = {}
        self.pokemonStats = {}
        self.foePokemonStats = {}

    def _decisionByPower(self):
        self.defPokemonStats()
        self.check_moves_available()
        self.sortMovesByPower()
        move = self.decisionByPower()
        return move
    
    def defPokemonStats(self):
        for stat in self.pokemon.stats:
            statBase = stat.base_stat
            finalStat = (statBase + 15) * 2 + 252 / 4 * 100 / 100
            if stat.stat == "hp":
                finalStat += 110
            else:
                finalStat += 5
            self.pokemonStats[stat.stat] = {finalStat}
        for stat in self.foePokemon.stats:
            self.foePokemonStats[stat.stat] = {stat.base_stat}
            statBase = stat.base_stat
            finalStat = (statBase + 15) * 2 + 252 / 4 * 100 / 100
            if stat.stat == "hp":
                finalStat += 110
            else:
                finalStat += 5
            self.foePokemonStats[stat.stat] = {finalStat}

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
                self.foePokemonType.append(str(type_.type))
        else:
            typesGenOne = self.foePokemon.past_types[0].types
            for type_ in typesGenOne:
                self.foePokemonType.append(str(type_.type))
    
    def setMovesPower(self, move, foePokemon, pokemon, pokemonStats, foePokemonStats):
        move = pokebase.move(move)
        moveDamageClass = {}
        movePower = 2 * 100 / 5 + 2
        if len(move.past_values) > 1: movePower *= move.past_values[1].power if move.past_values[1].power else 0
        else: movePower = move.power
        moveType = str(move.type)
        if not movePower:
            movePower = 0
            moveDamageClass[move] = 'status'
            return movePower
        else:
            if self.damageClassLogic(moveType) == 'ph':
                moveDamageClass[move] = 'physical'
                atkPokemon = pokemonStats['attack']
                defFoePokemon = foePokemonStats['defense']
            else:
                moveDamageClass[move] = 'special'
                atkPokemon = pokemonStats['special']
                defFoePokemon = foePokemonStats['special']
        movePower *= (atkPokemon /defFoePokemon) / 50 + 2
        if move.type == pokemon.type:
            movePower *= 1.5
        for type_ in foePokemon.type:
            moveType = moveType.capitalize()
            movePower += self.typechart(type_, moveType, movePower)
        movePower *= 217 / 255
        return movePower

    def checkMovesDamage(self):
        if self.foePokemon in pokemonsSet:
            moves = pokemonsSet[self.foePokemon]
            for move in moves:
                movePower = self.setMovesPower(move, self.pokemon, self.foePokemon, self.foePokemonStats, self.pokemonStats)
                if self.foePokemonStats['hp'] - movePower <= 0:
                    return

        if self.foePokemon in pokemonsSet:
            moves = pokemonsSet[self.foePokemon]
            for move in moves:
                movePower = self.setMovesPower(move, self.pokemon, self.foePokemon, self.foePokemonStats, self.pokemonStats)
                if self.foePokemonStats['hp'] - movePower <= 0:
                    return

    def decisionByPower(self):
        return list(self.movesPower)[0]
    
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
            pass
        elif damageTaken == 1:
            damage *= 2
        elif damageTaken == 2:
            damage /= 2
        elif damageTaken == 3:
            damage = 0
        return damage