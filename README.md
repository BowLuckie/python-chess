# **Python Chess**

over 2000 lines of code

## How To Use

### Playing the Game

To play the latest stable version, go to:
[https://github.com/BowLuckie/python-chess/releases](https://github.com/BowLuckie/python-chess/releases)

Open the most recent release, find the **Assets** section, and download the `.zip` file.
---

## Features

- Standard chess pieces and ruleset  
- Sleek and stylish UI  
- A strong AI to challenge players  
- A custom set of pieces with unique rules

## About the ai

making a proper ai was never my intention, but the infastructure is there and there is some basic logic behind it although right now it not very strong and tends to really like certian openings

## Contributing

I am no longer working on this project so forks are encouraged. if you come across an issue, you can submit a issue report but im unlikely to act on it.

## Building

if wish to build a release out of the latest version, run this command. note that this will produce a non-production ready version and may be filled with bugs or unfinished features

```bash
python -m PyInstaller `
--onedir `
--windowed `
--name PLACE-VER-NAME-HERE `
--hidden-import=pygame.transform `
--collect-data pygame `
--add-data "pieces;pieces" `
--add-data "theme.json;." `
--add-data "chess_ai.py;." `
--icon=pieces/wp.ico `
menu.py 
```
