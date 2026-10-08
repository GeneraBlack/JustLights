import os, sys, shutil
from PIL import Image
import numpy as np

BASE_DIR = 'd:/projekt/JustLights/src/main/resources/assets/justlights'
SRC_DIR = 'd:/projekt/JustLights/assets_source'
TEXTURES_DIR = os.path.join(BASE_DIR, 'textures/block')
OPTIFINE_CTM_DIR = os.path.join(BASE_DIR, 'optifine/ctm')
OPTIFINE_DIR = os.path.join(BASE_DIR, 'optifine')

COLORS = [
    'white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
    'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black'
]

# Map 16 pure cardinal tiles to their exact coordinates (row, col) in the artist's 4x4 collage:
# Each tile is 128x128.
CARDINAL_ROW_COL = {
    0:  (0, 0),  # TBLR  -> Isolated block (all 4 borders & bolts)
    1:  (3, 0),  # TBL-  -> Left end of horizontal strip
    2:  (1, 0),  # TB--  -> Middle of horizontal strip
    3:  (3, 1),  # TB-R  -> Right end of horizontal strip
    12: (2, 0),  # T-LR  -> Top end of vertical strip
    13: (2, 2),  # T-L-  -> Top-Left corner of 2x2/grid
    14: (0, 3),  # T---  -> Top edge of grid
    15: (2, 3),  # T--R  -> Top-Right corner of 2x2/grid
    24: (1, 1),  # --LR  -> Middle of vertical strip
    25: (1, 2),  # --L-  -> Left edge of grid
    26: (0, 1),  # ----  -> Seamless interior of grid
    27: (1, 3),  # ---R  -> Right edge of grid
    36: (2, 1),  # -BLR  -> Bottom end of vertical strip
    37: (3, 2),  # -BL-  -> Bottom-Left corner of 2x2/grid
    38: (0, 2),  # -B--  -> Bottom edge of grid
    39: (3, 3),  # -B-R  -> Bottom-Right corner of 2x2/grid
}

CARDINAL_BORDERS = {
    0:  (True,  True,  True,  True),   # TBLR
    1:  (True,  True,  True,  False),  # TBL-
    2:  (True,  True,  False, False),  # TB--
    3:  (True,  True,  False, True),   # TB-R
    12: (True,  False, True,  True),   # T-LR
    13: (True,  False, True,  False),  # T-L-
    14: (True,  False, False, False),  # T---
    15: (True,  False, False, True),   # T--R
    24: (False, False, True,  True),   # --LR
    25: (False, False, True,  False),  # --L-
    26: (False, False, False, False),  # ----
    27: (False, False, False, True),   # ---R
    36: (False, True,  True,  True),   # -BLR
    37: (False, True,  True,  False),  # -BL-
    38: (False, True,  False, False),  # -B--
    39: (False, True,  False, True),   # -B-R
}

# The complete 47-tile CTM standard definition: (base_cardinal_tile_id, [inner_corner_caps_needed])
TILE_DEFINITIONS = {
     0: ( 0, []),
     1: ( 1, []),
     2: ( 2, []),
     3: ( 3, []),
     4: (13, ['BR']),
     5: (15, ['BL']),
     6: (25, ['TR', 'BR']),
     7: (14, ['BL', 'BR']),
     8: (26, ['TL', 'BL', 'BR']),
     9: (26, ['TL', 'TR', 'BL']),
    10: (26, ['TR', 'BR']),
    11: (26, ['BL', 'BR']),
    12: (12, []),
    13: (13, []),
    14: (14, []),
    15: (15, []),
    16: (37, ['TR']),
    17: (39, ['TL']),
    18: (38, ['TL', 'TR']),
    19: (27, ['TL', 'BL']),
    20: (26, ['TR', 'BL', 'BR']),
    21: (26, ['TL', 'TR', 'BR']),
    22: (26, ['TL', 'TR']),
    23: (26, ['TL', 'BL']),
    24: (24, []),
    25: (25, []),
    26: (26, []),
    27: (27, []),
    28: (25, ['TR']),
    29: (14, ['BR']),
    30: (25, ['BR']),
    31: (14, ['BL']),
    32: (26, ['BR']),
    33: (26, ['BL']),
    34: (26, ['TL', 'BR']),
    35: (26, ['TR', 'BL']),
    36: (36, []),
    37: (37, []),
    38: (38, []),
    39: (39, []),
    40: (38, ['TL']),
    41: (27, ['BL']),
    42: (38, ['TR']),
    43: (27, ['TL']),
    44: (26, ['TR']),
    45: (26, ['TL']),
    46: (26, ['TL', 'TR', 'BL', 'BR']),
}

