import json
import os
import importlib
import mods
from src.modmanager.modmenu import load_all_mods
from typing import List, Union, Tuple

MOD_FILE = "mods.json"

ModItem = Union[str, Tuple[str, str]]

all_mods: List[ModItem] = load_all_mods()
active_mods: List[ModItem] = list(mods.active_mods)  


def load_mod_config():
    global active_mods
    if not os.path.exists(MOD_FILE):
        save_mod_config()

    with open(MOD_FILE, "r") as f:
        data = json.load(f)

    active_mods = data.get("active_mods", [])


def save_mod_config():
    with open(MOD_FILE, "w") as f:
        json.dump({"active_mods": active_mods}, f, indent=4)


def reload_modules():
    global loaded_modules
    loaded_modules = []

    for mod_name in active_mods:
        try:
            module = importlib.import_module(f"src.mod.mods.{mod_name}")
            importlib.reload(module)
            loaded_modules.append(module)
        except Exception as e:
            print(f"Failed to load mod {mod_name}:", e)


def apply_mods(gamestate):
    for mod in loaded_modules:
        if hasattr(mod, "apply"):
            mod.apply(gamestate)