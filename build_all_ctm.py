import os, sys, shutil
from PIL import Image
import numpy as np

BASE_DIR = 'd:/projekt/JustLights/src/main/resources/assets/justlights'
SOURCE_BACKUP_DIR = os.path.join(BASE_DIR, 'textures/block/ctm_source')
TEXTURES_DIR = os.path.join(BASE_DIR, 'textures/block')
OPTIFINE_CTM_DIR = os.path.join(BASE_DIR, 'optifine/ctm')
OPTIFINE_DIR = os.path.join(BASE_DIR, 'optifine')

# 1. Load ctm_template.png rules
template_path = 'd:/projekt/JustLights/ctm_template.png'
im_t = Image.open(template_path).convert('RGB')
arr_t = np.array(im_t)
is_green = (arr_t[:, :, 1] > 150) & (arr_t[:, :, 0] < 50) & (arr_t[:, :, 2] < 50)

cell_w = 64
cell_h = 64
offset_x = 1
offset_y = 1

rules = []
for idx in range(47):
    r = idx // 12
    c = idx % 12
    x0 = offset_x + c * cell_w
    y0 = offset_y + r * cell_h
    cell = is_green[y0:y0+cell_h, x0:x0+cell_w]
    
    top = bool(np.any(cell[0:4, 20:44]))
    bot = bool(np.any(cell[60:64, 20:44]))
    left = bool(np.any(cell[20:44, 0:4]))
    right = bool(np.any(cell[20:44, 60:64]))
    
    tl = bool((not top and not left) and np.any(cell[0:6, 0:6]))
    tr = bool((not top and not right) and np.any(cell[0:6, 58:64]))
    bl = bool((not bot and not left) and np.any(cell[58:64, 0:6]))
    br = bool((not bot and not right) and np.any(cell[58:64, 58:64]))
    
    rules.append({
        'tile': idx, 'T': top, 'B': bot, 'L': left, 'R': right,
        'TL': tl, 'TR': tr, 'BL': bl, 'BR': br
    })

print(f"Loaded {len(rules)} rules from ctm_template.png")

COLORS = [
    'white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
    'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black'
]

# Ensure backup dir
os.makedirs(SOURCE_BACKUP_DIR, exist_ok=True)
os.makedirs(OPTIFINE_CTM_DIR, exist_ok=True)

# Create emissive.properties
with open(os.path.join(OPTIFINE_DIR, 'emissive.properties'), 'w', encoding='utf-8') as f:
    f.write("# OptiFine / Continuity emissive textures\nsuffix.emissive=_e\n")

def process_collage(collage_img, bw=12):
    """
    Given a 512x512 collage Image (RGBA), generates a dict of {tile_idx: Image(128x128)}
    and returns (dict_of_tiles, tile_iso_128)
    """
    base_interior = collage_img.crop((1*128, 0*128, 2*128, 1*128))
    tile_iso = collage_img.crop((0*128, 0*128, 1*128, 1*128))
    
    tile_top_only = collage_img.crop((3*128, 0*128, 4*128, 1*128))
    tile_bot_only = collage_img.crop((2*128, 0*128, 3*128, 1*128))
    tile_left_only = collage_img.crop((2*128, 1*128, 3*128, 2*128))
    tile_right_only = collage_img.crop((3*128, 1*128, 4*128, 2*128))
    
    tile_tl = collage_img.crop((2*128, 2*128, 3*128, 3*128))
    tile_tr = collage_img.crop((3*128, 2*128, 4*128, 3*128))
    tile_bl = collage_img.crop((2*128, 3*128, 3*128, 4*128))
    tile_br = collage_img.crop((3*128, 3*128, 4*128, 4*128))
    
    top_edge = tile_top_only.crop((bw, 0, 128 - bw, bw))
    bot_edge = tile_bot_only.crop((bw, 128 - bw, 128 - bw, 128))
    left_edge = tile_left_only.crop((0, bw, bw, 128 - bw))
    right_edge = tile_right_only.crop((128 - bw, bw, 128, 128 - bw))
    
    tl_corner = tile_tl.crop((0, 0, bw, bw))
    tr_corner = tile_tr.crop((128 - bw, 0, 128, bw))
    bl_corner = tile_bl.crop((0, 128 - bw, bw, 128))
    br_corner = tile_br.crop((128 - bw, 128 - bw, 128, 128))
    
    top_full = tile_top_only.crop((0, 0, 128, bw))
    bot_full = tile_bot_only.crop((0, 128 - bw, 128, 128))
    left_full = tile_left_only.crop((0, 0, bw, 128))
    right_full = tile_right_only.crop((128 - bw, 0, 128, 128))

    inner_tl = tile_iso.crop((0, 0, bw, bw))
    inner_tr = tile_iso.crop((128 - bw, 0, 128, bw))
    inner_bl = tile_iso.crop((0, 128 - bw, bw, 128))
    inner_br = tile_iso.crop((128 - bw, 128 - bw, 128, 128))
    
    tiles = {}
    for rule in rules:
        idx = rule['tile']
        t, b, l, r = rule['T'], rule['B'], rule['L'], rule['R']
        tl, tr, bl, br = rule['TL'], rule['TR'], rule['BL'], rule['BR']
        
        img = base_interior.copy()
        
        if t:
            img.paste(top_edge, (bw, 0))
        if b:
            img.paste(bot_edge, (bw, 128 - bw))
        if l:
            img.paste(left_edge, (0, bw))
        if r:
            img.paste(right_edge, (128 - bw, bw))
            
        if t and l:
            img.paste(tl_corner, (0, 0))
        elif t and not l:
            img.paste(top_full.crop((0, 0, bw, bw)), (0, 0))
        elif l and not t:
            img.paste(left_full.crop((0, 0, bw, bw)), (0, 0))
        elif tl:
            img.paste(inner_tl, (0, 0))
            
        if t and r:
            img.paste(tr_corner, (128 - bw, 0))
        elif t and not r:
            img.paste(top_full.crop((128 - bw, 0, 128, bw)), (128 - bw, 0))
        elif r and not t:
            img.paste(right_full.crop((0, 0, bw, bw)), (128 - bw, 0))
        elif tr:
            img.paste(inner_tr, (128 - bw, 0))
            
        if b and l:
            img.paste(bl_corner, (0, 128 - bw))
        elif b and not l:
            img.paste(bot_full.crop((0, 0, bw, bw)), (0, 128 - bw))
        elif l and not b:
            img.paste(left_full.crop((0, 128 - bw, bw, 128)), (0, 128 - bw))
        elif bl:
            img.paste(inner_bl, (0, 128 - bw))
            
        if b and r:
            img.paste(br_corner, (128 - bw, 128 - bw))
        elif b and not r:
            img.paste(bot_full.crop((128 - bw, 0, 128, bw)), (128 - bw, 128 - bw))
        elif r and not b:
            img.paste(right_full.crop((0, 0, bw, bw)), (128 - bw, 0))
        elif br:
            img.paste(inner_br, (128 - bw, 128 - bw))
            
        tiles[idx] = img
        
    return tiles, tile_iso

