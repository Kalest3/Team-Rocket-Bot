import logging
from pokebase import pokemon
from team import *
from showdown.utils import name_to_id

logging.basicConfig(format='%(message)s', level=logging.INFO)

pokemonList = {}

def setPokemonList():
    logging.info("Setting the Pokémon list before connecting into Pokémon Showdown...")
    for pokemonAtt in teamPacked.split("]"):
        pokemonAttributesSplited = pokemonAtt.split("|")
        pokemonName = pokemonAttributesSplited[0]
        pokemonID = pokemonAttributesSplited[1]
        if not pokemonID:
            pokemonID = name_to_id(pokemonName)
        pokemonList[pokemonID] = pokemon(pokemonID)
    logging.info("Done.")
    return pokemonList