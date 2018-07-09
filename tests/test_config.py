import os
import sys
from unittest import TestCase

from meowth.config import Config

os.chdir(os.path.abspath(os.path.pardir))


class TestConfig(TestCase):

    def test_get_team_info(self):
        config = Config()
        print(config.get_team_info("valor")['role'])
        team_msg = _(' or ').join(['**!team {0}**'.format(team['name'])
                               for team in config.team_info.values()])
        print(team_msg)

