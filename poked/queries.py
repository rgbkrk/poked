# Query for the Pokemon list
pokemon_list_query = """
    query GetPokemon {
      pokemon_v2_pokemon {
        id
        name
        base_experience
        height
        weight
        pokemon_v2_pokemonstats {
          base_stat
          effort
          pokemon_v2_stat {
            name
          }
        }
        pokemon_v2_pokemontypes {
          slot
          pokemon_v2_type {
            name
          }
        }
        pokemon_v2_pokemongameindices {
          pokemon_v2_version {
            name
          }
        }
        pokemon_v2_pokemonspecy {
          base_happiness
          capture_rate
          is_baby
          is_mythical
          is_legendary
          gender_rate
          has_gender_differences
          pokemon_v2_pokemoncolor {
            name
          }
          pokemon_v2_evolutionchain {
            pokemon_v2_pokemonspecies {
              name
            }
          }
          pokemon_v2_pokemonshape {
            name
          }
        }
      }
    }
"""
