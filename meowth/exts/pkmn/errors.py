from discord.ext.commands import CommandError

class PokemonNotFound(CommandError):
    'Exception raised, Pokemon not found'
    pass

class PokemonInvalidContext(CommandError):
    'Exception raised, Pokemon invalid in context'
    pass

class MoveNotFound(CommandError):
    'Exception raised, move not found'
    pass

class MoveInvalid(CommandError):
    'Exception raised, move not learned by Pokemon'
    pass