def get_color_from_dist(dist, profile):
    d_clamped = np.clip(dist, 0.0, 52.0)
    idx_floor = np.floor(d_clamped).astype(int)
    idx_ceil = np.clip(idx_floor + 1, 0, 52)
    frac = (d_clamped - idx_floor)[..., None]
    return profile[idx_floor] * (1.0 - frac) + profile[idx_ceil] * frac

def compute_distance_field(has_t, has_b, has_l, has_r, caps):
    """
    Computes exact continuous distance field to the nearest physical metal border.
    Where a border exists, distance falls off towards 0 at the border (d=0..52).
    Where no border exists, light connects continuously across the edge (d >= 52).
    Inner corner caps create smooth rounded corner falloffs.
    """
    Y, X = np.ogrid[:128, :128]
    d = np.full((128, 128), 999.0)
    
    if has_t: d = np.minimum(d, Y - 12.0)
    if has_b: d = np.minimum(d, 115.0 - Y)
    if has_l: d = np.minimum(d, X - 12.0)
    if has_r: d = np.minimum(d, 115.0 - X)
    
    for cap in caps:
        if cap == 'TL':
            d_cap = np.where((X > 12) & (Y > 12), np.sqrt((X - 12.0)**2 + (Y - 12.0)**2),
                    np.where(X <= 12, np.maximum(0.0, Y - 12.0), np.maximum(0.0, X - 12.0)))
            d = np.minimum(d, d_cap)
        elif cap == 'TR':
            d_cap = np.where((X < 115) & (Y > 12), np.sqrt((115.0 - X)**2 + (Y - 12.0)**2),
                    np.where(X >= 115, np.maximum(0.0, Y - 12.0), np.maximum(0.0, 115.0 - X)))
            d = np.minimum(d, d_cap)
        elif cap == 'BL':
            d_cap = np.where((X > 12) & (Y < 115), np.sqrt((X - 12.0)**2 + (115.0 - Y)**2),
                    np.where(X <= 12, np.maximum(0.0, 115.0 - Y), np.maximum(0.0, X - 12.0)))
            d = np.minimum(d, d_cap)
        elif cap == 'BR':
            d_cap = np.where((X < 115) & (Y < 115), np.sqrt((115.0 - X)**2 + (115.0 - Y)**2),
                    np.where(X >= 115, np.maximum(0.0, 115.0 - Y), np.maximum(0.0, 115.0 - X)))
            d = np.minimum(d, d_cap)
            
    return d

def generate_tile(tile_idx, raw_tiles, profile, iso):
    base_id, caps = TILE_DEFINITIONS[tile_idx]
    if tile_idx == 0:
        return Image.fromarray(iso)
        
    has_t, has_b, has_l, has_r = CARDINAL_BORDERS[base_id]
    d = compute_distance_field(has_t, has_b, has_l, has_r, caps)
    glass_rgb = get_color_from_dist(d, profile)
    
    out = raw_tiles[base_id].copy()
    
    x_min = 12 if has_l else 0
    x_max = 116 if has_r else 128
    y_min = 12 if has_t else 0
    y_max = 116 if has_b else 128
    out[y_min:y_max, x_min:x_max, :3] = np.clip(glass_rgb[y_min:y_max, x_min:x_max], 0, 255).astype(np.uint8)
    
    for cap in caps:
        if cap == 'TL': out[:12, :12, :] = iso[:12, :12, :]
        elif cap == 'TR': out[:12, 116:, :] = iso[:12, 116:, :]
        elif cap == 'BL': out[116:, :12, :] = iso[116:, :12, :]
        elif cap == 'BR': out[116:, 116:, :] = iso[116:, 116:, :]
        
    return Image.fromarray(out)

