package net.justlights.init;

import net.justlights.JustLights;
import net.justlights.block.ColoredCampfireBlock;
import net.justlights.block.ColoredChandelierBlock;
import net.justlights.block.ColoredFloorLightBlock;
import net.justlights.block.ColoredJackOLanternBlock;
import net.justlights.block.ColoredLampBlock;
import net.justlights.block.ColoredUnderwaterTorchBlock;
import net.justlights.block.ColoredUnderwaterWallTorchBlock;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.TorchBlock;
import net.minecraft.world.level.block.WallTorchBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.Map;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(JustLights.MODID);

    public static final Map<DyeColor, DeferredBlock<ColoredLampBlock>> COLORED_LAMPS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<TorchBlock>> COLORED_TORCHES = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<WallTorchBlock>> COLORED_WALL_TORCHES = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<LanternBlock>> COLORED_LANTERNS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<ColoredCampfireBlock>> COLORED_CAMPFIRES = new EnumMap<>(DyeColor.class);

    public static final Map<DyeColor, DeferredBlock<ColoredFloorLightBlock>> COLORED_FLOOR_LIGHTS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<ColoredChandelierBlock>> COLORED_CHANDELIERS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<ColoredJackOLanternBlock>> COLORED_JACK_O_LANTERNS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<ColoredUnderwaterTorchBlock>> COLORED_UNDERWATER_TORCHES = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredBlock<ColoredUnderwaterWallTorchBlock>> COLORED_UNDERWATER_WALL_TORCHES = new EnumMap<>(DyeColor.class);

    static {
        for (DyeColor color : DyeColor.values()) {
            String colorName = color.getName();

            // 1. Lamps
            String lampName = colorName + "_lamp";
            DeferredBlock<ColoredLampBlock> lamp = BLOCKS.register(lampName, () -> new ColoredLampBlock(color));
            COLORED_LAMPS.put(color, lamp);

            // Particle selection: Blue tones get soul fire particles, others get classic flame
            SimpleParticleType particle = (color == DyeColor.BLUE || color == DyeColor.CYAN || color == DyeColor.LIGHT_BLUE)
                    ? ParticleTypes.SOUL_FIRE_FLAME
                    : ParticleTypes.FLAME;

            // 2. Torches (Standing & Wall)
            String torchName = colorName + "_torch";
            DeferredBlock<TorchBlock> torch = BLOCKS.register(torchName, () -> new TorchBlock(particle,
                    BlockBehaviour.Properties.of()
                            .noCollission()
                            .instabreak()
                            .lightLevel(state -> 15)
                            .sound(SoundType.WOOD)
            ));
            COLORED_TORCHES.put(color, torch);

            String wallTorchName = colorName + "_wall_torch";
            DeferredBlock<WallTorchBlock> wallTorch = BLOCKS.register(wallTorchName, () -> new WallTorchBlock(particle,
                    BlockBehaviour.Properties.of()
                            .noCollission()
                            .instabreak()
                            .lightLevel(state -> 15)
                            .sound(SoundType.WOOD)
                            .dropsLike(torch.get())
            ));
            COLORED_WALL_TORCHES.put(color, wallTorch);

            // 3. Lanterns
            String lanternName = colorName + "_lantern";
            DeferredBlock<LanternBlock> lantern = BLOCKS.register(lanternName, () -> new LanternBlock(
                    BlockBehaviour.Properties.of()
                            .strength(3.5F)
                            .sound(SoundType.LANTERN)
                            .lightLevel(state -> 15)
                            .noOcclusion()
            ));
            COLORED_LANTERNS.put(color, lantern);

            // 4. Campfires
            String campfireName = colorName + "_campfire";
            DeferredBlock<ColoredCampfireBlock> campfire = BLOCKS.register(campfireName, () -> new ColoredCampfireBlock(
                    color,
                    BlockBehaviour.Properties.of()
                            .mapColor(MapColor.PODZOL)
                            .instrument(NoteBlockInstrument.BASS)
                            .strength(2.0F)
                            .sound(SoundType.WOOD)
                            .lightLevel(state -> state.getValue(CampfireBlock.LIT) ? 15 : 0)
                            .noOcclusion()
                            .ignitedByLava()
            ));
            COLORED_CAMPFIRES.put(color, campfire);

            // 5. Floor Grate Lights
            String floorLightName = colorName + "_floor_light";
            DeferredBlock<ColoredFloorLightBlock> floorLight = BLOCKS.register(floorLightName, () -> new ColoredFloorLightBlock(color));
            COLORED_FLOOR_LIGHTS.put(color, floorLight);

            // 6. Chandeliers
            String chandelierName = colorName + "_chandelier";
            DeferredBlock<ColoredChandelierBlock> chandelier = BLOCKS.register(chandelierName, () -> new ColoredChandelierBlock(color));
            COLORED_CHANDELIERS.put(color, chandelier);

            // 7. Jack o'Lanterns
            String jackName = colorName + "_jack_o_lantern";
            DeferredBlock<ColoredJackOLanternBlock> jack = BLOCKS.register(jackName, () -> new ColoredJackOLanternBlock(color));
            COLORED_JACK_O_LANTERNS.put(color, jack);

            // 8. Underwater Torches (Standing & Wall)
            String uwTorchName = colorName + "_underwater_torch";
            DeferredBlock<ColoredUnderwaterTorchBlock> uwTorch = BLOCKS.register(uwTorchName, () -> new ColoredUnderwaterTorchBlock(color, particle));
            COLORED_UNDERWATER_TORCHES.put(color, uwTorch);

            String uwWallTorchName = colorName + "_underwater_wall_torch";
            DeferredBlock<ColoredUnderwaterWallTorchBlock> uwWallTorch = BLOCKS.register(uwWallTorchName, () -> new ColoredUnderwaterWallTorchBlock(color, particle));
            COLORED_UNDERWATER_WALL_TORCHES.put(color, uwWallTorch);
        }
    }

    public static DeferredBlock<ColoredLampBlock> getLamp(DyeColor color) {
        return COLORED_LAMPS.get(color);
    }

    public static DeferredBlock<TorchBlock> getTorch(DyeColor color) {
        return COLORED_TORCHES.get(color);
    }

    public static DeferredBlock<WallTorchBlock> getWallTorch(DyeColor color) {
        return COLORED_WALL_TORCHES.get(color);
    }

    public static DeferredBlock<LanternBlock> getLantern(DyeColor color) {
        return COLORED_LANTERNS.get(color);
    }

    public static DeferredBlock<ColoredCampfireBlock> getCampfire(DyeColor color) {
        return COLORED_CAMPFIRES.get(color);
    }

    public static DeferredBlock<ColoredFloorLightBlock> getFloorLight(DyeColor color) {
        return COLORED_FLOOR_LIGHTS.get(color);
    }

    public static DeferredBlock<ColoredChandelierBlock> getChandelier(DyeColor color) {
        return COLORED_CHANDELIERS.get(color);
    }

    public static DeferredBlock<ColoredJackOLanternBlock> getJackOLantern(DyeColor color) {
        return COLORED_JACK_O_LANTERNS.get(color);
    }

    public static DeferredBlock<ColoredUnderwaterTorchBlock> getUnderwaterTorch(DyeColor color) {
        return COLORED_UNDERWATER_TORCHES.get(color);
    }

    public static DeferredBlock<ColoredUnderwaterWallTorchBlock> getUnderwaterWallTorch(DyeColor color) {
        return COLORED_UNDERWATER_WALL_TORCHES.get(color);
    }
}
