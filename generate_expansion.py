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

# ==========================================
# TEXTURE GENERATION FUNCTIONS
# ==========================================

def create_floor_light_textures(color_name, info):
    img_on = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    emissive = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    img_off = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_floor")

    for y in range(128):
        for x in range(128):
            is_outer_border = (x < 12 or x >= 116 or y < 12 or y >= 116)
            is_rib_x = (x >= 12 and x < 116 and ((x - 12) % 26 < 6))
            is_rib_y = (y >= 12 and y < 116 and ((y - 12) % 26 < 6))
            is_iron = is_outer_border or is_rib_x or is_rib_y
            
            if is_iron:
                val = clamp(38 + rnd.uniform(-4, 4))
                if x in (0, 1) or y in (0, 1): val += 28
                elif x in (126, 127) or y in (126, 127): val -= 15
                if is_rib_x and (x - 12) % 26 == 0: val += 15
                if is_rib_y and (y - 12) % 26 == 0: val += 15
                for bx, by in [(6, 6), (121, 6), (6, 121), (121, 121)]:
                    if math.hypot(x - bx, y - by) < 3.5: val = 85
                iron_col = (val, val, val + 2, 255)
                img_on.putpixel((x, y), iron_col)
                img_off.putpixel((x, y), iron_col)
            else:
                d_center = math.hypot(x - 63.5, y - 63.5) / 60.0
                intensity = max(0.0, 1.0 - d_center) ** 1.3
                if intensity > 0.7:
                    c = blend(glow_rgb, core_rgb, (intensity - 0.7) / 0.3)
                else:
                    c = blend(rgb, glow_rgb, intensity / 0.7)
                glass_noise = rnd.uniform(0.94, 1.06)
                fr = clamp(c[0] * glass_noise)
                fg = clamp(c[1] * glass_noise)
                fb = clamp(c[2] * glass_noise)
                img_on.putpixel((x, y), (fr, fg, fb, 255))
                emissive.putpixel((x, y), (fr, fg, fb, 255))
                off_tint = clamp(32 + rnd.uniform(-3, 3))
                img_off.putpixel((x, y), (off_tint, off_tint, off_tint + 3, 255))
                
    return img_on, emissive, img_off

def create_floor_light_side_texture():
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    rnd = random.Random("floor_light_side")
    for y in range(128):
        for x in range(128):
            val = clamp(42 + rnd.uniform(-4, 4))
            if y < 4: val += 30
            elif y > 123: val -= 15
            if x % 32 < 2: val -= 10
            if (y in (10, 11) or y in (116, 117)) and x % 32 == 16: val += 45
            img.putpixel((x, y), (val, val, val + 2, 255))
    return img