for color in COLORS:
    print(f"Processing {color} lamp...")
    
    # Paths to source collages
    path_on = os.path.join(TEXTURES_DIR, f"{color}_lamp_on.png")
    path_off = os.path.join(TEXTURES_DIR, f"{color}_lamp_off.png")
    path_e = os.path.join(TEXTURES_DIR, f"{color}_lamp_on_e.png")
    
    # Back up source 512x512 collages
    shutil.copyfile(path_on, os.path.join(SOURCE_BACKUP_DIR, f"{color}_lamp_on.png"))
    shutil.copyfile(path_off, os.path.join(SOURCE_BACKUP_DIR, f"{color}_lamp_off.png"))
    shutil.copyfile(path_e, os.path.join(SOURCE_BACKUP_DIR, f"{color}_lamp_on_e.png"))
    
    # Open images
    img_on = Image.open(path_on).convert('RGBA')
    img_off = Image.open(path_off).convert('RGBA')
    img_e = Image.open(path_e).convert('RGBA')
    
    # Process tiles
    tiles_on, iso_on = process_collage(img_on)
    tiles_off, iso_off = process_collage(img_off)
    tiles_e, iso_e = process_collage(img_e)
    
    # 1. Output directory for lit state
    dir_on = os.path.join(OPTIFINE_CTM_DIR, f"{color}_lamp_on")
    os.makedirs(dir_on, exist_ok=True)
    for idx in range(47):
        tiles_on[idx].save(os.path.join(dir_on, f"{idx}.png"))
        tiles_e[idx].save(os.path.join(dir_on, f"{idx}_e.png"))
    
    # Properties for lit state
    with open(os.path.join(dir_on, f"{color}_lamp_on.properties"), 'w', encoding='utf-8') as f:
        f.write(f"matchTiles=justlights:block/{color}_lamp_on\n")
        f.write(f"method=ctm\n")
        f.write(f"tiles=0-46\n")
        f.write(f"connect=tile\n")
        
    # 2. Output directory for unlit state
    dir_off = os.path.join(OPTIFINE_CTM_DIR, f"{color}_lamp_off")
    os.makedirs(dir_off, exist_ok=True)
    for idx in range(47):
        tiles_off[idx].save(os.path.join(dir_off, f"{idx}.png"))
        
    # Properties for unlit state
    with open(os.path.join(dir_off, f"{color}_lamp_off.properties"), 'w', encoding='utf-8') as f:
        f.write(f"matchTiles=justlights:block/{color}_lamp_off\n")
        f.write(f"method=ctm\n")
        f.write(f"tiles=0-46\n")
        f.write(f"connect=tile\n")
        
    # 3. Update base textures to the single 128x128 isolated tile (tile 0)
    iso_on.save(path_on)
    iso_off.save(path_off)
    iso_e.save(path_e)

print("All 16 colors successfully generated and updated!")
