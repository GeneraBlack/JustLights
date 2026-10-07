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

def bilinear_interp(arr, src_y, src_x):
    H, W, C = arr.shape
    y0 = np.clip(np.floor(src_y).astype(int), 0, H - 2)
    y1 = y0 + 1
    fy = (src_y - y0).reshape(-1, 1, 1)
    
    x0 = np.clip(np.floor(src_x).astype(int), 0, W - 2)
    x1 = x0 + 1
    fx = (src_x - x0).reshape(1, -1, 1)
    
    Ia = arr[y0[:, None], x0[None, :], :]
    Ib = arr[y0[:, None], x1[None, :], :]
    Ic = arr[y1[:, None], x0[None, :], :]
    Id = arr[y1[:, None], x1[None, :], :]
    
    top = Ia * (1.0 - fx) + Ib * fx
    bot = Ic * (1.0 - fx) + Id * fx
    return top * (1.0 - fy) + bot * fy

def warp_glass(arr, x_bounds, y_bounds, tgt_cx, tgt_cy):
    H, W, C = arr.shape
    orig_cx, orig_cy = 63.5, 63.5
    x_min, x_max = x_bounds
    y_min, y_max = y_bounds
    
    src_x = np.arange(W, dtype=float)
    if tgt_cx != orig_cx and x_max > x_min:
        m_l = (src_x >= x_min) & (src_x <= tgt_cx)
        m_r = (src_x > tgt_cx) & (src_x <= x_max)
        if tgt_cx > x_min:
            src_x[m_l] = x_min + (src_x[m_l] - x_min) * ((orig_cx - x_min) / (tgt_cx - x_min))
        if x_max > tgt_cx:
            src_x[m_r] = orig_cx + (src_x[m_r] - tgt_cx) * ((x_max - orig_cx) / (x_max - tgt_cx))
            
    src_y = np.arange(H, dtype=float)
    if tgt_cy != orig_cy and y_max > y_min:
        m_t = (src_y >= y_min) & (src_y <= tgt_cy)
        m_b = (src_y > tgt_cy) & (src_y <= y_max)
        if tgt_cy > y_min:
            src_y[m_t] = y_min + (src_y[m_t] - y_min) * ((orig_cy - y_min) / (tgt_cy - y_min))
        if y_max > tgt_cy:
            src_y[m_b] = orig_cy + (src_y[m_b] - tgt_cy) * ((y_max - orig_cy) / (y_max - tgt_cy))
            
    return bilinear_interp(arr, src_y, src_x)

def get_bezel_falloff_1d(coords, center, has_neg, has_pos, bezel_dist=52.0):
    w = np.ones_like(coords, dtype=float)
    if has_neg:
        neg_mask = coords < center
        d = center - coords[neg_mask]
        w[neg_mask] = np.clip(1.0 - (d / bezel_dist)**2, 0.0, 1.0)
    if has_pos:
        pos_mask = coords > center
        d = coords[pos_mask] - center
        w[pos_mask] = np.clip(1.0 - (d / bezel_dist)**2, 0.0, 1.0)
    return w