def generate_all_47_tiles(collage_img):
    raw_tiles = {}
    for tile_id, (r, c) in CARDINAL_ROW_COL.items():
        box = (c * 128, r * 128, (c + 1) * 128, (r + 1) * 128)
        raw_tiles[tile_id] = np.array(collage_img.crop(box))

    iso = raw_tiles[0]
    profile = iso[12:65, 64, :3].astype(float)
    
    tiles = {}
    for i in range(47):
        tiles[i] = generate_tile(i, raw_tiles, profile, iso)
        
    return tiles, Image.fromarray(iso)

def main():
    os.makedirs(OPTIFINE_CTM_DIR, exist_ok=True)
    os.makedirs(TEXTURES_DIR, exist_ok=True)

    with open(os.path.join(OPTIFINE_DIR, 'emissive.properties'), 'w', encoding='utf-8') as f:
        f.write("# OptiFine / Continuity emissive textures\nsuffix.emissive=_e\n")

    print(f"Generating true connected continuous CTM textures from {SRC_DIR}...")

    for color in COLORS:
        print(f"Processing {color} lamp...")
        
        path_src_on = os.path.join(SRC_DIR, f"{color}_lamp_on.png")
        path_src_off = os.path.join(SRC_DIR, f"{color}_lamp_off.png")
        path_src_e = os.path.join(SRC_DIR, f"{color}_lamp_on_e.png")
        
        img_on = Image.open(path_src_on).convert('RGBA')
        img_off = Image.open(path_src_off).convert('RGBA')
        img_e = Image.open(path_src_e).convert('RGBA')
        
        tiles_on, iso_on = generate_all_47_tiles(img_on)
        tiles_off, iso_off = generate_all_47_tiles(img_off)
        tiles_e, iso_e = generate_all_47_tiles(img_e)
        
        # 1. Lit state CTM directory
        dir_on = os.path.join(OPTIFINE_CTM_DIR, f"{color}_lamp_on")
        os.makedirs(dir_on, exist_ok=True)
        for idx in range(47):
            tiles_on[idx].save(os.path.join(dir_on, f"{idx}.png"))
            tiles_e[idx].save(os.path.join(dir_on, f"{idx}_e.png"))
            
        with open(os.path.join(dir_on, f"{color}_lamp_on.properties"), 'w', encoding='utf-8') as f:
            f.write(f"matchTiles=justlights:block/{color}_lamp_on\n")
            f.write(f"matchBlocks=justlights:{color}_lamp\n")
            f.write(f"method=ctm\n")
            f.write(f"tiles=0-46\n")
            f.write(f"connect=tile\n")
            f.write(f"innerSeams=false\n")
            
        # 2. Unlit state CTM directory
        dir_off = os.path.join(OPTIFINE_CTM_DIR, f"{color}_lamp_off")
        os.makedirs(dir_off, exist_ok=True)
        for idx in range(47):
            tiles_off[idx].save(os.path.join(dir_off, f"{idx}.png"))
            
        with open(os.path.join(dir_off, f"{color}_lamp_off.properties"), 'w', encoding='utf-8') as f:
            f.write(f"matchTiles=justlights:block/{color}_lamp_off\n")
            f.write(f"matchBlocks=justlights:{color}_lamp\n")
            f.write(f"method=ctm\n")
            f.write(f"tiles=0-46\n")
            f.write(f"connect=tile\n")
            f.write(f"innerSeams=false\n")
            
        # 3. Base isolated 128x128 textures for standalone blocks
        iso_on.save(os.path.join(TEXTURES_DIR, f"{color}_lamp_on.png"))
        iso_off.save(os.path.join(TEXTURES_DIR, f"{color}_lamp_off.png"))
        iso_e.save(os.path.join(TEXTURES_DIR, f"{color}_lamp_on_e.png"))

    print("All 16 colors successfully generated with true continuous connected lighting!")

if __name__ == '__main__':
    main()
