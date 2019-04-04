"""Meowth Bot Module.

By using this command instead of ``meowth``, the bot will bypass the
launcher.

Command:
    ``meowth-bot``

Options:
    -d, --debug   Enable debug mode.
"""

import argparse
import asyncio
import sys
import os
from multiprocessing import Pool
from functools import partial

import discord

from meowth.core import Bot, logger, context
from meowth.utils import ExitCodes

if discord.version_info.major < 1:
    print("You are not running discord.py v1.0.0a or above.\n\n"
          "Meowth v3 requires the new discord.py library to function "
          "correctly. Please install the correct version.")
    sys.exit(1)

def run_bot(debug=False, launcher=None, from_restart=False, shard_count=1, shard_id=0):
    """Sets up the bot, runs it and handles exit codes."""

    # create async loop and setup contextvar
    loop = asyncio.get_event_loop()
    context.ctx_setup(loop)
    print(5)

    # create bot instance
    description = "Meowth v3 - Beta"
    bot = Bot(
        description=description, launcher=launcher,
        debug=debug, from_restart=from_restart,
        shard_count=shard_count, shard_id=shard_id)

    print(6)
    # setup logging
    bot.logger = logger.init_logger(bot, debug)

    # load the required core modules
    bot.load_extension('meowth.core.error_handling')
    bot.load_extension('meowth.core.commands')
    bot.load_extension('meowth.core.cog_manager')

    print(7)
    # load extensions marked for preload in config
    for ext in bot.preload_ext:
        ext_name = ("meowth.exts."+ext)
        bot.load_extension(ext_name)

    print(8)
    if bot.token is None or not bot.default_prefix:
        bot.logger.critical(
            "Token and prefix must be set in order to login.")
        sys.exit(1)
    try:
        loop.run_until_complete(bot.start(bot.token))
    except discord.LoginFailure:
        bot.logger.critical("Invalid token")
        loop.run_until_complete(bot.logout())
        bot.shutdown_mode = ExitCodes.SHUTDOWN
    except KeyboardInterrupt:
        bot.logger.info("Keyboard interrupt detected. Quitting...")
        loop.run_until_complete(bot.logout())
        bot.shutdown_mode = ExitCodes.SHUTDOWN
    except Exception as exc:
        bot.logger.critical("Fatal exception", exc_info=exc)
        loop.run_until_complete(bot.logout())
    finally:
        code = bot.shutdown_mode
        sys.exit(code.value)

def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Meowth - Discord Bot for Pokemon Go Communities")
    parser.add_argument(
        "--debug", "-d", help="Enabled debug mode.", action="store_true")
    parser.add_argument(
        "--launcher", "-l", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument(
        "--fromrestart", help=argparse.SUPPRESS, action="store_true")
    return parser.parse_args()

def main():
    print(0)
    cores = os.cpu_count()
    args = parse_cli_args()
    print(1)
    func = partial(run_bot, debug=args.debug, launcher=args.launcher, 
        from_restart=args.fromrestart, shard_count=cores)
    print(2)
    p = Pool(cores)
    print(3)
    r = p.imap_unordered(func, shard_id=range(cores))
    for i in r:
        print(i)
    print(4)

if __name__ == '__main__':
    main()
