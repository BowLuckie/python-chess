# **Python Chess**

## How To Use

### Playing the Game

To play the latest stable version, go to:
[https://github.com/BowLuckie/python-chess/releases](https://github.com/BowLuckie/python-chess/releases)

Open the most recent release, find the **Assets** section, and download the `.zip` file.

### Viewing the Code

You can browse the source directly on GitHub, or download it locally:

[https://github.com/BowLuckie/python-chess/releases](https://github.com/BowLuckie/python-chess/releases)

In the latest release, download the **source code** from the **Assets** section to open it in your own editor.

### Running the `.py` Files (NOT RECOMMENDED)

Running the project from source is not recommended due to current compatibility issues between Python and Pygame.

If you still want to run it manually:

1. Uninstall any Python version above **3.12.x**
2. Install **Python 3.12.x** (if not already installed)
3. Install required dependencies:

```bash
pip install pygame
pip install pygame_gui
```

If `pip` is not installed, download it from:
[https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)

---

## Features
- Standard chess pieces and ruleset  
- Sleek and stylish UI  
- A strong AI to challenge players  
- A custom set of pieces with unique rules  

## Contributing
This is currently a solo project. You are welcome to fork the repository, but pull requests are not being accepted at this time.  
If you have suggestions or want to contribute, please open an issue.

## Building

if wish to build a release out of the latest version, run this command. note that this will produce a non-production ready version and may be filled with bugs or unfinished features

```bash
python -m PyInstaller --onedir --windowed --name PLACE-VERSION-NAME-HERE --hidden-import=pygame.transform --collect-data pygame --add-data "pieces;pieces" --add-data "theme.json;." menu.py
```
