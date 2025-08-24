BLACK = '\033[0;30m'
DARK_GRAY = '\033[1;30m'
RED = '\033[0;31m'
LIGHT_RED = '\033[1;31m'
GREEN = '\033[0;32m'
LIGHT_GREEN = '\033[1;32m'
BROWN_ORANGE = '\033[0;33m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
LIGHT_BLUE = '\033[1;34m'
PURPLE = '\033[0;35m'
LIGHT_PURPLE = '\033[1;35m'
CYAN = '\033[0;36m'
LIGHT_CYAN = '\033[1;36m'
LIGHT_GRAY = '\033[0;37m'
WHITE = '\033[1;37m'
PINK = '\033[1;95m'


NC = '\033[0m'  # No Color

# это финт для цвета в windows
import os
from sys import platform
if platform not in ("linux", "linux2"):
    os.system("cls")
    #  print(f"I {PINK}love{NC} Stack Overflow\n")

"""
чтобы линтер не ругался, не использовать wildcard а импортровать через, например as dc
и обращаться как к dc.dark_gray

black = '\033[0;30m'
dark_gray = '\033[1;30m'
red = '\033[0;31m'
light_red = '\033[1;31m'
green = '\033[0;32m'
light_green = '\033[1;32m'
brown_orange = '\033[0;33m'
yellow = '\033[1;33m'
blue = '\033[0;34m'
light_blue = '\033[1;34m'
purple = '\033[0;35m'
light_purple = '\033[1;35m'
cyan = '\033[0;36m'
light_cyan = '\033[1;36m'
light_gray = '\033[0;37m'
white = '\033[1;37m'
pink = '\033[1;95m'
"""


NC = '\033[0m'  # No Color
