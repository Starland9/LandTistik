import subprocess
from pathlib import Path

if __name__ == '__main__':
    for file in Path("../src/ui").glob("*.ui"):
        print("Parsing", file)
        subprocess.run(["pyuic6", "-x", str(file), "-o", f"../src/ui/{file.stem}.py"])

