import platform
import zipfile
import subprocess, urllib.request
import os


class Setup(object):
    def __init__(self) -> None:
        super(Setup, self).__init__()
        
    def system(self):
        OS = platform.system().lower()
        PLATFORM = platform.processor()
        NAME = platform.uname()
        VERSION = platform.python_version()

        return {"os": OS, "platform": PLATFORM, "name": NAME, "version": VERSION}
    
    def creator(self):
        dirs = {"./upload", "./static/temporal", "./keys"}
        for i in dirs: 
            if not os.path.exists(i):
                os.makedirs(i, exist_ok=True)
                return f"\033[1;32m[+]\033[1;37m Folder \033[1;36m\033[4m{i}\033[0m\033[1;37m created !!"
    
    def unzip(self, x:os.PathLike):
        with zipfile.ZipFile(x, "r") as f:
            f.extractall()

        return f"\033[1;34m[+]\033[1;37m Extracted \033[1;36m\033[4m{x}\033[0m\033[1;37m Zip File"

    def _analyze(self):
        x = os.path.abspath(os.path.dirname(__file__))
        for i in os.listdir(x):
            if zipfile.is_zipfile(i):
                file = str(i).split("-")[0]
                if file == "models":
                    self.unzip(os.path.join(x, i))
                    return True
            else:
                return False
            
    def is_internet(self):
        try:
            urllib.request.urlopen("https://google.com/")
            return True
        except Exception: return False

    def style(self, x, y, color="yellow", sep="+") -> None:
        dicts = {"green": "\033[1;32m", "red": "\033[1;31m", "yellow": "\033[1;33m", "cyan": "\033[1;36m", "white": "\033[1;37m"}
        print(f"{dicts[color]}[{sep}]{dicts['white']} {x} => \033[4m{dicts['cyan']}{y}\033[0m")

    def setup(self):
        system = self.system()
        creator = self.creator()
        self.style("Name of the OS", system["name"])
        self.style("Type os OS", system["os"])
        self.style("Type of Platform", system["platform"])
        self.style("Version of Installed python", system["version"])
        self.style("Creating Directories", "")
        print(creator)
        self.style("Directories has done", "", "green", "#")            
        self.style("Installing Python Packages", "")
        x = ""
        if system["os"] == "linux":
                x = "3"

        if self.is_internet():
            status = subprocess.getstatusoutput(f"pip{x} install -r requirements.txt")
            self.style("Python Packages has Installed", str(bool(status[0])), "green", "#")
        else:
            self.style("Python Packages hasnot Installed due to your Internet Connection", "", "red", "-")
        analyze = self._analyze()
        if analyze:
            self.style("Models Zip file Unzipped", "Installation is successful", "green", "#")
            self.style("Run this Command to start the server", f"python{x} app.py")
        else:
            self.style("Models Zip file hasn't Unzipped", "Try Again !!", "red", "-")

if __name__ == '__main__':
    setup = Setup()
    setup.setup()