def create_chandelier_textures(color_name, info):
    block_img = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    emissive = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_chand")

    for y in range(64):
        for x in range(128):
            v = clamp(44 + rnd.uniform(-4, 4))
            if y % 16 < 2: v += 18
            block_img.putpixel((x, y), (v, v, v + 2, 255))

    for y in range(64, 96):
        for x in range(128):
            wax_v = clamp(215 + rnd.uniform(-8, 8))
            block_img.putpixel((x, y), (wax_v, wax_v - 10, wax_v - 25, 255))

    for y in range(96, 128):
        for x in range(128):
            cx = (x % 32) - 15.5
            cy = (y - 96) - 15.5
            d = math.hypot(cx, cy)
            if d < 12.0:
                intensity = max(0.0, 1.0 - d / 12.0) ** 1.2
                if intensity > 0.65:
                    c = blend(glow_rgb, core_rgb, (intensity - 0.65) / 0.35)
                else:
                    c = blend(rgb, glow_rgb, intensity / 0.65)
                block_img.putpixel((x, y), (c[0], c[1], c[2], 255))
                emissive.putpixel((x, y), (c[0], c[1], c[2], 255))
            else:
                block_img.putpixel((x, y), (0, 0, 0, 0))

    item_img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    for y in range(8, 48):
        for x in (62, 63, 64, 65): item_img.putpixel((x, y), (50, 50, 55, 255))

    for y in range(54, 94):
        for x in range(12, 116):
            dx = (x - 63.5) / 48.0
            dy = (y - 73.5) / 18.0
            d = math.hypot(dx, dy)
            if 0.88 <= d <= 1.12:
                v = clamp(48 + rnd.uniform(-4, 4))
                if dy < -0.2: v += 22
                item_img.putpixel((x, y), (v, v, v + 2, 255))

    candle_positions = [(16, 70), (44, 78), (84, 78), (112, 70)]
    for cx, base_y in candle_positions:
        for y in range(base_y - 2, base_y + 4):
            for x in range(cx - 4, cx + 5): item_img.putpixel((x, y), (55, 55, 60, 255))
        for y in range(base_y - 16, base_y - 2):
            for x in range(cx - 3, cx + 4): item_img.putpixel((x, y), (220, 215, 195, 255))
        for y in range(base_y - 30, base_y - 16):
            for x in range(cx - 6, cx + 7):
                fdx = (x - cx) / 5.0
                fdy = (y - (base_y - 23)) / 7.0
                fd = math.hypot(fdx, fdy)
                if fd < 1.0:
                    f_int = (1.0 - fd) ** 1.2
                    fc = blend(rgb, glow_rgb, f_int)
                    if fd < 0.35: fc = blend(glow_rgb, core_rgb, 1.0 - fd/0.35)
                    item_img.putpixel((x, y), (fc[0], fc[1], fc[2], 255))

    return block_img, emissive, item_img

def create_jack_o_lantern_textures(color_name, info):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    emissive = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_jack")

    for y in range(128):
        for x in range(128):
            rib = math.sin(x * 0.196) * 18.0
            r = clamp(210 + rib + rnd.uniform(-6, 6))
            g = clamp(112 + (rib * 0.7) + rnd.uniform(-5, 5))
            b = clamp(22 + (rib * 0.3) + rnd.uniform(-3, 3))
            if y < 4: r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
            img.putpixel((x, y), (r, g, b, 255))

    def carve_shape(is_inside_fn):
        for y in range(128):
            for x in range(128):
                if is_inside_fn(x, y):
                    glow_val = blend(rgb, glow_rgb, 0.6)
                    if is_inside_fn(x, y + 2) and is_inside_fn(x, y - 2) and is_inside_fn(x + 2, y) and is_inside_fn(x - 2, y):
                        glow_val = blend(glow_rgb, core_rgb, 0.75)
                    fr, fg, fb = glow_val
                    img.putpixel((x, y), (fr, fg, fb, 255))
                    emissive.putpixel((x, y), (fr, fg, fb, 255))

    def left_eye(x, y):
        return (y >= 32 and y <= 56 and abs(x - 38) <= (y - 32) * 0.6)

    def right_eye(x, y):
        return (y >= 32 and y <= 56 and abs(x - 90) <= (y - 32) * 0.6)

    def nose(x, y):
        return (y >= 58 and y <= 70 and abs(x - 64) <= (70 - y) * 0.6)

    def mouth(x, y):
        if y < 76 or y > 104 or x < 24 or x > 104: return False
        curve_bottom = 98 + int(math.sin((x - 24) / 80.0 * math.pi) * 6)
        is_top_tooth = (y <= 88 and ((x >= 40 and x <= 48) or (x >= 80 and x <= 88)))
        is_bottom_tooth = (y >= 88 and (x >= 58 and x <= 70))
        return y <= curve_bottom and not is_top_tooth and not is_bottom_tooth

    carve_shape(lambda x, y: left_eye(x, y) or right_eye(x, y) or nose(x, y) or mouth(x, y))
    return img, emissive

