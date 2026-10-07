# 🕯️ JustLights — Ultra-HD Colored Lighting & Rustic Fixtures

[![Minecraft 1.21.1](https://img.shields.io/badge/Minecraft-1.21.1-brightgreen.svg)](https://curseforge.com)
[![NeoForge](https://img.shields.io/badge/Modloader-NeoForge-orange.svg)](https://neoforged.net)
[![Shader Compatible](https://img.shields.io/badge/Shaders-Iris%20%7C%20BSL%20%7C%20Complementary-blue.svg)](https://curseforge.com)
[![Resolution](https://img.shields.io/badge/Textures-128x128%20Ultra--HD-purple.svg)](https://curseforge.com)

**JustLights** brings true, vibrant, colored illumination to Minecraft 1.21.1. Designed from the ground up for high-resolution texture packs, rustic town-building, and high-end shaders (**Iris, Sodium, Complementary Reimagined & BSL**), JustLights transforms your builds with handcrafted **128×128 Ultra-HD textures**, dynamic **Connected Textures (CTM)**, and **real colored light radiance** that illuminates surrounding walls and fog.

Whether you're decorating a medieval tavern, a sprawling town colony, an industrial mining dock, or a magical underwater grotto, JustLights has the perfect fixture for every build.

---

## ✨ Key Features

* 🎨 **All 16 Minecraft Dye Colors:** Every single fixture is available in all 16 colors.
* 💎 **128×128 Ultra-HD Handcrafted Textures:** Brushed anthracite frames, forged wrought-iron metalwork, rustic dark oak fibers, and frosted stained glass diffusers.
* 🌟 **Native Shader Integration & Emissive Maps:** Pre-configured `block.properties` for **Complementary Reimagined**, **BSL**, and **Iris**. Casts real colored voxel light onto floors, ceilings, and atmospheric fog!
* 🔗 **Connected Textures (Fusion CTM):** Multi-block lamp arrays dynamically connect into seamless fixtures without borders.
* 💡 **3-Stage Dimmable Brightness:** Adjust lamps and floor grates between ambient candlelight (Light 5), cozy room light (Light 10), and maximum security light (Light 15).
* 🌙 **Integrated Streetlight Mode (Day/Night Auto):** Lamps automatically turn on at dusk and shut off at sunrise—no Redstone wiring required!
* 🖌️ **In-World Dyeing:** Change the color of any placed JustLights fixture on the fly by simply right-clicking it with a dye in hand.
* 🍖 **Full Survival & Vanilla Mechanics:** 368 balanced recipes, explosion-proof block drops, and fully functional campfires that cook food!

---

## 🏮 The Fixtures Collection

### 1. 💡 Connected Fixture Lamps
* **Aesthetic:** Industrial brushed metal casing with hex bolts and frosted glass diffusers.
* **Connected Textures:** Seamlessly connects horizontally and vertically when placed together.
* **Controls:** Click to toggle on/off, or power with Redstone. Shift + Right-Click to adjust dimming or enable Streetlight mode.

### 2. 🕯️ Rustic Torches & Wall Torches
* **Aesthetic:** Hand-carved rustic dark oak shaft, forged iron collar, and glowing ember flame tip.
* **Special Particles:** Blue, Cyan, and Light Blue torches produce atmospheric Soul Fire particles (`SOUL_FIRE_FLAME`), while others produce dancing warm flame particles.

### 3. 🏮 Wrought-Iron Lanterns
* **Aesthetic:** Heavy wrought-iron cage with corner rivets, hanging loop, and glowing frosted glass core.
* **Placement:** Place on the floor, hang from ceilings/chains, or mount to walls.

### 4. 🔥 Cooking Campfires
* **Aesthetic:** Criss-cross oak logs over a glowing bed of pulsating embers with procedural leaping flames.
* **Full Mechanics:** Cooks up to 4 raw food items, produces cozy smoke (or high signal smoke with a hay bale underneath), can be extinguished with a shovel or water, and relit with flint & steel.

### 5. ⛓️ Heavy Floor Grate Lights
* **Aesthetic:** Flush cast-iron floor grates with recessed colored uplighting.
* **Ideal for:** Streets, town squares, harbor docks, castle courtyards, and mine cart tunnels. Smooth walkover with zero collision snags! Fully dimmable.

### 6. 👑 Wrought-Iron Chandeliers
* **Aesthetic:** 4-arm circular forged-iron chandelier with scrollwork arms, candle cups, wax candles, and 4 flickering flames.
* **Placement:** Hang from ceilings and chains or place as a freestanding candelabra. Waterloggable!

### 7. 🎃 Carved Jack o'Lanterns
* **Aesthetic:** Ribbed pumpkin rind featuring an ominous carved grin where the eyes, nose, and teeth radiate bright colored light. Rotatable in all 4 cardinal directions.

### 8. 🫧 Waterproof Diving Torches
* **Aesthetic:** Reinforced aged-bronze casing with waterproof resin and an eternal submerged flame.
* **Mechanics:** Waterloggable! Does not pop off when submerged in water and emits rising air bubbles. Perfect for canals, fountains, and underwater grottos.

---

## 🎮 How It Works & Controls

| Action | Control | Description |
| :--- | :--- | :--- |
| **Toggle Light** | **Right-Click** | Turns the lamp or floor grate on/off. Features a memory function that remembers your set brightness! |
| **Cycle Brightness** | **Shift + Right-Click** | Cycles through **100% (Light 15)** $\rightarrow$ **66% (Light 10)** $\rightarrow$ **33% (Light 5)** $\rightarrow$ **Streetlight Auto**. |
| **In-World Recolor** | **Right-Click with Dye** | Instantly changes the fixture's color without breaking it, preserving its on/off state and direction! |
| **Auto Streetlight** | **Shift + Right-Click** | Switches into automatic mode: light turns on when night falls and turns off at sunrise. |

---

## 🎨 Shader Compatibility & Recommended Settings

JustLights is built from the ground up for high-end shaders (**Complementary Reimagined**, **Euphoria Patches**, and **BSL**).

> [!TIP]
> **Automatic Shader Integration:** JustLights automatically detects Complementary Reimagined and BSL in your `shaderpacks` folder upon game launch and configures them so colored lighting works seamlessly out-of-the-box!

### 🌟 Recommended Complementary Settings (For Ultra-Vibrant Colored Radiance):
To get the most dramatic, vivid, and atmospheric colored light rays and volumetric fog, open **Options → Video Settings → Shader Packs → Shader Options**:

1. **Performance & Settings** (or **Other Settings**) → **ACT Features Settings**:
   * **`Colored Candle Light`**: **ON** *(Essential: allows all 16 dye colors to cast colored voxel radiance)*
   * **`Colored Light Saturation`**: **125%** *(Boosts color richness so it completely overrides bland yellowish light)*
   * **`Colored Light Fog`**: **ON** *(Enables gorgeous volumetric godrays and colored atmosphere in the air)*
   * **`Colored Light Fog Intensity`**: **1.00 – 1.50** *(Increases the intensity of colored light beams)*

2. **Performance Settings**:
   * **`Colored Lighting`**: **512** or **1024** *(Controls voxel volume radius and colored light distance)*

3. **Lighting & Atmosphere** (Optional for Extra Coziness):
   * **`Blocklight Flickering`**: **ON** *(Creates subtle cozy flame flicker for Torches, Lanterns & Campfires)*
   * **`World Space Reflections`**: **ON** *(Reflects glowing colored lamps on wet floors, puddles, and water!)*

### 💡 Non-Shader / Vanilla Experience
Even without shaders, JustLights looks stunning! Every block features handcrafted **128×128 Ultra-HD textures** with brushed metal frames, wrought-iron rivets, rustic wood fibers, and bright vanilla light emission (Light Level 15).

---

## 🛠️ Requirements & Recommendations

* **Minecraft:** 1.21.1
* **Mod Loader:** [NeoForge](https://neoforged.net) (21.1.x)
* **Recommended Mods for Maximum Visuals:**
  * [Iris Shaders](https://curseforge.com) + [Sodium](https://curseforge.com)
  * [Fusion (Connected Textures)](https://curseforge.com) *(enables dynamic connected textures for lamps)*
  * [Complementary Reimagined](https://curseforge.com) or [BSL Shaders](https://curseforge.com)

---

## 📜 Permissions & Modpacks
* **Modpacks:** Feel free to include **JustLights** in any CurseForge or Modrinth modpack! No permission needed.
* **Bug Reports & Suggestions:** Found an issue or have an idea for a new fixture? Leave a comment or open an issue on our GitHub repository.
