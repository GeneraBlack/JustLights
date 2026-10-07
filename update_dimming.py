import os
import json
import math
import random
from PIL import Image, ImageDraw

COLORS = {
    "white":      {"rgb": (255, 255, 255), "glow": (245, 250, 255), "core": (255, 255, 255), "en": "White",      "de_f": "Weiße",      "de_m": "Weißer",      "de_n": "Weißes",      "code": 10900},
    "orange":     {"rgb": (255, 120, 10),  "glow": (255, 140, 20),  "core": (255, 240, 180), "en": "Orange",     "de_f": "Orange",     "de_m": "Oranger",     "de_n": "Oranges",     "code": 10904},
    "magenta":    {"rgb": (230, 45, 200),  "glow": (245, 60, 220),  "core": (255, 210, 250), "en": "Magenta",    "de_f": "Magenta",    "de_m": "Magenta",     "de_n": "Magenta",     "code": 10920},
    "light_blue": {"rgb": (60, 190, 255),  "glow": (90, 210, 255),  "core": (220, 245, 255), "en": "Light Blue", "de_f": "Hellblaue", "de_m": "Hellblauer", "de_n": "Hellblaues", "code": 10914},
    "yellow":     {"rgb": (255, 225, 25),  "glow": (255, 235, 50),  "core": (255, 255, 210), "en": "Yellow",     "de_f": "Gelbe",      "de_m": "Gelber",      "de_n": "Gelbes",      "code": 10906},
    "lime":       {"rgb": (120, 255, 25),  "glow": (145, 255, 45),  "core": (235, 255, 200), "en": "Lime",       "de_f": "Hellgrüne",  "de_m": "Hellgrüner",  "de_n": "Hellgrünes",  "code": 10908},
    "pink":       {"rgb": (255, 115, 180), "glow": (255, 145, 200), "core": (255, 235, 245), "en": "Pink",       "de_f": "Rosa",       "de_m": "Rosa",        "de_n": "Rosa",        "code": 10922},
    "gray":       {"rgb": (130, 140, 160), "glow": (160, 175, 195), "core": (230, 235, 245), "en": "Gray",       "de_f": "Graue",      "de_m": "Grauer",      "de_n": "Graues",      "code": 10900},
    "light_gray": {"rgb": (205, 215, 225), "glow": (225, 235, 245), "core": (255, 255, 255), "en": "Light Gray", "de_f": "Hellgraue", "de_m": "Hellgrauer", "de_n": "Hellgraues", "code": 10900},
    "cyan":       {"rgb": (15, 235, 215),  "glow": (40, 250, 235),  "core": (210, 255, 250), "en": "Cyan",       "de_f": "Türkise",    "de_m": "Türkiser",    "de_n": "Türkises",    "code": 10912},
    "purple":     {"rgb": (155, 40, 245),  "glow": (180, 60, 255),  "core": (240, 200, 255), "en": "Purple",     "de_f": "Violette",   "de_m": "Violetter",   "de_n": "Violettes",   "code": 10918},
    "blue":       {"rgb": (30, 85, 255),   "glow": (55, 120, 255),  "core": (210, 225, 255), "en": "Blue",       "de_f": "Blaue",      "de_m": "Blauer",      "de_n": "Blaues",      "code": 10916},
    "brown":      {"rgb": (175, 95, 35),   "glow": (205, 125, 55),  "core": (255, 220, 180), "en": "Brown",      "de_f": "Braune",     "de_m": "Brauner",     "de_n": "Braunes",     "code": 10900},
    "green":      {"rgb": (25, 210, 45),   "glow": (45, 240, 75),   "core": (210, 255, 215), "en": "Green",      "de_f": "Grüne",      "de_m": "Grüner",      "de_n": "Grünes",      "code": 10910},
    "red":        {"rgb": (255, 30, 30),   "glow": (255, 60, 50),   "core": (255, 215, 205), "en": "Red",        "de_f": "Rote",       "de_m": "Roter",       "de_n": "Rotes",       "code": 10902},
    "black":      {"rgb": (85, 60, 110),   "glow": (115, 85, 145),  "core": (205, 195, 225), "en": "Black",      "de_f": "Schwarze",   "de_m": "Schwarzer",   "de_n": "Schwarzes",   "code": 10900},
}

