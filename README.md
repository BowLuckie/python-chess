# python chess

## to play the game

go to the release tab on the side and download the latest release (click chess.exe)

![download](https://github.com/BowLuckie/python-chess/blob/54da43c715b9a6074dbedbb864e11ae1854cf54c/pieces/instructions/release%20instructions.png)

## to see the code

you can view my code directly from this website or you can download the .zip of the source from the releases or main page.
be warned that in order to run the game directly from chess.py, you must have pygame installed which may not work on your version of python.
it is recomended to use the .exe instead as you dont need any prerequisites

![release](https://github.com/BowLuckie/python-chess/blob/26cc457a3bdb3e745e1cea0f2be9b5b8d86ffba7/pieces/instructions/code_download_instructions.png)

## Building

```bash
python -m PyInstaller --onedir --windowed --name PLACE-VERSION-NAME-HERE --hidden-import=pygame.transform --collect-data pygame --add-data "pieces;pieces" --add-data "theme.json;." menu.py
```

## DLC coming soon

![poster](https://github.com/BowLuckie/python-chess/blob/a12e1c7284e39ad0a05c93da125628749568be96/pieces/instructions/sinister%20edition%20promotion%20poster.png)
