import sys
import os
import subprocess
import argparse

#Launcher for Meowthv2

def parse_cli_args():
    parser = argparse.ArgumentParser(description="Meowth Launcher - Pokemon Go Bot for Discord")
    parser.add_argument("--start","-s",help="Starts Meowth",action="store_true")
    parser.add_argument("--announce","-a",help="Announces Update/Reboot Message to all server owners.",action="store_true")
    parser.add_argument("--auto-restart",help="Auto-Restarts Meowth in case of a crash.",action="store_true")
    return parser.parse_args()

def run_meowth(autorestart):
    interpreter = sys.executable
    if interpreter is None:
        raise RuntimeError("Python could not be found")

    if args.announce:
        cmd = (interpreter, "meowth.py", "reboot")
    else:
        cmd = (interpreter, "meowth.py")

    while True:
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
                print("Restarting Meowth\n")
                cmd = (interpreter, "meowth.py")
                continue
            elif code == 27:
                #announce on restart
                print("Restarting Meowth\n")
                cmd = (interpreter, "meowth.py", "reboot")
                continue
            else:
                if not autorestart:
                    break

    print("Meowth has closed. Exit code: {exit_code}".format(exit_code=code))

args = parse_cli_args()

if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)

    if args.start:
        print("Launching Meowth...")
        run_meowth(autorestart=args.auto_restart)