BASE_DIR = r"D:\projekt\JustLights\src\main\resources"
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "justlights")
DATA_DIR = os.path.join(BASE_DIR, "data", "justlights")

def clamp(val, low=0, high=255):
    return max(low, min(high, int(val)))

def blend(c1, c2, factor):
    return tuple(clamp(c1[i] * (1 - factor) + c2[i] * factor) for i in range(len(c1)))

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_dimming_and_blockstates():
    print("Updating blockstates with Dimmable Brightness...")
    blockstates = os.path.join(ASSETS_DIR, "blockstates")

    for color in COLORS.keys():
        # 1. Lamp Blockstate with AUTO and BRIGHTNESS (1, 2, 3)
        lamp_variants = {}
        for auto in ["false", "true"]:
            for b in [1, 2, 3]:
                for lit in ["false", "true"]:
                    key = f"auto={auto},brightness={b},lit={lit}"
                    model = f"justlights:block/{color}_lamp_on" if lit == "true" else f"justlights:block/{color}_lamp_off"
                    lamp_variants[key] = {"model": model}
        write_json(os.path.join(blockstates, f"{color}_lamp.json"), {"variants": lamp_variants})

        # Also ensure {color}_lamp.json exists in models/block as an alias to {color}_lamp_on.json
        models_block = os.path.join(ASSETS_DIR, "models", "block")
        lamp_alias = {
            "parent": "minecraft:block/cube_all",
            "textures": {
                "all": f"justlights:block/{color}_lamp_on"
            }
        }
        write_json(os.path.join(models_block, f"{color}_lamp.json"), lamp_alias)

        # 2. Floor Light Blockstate with BRIGHTNESS (1, 2, 3)
        fl_variants = {}
        for b in [1, 2, 3]:
            for lit in ["false", "true"]:
                key = f"brightness={b},lit={lit}"
                model = f"justlights:block/{color}_floor_light" if lit == "true" else f"justlights:block/{color}_floor_light_off"
                fl_variants[key] = {"model": model}
        write_json(os.path.join(blockstates, f"{color}_floor_light.json"), {"variants": fl_variants})

    # Update Lang Files with Dimmable Brightness Messages
    en_path = os.path.join(ASSETS_DIR, "lang", "en_us.json")
    de_path = os.path.join(ASSETS_DIR, "lang", "de_de.json")
    with open(en_path, "r", encoding="utf-8") as f: en_data = json.load(f)
    with open(de_path, "r", encoding="utf-8") as f: de_data = json.load(f)

    en_data["message.justlights.brightness_3"] = "§a[JustLights] Brightness: 100% (Light 15 - Maximum)"
    en_data["message.justlights.brightness_2"] = "§e[JustLights] Brightness: 66% (Light 10 - Cozy)"
    en_data["message.justlights.brightness_1"] = "§6[JustLights] Brightness: 33% (Light 5 - Ambient)"
    en_data["message.justlights.auto_on"] = "§b[JustLights] Mode: Streetlight Auto (Turns on at night)"
    en_data["message.justlights.auto_off"] = "§7[JustLights] Mode: Manual (Streetlight Deactivated)"

    de_data["message.justlights.brightness_3"] = "§a[JustLights] Helligkeit: 100% (Licht 15 - Hell)"
    de_data["message.justlights.brightness_2"] = "§e[JustLights] Helligkeit: 66% (Licht 10 - Gemütlich)"
    de_data["message.justlights.brightness_1"] = "§6[JustLights] Helligkeit: 33% (Licht 5 - Dämmerlicht)"
    de_data["message.justlights.auto_on"] = "§b[JustLights] Modus: Dämmerungs-Automatik (Nacht an / Tag aus)"
    de_data["message.justlights.auto_off"] = "§7[JustLights] Modus: Manuell (Dämmerungs-Automatik deaktiviert)"

    write_json(en_path, en_data)
    write_json(de_path, de_data)
    print("Blockstates and language files updated successfully!")

if __name__ == "__main__":
    generate_dimming_and_blockstates()