def process_cardinal_tile(orig_tile_img, has_t, has_b, has_l, has_r, peak_color, ratio=0.85, bw=12):
    arr = np.array(orig_tile_img).astype(float)
    H, W, C = arr.shape
    
    x_min = bw if has_l else 0
    x_max = W - bw if has_r else W
    y_min = bw if has_t else 0
    y_max = H - bw if has_b else H
    
    tgt_cx = (x_min + x_max) / 2.0
    tgt_cy = (y_min + y_max) / 2.0
    
    # 1. Warp glass so bulb sits at exact geometric center of the visible glass window
    warped = warp_glass(arr, (x_min, x_max), (y_min, y_max), tgt_cx, tgt_cy)
    
    if ratio > 0:
        # 2. Add smooth bridging light towards open edges so connected lamps transition seamlessly
        y_coords = np.arange(H).reshape(-1, 1)
        x_coords = np.arange(W).reshape(1, -1)
        
        w_y_bezel = get_bezel_falloff_1d(y_coords, tgt_cy, has_t, has_b)
        w_x_bezel = get_bezel_falloff_1d(x_coords, tgt_cx, has_l, has_r)
        
        bridge = np.zeros((H, W), dtype=float)
        
        # Right open edge
        if not has_r:
            dx = np.maximum(0.0, x_coords - tgt_cx)
            t = dx / (W - tgt_cx)
            w_x = np.sin(t * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, w_x * w_y_bezel * ratio)
            
        # Left open edge
        if not has_l:
            dx = np.maximum(0.0, tgt_cx - x_coords)
            t = dx / tgt_cx
            w_x = np.sin(t * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, w_x * w_y_bezel * ratio)
            
        # Bottom open edge
        if not has_b:
            dy = np.maximum(0.0, y_coords - tgt_cy)
            t = dy / (H - tgt_cy)
            w_y = np.sin(t * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, w_y * w_x_bezel * ratio)
            
        # Top open edge
        if not has_t:
            dy = np.maximum(0.0, tgt_cy - y_coords)
            t = dy / tgt_cy
            w_y = np.sin(t * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, w_y * w_x_bezel * ratio)
            
        # Inner diagonal corners (when both adjacent edges are open)
        if not has_r and not has_b:
            dx = np.maximum(0.0, x_coords - tgt_cx) / (W - tgt_cx)
            dy = np.maximum(0.0, y_coords - tgt_cy) / (H - tgt_cy)
            diag = np.sin(np.minimum(dx, dy) * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, diag * ratio)
        if not has_l and not has_b:
            dx = np.maximum(0.0, tgt_cx - x_coords) / tgt_cx
            dy = np.maximum(0.0, y_coords - tgt_cy) / (H - tgt_cy)
            diag = np.sin(np.minimum(dx, dy) * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, diag * ratio)
        if not has_r and not has_t:
            dx = np.maximum(0.0, x_coords - tgt_cx) / (W - tgt_cx)
            dy = np.maximum(0.0, tgt_cy - y_coords) / tgt_cy
            diag = np.sin(np.minimum(dx, dy) * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, diag * ratio)
        if not has_l and not has_t:
            dx = np.maximum(0.0, tgt_cx - x_coords) / tgt_cx
            dy = np.maximum(0.0, tgt_cy - y_coords) / tgt_cy
            diag = np.sin(np.minimum(dx, dy) * (np.pi / 2.0)) ** 1.5
            bridge = np.maximum(bridge, diag * ratio)
            
        glass_mask = (x_coords >= x_min) & (x_coords < x_max) & (y_coords >= y_min) & (y_coords < y_max)
        out = warped.copy()
        for ch in range(3):
            diff = np.maximum(0.0, peak_color[ch] - warped[:, :, ch])
            out[:, :, ch] += bridge * diff * glass_mask
    else:
        out = warped.copy()
        
    # 3. Always preserve exact 100% authentic metal bezel borders and bolts
    if has_t: out[:bw, :, :] = arr[:bw, :, :]
    if has_b: out[H-bw:, :, :] = arr[H-bw:, :, :]
    if has_l: out[:, :bw, :] = arr[:, :bw, :]
    if has_r: out[:, W-bw:, :] = arr[:, W-bw:, :]
    
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def generate_tiles(collage_img, peak_color, ratio=0.85, bw=12):
    cardinal_tiles = {}
    for tile_id, (r, c) in CARDINAL_ROW_COL.items():
        box = (c * 128, r * 128, (c + 1) * 128, (r + 1) * 128)
        raw_tile = collage_img.crop(box)
        has_t, has_b, has_l, has_r = CARDINAL_BORDERS[tile_id]
        if tile_id == 0:
            # Standalone tile 0 is 100% untouched
            cardinal_tiles[0] = raw_tile
        else:
            cardinal_tiles[tile_id] = process_cardinal_tile(
                raw_tile, has_t, has_b, has_l, has_r, peak_color, ratio=ratio, bw=bw
            )

    iso = cardinal_tiles[0]
    cap_tl = iso.crop((0, 0, bw, bw))
    cap_tr = iso.crop((128 - bw, 0, 128, bw))
    cap_bl = iso.crop((0, 128 - bw, bw, 128))
    cap_br = iso.crop((128 - bw, 128 - bw, 128, 128))

    tiles = {}
    for tile_idx in range(47):
        base_id, caps = TILE_DEFINITIONS[tile_idx]
        img = cardinal_tiles[base_id].copy()
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


# Ensure output directories exist
os.makedirs(OPTIFINE_CTM_DIR, exist_ok=True)
os.makedirs(TEXTURES_DIR, exist_ok=True)

# Write emissive.properties
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
    
    peak_on = np.array(img_on.crop((0, 0, 128, 128)))[64, 64, :3].astype(float)
    peak_off = np.array(img_off.crop((0, 0, 128, 128)))[64, 64, :3].astype(float)
    peak_e = np.array(img_e.crop((0, 0, 128, 128)))[64, 64, :3].astype(float)
    
    tiles_on, iso_on = generate_tiles(img_on, peak_on, ratio=0.85)
    tiles_off, iso_off = generate_tiles(img_off, peak_off, ratio=0.5)
    tiles_e, iso_e = generate_tiles(img_e, peak_e, ratio=0.85)
    
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

print("All 16 colors successfully generated and updated with perfect centered bulbs and seamless transitions!")
