import os
import json
import math
import random
from PIL import Image, ImageDraw

COLORS = {
    "white":      {"rgb": (255, 255, 255), "glow": (245, 250, 255), "core": (255, 255, 255), "en": "White",      "de": "Weiße",      "code": 10900},
    "orange":     {"rgb": (255, 120, 10),  "glow": (255, 140, 20),  "core": (255, 240, 180), "en": "Orange",     "de": "Orange",     "code": 10904},
    "magenta":    {"rgb": (230, 45, 200),  "glow": (245, 60, 220),  "core": (255, 210, 250), "en": "Magenta",    "de": "Magenta",    "code": 10920},
    "light_blue": {"rgb": (60, 190, 255),  "glow": (90, 210, 255),  "core": (220, 245, 255), "en": "Light Blue", "de": "Hellblaue", "code": 10914},
    "yellow":     {"rgb": (255, 225, 25),  "glow": (255, 235, 50),  "core": (255, 255, 210), "en": "Yellow",     "de": "Gelbe",      "code": 10906},
    "lime":       {"rgb": (120, 255, 25),  "glow": (145, 255, 45),  "core": (235, 255, 200), "en": "Lime",       "de": "Hellgrüne",  "code": 10908},
    "pink":       {"rgb": (255, 115, 180), "glow": (255, 145, 200), "core": (255, 235, 245), "en": "Pink",       "de": "Rosa",       "code": 10922},
    "gray":       {"rgb": (130, 140, 160), "glow": (160, 175, 195), "core": (230, 235, 245), "en": "Gray",       "de": "Graue",      "code": 10900},
    "light_gray": {"rgb": (205, 215, 225), "glow": (225, 235, 245), "core": (255, 255, 255), "en": "Light Gray", "de": "Hellgraue", "code": 10900},
    "cyan":       {"rgb": (15, 235, 215),  "glow": (40, 250, 235),  "core": (210, 255, 250), "en": "Cyan",       "de": "Türkise",    "code": 10912},
    "purple":     {"rgb": (155, 40, 245),  "glow": (180, 60, 255),  "core": (240, 200, 255), "en": "Purple",     "de": "Violette",   "code": 10918},
    "blue":       {"rgb": (30, 85, 255),   "glow": (55, 120, 255),  "core": (210, 225, 255), "en": "Blue",       "de": "Blaue",      "code": 10916},
    "brown":      {"rgb": (175, 95, 35),   "glow": (205, 125, 55),  "core": (255, 220, 180), "en": "Brown",      "de": "Braune",     "code": 10900},
    "green":      {"rgb": (25, 210, 45),   "glow": (45, 240, 75),   "core": (210, 255, 215), "en": "Green",      "de": "Grüne",      "code": 10910},
    "red":        {"rgb": (255, 30, 30),   "glow": (255, 60, 50),   "core": (255, 215, 205), "en": "Red",        "de": "Rote",       "code": 10902},
    "black":      {"rgb": (85, 60, 110),   "glow": (115, 85, 145),  "core": (205, 195, 225), "en": "Black",      "de": "Schwarze",   "code": 10900},
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

# ==========================================
# 1. TEXTURE GENERATORS (128x128 HD)
# ==========================================

def create_torch_textures(color_name, info):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    emissive = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    
    rnd = random.Random(color_name + "_torch")
    
    # 1. Rustic Wood Stick (y: 66..127, x: 56..71)
    for y in range(66, 128):
        grain = rnd.uniform(-10, 10)
        for x in range(56, 72):
            nx = (x - 56) / 15.0
            light_factor = 1.15 - 0.45 * nx + rnd.uniform(-0.05, 0.05)
            fiber = math.sin((x * 3.7) + rnd.uniform(0, 0.5)) * 8
            
            base_r = 115 + grain + fiber
            base_g = 82 + (grain * 0.7) + (fiber * 0.7)
            base_b = 48 + (grain * 0.4) + (fiber * 0.4)
            
            r = clamp(base_r * light_factor)
            g = clamp(base_g * light_factor)
            b = clamp(base_b * light_factor)
            img.putpixel((x, y), (r, g, b, 255))
            
    # 2. Forged Iron / Charred Collar (y: 62..65, x: 56..71)
    for y in range(62, 66):
        for x in range(56, 72):
            iron_base = 45 + rnd.uniform(-4, 4)
            if y == 62: iron_base += 25
            elif y == 65: iron_base -= 15
            if x in (63, 64) and y in (63, 64):
                iron_base += 50
            iron_val = clamp(iron_base)
            img.putpixel((x, y), (iron_val, iron_val, iron_val + 4, 255))

    # 3. Glowing Flame / Ember Tip (y: 48..61, x: 56..71)
    cx, cy = 63.5, 54.5
    for y in range(48, 62):
        for x in range(56, 72):
            dx = (x - cx) / 7.5
            dy = (y - cy) / 6.5
            dist = math.sqrt(dx*dx + dy*dy)
            
            if y >= 59:
                char_r = clamp(55 + rnd.uniform(-10, 10))
                char_g = clamp(40 + rnd.uniform(-8, 8))
                char_b = clamp(35 + rnd.uniform(-6, 6))
                
                glow_amt = max(0.0, 1.0 - dist)
                er = clamp(char_r * (1 - glow_amt) + rgb[0] * glow_amt)
                eg = clamp(char_g * (1 - glow_amt) + rgb[1] * glow_amt)
                eb = clamp(char_b * (1 - glow_amt) + rgb[2] * glow_amt)
                img.putpixel((x, y), (er, eg, eb, 255))
                emissive.putpixel((x, y), (clamp(rgb[0] * glow_amt * 0.8), clamp(rgb[1] * glow_amt * 0.8), clamp(rgb[2] * glow_amt * 0.8), 255))
            else:
                intensity = max(0.0, 1.0 - (dist * 0.8)) ** 1.3
                if dist < 0.45:
                    core_f = 1.0 - (dist / 0.45)
                    color = blend(glow_rgb, core_rgb, core_f)
                else:
                    color = blend(rgb, glow_rgb, intensity)
                
                flicker = rnd.uniform(0.92, 1.08)
                fr = clamp(color[0] * flicker)
                fg = clamp(color[1] * flicker)
                fb = clamp(color[2] * flicker)
                
                alpha = 255
                if y == 48 and (x < 58 or x > 69):
                    alpha = 0
                
                img.putpixel((x, y), (fr, fg, fb, alpha))
                if alpha > 0:
                    emissive.putpixel((x, y), (fr, fg, fb, 255))
                    
    return img, emissive

def create_lantern_textures(color_name, info):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    emissive = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_lantern")

    def get_iron(x, y, bevel_type="none"):
        base = 40 + rnd.uniform(-3, 3)
        if bevel_type == "top": base += 28
        elif bevel_type == "bottom": base -= 16
        elif bevel_type == "left": base += 18
        elif bevel_type == "right": base -= 14
        v = clamp(base)
        return (v, v, v + 3, 255)

    # 1. Cap Side (x: 8..39, y: 0..15)
    for y in range(0, 16):
        for x in range(8, 40):
            b_type = "top" if y <= 1 else ("bottom" if y >= 14 else "none")
            c = get_iron(x, y, b_type)
            if x in (14, 33) and y in (7, 8):
                c = (90, 90, 95, 255)
            img.putpixel((x, y), c)

    # 2. Main Body Side (x: 0..47, y: 16..71)
    cx, cy = 23.5, 43.5
    for y in range(16, 72):
        for x in range(0, 48):
            is_frame = (x < 6 or x >= 42 or y < 22 or y >= 66)
            if is_frame:
                b_type = "none"
                if y in (16, 17) or (x in (0, 1) and y < 66): b_type = "top"
                elif y in (70, 71) or x in (46, 47): b_type = "bottom"
                c = get_iron(x, y, b_type)
                if (x in (3, 4) or x in (43, 44)) and (y in (19, 20) or y in (67, 68)):
                    c = (95, 95, 100, 255)
                img.putpixel((x, y), c)
            else:
                dx = (x - cx) / 17.0
                dy = (y - cy) / 21.0
                dist = math.sqrt(dx*dx + dy*dy)
                
                frosted_noise = rnd.uniform(0.93, 1.07)
                glass_tint = (
                    clamp(rgb[0] * 0.28 * frosted_noise),
                    clamp(rgb[1] * 0.28 * frosted_noise),
                    clamp(rgb[2] * 0.28 * frosted_noise)
                )
                
                diag = (x + y * 0.6) % 18
                if diag < 3:
                    glass_tint = blend(glass_tint, (200, 220, 240), 0.2)
                
                if dist < 1.0:
                    glow_factor = (1.0 - dist) ** 1.4
                    if dist < 0.35:
                        core_f = 1.0 - (dist / 0.35)
                        flame_color = blend(glow_rgb, core_rgb, core_f)
                    else:
                        flame_color = blend(rgb, glow_rgb, glow_factor)
                    final_color = blend(glass_tint, flame_color, glow_factor * 0.95)
                    emiss_intensity = glow_factor
                else:
                    final_color = glass_tint
                    emiss_intensity = 0.05
                    
                img.putpixel((x, y), (final_color[0], final_color[1], final_color[2], 255))
                
                if emiss_intensity > 0.02:
                    er = clamp(rgb[0] * emiss_intensity)
                    eg = clamp(rgb[1] * emiss_intensity)
                    eb = clamp(rgb[2] * emiss_intensity)
                    emissive.putpixel((x, y), (er, eg, eb, 255))

    # 3. Top / Bottom Caps Plate (x: 0..47, y: 72..119)
    for y in range(72, 120):
        for x in range(0, 48):
            edge = (x < 2 or x >= 46 or y < 74 or y >= 118)
            b_type = "top" if edge and (x < 2 or y < 74) else ("bottom" if edge else "none")
            c = get_iron(x, y, b_type)
            if x in (23, 24) or y in (95, 96):
                c = (32, 32, 35, 255)
            if (x in (6, 7, 40, 41)) and (y in (78, 79, 112, 113)):
                c = (95, 95, 100, 255)
            img.putpixel((x, y), c)

    # 4. Ring Handle (x: 88..111, y: 8..31)
    rcx, rcy = 99.5, 19.5
    for y in range(8, 32):
        for x in range(88, 112):
            dx = x - rcx
            dy = y - rcy
            dist = math.sqrt(dx*dx + dy*dy)
            if 4.8 <= dist <= 9.8:
                rim = "top" if dy < -2 else ("bottom" if dy > 2 else "none")
                c = get_iron(x, y, rim)
                img.putpixel((x, y), c)

    # 5. Chain Links (x: 88..111, y: 48..95)
    for y in range(48, 96):
        link_y = (y - 48) % 24
        for x in range(88, 112):
            dx = abs(x - 99.5)
            if link_y < 12:
                if (dx >= 4 and dx <= 7) or (link_y in (0, 1, 10, 11) and dx <= 7):
                    img.putpixel((x, y), get_iron(x, y, "left" if dx < 6 else "right"))
            else:
                if (dx <= 4) and (link_y in (12, 13, 22, 23) or dx in (3, 4)):
                    img.putpixel((x, y), get_iron(x, y, "top" if link_y < 18 else "bottom"))

    return img, emissive

def create_lantern_item_icon(color_name, info):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_item")

    def iron_col(light=1.0):
        v = clamp(42 * light + rnd.uniform(-2, 2))
        return (v, v, v + 3, 255)

    # 1. Top Hanging Ring (Center x=64, y=16)
    for y in range(6, 26):
        for x in range(54, 74):
            dx = x - 63.5
            dy = y - 15.5
            d = math.sqrt(dx*dx + dy*dy)
            if 4.5 <= d <= 8.5:
                l = 1.3 if dy < -1 else (0.75 if dy > 1 else 1.0)
                img.putpixel((x, y), iron_col(l))

    # 2. Roof / Canopy (x: 36..91, y: 26..46)
    for y in range(26, 47):
        progress = (y - 26) / 20.0
        hw = int(12 + progress * 16)
        for x in range(64 - hw, 64 + hw):
            nx = (x - (64 - hw)) / max(1, (2 * hw - 1))
            l = 1.25 - 0.45 * nx
            if y == 26 or y == 46: l *= 0.8
            img.putpixel((x, y), iron_col(l))
    for x in range(34, 94):
        for y in (47, 48):
            img.putpixel((x, y), iron_col(1.1 if y == 47 else 0.7))

    # 3. Glass Chamber Background & Glowing Core (x: 39..88, y: 49..98)
    cx, cy = 63.5, 73.5
    for y in range(49, 99):
        for x in range(39, 89):
            dx = (x - cx) / 21.0
            dy = (y - cy) / 21.0
            d = math.sqrt(dx*dx + dy*dy)
            
            tint = (clamp(rgb[0] * 0.25), clamp(rgb[1] * 0.25), clamp(rgb[2] * 0.25))
            if d < 1.0:
                glow = (1.0 - d) ** 1.3
                if d < 0.32:
                    flame = blend(glow_rgb, core_rgb, 1.0 - (d / 0.32))
                else:
                    flame = blend(rgb, glow_rgb, glow)
                col = blend(tint, flame, glow * 0.95)
            else:
                col = tint
            img.putpixel((x, y), (col[0], col[1], col[2], 255))

    # 4. Cage Struts
    for y in range(49, 99):
        for x in range(38, 43):
            img.putpixel((x, y), iron_col(1.15))
        for x in range(85, 90):
            img.putpixel((x, y), iron_col(0.75))
        img.putpixel((54, y), iron_col(0.95))
        img.putpixel((73, y), iron_col(0.85))

    # 5. Sturdy Base
    for y in range(99, 115):
        for x in range(34, 94):
            nx = (x - 34) / 59.0
            l = 1.15 - 0.4 * nx
            if y in (99, 100): l *= 1.2
            elif y in (113, 114): l *= 0.75
            img.putpixel((x, y), iron_col(l))
            
    for y in range(115, 118):
        for x in list(range(35, 43)) + list(range(85, 93)):
            img.putpixel((x, y), iron_col(0.7))

    return img

# ==========================================
# 2. JSON GENERATORS
# ==========================================

def write_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_all():
    print("Generating assets and data for JustLights...")
    
    # Dirs
    textures_block = os.path.join(ASSETS_DIR, "textures", "block")
    textures_item = os.path.join(ASSETS_DIR, "textures", "item")
    models_block = os.path.join(ASSETS_DIR, "models", "block")
    models_item = os.path.join(ASSETS_DIR, "models", "item")
    blockstates = os.path.join(ASSETS_DIR, "blockstates")
    loot_blocks = os.path.join(DATA_DIR, "loot_table", "blocks")
    recipes_dir = os.path.join(DATA_DIR, "recipe")
    tags_block_dir = os.path.join(DATA_DIR, "tags", "block")
    tags_item_dir = os.path.join(DATA_DIR, "tags", "item")
    mc_tags_block_dir = os.path.join(BASE_DIR, "data", "minecraft", "tags", "block", "mineable")
    
    ensure_dir(textures_block)
    ensure_dir(textures_item)
    ensure_dir(models_block)
    ensure_dir(models_item)
    ensure_dir(blockstates)
    ensure_dir(loot_blocks)
    ensure_dir(recipes_dir)
    ensure_dir(tags_block_dir)
    ensure_dir(tags_item_dir)
    ensure_dir(mc_tags_block_dir)
    
    torch_items_list = []
    torch_blocks_list = []
    lantern_items_list = []
    lantern_blocks_list = []
    pickaxe_blocks_list = []
    
    # 1. Generate for each color
    for color, info in COLORS.items():
        print(f"Processing color: {color}...")
        
        # --- A. Textures ---
        torch_img, torch_emissive = create_torch_textures(color, info)
        torch_img.save(os.path.join(textures_block, f"{color}_torch.png"))
        torch_emissive.save(os.path.join(textures_block, f"{color}_torch_e.png"))
        
        lantern_img, lantern_emissive = create_lantern_textures(color, info)
        lantern_img.save(os.path.join(textures_block, f"{color}_lantern.png"))
        lantern_emissive.save(os.path.join(textures_block, f"{color}_lantern_e.png"))
        
        lantern_icon = create_lantern_item_icon(color, info)
        lantern_icon.save(os.path.join(textures_item, f"{color}_lantern.png"))
        
        # --- B. Blockstates ---
        # Torch
        write_json(os.path.join(blockstates, f"{color}_torch.json"), {
            "variants": {
                "": {"model": f"justlights:block/{color}_torch"}
            }
        })
        # Wall Torch
        write_json(os.path.join(blockstates, f"{color}_wall_torch.json"), {
            "variants": {
                "facing=east": {"model": f"justlights:block/{color}_wall_torch"},
                "facing=north": {"model": f"justlights:block/{color}_wall_torch", "y": 270},
                "facing=south": {"model": f"justlights:block/{color}_wall_torch", "y": 90},
                "facing=west": {"model": f"justlights:block/{color}_wall_torch", "y": 180}
            }
        })
        # Lantern
        write_json(os.path.join(blockstates, f"{color}_lantern.json"), {
            "variants": {
                "hanging=false": {"model": f"justlights:block/{color}_lantern"},
                "hanging=true": {"model": f"justlights:block/{color}_lantern_hanging"}
            }
        })
        
        # --- C. Block Models ---
        # Torch
        write_json(os.path.join(models_block, f"{color}_torch.json"), {
            "parent": "minecraft:block/template_torch",
            "textures": {
                "torch": f"justlights:block/{color}_torch"
            }
        })
        # Wall Torch
        write_json(os.path.join(models_block, f"{color}_wall_torch.json"), {
            "parent": "minecraft:block/template_torch_wall",
            "textures": {
                "torch": f"justlights:block/{color}_torch"
            }
        })
        # Standing Lantern
        write_json(os.path.join(models_block, f"{color}_lantern.json"), {
            "parent": "minecraft:block/template_lantern",
            "textures": {
                "lantern": f"justlights:block/{color}_lantern"
            }
        })
        # Hanging Lantern
        write_json(os.path.join(models_block, f"{color}_lantern_hanging.json"), {
            "parent": "minecraft:block/template_hanging_lantern",
            "textures": {
                "lantern": f"justlights:block/{color}_lantern"
            }
        })
        
        # --- D. Item Models ---
        write_json(os.path.join(models_item, f"{color}_torch.json"), {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": f"justlights:block/{color}_torch"
            }
        })
        write_json(os.path.join(models_item, f"{color}_lantern.json"), {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": f"justlights:item/{color}_lantern"
            }
        })
        
        # --- E. Loot Tables ---
        # Torch drops torch
        write_json(os.path.join(loot_blocks, f"{color}_torch.json"), {
            "type": "minecraft:block",
            "pools": [
                {
                    "bonus_rolls": 0.0,
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                    "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_torch"}],
                    "rolls": 1.0
                }
            ]
        })
        # Wall torch drops torch
        write_json(os.path.join(loot_blocks, f"{color}_wall_torch.json"), {
            "type": "minecraft:block",
            "pools": [
                {
                    "bonus_rolls": 0.0,
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                    "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_torch"}],
                    "rolls": 1.0
                }
            ]
        })
        # Lantern drops lantern
        write_json(os.path.join(loot_blocks, f"{color}_lantern.json"), {
            "type": "minecraft:block",
            "pools": [
                {
                    "bonus_rolls": 0.0,
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                    "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_lantern"}],
                    "rolls": 1.0
                }
            ]
        })
        
        # --- F. Recipes ---
        dye_item = f"minecraft:{color}_dye"
        # 1. Torch from vanilla torch (shapeless 1:1)
        write_json(os.path.join(recipes_dir, f"{color}_torch_from_torch.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"item": "minecraft:torch"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_torch"}
        })
        # 2. Torch batch (8 vanilla torches around 1 dye)
        write_json(os.path.join(recipes_dir, f"{color}_torch_batch.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {"T": {"item": "minecraft:torch"}, "D": {"item": dye_item}},
            "pattern": ["TTT", "TDT", "TTT"],
            "result": {"count": 8, "id": f"justlights:{color}_torch"}
        })
        # 3. Torch craft from coal + stick + dye
        write_json(os.path.join(recipes_dir, f"{color}_torch_from_coal.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {"C": {"tag": "minecraft:coals"}, "D": {"item": dye_item}, "S": {"item": "minecraft:stick"}},
            "pattern": ["C", "D", "S"],
            "result": {"count": 4, "id": f"justlights:{color}_torch"}
        })
        # 4. Torch recolor (8 colored torches around dye)
        write_json(os.path.join(recipes_dir, f"{color}_torch_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_torches"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_torch"}
        })
        
        # 5. Lantern from colored torch + 8 iron nuggets
        write_json(os.path.join(recipes_dir, f"{color}_lantern_from_torch.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {"N": {"item": "minecraft:iron_nugget"}, "T": {"item": f"justlights:{color}_torch"}},
            "pattern": ["NNN", "NTN", "NNN"],
            "result": {"count": 1, "id": f"justlights:{color}_lantern"}
        })
        # 6. Lantern from vanilla lantern (shapeless 1:1)
        write_json(os.path.join(recipes_dir, f"{color}_lantern_from_lantern.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"item": "minecraft:lantern"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_lantern"}
        })
        # 7. Lantern batch (8 vanilla lanterns around 1 dye)
        write_json(os.path.join(recipes_dir, f"{color}_lantern_batch.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {"L": {"item": "minecraft:lantern"}, "D": {"item": dye_item}},
            "pattern": ["LLL", "LDL", "LLL"],
            "result": {"count": 8, "id": f"justlights:{color}_lantern"}
        })
        # 8. Lantern recolor (shapeless colored lantern + dye)
        write_json(os.path.join(recipes_dir, f"{color}_lantern_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_lanterns"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_lantern"}
        })
        
        # Lists for tags
        torch_items_list.append(f"justlights:{color}_torch")
        torch_blocks_list.append(f"justlights:{color}_torch")
        torch_blocks_list.append(f"justlights:{color}_wall_torch")
        lantern_items_list.append(f"justlights:{color}_lantern")
        lantern_blocks_list.append(f"justlights:{color}_lantern")
        
        pickaxe_blocks_list.append(f"justlights:{color}_lamp")
        pickaxe_blocks_list.append(f"justlights:{color}_lantern")

    # --- G. Tags ---
    write_json(os.path.join(tags_item_dir, "colored_torches.json"), {"values": torch_items_list})
    write_json(os.path.join(tags_block_dir, "colored_torches.json"), {"values": torch_blocks_list})
    write_json(os.path.join(tags_item_dir, "colored_lanterns.json"), {"values": lantern_items_list})
    write_json(os.path.join(tags_block_dir, "colored_lanterns.json"), {"values": lantern_blocks_list})
    write_json(os.path.join(mc_tags_block_dir, "pickaxe.json"), {"values": pickaxe_blocks_list})
    
    # --- H. Lang Files ---
    en_lang_path = os.path.join(ASSETS_DIR, "lang", "en_us.json")
    de_lang_path = os.path.join(ASSETS_DIR, "lang", "de_de.json")
    
    with open(en_lang_path, "r", encoding="utf-8") as f:
        en_lang = json.load(f)
    with open(de_lang_path, "r", encoding="utf-8") as f:
        de_lang = json.load(f)
        
    for color, info in COLORS.items():
        en_lang[f"block.justlights.{color}_torch"] = f"{info['en']} Torch"
        en_lang[f"block.justlights.{color}_wall_torch"] = f"{info['en']} Wall Torch"
        en_lang[f"block.justlights.{color}_lantern"] = f"{info['en']} Lantern"
        
        de_lang[f"block.justlights.{color}_torch"] = f"{info['de']} Fackel"
        de_lang[f"block.justlights.{color}_wall_torch"] = f"{info['de']} Wandfackel"
        de_lang[f"block.justlights.{color}_lantern"] = f"{info['de']} Laterne"
        
    write_json(en_lang_path, en_lang)
    write_json(de_lang_path, de_lang)
    
    # --- I. Shader Properties ---
    # Map each color code
    props_lines = [
        "# JustLights Shader Mappings for Iris / Complementary / BSL / Euphoria"
    ]
    
    # Group colors by code
    code_groups = {}
    for color, info in COLORS.items():
        code = info["code"]
        if code not in code_groups:
            code_groups[code] = []
        code_groups[code].append(color)
        
    for code in sorted(code_groups.keys()):
        colors_in_code = code_groups[code]
        blocks = []
        for c in colors_in_code:
            blocks.append(f"justlights:{c}_lamp:lit=true")
            blocks.append(f"justlights:{c}_torch")
            blocks.append(f"justlights:{c}_wall_torch")
            blocks.append(f"justlights:{c}_lantern")
        props_lines.append(f"block.{code}=" + " ".join(blocks))
        
    props_lines.append("")
    # Unlit lamps
    unlit = " ".join([f"justlights:{c}_lamp:lit=false" for c in COLORS.keys()])
    props_lines.append(f"block.10636={unlit}")
    props_lines.append("")
    
    props_text = "\n".join(props_lines)
    
    p1 = os.path.join(BASE_DIR, "assets", "minecraft", "shaders", "block.properties")
    p2 = os.path.join(BASE_DIR, "shaders", "block.properties")
    ensure_dir(os.path.dirname(p1))
    ensure_dir(os.path.dirname(p2))
    with open(p1, "w", encoding="utf-8") as f:
        f.write(props_text)
    with open(p2, "w", encoding="utf-8") as f:
        f.write(props_text)
        
    print("All assets, data, and shader mappings generated successfully!")

if __name__ == "__main__":
    generate_all()
