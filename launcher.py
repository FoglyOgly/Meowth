#!/usr/bin/python3

import sys
import os
import time
import subprocess
import argparse

#Launcher for Meowthv2

def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Meowth Launcher - Pokemon Go Bot for Discord")
    parser.add_argument(
        "--auto-restart", "-r",
        help="Auto-Restarts Meowth in case of a crash.", action="store_true")
    parser.add_argument(
        "--debug", "-d",
        help=("Prevents output being sent to Discord DM, "
              "as restarting could occur often."),
        action="store_true")
    return parser.parse_args()

def run_meowth(autorestart):
    interpreter = sys.executable
    if interpreter is None:
        raise RuntimeError("Python could not be found")

    cmd = [interpreter, "-m", "meowth", "launcher"]

    retries = 0

    while True:
        if args.debug:
            cmd.append("debug")
        try:
            code = subprocess.call(cmd)
        except KeyboardInterrupt:
            code = 0
            break
        else:
            if code == 0:
                break
            elif code == 26:
                #standard restart
                retries = 0
                print("")
                print("Restarting Meowth")
                print("")
                continue
            else:
                if not autorestart:
                    break
                retries += 1
                wait_time = min([retries^2, 60])
                print("")
                print("Meowth experienced a crash.")
                print("")
                for i in range(wait_time, 0, -1):
                    sys.stdout.write("\r")
                    sys.stdout.write(
                        "Restarting Meowth from crash in {:0d}".format(i))
                    sys.stdout.flush()
                    time.sleep()

    print("Meowth has closed. Exit code: {exit_code}".format(exit_code=code))

args = parse_cli_args()

if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    print("Launching Meowth...")
    run_meowth(autorestart=args.auto_restart)