def create_underwater_torch_textures(color_name, info):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    emissive = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_uw_torch")

    for y in range(66, 128):
        for x in range(56, 72):
            nx = (x - 56) / 15.0
            bronze_r = 160 + rnd.uniform(-8, 8)
            bronze_g = 105 + rnd.uniform(-6, 6)
            bronze_b = 60 + rnd.uniform(-4, 4)
            if rnd.random() < 0.12:
                bronze_r, bronze_g, bronze_b = 65, 175, 145
            light = 1.2 - 0.45 * nx
            img.putpixel((x, y), (clamp(bronze_r * light), clamp(bronze_g * light), clamp(bronze_b * light), 255))

    for y in range(62, 66):
        for x in range(56, 72):
            v_r, v_g, v_b = 195, 160, 50
            if y == 62: v_r, v_g, v_b = 225, 190, 80
            img.putpixel((x, y), (v_r, v_g, v_b, 255))

    cx, cy = 63.5, 54.5
    for y in range(48, 62):
        for x in range(56, 72):
            dx = (x - cx) / 7.5
            dy = (y - cy) / 6.5
            d = math.hypot(dx, dy)
            if d <= 1.0:
                intensity = (1.0 - d) ** 1.3
                if d < 0.4:
                    c = blend(glow_rgb, core_rgb, 1.0 - (d / 0.4))
                else:
                    c = blend(rgb, glow_rgb, intensity)
                alpha = 255
                if y == 48 and (x < 58 or x > 69): alpha = 0
                img.putpixel((x, y), (c[0], c[1], c[2], alpha))
                if alpha > 0:
                    emissive.putpixel((x, y), (c[0], c[1], c[2], 255))

    return img, emissive

# ==========================================
# CHANDELIER BLOCK MODEL JSON BUILDER
# ==========================================

def get_chandelier_model_json(color, is_hanging):
    model = {
        "parent": "block/block",
        "textures": {
            "particle": f"justlights:block/{color}_chandelier",
            "texture": f"justlights:block/{color}_chandelier"
        },
        "elements": [
            # 1. Central Rod
            {
                "from": [7, 8 if is_hanging else 0, 7],
                "to": [9, 16 if is_hanging else 8, 9],
                "faces": {
                    "north": {"uv": [0, 0, 2, 8], "texture": "#texture"},
                    "south": {"uv": [0, 0, 2, 8], "texture": "#texture"},
                    "west": {"uv": [0, 0, 2, 8], "texture": "#texture"},
                    "east": {"uv": [0, 0, 2, 8], "texture": "#texture"},
                    "down": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "up": {"uv": [0, 0, 2, 2], "texture": "#texture"}
                }
            },
            # 2. Four Arms
            {
                "from": [7, 5, 2], "to": [9, 7, 7],
                "faces": {
                    "north": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 2, 5], "texture": "#texture"},
                    "up": {"uv": [0, 0, 2, 5], "texture": "#texture"}
                }
            },
            {
                "from": [7, 5, 9], "to": [9, 7, 14],
                "faces": {
                    "north": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 2, 5], "texture": "#texture"},
                    "up": {"uv": [0, 0, 2, 5], "texture": "#texture"}
                }
            },
            {
                "from": [2, 5, 7], "to": [7, 7, 9],
                "faces": {
                    "north": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "up": {"uv": [0, 0, 5, 2], "texture": "#texture"}
                }
            },
            {
                "from": [9, 5, 7], "to": [14, 7, 9],
                "faces": {
                    "north": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 2, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 5, 2], "texture": "#texture"},
                    "up": {"uv": [0, 0, 5, 2], "texture": "#texture"}
                }
            },
            # 3. Candle Cups & Wax
            # North Candle
            {
                "from": [6.5, 6, 1.5], "to": [9.5, 7.5, 4.5],
                "faces": {
                    "north": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 3, 3], "texture": "#texture"},
                    "up": {"uv": [0, 0, 3, 3], "texture": "#texture"}
                }
            },
            {
                "from": [7, 7.5, 2], "to": [9, 10.5, 4],
                "faces": {
                    "north": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "south": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "west": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "east": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "up": {"uv": [0, 8, 2, 10], "texture": "#texture"}
                }
            },
            # South Candle
            {
                "from": [6.5, 6, 11.5], "to": [9.5, 7.5, 14.5],
                "faces": {
                    "north": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 3, 3], "texture": "#texture"},
                    "up": {"uv": [0, 0, 3, 3], "texture": "#texture"}
                }
            },
            {
                "from": [7, 7.5, 12], "to": [9, 10.5, 14],
                "faces": {
                    "north": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "south": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "west": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "east": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "up": {"uv": [0, 8, 2, 10], "texture": "#texture"}
                }
            },
            # West Candle
            {
                "from": [1.5, 6, 6.5], "to": [4.5, 7.5, 9.5],
                "faces": {
                    "north": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 3, 3], "texture": "#texture"},
                    "up": {"uv": [0, 0, 3, 3], "texture": "#texture"}
                }
            },
            {
                "from": [2, 7.5, 7], "to": [4, 10.5, 9],
                "faces": {
                    "north": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "south": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "west": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "east": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "up": {"uv": [0, 8, 2, 10], "texture": "#texture"}
                }
            },
            # East Candle
            {
                "from": [11.5, 6, 6.5], "to": [14.5, 7.5, 9.5],
                "faces": {
                    "north": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "south": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "west": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "east": {"uv": [0, 0, 3, 2], "texture": "#texture"},
                    "down": {"uv": [0, 0, 3, 3], "texture": "#texture"},
                    "up": {"uv": [0, 0, 3, 3], "texture": "#texture"}
                }
            },
            {
                "from": [12, 7.5, 7], "to": [14, 10.5, 9],
                "faces": {
                    "north": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "south": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "west": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "east": {"uv": [0, 8, 2, 11], "texture": "#texture"},
                    "up": {"uv": [0, 8, 2, 10], "texture": "#texture"}
                }
            }
        ]
    }
    return model

