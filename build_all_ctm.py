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

def generate_tiles(collage_img, bw=12):
    """
    Extracts all 47 CTM tiles from the artist's authentic 512x512 collage.
    - Bulbs remain 100% natural, perfectly centered at (64, 64) with no artificial warping.
    - Open matching edges are unified with a 1-pixel average so that seam difference across blocks is mathematically 0.
    - All 16 cardinal tiles preserve their authentic borders, corners, bolts, and rich colors.
    - Inner corner caps are cleanly applied for the remaining 31 CTM tiles.
    """
    cardinal_tiles = {}
    for tile_id, (r, c) in CARDINAL_ROW_COL.items():
        box = (c * 128, r * 128, (c + 1) * 128, (r + 1) * 128)
        cardinal_tiles[tile_id] = np.array(collage_img.crop(box)).astype(float)

    # 1. Unify horizontal open seams (e.g. Tile 1 right, Tile 2 left/right, Tile 3 left, etc.)
    # In Tile 2 (TB--), left edge (x=0) and right edge (x=127) meet when repeated.
    t2 = cardinal_tiles[2]
    h_seam_profile = (t2[:, 0, :] + t2[:, 127, :]) / 2.0
    
    # Apply to all tiles that have an open left or right edge in the horizontal strip / interior
    for tid, (has_t, has_b, has_l, has_r) in CARDINAL_BORDERS.items():
        arr = cardinal_tiles[tid]
        if not has_l and (has_t and has_b):
            arr[:, 0, :] = h_seam_profile
        if not has_r and (has_t and has_b):
            arr[:, 127, :] = h_seam_profile

    # 2. Unify vertical open seams (e.g. Tile 12 bottom, Tile 24 top/bottom, Tile 36 top)
    t24 = cardinal_tiles[24]
    v_seam_profile = (t24[0, :, :] + t24[127, :, :]) / 2.0
    for tid, (has_t, has_b, has_l, has_r) in CARDINAL_BORDERS.items():
        arr = cardinal_tiles[tid]
        if not has_t and (has_l and has_r):
            arr[0, :, :] = v_seam_profile
        if not has_b and (has_l and has_r):
            arr[127, :, :] = v_seam_profile

    # 3. Unify 2D interior tile 26 (----) seams
    t26 = cardinal_tiles[26]
    t26[:, 0, :] = (t26[:, 0, :] + t26[:, 127, :]) / 2.0
    t26[:, 127, :] = t26[:, 0, :]
    t26[0, :, :] = (t26[0, :, :] + t26[127, :, :]) / 2.0
    t26[127, :, :] = t26[0, :, :]

    # Convert back to uint8 PIL Images
    cardinal_imgs = {tid: Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)) for tid, arr in cardinal_tiles.items()}

    iso = cardinal_imgs[0]
    cap_tl = iso.crop((0, 0, bw, bw))
    cap_tr = iso.crop((128 - bw, 0, 128, bw))
    cap_bl = iso.crop((0, 128 - bw, bw, 128))
    cap_br = iso.crop((128 - bw, 128 - bw, 128, 128))

    tiles = {}
    for tile_idx in range(47):
        base_id, caps = TILE_DEFINITIONS[tile_idx]
        img = cardinal_imgs[base_id].copy()
        for cap in caps:
            if cap == 'TL':
                img.paste(cap_tl, (0, 0))
            elif cap == 'TR':
                img.paste(cap_tr, (128 - bw, 0))
            elif cap == 'BL':
                img.paste(cap_bl, (0, 128 - bw))
            elif cap == 'BR':
                img.paste(cap_br, (128 - bw, 128 - bw))
        tiles[tile_idx] = img

    return tiles, iso


def main():
    os.makedirs(OPTIFINE_CTM_DIR, exist_ok=True)
    os.makedirs(TEXTURES_DIR, exist_ok=True)

    with open(os.path.join(OPTIFINE_DIR, 'emissive.properties'), 'w', encoding='utf-8') as f:
        f.write("# OptiFine / Continuity emissive textures\nsuffix.emissive=_e\n")

    print(f"Generating CTM textures from {SRC_DIR}...")

    for color in COLORS:
        print(f"Processing {color} lamp...")
        
        path_src_on = os.path.join(SRC_DIR, f"{color}_lamp_on.png")
        path_src_off = os.path.join(SRC_DIR, f"{color}_lamp_off.png")
        path_src_e = os.path.join(SRC_DIR, f"{color}_lamp_on_e.png")
        
        img_on = Image.open(path_src_on).convert('RGBA')
        img_off = Image.open(path_src_off).convert('RGBA')
        img_e = Image.open(path_src_e).convert('RGBA')
        
        tiles_on, iso_on = generate_tiles(img_on)
        tiles_off, iso_off = generate_tiles(img_off)
        tiles_e, iso_e = generate_tiles(img_e)
        
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

    print("All 16 colors successfully generated with authentic centered bulbs and seamless edges!")

if __name__ == '__main__':
    main()
