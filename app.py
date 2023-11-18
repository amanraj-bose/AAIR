import os
import webbrowser
import json, sys, time
from main import run
from util import path_replacer

class Scan(object):
    def __init__(self) -> None:
        super(Scan, self).__init__()
    
    def clean(self, x) -> None:
        if os.path.exists(x):
            W = os.listdir(x)
            if W:
                for i in W:
                    os.remove(path_replacer(os.path.join(x, i)))
                print(f"\033[1;33m[+]\033[1;37m Cleaning Process of \033[1;36m\033[4m{x}\033[0m\033[1;37m has completed")
            else:
                print(f"\033[1;33m[+]\033[1;37m Cleaning Process of \033[1;36m\033[4m{x}\033[0m\033[1;37m has Already completed")
        else:
            raise FileNotFoundError("File not Found !!")
    
    def analyze(self, x:str or os.PathLike) -> None:
        if os.path.exists(x):
            print(f"\033[1;32m[+]\033[1;37m \033[1;36m\033[4m{x}\033[0m\033[1;37m Directory Detected")
        else:
            print(f"\033[1;31m[+]\033[1;37m \033[1;36m\033[4m{x}\033[0m\033[1;37m Directory Not Detected")
            sys.exit(1)
    
    def sprint(self, x:str, sleep:float=.05):
        for i in x + "\n":
            sys.stdout.write(i)
            sys.stdout.flush()
            time.sleep(sleep)

    def _scan(self) -> None:
        self.clean("./upload")
        self.clean("./static/temporal")
        self.clean("./keys")
        self.analyze("./models/detector")
        self.analyze("./models/gender-ethnic")
        self.analyze("./config/setting.json")
        print("\n\033[1;35m[+]\033[1;37m Server is Starting...")
        time.sleep(.3)
        self.sprint("\033[1;35m[+]\033[1;37m Server Has Started...\033[0m")
        with open("./config/setting.json", "r") as f:
            port = json.load(f)["port"]
        webbrowser.open_new(f"http://127.0.0.1:{port}")
        run(False)
        self.sprint("\033[1;35m[+]\033[1;37m Server Has Closed...\033[0m")

if __name__ == '__main__':
    try:
        scan = Scan()
        scan._scan()
    except KeyboardInterrupt:
        sys.exit(0)
