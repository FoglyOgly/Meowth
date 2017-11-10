import subprocess
import pip
from sys import platform

_apt_req_= [
    "tesseract-ocr",
    "tesseract-ocr-eng"
]

apt_cmd = "apt install "

_pip_req_= [
    "discord.py>=0.16.6",
    "pillow>=4.2.1",
    "requests>=2.18.4",
    "pytesseract>=0.1.7",
    "hastebin.py>=0.2",
    "python-dateutil>=2.6.1"
]

def apt_install(packages):
    for package in packages:
        cmd = apt_cmd+package
        subprocess.run(cmd.split())
        print("[+] Package {} Installed".format(str(package)))

def pip_install(packages):
    for package in packages:
        pip.main(['install',package])

if __name__ == '__main__':
    print(str(platform))
    if platform == "linux" or platform == "linux2":
        apt_install(_apt_req_)
    pip_install(_pip_req_)
    if platform == "win32":
        print("\n\nPlease install Tesseract OCR with the installer for Windows by visiting:\nhttps://github.com/tesseract-ocr/tesseract/wiki/Downloads")
    if platform == "darwin":
        print("\n\nPython packages installed. Please ensure Tesseract OCR for OSX is installed manually.")
    print("\nRequirements installation is now complete.")
