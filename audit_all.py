import os, json, glob, re

BASE = r"D:\projekt\JustLights"
SRC_MAIN = os.path.join(BASE, "src", "main")
ASSETS = os.path.join(SRC_MAIN, "resources", "assets", "justlights")
DATA = os.path.join(SRC_MAIN, "resources", "data", "justlights")
JAVA_BLOCKS = os.path.join(SRC_MAIN, "java", "net", "justlights", "init", "ModBlocks.java")
JAVA_ITEMS = os.path.join(SRC_MAIN, "java", "net", "justlights", "init", "ModItems.java")

issues = []

DYE_COLORS = [
    "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
    "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"
]

BLOCK_TYPES = [
    "{color}_lamp",
    "{color}_torch",
    "{color}_wall_torch",
    "{color}_lantern",
    "{color}_campfire",
    "{color}_floor_light",
    "{color}_chandelier",
    "{color}_jack_o_lantern",
    "{color}_underwater_torch",
    "{color}_underwater_wall_torch"
]

ITEM_TYPES = [
    "{color}_lamp",
    "{color}_torch",
    "{color}_lantern",
    "{color}_campfire",
    "{color}_floor_light",
    "{color}_chandelier",
    "{color}_jack_o_lantern",
    "{color}_underwater_torch"
]

registered_blocks = [bt.format(color=c) for c in DYE_COLORS for bt in BLOCK_TYPES]
registered_items = [it.format(color=c) for c in DYE_COLORS for it in ITEM_TYPES]
print(f"Total registered blocks in Java: {len(registered_blocks)}")
print(f"Total registered items in Java: {len(registered_items)}")

# Check blockstates exist for all blocks
for b in registered_blocks:
    bs_file = os.path.join(ASSETS, "blockstates", f"{b}.json")
    if not os.path.exists(bs_file):
        issues.append(f"Missing blockstate file: {b}.json")

# Check item models exist for all items
for item in registered_items:
    im_file = os.path.join(ASSETS, "models", "item", f"{item}.json")
    if not os.path.exists(im_file):
        issues.append(f"Missing item model file: {item}.json")

# Check loot tables exist for all blocks
for b in registered_blocks:
    lt_file = os.path.join(DATA, "loot_table", "blocks", f"{b}.json")
    if not os.path.exists(lt_file):
        issues.append(f"Missing loot table for block: {b}.json")

# --- 3. Check every Blockstate -> Model ---
blockstate_files = glob.glob(os.path.join(ASSETS, "blockstates", "*.json"))
print(f"Total blockstate files: {len(blockstate_files)}")

for bs_path in blockstate_files:
    bs_name = os.path.basename(bs_path)
    with open(bs_path, "r", encoding="utf-8") as f:
        try:
            bs_data = json.load(f)
        except Exception as e:
            issues.append(f"JSON syntax error in blockstate {bs_name}: {e}")
            continue
            
    models_to_check = []
    if "variants" in bs_data:
        for v_name, v_data in bs_data["variants"].items():
            if isinstance(v_data, list):
                for e in v_data: models_to_check.append((v_name, e.get("model")))
            elif isinstance(v_data, dict):
                models_to_check.append((v_name, v_data.get("model")))
    if "multipart" in bs_data:
        for part in bs_data["multipart"]:
            apply = part.get("apply", {})
            if isinstance(apply, list):
                for e in apply: models_to_check.append(("multipart", e.get("model")))
            elif isinstance(apply, dict):
                models_to_check.append(("multipart", apply.get("model")))

    for variant_name, m in models_to_check:
        if not m:
            issues.append(f"Empty model in {bs_name} ({variant_name})")
            continue
        if m.startswith("justlights:block/"):
            model_rel = m.replace("justlights:block/", "") + ".json"
            m_path = os.path.join(ASSETS, "models", "block", model_rel)
            if not os.path.exists(m_path):
                issues.append(f"Missing model: {m_path} referenced by {bs_name} ({variant_name})")

# --- 4. Check every Model -> Texture and Parent ---
model_files = glob.glob(os.path.join(ASSETS, "models", "**", "*.json"), recursive=True)
print(f"Total model files: {len(model_files)}")

for m_path in model_files:
    m_name = os.path.relpath(m_path, ASSETS)
    with open(m_path, "r", encoding="utf-8") as f:
        try:
            m_data = json.load(f)
        except Exception as e:
            issues.append(f"JSON syntax error in model {m_name}: {e}")
            continue
            
    # Check parent if local
    parent = m_data.get("parent")
    if parent and parent.startswith("justlights:"):
        parent_rel = parent.replace("justlights:", "") + ".json"
        p_path = os.path.join(ASSETS, "models", parent_rel)
        if not os.path.exists(p_path):
            issues.append(f"Missing parent model: {parent} in {m_name}")
            
    # Check textures
    textures = m_data.get("textures", {})
    for tex_key, tex_val in textures.items():
        if isinstance(tex_val, str) and tex_val.startswith("justlights:"):
            tex_rel = tex_val.replace("justlights:", "") + ".png"
            t_path = os.path.join(ASSETS, "textures", tex_rel)
            if not os.path.exists(t_path):
                issues.append(f"Missing texture: {tex_val} ({t_path}) in {m_name} (key: {tex_key})")

# --- 5. Check Lang Translations ---
en_lang = os.path.join(ASSETS, "lang", "en_us.json")
de_lang = os.path.join(ASSETS, "lang", "de_de.json")
with open(en_lang, "r", encoding="utf-8") as f: en_data = json.load(f)
with open(de_lang, "r", encoding="utf-8") as f: de_data = json.load(f)

for b in registered_blocks:
    key = f"block.justlights.{b}"
    if key not in en_data:
        issues.append(f"Missing EN lang for block: {key}")
    if key not in de_data:
        issues.append(f"Missing DE lang for block: {key}")

for item in registered_items:
    key = f"item.justlights.{item}"
    if key not in en_data:
        issues.append(f"Missing EN lang for item: {key}")
    if key not in de_data:
        issues.append(f"Missing DE lang for item: {key}")

print(f"\n================ AUDIT SUMMARY ================")
print(f"Total potential issues detected: {len(issues)}")
if issues:
    for i in issues[:30]:
        print(" [!] ", i)
else:
    print(" ALL CHECKS PASSED PERFECTLY! 100% HEALTHY!")
