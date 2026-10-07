import os
import json
import math
import random
from PIL import Image, ImageDraw

COLORS = {
    "white":      {"rgb": (255, 255, 255), "glow": (245, 250, 255), "core": (255, 255, 255), "en": "White",      "de_torch": "Weiße",      "de_fire": "Weißes",      "code": 10900},
    "orange":     {"rgb": (255, 120, 10),  "glow": (255, 140, 20),  "core": (255, 240, 180), "en": "Orange",     "de_torch": "Orange",     "de_fire": "Oranges",     "code": 10904},
    "magenta":    {"rgb": (230, 45, 200),  "glow": (245, 60, 220),  "core": (255, 210, 250), "en": "Magenta",    "de_torch": "Magenta",    "de_fire": "Magenta",     "code": 10920},
    "light_blue": {"rgb": (60, 190, 255),  "glow": (90, 210, 255),  "core": (220, 245, 255), "en": "Light Blue", "de_torch": "Hellblaue", "de_fire": "Hellblaues", "code": 10914},
    "yellow":     {"rgb": (255, 225, 25),  "glow": (255, 235, 50),  "core": (255, 255, 210), "en": "Yellow",     "de_torch": "Gelbe",      "de_fire": "Gelbes",      "code": 10906},
    "lime":       {"rgb": (120, 255, 25),  "glow": (145, 255, 45),  "core": (235, 255, 200), "en": "Lime",       "de_torch": "Hellgrüne",  "de_fire": "Hellgrünes",  "code": 10908},
    "pink":       {"rgb": (255, 115, 180), "glow": (255, 145, 200), "core": (255, 235, 245), "en": "Pink",       "de_torch": "Rosa",       "de_fire": "Rosa",        "code": 10922},
    "gray":       {"rgb": (130, 140, 160), "glow": (160, 175, 195), "core": (230, 235, 245), "en": "Gray",       "de_torch": "Graue",      "de_fire": "Graues",      "code": 10900},
    "light_gray": {"rgb": (205, 215, 225), "glow": (225, 235, 245), "core": (255, 255, 255), "en": "Light Gray", "de_torch": "Hellgraue", "de_fire": "Hellgraues", "code": 10900},
    "cyan":       {"rgb": (15, 235, 215),  "glow": (40, 250, 235),  "core": (210, 255, 250), "en": "Cyan",       "de_torch": "Türkise",    "de_fire": "Türkises",    "code": 10912},
    "purple":     {"rgb": (155, 40, 245),  "glow": (180, 60, 255),  "core": (240, 200, 255), "en": "Purple",     "de_torch": "Violette",   "de_fire": "Violettes",   "code": 10918},
    "blue":       {"rgb": (30, 85, 255),   "glow": (55, 120, 255),  "core": (210, 225, 255), "en": "Blue",       "de_torch": "Blaue",      "de_fire": "Blaues",      "code": 10916},
    "brown":      {"rgb": (175, 95, 35),   "glow": (205, 125, 55),  "core": (255, 220, 180), "en": "Brown",      "de_torch": "Braune",     "de_fire": "Braunes",     "code": 10900},
    "green":      {"rgb": (25, 210, 45),   "glow": (45, 240, 75),   "core": (210, 255, 215), "en": "Green",      "de_torch": "Grüne",      "de_fire": "Grünes",      "code": 10910},
    "red":        {"rgb": (255, 30, 30),   "glow": (255, 60, 50),   "core": (255, 215, 205), "en": "Red",        "de_torch": "Rote",       "de_fire": "Rotes",       "code": 10902},
    "black":      {"rgb": (85, 60, 110),   "glow": (115, 85, 145),  "core": (205, 195, 225), "en": "Black",      "de_torch": "Schwarze",   "de_fire": "Schwarzes",   "code": 10900},
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
# CAMPFIRE PROCEDURAL TEXTURES (128x128 HD)
# ==========================================

def create_campfire_fire_animation(color_name, info):
    """
    Creates 8 frames of animated fire: 128x1024 image.
    Each frame is 128x128.
    """
    total_w = 128
    total_h = 1024 # 8 frames of 128
    img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    emissive = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_fire")
    
    num_frames = 8
    frame_h = 128
    
    for f in range(num_frames):
        y_offset = f * frame_h
        phase = (f / float(num_frames)) * 2 * math.pi
        
        for y in range(frame_h):
            ny = y / 127.0 # 0.0 at top, 1.0 at bottom
            
            # Fire silhouette shape
            # Bottom (y=127) is wide: half-width ~48 (x: 16..112)
            # Mid (y=64) is medium: half-width ~36
            # Top (y=15) is narrow tip: half-width ~10
            # Flame tips sway with phase and y
            sway = math.sin(phase + (1.0 - ny) * 4.0) * 14.0 * (1.0 - ny)
            center_x = 63.5 + sway
            
            base_hw = 50.0 * (ny ** 0.6) + 4.0
            
            # Wavy flame tongue edges
            edge_waviness = math.sin((y * 0.18) + phase * 2) * 6.0
            hw = max(0.0, base_hw + edge_waviness)
            
            # Skip if above flame tip
            flame_tip_min_y = 12 + int(math.sin(phase * 1.5) * 8)
            if y < flame_tip_min_y:
                continue
                
            for x in range(total_w):
                dx = abs(x - center_x)
                if dx > hw:
                    continue
                    
                rel_d = dx / max(1.0, hw) # 0.0 at center, 1.0 at edge
                
                # Height factor: hottest near bottom, cooling towards tip
                h_factor = (y - flame_tip_min_y) / max(1.0, (127 - flame_tip_min_y))
                
                # Intensity combining center proximity and height
                intensity = ((1.0 - rel_d) ** 1.1) * (0.4 + 0.6 * h_factor)
                
                # Noise/flicker
                flicker = rnd.uniform(0.92, 1.08)
                
                # Color blending:
                # Center (rel_d < 0.28 and h_factor > 0.3) -> hot white/pastel core
                if rel_d < 0.28 and h_factor > 0.25:
                    core_f = (1.0 - rel_d / 0.28) * h_factor
                    c = blend(glow_rgb, core_rgb, core_f)
                else:
                    c = blend(rgb, glow_rgb, intensity)
                    
                fr = clamp(c[0] * flicker)
                fg = clamp(c[1] * flicker)
                fb = clamp(c[2] * flicker)
                
                # Edge soft transparency
                alpha = 255
                if rel_d > 0.82:
                    alpha = clamp(255 * ((1.0 - rel_d) / 0.18))
                if y < flame_tip_min_y + 10:
                    alpha = clamp(alpha * ((y - flame_tip_min_y) / 10.0))
                    
                py = y_offset + y
                img.putpixel((x, py), (fr, fg, fb, alpha))
                if alpha > 20:
                    emissive.putpixel((x, py), (fr, fg, fb, alpha))
                    
    return img, emissive

def create_campfire_log_lit_animation(color_name, info):
    """
    Creates 4 frames of glowing coal / lit logs: 128x512 image.
    Each frame is 128x128.
    """
    total_w = 128
    total_h = 512
    img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    emissive = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_lit_log")
    
    num_frames = 4
    frame_h = 128
    
    for f in range(num_frames):
        y_offset = f * frame_h
        pulse = 0.85 + 0.15 * math.sin((f / float(num_frames)) * 2 * math.pi)
        
        for y in range(frame_h):
            for x in range(total_w):
                # Region 1: Upper section (y in 0..63) - Charred logs with glowing heat
                if y < 64:
                    # Dark oak wood base with vertical grain
                    wood_val = 60 + int(math.sin(x * 0.4) * 12) + rnd.randint(-6, 6)
                    r = clamp(wood_val * 1.1)
                    g = clamp(wood_val * 0.8)
                    b = clamp(wood_val * 0.5)
                    
                    # Charred ash edges
                    if y >= 45:
                        char_factor = (y - 45) / 19.0
                        r = clamp(r * (1 - char_factor) + 30 * char_factor)
                        g = clamp(g * (1 - char_factor) + 25 * char_factor)
                        b = clamp(b * (1 - char_factor) + 25 * char_factor)
                        
                        # Glowing fissures
                        if (x + y) % 17 < 3:
                            heat_col = blend(rgb, glow_rgb, pulse)
                            r = blend((r,), (heat_col[0],), 0.75 * pulse)[0]
                            g = blend((g,), (heat_col[1],), 0.75 * pulse)[0]
                            b = blend((b,), (heat_col[2],), 0.75 * pulse)[0]
                            emissive.putpixel((x, y_offset + y), (heat_col[0], heat_col[1], heat_col[2], 255))
                    img.putpixel((x, y_offset + y), (r, g, b, 255))
                else:
                    # Region 2: Lower section (y in 64..127) - Glowing coal bed & glowing ash
                    dist_from_center = math.hypot(x - 63.5, y - 95.5) / 50.0
                    coal_noise = rnd.uniform(0.85, 1.15)
                    
                    # Fissure pattern
                    fissure = math.sin(x * 0.25) * math.cos(y * 0.25)
                    is_hot_fissure = (abs(fissure) > 0.35)
                    
                    if is_hot_fissure:
                        intensity = clamp(pulse * (1.2 - dist_from_center * 0.5) * 255) / 255.0
                        col = blend(rgb, core_rgb, max(0.0, min(1.0, intensity * 0.8)))
                        r = clamp(col[0] * coal_noise)
                        g = clamp(col[1] * coal_noise)
                        b = clamp(col[2] * coal_noise)
                        emissive.putpixel((x, y_offset + y), (r, g, b, 255))
                    else:
                        # Dark burning charcoal lumps
                        char_val = clamp(35 + rnd.uniform(-8, 8))
                        glow_tint = blend((char_val, char_val - 5, char_val - 10), rgb, 0.25 * pulse)
                        r, g, b = glow_tint
                        emissive.putpixel((x, y_offset + y), (clamp(rgb[0] * 0.25 * pulse), clamp(rgb[1] * 0.25 * pulse), clamp(rgb[2] * 0.25 * pulse), 255))
                        
                    img.putpixel((x, y_offset + y), (r, g, b, 255))
                    
    return img, emissive

def create_campfire_item_icon(color_name, info):
    """
    Creates 128x128 HD item icon for campfire
    """
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    rgb = info["rgb"]
    glow_rgb = info["glow"]
    core_rgb = info["core"]
    rnd = random.Random(color_name + "_item_camp")

    # 1. Base Criss-Cross Logs (y: 78..118, x: 14..114)
    # Bottom logs: angled logs
    for y in range(80, 118):
        for x in range(14, 114):
            # Check if inside crossed logs silhouette
            dx1 = abs((x - 64) - (y - 98) * 1.1)
            dx2 = abs((x - 64) + (y - 98) * 1.1)
            is_log = (dx1 < 16 or dx2 < 16 or (y > 96 and abs(x - 64) < 46))
            if is_log:
                bark = 55 + int(math.sin(x * 0.5) * 10) + rnd.randint(-5, 5)
                r = clamp(bark * 1.2)
                g = clamp(bark * 0.85)
                b = clamp(bark * 0.55)
                if y > 112:
                    r, g, b = int(r * 0.7), int(g * 0.7), int(b * 0.7)
                img.putpixel((x, y), (r, g, b, 255))

    # 2. Glowing Coal Center (x: 42..86, y: 74..98)
    for y in range(74, 99):
        for x in range(42, 86):
            d = math.hypot(x - 63.5, y - 86.5)
            if d < 22:
                intensity = (1.0 - d / 22.0) ** 1.2
                col = blend(rgb, glow_rgb, intensity)
                img.putpixel((x, y), (col[0], col[1], col[2], 255))

    # 3. Roaring Leaping Fire (x: 24..104, y: 12..78)
    cx = 63.5
    for y in range(12, 79):
        ny = (y - 12) / 66.0 # 0.0 at top tip, 1.0 at base
        hw = 38.0 * (ny ** 0.55) + 3.0
        for x in range(24, 105):
            dx = abs(x - cx)
            if dx <= hw:
                rel_d = dx / hw
                intensity = ((1.0 - rel_d) ** 1.2) * (0.3 + 0.7 * ny)
                if rel_d < 0.28 and ny > 0.35:
                    c = blend(glow_rgb, core_rgb, 1.0 - rel_d / 0.28)
                else:
                    c = blend(rgb, glow_rgb, intensity)
                alpha = 255
                if rel_d > 0.85:
                    alpha = clamp(255 * ((1.0 - rel_d) / 0.15))
                if y < 18:
                    alpha = clamp(alpha * ((y - 12) / 6.0))
                img.putpixel((x, y), (c[0], c[1], c[2], alpha))

    return img

# ==========================================
# GENERATE EVERYTHING
# ==========================================

def generate_all():
    print("Generating Campfire assets and data for JustLights...")
    
    textures_block = os.path.join(ASSETS_DIR, "textures", "block")
    textures_item = os.path.join(ASSETS_DIR, "textures", "item")
    models_block = os.path.join(ASSETS_DIR, "models", "block")
    models_item = os.path.join(ASSETS_DIR, "models", "item")
    blockstates = os.path.join(ASSETS_DIR, "blockstates")
    loot_blocks = os.path.join(DATA_DIR, "loot_table", "blocks")
    recipes_dir = os.path.join(DATA_DIR, "recipe")
    tags_block_dir = os.path.join(DATA_DIR, "tags", "block")
    tags_item_dir = os.path.join(DATA_DIR, "tags", "item")
    mc_tags_block_dir = os.path.join(BASE_DIR, "data", "minecraft", "tags", "block")
    mc_tags_mineable_dir = os.path.join(mc_tags_block_dir, "mineable")
    
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
    ensure_dir(mc_tags_mineable_dir)
    
    # mcmeta JSONs
    fire_mcmeta = {"animation": {"frametime": 2}}
    lit_log_mcmeta = {"animation": {"interpolate": True, "frametime": 20}}
    
    campfire_items_list = []
    campfire_blocks_list = []
    axe_blocks_list = []
    
    for color, info in COLORS.items():
        print(f"Generating campfire: {color}...")
        
        # 1. Textures & Emissives
        fire_img, fire_emissive = create_campfire_fire_animation(color, info)
        fire_img.save(os.path.join(textures_block, f"{color}_campfire_fire.png"))
        fire_emissive.save(os.path.join(textures_block, f"{color}_campfire_fire_e.png"))
        write_json(os.path.join(textures_block, f"{color}_campfire_fire.png.mcmeta"), fire_mcmeta)
        
        lit_log_img, lit_log_emissive = create_campfire_log_lit_animation(color, info)
        lit_log_img.save(os.path.join(textures_block, f"{color}_campfire_log_lit.png"))
        lit_log_emissive.save(os.path.join(textures_block, f"{color}_campfire_log_lit_e.png"))
        write_json(os.path.join(textures_block, f"{color}_campfire_log_lit.png.mcmeta"), lit_log_mcmeta)
        
        item_icon = create_campfire_item_icon(color, info)
        item_icon.save(os.path.join(textures_item, f"{color}_campfire.png"))
        
        # 2. Blockstate
        write_json(os.path.join(blockstates, f"{color}_campfire.json"), {
            "variants": {
                "facing=east,lit=false":  {"model": f"justlights:block/{color}_campfire_off", "y": 270},
                "facing=east,lit=true":   {"model": f"justlights:block/{color}_campfire",     "y": 270},
                "facing=north,lit=false": {"model": f"justlights:block/{color}_campfire_off", "y": 180},
                "facing=north,lit=true":  {"model": f"justlights:block/{color}_campfire",     "y": 180},
                "facing=south,lit=false": {"model": f"justlights:block/{color}_campfire_off"},
                "facing=south,lit=true":  {"model": f"justlights:block/{color}_campfire"},
                "facing=west,lit=false":  {"model": f"justlights:block/{color}_campfire_off", "y": 90},
                "facing=west,lit=true":   {"model": f"justlights:block/{color}_campfire",     "y": 90}
            }
        })
        
        # 3. Block Models
        write_json(os.path.join(models_block, f"{color}_campfire.json"), {
            "parent": "minecraft:block/template_campfire",
            "textures": {
                "fire": f"justlights:block/{color}_campfire_fire",
                "lit_log": f"justlights:block/{color}_campfire_log_lit"
            }
        })
        write_json(os.path.join(models_block, f"{color}_campfire_off.json"), {
            "parent": "minecraft:block/campfire_off"
        })
        
        # 4. Item Model
        write_json(os.path.join(models_item, f"{color}_campfire.json"), {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": f"justlights:item/{color}_campfire"
            }
        })
        
        # 5. Loot Table
        write_json(os.path.join(loot_blocks, f"{color}_campfire.json"), {
            "type": "minecraft:block",
            "pools": [
                {
                    "bonus_rolls": 0.0,
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                    "entries": [{"type": "minecraft:item", "name": f"justlights:{color}_campfire"}],
                    "rolls": 1.0
                }
            ]
        })
        
        # 6. Recipes
        dye_item = f"minecraft:{color}_dye"
        # From colored torch + sticks + logs
        write_json(os.path.join(recipes_dir, f"{color}_campfire_from_torch.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {
                "S": {"item": "minecraft:stick"},
                "T": {"item": f"justlights:{color}_torch"},
                "L": {"tag": "minecraft:logs"}
            },
            "pattern": [" S ", "STS", "LLL"],
            "result": {"count": 1, "id": f"justlights:{color}_campfire"}
        })
        # 1:1 shapeless from vanilla campfire
        write_json(os.path.join(recipes_dir, f"{color}_campfire_from_campfire.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"item": "minecraft:campfire"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_campfire"}
        })
        # 8x batch from vanilla campfires
        write_json(os.path.join(recipes_dir, f"{color}_campfire_batch.json"), {
            "type": "minecraft:crafting_shaped",
            "category": "building",
            "key": {"C": {"item": "minecraft:campfire"}, "D": {"item": dye_item}},
            "pattern": ["CCC", "CDC", "CCC"],
            "result": {"count": 8, "id": f"justlights:{color}_campfire"}
        })
        # Recolor
        write_json(os.path.join(recipes_dir, f"{color}_campfire_recolor.json"), {
            "type": "minecraft:crafting_shapeless",
            "category": "building",
            "ingredients": [{"tag": "justlights:colored_campfires"}, {"item": dye_item}],
            "result": {"count": 1, "id": f"justlights:{color}_campfire"}
        })
        
        campfire_items_list.append(f"justlights:{color}_campfire")
        campfire_blocks_list.append(f"justlights:{color}_campfire")
        axe_blocks_list.append(f"justlights:{color}_campfire")

    # 7. Tags
    write_json(os.path.join(tags_item_dir, "colored_campfires.json"), {"values": campfire_items_list})
    write_json(os.path.join(tags_block_dir, "colored_campfires.json"), {"values": campfire_blocks_list})
    write_json(os.path.join(mc_tags_block_dir, "campfires.json"), {"values": campfire_blocks_list})
    write_json(os.path.join(mc_tags_mineable_dir, "axe.json"), {"values": axe_blocks_list})
    
    # 8. Lang Files
    en_lang_path = os.path.join(ASSETS_DIR, "lang", "en_us.json")
    de_lang_path = os.path.join(ASSETS_DIR, "lang", "de_de.json")
    with open(en_lang_path, "r", encoding="utf-8") as f:
        en_lang = json.load(f)
    with open(de_lang_path, "r", encoding="utf-8") as f:
        de_lang = json.load(f)
        
    for color, info in COLORS.items():
        en_lang[f"block.justlights.{color}_campfire"] = f"{info['en']} Campfire"
        de_lang[f"block.justlights.{color}_campfire"] = f"{info['de_fire']} Lagerfeuer"
        
    write_json(en_lang_path, en_lang)
    write_json(de_lang_path, de_lang)
    
    # 9. Update Shader Properties
    props_lines = [
        "# JustLights Shader Mappings for Iris / Complementary / BSL / Euphoria"
    ]
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
            blocks.append(f"justlights:{c}_campfire:lit=true")
        props_lines.append(f"block.{code}=" + " ".join(blocks))
        
    props_lines.append("")
    # Unlit lamps & unlit campfires
    unlit_lamps = " ".join([f"justlights:{c}_lamp:lit=false" for c in COLORS.keys()])
    unlit_camps = " ".join([f"justlights:{c}_campfire:lit=false" for c in COLORS.keys()])
    props_lines.append(f"block.10636={unlit_lamps} {unlit_camps}")
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
        
    print("Campfire generation completed successfully!")

if __name__ == "__main__":
    generate_all()
