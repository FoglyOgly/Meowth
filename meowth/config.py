import json
import gettext
import os


class Config:

    language = None
    config = None
    pokemon_path_source = None
    raid_path_source = None
    pkmn_info = None
    raid_info = None
    team_info = None
    type_list = None
    type_chart = None

    def __init__(self, configpath='config.json'):
        # Load configuration
        with open(configpath, 'r') as fd:
            self.config = json.load(fd)
        # Set up message catalog access
        language_ = self.config['bot-language']
        self.language = gettext.translation(
            'meowth', localedir='locale', languages=[language_])
        self.language.install()
        self.pokemon_path_source = os.path.join(
            'locale', '{0}', 'pkmn.json').format(self.config['pokemon-language'])
        self.raid_path_source = os.path.join('data', 'raid_info.json')
        # Load Pokemon list and raid info
        with open(self.pokemon_path_source, 'r') as fd:
            self.pkmn_info = json.load(fd)
        with open(self.raid_path_source, 'r') as fd:
            self.raid_info = json.load(fd)
        # Load type information
        with open(os.path.join('data', 'type_chart.json'), 'r') as fd:
            self.type_chart = json.load(fd)
        with open(os.path.join('data', 'type_list.json'), 'r') as fd:
            self.type_list = json.load(fd)
        # Load team information
        self.team_info = self.config['team_dict']
        team_path_source = os.path.join('locale', '{0}', 'team.json').format(language_)
        with open(team_path_source, 'r') as fd:
            team_lang_info = json.load(fd)
        for k, v in team_lang_info.items():
            for a, b in v.items():
                self.team_info[k][a] = b

    def get_pokemon_list(self):
        return self.pkmn_info['pokemon_list']

    def get_team_info(self, team):
        return self.team_info[team]

