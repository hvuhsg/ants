from sys import path
from pathlib import Path

path.append(str(Path(__file__).parent))
path.append(str(Path(__file__).parent.parent.parent))

from monitor_node import run

if __name__ == '__main__':
    run()