# ==========================================
# MAIN EXPANSION GENERATOR
# ==========================================

def generate_expansion():
    print("Generating JustLights Expansion Assets & Data...")

    textures_block = os.path.join(ASSETS_DIR, "textures", "block")
    textures_item = os.path.join(ASSETS_DIR, "textures", "item")
    models_block = os.path.join(ASSETS_DIR, "models", "block")
    models_item = os.path.join(ASSETS_DIR, "models", "item")
    blockstates = os.path.join(ASSETS_DIR, "blockstates")
    loot_blocks = os.path.join(DATA_DIR, "loot_table", "blocks")
    recipes_dir = os.path.join(DATA_DIR, "recipe")
    tags_block_dir = os.path.join(DATA_DIR, "tags", "block")
    tags_item_dir = os.path.join(DATA_DIR, "tags", "item")
    mc_tags_mineable_dir = os.path.join(BASE_DIR, "data", "minecraft", "tags", "block", "mineable")

    ensure_dir(textures_block)
    ensure_dir(textures_item)
    ensure_dir(models_block)
    ensure_dir(models_item)
    ensure_dir(blockstates)
    ensure_dir(loot_blocks)
    ensure_dir(recipes_dir)
    ensure_dir(tags_block_dir)
    ensure_dir(tags_item_dir)
    ensure_dir(mc_tags_mineable_dir)

    # Common side texture for floor lights
    floor_side = create_floor_light_side_texture()
    floor_side.save(os.path.join(textures_block, "floor_light_side.png"))

    floor_items_list = []
    chand_items_list = []
    jack_items_list = []
    uw_items_list = []

    pickaxe_additions = []
    axe_additions = []

    for color, info in COLORS.items():
        print(f"Generating expansion for {color}...")
        dye_item = f"minecraft:{color}_dye"

        # --- 0. Update Lamp Blockstate for AUTO property ---
        write_json(os.path.join(blockstates, f"{color}_lamp.json"), {
            "variants": {
                "auto=false,lit=false": {"model": f"justlights:block/{color}_lamp_off"},
                "auto=false,lit=true":  {"model": f"justlights:block/{color}_lamp_on"},
                "auto=true,lit=false":  {"model": f"justlights:block/{color}_lamp_off"},
                "auto=true,lit=true":   {"model": f"justlights:block/{color}_lamp_on"}
            }
        })

        # --- 1. Floor Lights ---
        fl_on, fl_emiss, fl_off = create_floor_light_textures(color, info)
        fl_on.save(os.path.join(textures_block, f"{color}_floor_light_top.png"))
        fl_emiss.save(os.path.join(textures_block, f"{color}_floor_light_top_e.png"))
        fl_off.save(os.path.join(textures_block, f"{color}_floor_light_top_off.png"))

        write_json(os.path.join(blockstates, f"{color}_floor_light.json"), {
            "variants": {
                "lit=false": {"model": f"justlights:block/{color}_floor_light_off"},
                "lit=true":  {"model": f"justlights:block/{color}_floor_light"}
            }
        })
        write_json(os.path.join(models_block, f"{color}_floor_light.json"), {
            "parent": "minecraft:block/cube_bottom_top",
            "textures": {
                "top": f"justlights:block/{color}_floor_light_top",
                "bottom": "justlights:block/floor_light_side",
                "side": "justlights:block/floor_light_side"
            }
        })
        write_json(os.path.join(models_block, f"{color}_floor_light_off.json"), {
            "parent": "minecraft:block/cube_bottom_top",
            "textures": {
                "top": f"justlights:block/{color}_floor_light_top_off",
                "bottom": "justlights:block/floor_light_side",
                "side": "justlights:block/floor_light_side"
            }
        })
        write_json(os.path.join(models_item, f"{color}_floor_light.json"), {
            "parent": f"justlights:block/{color}_floor_light"
        })
        write_json(os.path.join(loot_blocks, f"{color}_floor_light.json"), {
            "type": "minecraft:block",
            "pools": [{
                "bonus_rolls": 0.0,
                "conditions": [{"condition": "minecraft:survives_explosion"}],
                "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_floor_light"}],
                "rolls": 1.0
            }]
        })
        # Floor light recipes
        write_json(os.path.join(recipes_dir, f"{color}_floor_light_craft.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {"I": {"item": "minecraft:iron_ingot"}, "L": {"item": f"justlights:{color}_lamp"}},
            "pattern": [" I ", "ILI", " I "],
            "result": {"count": 1, "id": f"justlights:{color}_floor_light"}
        })
        write_json(os.path.join(recipes_dir, f"{color}_floor_light_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_floor_lights"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_floor_light"}
        })

        # --- 2. Chandeliers ---
        ch_b, ch_e, ch_icon = create_chandelier_textures(color, info)
        ch_b.save(os.path.join(textures_block, f"{color}_chandelier.png"))
        ch_e.save(os.path.join(textures_block, f"{color}_chandelier_e.png"))
        ch_icon.save(os.path.join(textures_item, f"{color}_chandelier.png"))

        write_json(os.path.join(blockstates, f"{color}_chandelier.json"), {
            "variants": {
                "hanging=false": {"model": f"justlights:block/{color}_chandelier_standing"},
                "hanging=true":  {"model": f"justlights:block/{color}_chandelier_hanging"}
            }
        })
        write_json(os.path.join(models_block, f"{color}_chandelier_hanging.json"), get_chandelier_model_json(color, True))
        write_json(os.path.join(models_block, f"{color}_chandelier_standing.json"), get_chandelier_model_json(color, False))
        write_json(os.path.join(models_item, f"{color}_chandelier.json"), {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"justlights:item/{color}_chandelier"}
        })
        write_json(os.path.join(loot_blocks, f"{color}_chandelier.json"), {
            "type": "minecraft:block",
            "pools": [{
                "bonus_rolls": 0.0,
                "conditions": [{"condition": "minecraft:survives_explosion"}],
                "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_chandelier"}],
                "rolls": 1.0
            }]
        })
        write_json(os.path.join(recipes_dir, f"{color}_chandelier_craft.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {
                "C": {"item": "minecraft:chain"},
                "I": {"item": "minecraft:iron_ingot"},
                "T": {"item": f"justlights:{color}_torch"}
            },
            "pattern": [" T ", "ICI", "TIT"],
            "result": {"count": 1, "id": f"justlights:{color}_chandelier"}
        })
        write_json(os.path.join(recipes_dir, f"{color}_chandelier_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_chandeliers"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_chandelier"}
        })

        # --- 3. Jack o'Lanterns ---
        jk_img, jk_emiss = create_jack_o_lantern_textures(color, info)
        jk_img.save(os.path.join(textures_block, f"{color}_jack_o_lantern.png"))
        jk_emiss.save(os.path.join(textures_block, f"{color}_jack_o_lantern_e.png"))

        write_json(os.path.join(blockstates, f"{color}_jack_o_lantern.json"), {
            "variants": {
                "facing=east":  {"model": f"justlights:block/{color}_jack_o_lantern", "y": 90},
                "facing=north": {"model": f"justlights:block/{color}_jack_o_lantern"},
                "facing=south": {"model": f"justlights:block/{color}_jack_o_lantern", "y": 180},
                "facing=west":  {"model": f"justlights:block/{color}_jack_o_lantern", "y": 270}
            }
        })
        write_json(os.path.join(models_block, f"{color}_jack_o_lantern.json"), {
            "parent": "minecraft:block/orientable",
            "textures": {
                "front": f"justlights:block/{color}_jack_o_lantern",
                "side": "minecraft:block/pumpkin_side",
                "top": "minecraft:block/pumpkin_top"
            }
        })
        write_json(os.path.join(models_item, f"{color}_jack_o_lantern.json"), {
            "parent": f"justlights:block/{color}_jack_o_lantern"
        })
        write_json(os.path.join(loot_blocks, f"{color}_jack_o_lantern.json"), {
            "type": "minecraft:block",
            "pools": [{
                "bonus_rolls": 0.0,
                "conditions": [{"condition": "minecraft:survives_explosion"}],
                "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_jack_o_lantern"}],
                "rolls": 1.0
            }]
        })
        write_json(os.path.join(recipes_dir, f"{color}_jack_o_lantern_craft.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"item": "minecraft:carved_pumpkin"}, {"item": f"justlights:{color}_torch"}],
            "result": {"count": 1, "id": f"justlights:{color}_jack_o_lantern"}
        })
        write_json(os.path.join(recipes_dir, f"{color}_jack_o_lantern_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_jack_o_lanterns"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_jack_o_lantern"}
        })

        # --- 4. Underwater Torches ---
        uw_img, uw_emiss = create_underwater_torch_textures(color, info)
        uw_img.save(os.path.join(textures_block, f"{color}_underwater_torch.png"))
        uw_emiss.save(os.path.join(textures_block, f"{color}_underwater_torch_e.png"))

        write_json(os.path.join(blockstates, f"{color}_underwater_torch.json"), {
            "variants": {"": {"model": f"justlights:block/{color}_underwater_torch"}}
        })
        write_json(os.path.join(blockstates, f"{color}_underwater_wall_torch.json"), {
            "variants": {
                "facing=east":  {"model": f"justlights:block/{color}_underwater_wall_torch"},
                "facing=north": {"model": f"justlights:block/{color}_underwater_wall_torch", "y": 270},
                "facing=south": {"model": f"justlights:block/{color}_underwater_wall_torch", "y": 90},
                "facing=west":  {"model": f"justlights:block/{color}_underwater_wall_torch", "y": 180}
            }
        })
        write_json(os.path.join(models_block, f"{color}_underwater_torch.json"), {
            "parent": "minecraft:block/template_torch",
            "textures": {"torch": f"justlights:block/{color}_underwater_torch"}
        })
        write_json(os.path.join(models_block, f"{color}_underwater_wall_torch.json"), {
            "parent": "minecraft:block/template_torch_wall",
            "textures": {"torch": f"justlights:block/{color}_underwater_torch"}
        })
        write_json(os.path.join(models_item, f"{color}_underwater_torch.json"), {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"justlights:block/{color}_underwater_torch"}
        })
        write_json(os.path.join(loot_blocks, f"{color}_underwater_torch.json"), {
            "type": "minecraft:block",
            "pools": [{
                "bonus_rolls": 0.0,
                "conditions": [{"condition": "minecraft:survives_explosion"}],
                "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_underwater_torch"}],
                "rolls": 1.0
            }]
        })
        write_json(os.path.join(loot_blocks, f"{color}_underwater_wall_torch.json"), {
            "type": "minecraft:block",
            "pools": [{
                "bonus_rolls": 0.0,
                "conditions": [{"condition": "minecraft:survives_explosion"}],
                "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_underwater_torch"}],
                "rolls": 1.0
            }]
        })
        write_json(os.path.join(recipes_dir, f"{color}_underwater_torch_craft.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"item": f"justlights:{color}_torch"}, {"item": "minecraft:prismarine_shard"}],
            "result": {"count": 1, "id": f"justlights:{color}_underwater_torch"}
        })
        write_json(os.path.join(recipes_dir, f"{color}_underwater_torch_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_underwater_torches"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_underwater_torch"}
        })

        floor_items_list.append(f"justlights:{color}_floor_light")
        chand_items_list.append(f"justlights:{color}_chandelier")
        jack_items_list.append(f"justlights:{color}_jack_o_lantern")
        uw_items_list.append(f"justlights:{color}_underwater_torch")

        pickaxe_additions.append(f"justlights:{color}_floor_light")
        pickaxe_additions.append(f"justlights:{color}_chandelier")
        axe_additions.append(f"justlights:{color}_jack_o_lantern")

    # --- Tags ---
    write_json(os.path.join(tags_item_dir, "colored_floor_lights.json"), {"values": floor_items_list})
    write_json(os.path.join(tags_block_dir, "colored_floor_lights.json"), {"values": floor_items_list})
    write_json(os.path.join(tags_item_dir, "colored_chandeliers.json"), {"values": chand_items_list})
    write_json(os.path.join(tags_block_dir, "colored_chandeliers.json"), {"values": chand_items_list})
    write_json(os.path.join(tags_item_dir, "colored_jack_o_lanterns.json"), {"values": jack_items_list})
    write_json(os.path.join(tags_block_dir, "colored_jack_o_lanterns.json"), {"values": jack_items_list})
    write_json(os.path.join(tags_item_dir, "colored_underwater_torches.json"), {"values": uw_items_list})
    
    # Update pickaxe & axe tags
    pickaxe_path = os.path.join(mc_tags_mineable_dir, "pickaxe.json")
    with open(pickaxe_path, "r", encoding="utf-8") as f:
        pick_data = json.load(f)
    pick_data["values"].extend([p for p in pickaxe_additions if p not in pick_data["values"]])
    write_json(pickaxe_path, pick_data)

    axe_path = os.path.join(mc_tags_mineable_dir, "axe.json")
    with open(axe_path, "r", encoding="utf-8") as f:
        axe_data = json.load(f)
    axe_data["values"].extend([a for a in axe_additions if a not in axe_data["values"]])
    write_json(axe_path, axe_data)

    # --- Lang files ---
    en_path = os.path.join(ASSETS_DIR, "lang", "en_us.json")
    de_path = os.path.join(ASSETS_DIR, "lang", "de_de.json")
    with open(en_path, "r", encoding="utf-8") as f: en_data = json.load(f)
    with open(de_path, "r", encoding="utf-8") as f: de_data = json.load(f)

    en_data["message.justlights.auto_on"] = "§e[JustLights] Streetlight Mode: Activated (Turns on at night)"
    en_data["message.justlights.auto_off"] = "§7[JustLights] Streetlight Mode: Deactivated"
    de_data["message.justlights.auto_on"] = "§e[JustLights] Dämmerungs-Automatik: Aktiviert (Geht bei Nacht an)"
    de_data["message.justlights.auto_off"] = "§7[JustLights] Dämmerungs-Automatik: Deaktiviert"

    for color, info in COLORS.items():
        en_data[f"block.justlights.{color}_floor_light"] = f"{info['en']} Floor Grate Light"
        en_data[f"block.justlights.{color}_chandelier"] = f"{info['en']} Chandelier"
        en_data[f"block.justlights.{color}_jack_o_lantern"] = f"{info['en']} Jack o'Lantern"
        en_data[f"block.justlights.{color}_underwater_torch"] = f"{info['en']} Underwater Torch"
        en_data[f"block.justlights.{color}_underwater_wall_torch"] = f"{info['en']} Underwater Wall Torch"

        de_data[f"block.justlights.{color}_floor_light"] = f"{info['de_n']} Bodengitterlicht"
        de_data[f"block.justlights.{color}_chandelier"] = f"{info['de_m']} Kronleuchter"
        de_data[f"block.justlights.{color}_jack_o_lantern"] = f"{info['de_f']} Kürbislaterne"
        de_data[f"block.justlights.{color}_underwater_torch"] = f"{info['de_f']} Tauchfackel"
        de_data[f"block.justlights.{color}_underwater_wall_torch"] = f"{info['de_f']} Unterwasser-Wandfackel"

    write_json(en_path, en_data)
    write_json(de_path, de_data)

    # --- Shader block.properties ---
    props_lines = [
        "# JustLights Shader Mappings for Iris / Complementary / BSL / Euphoria"
    ]
    code_groups = {}
    for color, info in COLORS.items():
        code = info["code"]
        if code not in code_groups: code_groups[code] = []
        code_groups[code].append(color)

    for code in sorted(code_groups.keys()):
        colors_in_code = code_groups[code]
        blocks = []
        for c in colors_in_code:
            blocks.append(f"justlights:{c}_lamp:lit=true")
            blocks.append(f"justlights:{c}_torch")
            blocks.append(f"justlights:{c}_wall_torch")
            blocks.append(f"justlights:{c}_lantern")
            blocks.append(f"justlights:{c}_campfire:lit=true")
            blocks.append(f"justlights:{c}_floor_light:lit=true")
            blocks.append(f"justlights:{c}_chandelier")
            blocks.append(f"justlights:{c}_jack_o_lantern")
            blocks.append(f"justlights:{c}_underwater_torch")
            blocks.append(f"justlights:{c}_underwater_wall_torch")
        props_lines.append(f"block.{code}=" + " ".join(blocks))

    props_lines.append("")
    unlit_lamps = " ".join([f"justlights:{c}_lamp:lit=false" for c in COLORS.keys()])
    unlit_camps = " ".join([f"justlights:{c}_campfire:lit=false" for c in COLORS.keys()])
    unlit_floors = " ".join([f"justlights:{c}_floor_light:lit=false" for c in COLORS.keys()])
    props_lines.append(f"block.10636={unlit_lamps} {unlit_camps} {unlit_floors}")
    props_lines.append("")

    props_text = "\n".join(props_lines)
    p1 = os.path.join(BASE_DIR, "assets", "minecraft", "shaders", "block.properties")
    p2 = os.path.join(BASE_DIR, "shaders", "block.properties")
    with open(p1, "w", encoding="utf-8") as f: f.write(props_text)
    with open(p2, "w", encoding="utf-8") as f: f.write(props_text)

    print("Expansion generation finished successfully!")

if __name__ == "__main__":
    generate_expansion()
