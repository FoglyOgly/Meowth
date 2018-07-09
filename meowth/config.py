import errno
import json
import gettext
import os
import pickle
import tempfile


class Config:

    language = None
    config = None
    pokemon_path_source = None
    pkmn_info = None
    raid_info = None
    team_info = None
    type_list = None
    type_chart = None

    def __init__(self):
        self.reload()

    def reload(self):
        # Load configuration
        with open('config/config.json', 'r') as fd:
            self.config = json.load(fd)

        # Set up message catalog access
        language_ = self.config['bot-language']
        self.language = gettext.translation(
            'meowth', localedir='locale', languages=[language_])
        self.language.install()
        self.pokemon_path_source = os.path.join(
            'locale', '{0}', 'pkmn.json').format(self.config['pokemon-language'])

        # Load Pokemon list and raid info
        with open(self.pokemon_path_source, 'r') as fd:
            self.pkmn_info = json.load(fd)

        self.__load_raid_info()

        self.__load_type_info()

        self.__load_team_info(language_)

    def __load_type_info(self):
        # Load type information
        with open(os.path.join('data', 'type_chart.json'), 'r') as fd:
            self.type_chart = json.load(fd)
        with open(os.path.join('data', 'type_list.json'), 'r') as fd:
            self.type_list = json.load(fd)

    def __load_team_info(self, language_):
        # Load team information
        self.team_info = self.config['team_dict']
        team_path_source = os.path.join('locale', '{0}', 'team.json').format(language_)
        with open(team_path_source, 'r') as fd:
            team_lang_info = json.load(fd)
        for k, v in team_lang_info.items():
            for a, b in v.items():
                self.team_info[k][a] = b
        # set default roles
        for team in self.team_info.values():
            if not 'role' in team:
                team['role'] = team['name']

    def __load_raid_info(self):
        # Check first if the server has its own configuration for raid source
        raid_path_source = os.path.join('config', 'raid_info.json')
        if not os.path.isfile(raid_path_source):
            raid_path_source = os.path.join('data', 'raid_info.json')
        with open(raid_path_source, 'r') as fd:
            self.raid_info = json.load(fd)

    def get_pokemon_list(self):
        return self.pkmn_info['pokemon_list']

    def get_team_info(self, team):
        return self.team_info[team]

    def get_raid_info(self):
        return self.raid_info

    def save_raidegg_info(self, level, intlist):
        self.__load_raid_info()
        self.raid_info['raid_eggs'][level]['pokemon'] = intlist
        with open(os.path.join('config', 'raid_info.json'), 'w') as fd:
            json.dump(self.raid_info, fd, indent=2, separators=(', ', ': '))
        self.__load_raid_info()

    @staticmethod
    def save_serverdict(guild_dict):
        with tempfile.NamedTemporaryFile('wb', dir=os.path.dirname(os.path.join('config', 'serverdict')), delete=False) as tf:
            pickle.dump(guild_dict, tf, (- 1))
            tempname = tf.name
        try:
            os.remove(os.path.join('config', 'serverdict_backup'))
        except OSError as e:
            pass
        try:
            os.rename(os.path.join('config', 'serverdict'), os.path.join('config', 'serverdict_backup'))
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
        os.rename(tempname, os.path.join('config', 'serverdict'))