#!/usr/bin/python3

import sys
import os
import subprocess
import argparse
import time
import logging
import socket


lock_socket = None  # we want to keep the socket open until the very end of
                    # our script so we use a global variable to avoid going
                    # out of scope and being garbage-collected

def is_lock_free():
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_id = "meowth2_0-prod"   # this should be unique. using your username as a prefix is a convention
        lock_socket.bind('\0' + lock_id)
        logging.info("Acquired lock %r" % (lock_id,))
        print("Acquired lock %r" % (lock_id,))
        return True
    except socket.error:
        # socket already locked, task must already be running
        logging.info("Failed to acquire lock %r" % (lock_id,))
        print("Failed to acquire lock %r" % (lock_id,))
        return False

if not is_lock_free():
    sys.exit()

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
                    time.sleep(1)

    print("Meowth has closed. Exit code: {exit_code}".format(exit_code=code))

args = parse_cli_args()

if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    print("Launching Meowth...")
    run_meowth(autorestart=args.auto_restart)
