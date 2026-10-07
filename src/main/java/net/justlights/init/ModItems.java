package net.justlights.init;

import net.justlights.JustLights;
import net.minecraft.core.Direction;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.StandingAndWallBlockItem;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.Map;

public class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(JustLights.MODID);

    public static final Map<DyeColor, DeferredItem<BlockItem>> LAMP_ITEMS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredItem<StandingAndWallBlockItem>> TORCH_ITEMS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredItem<BlockItem>> LANTERN_ITEMS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredItem<BlockItem>> CAMPFIRE_ITEMS = new EnumMap<>(DyeColor.class);

    public static final Map<DyeColor, DeferredItem<BlockItem>> FLOOR_LIGHT_ITEMS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredItem<BlockItem>> CHANDELIER_ITEMS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredItem<BlockItem>> JACK_O_LANTERN_ITEMS = new EnumMap<>(DyeColor.class);
    public static final Map<DyeColor, DeferredItem<StandingAndWallBlockItem>> UNDERWATER_TORCH_ITEMS = new EnumMap<>(DyeColor.class);

    static {
        for (DyeColor color : DyeColor.values()) {
            String colorName = color.getName();

            // 1. Lamp items
            String lampName = colorName + "_lamp";
            DeferredItem<BlockItem> lampItem = ITEMS.registerSimpleBlockItem(lampName, ModBlocks.getLamp(color));
            LAMP_ITEMS.put(color, lampItem);

            // 2. Torch items
            String torchName = colorName + "_torch";
            DeferredItem<StandingAndWallBlockItem> torchItem = ITEMS.register(torchName, () -> new StandingAndWallBlockItem(
                    ModBlocks.getTorch(color).get(),
                    ModBlocks.getWallTorch(color).get(),
                    new Item.Properties(),
                    Direction.DOWN
            ));
            TORCH_ITEMS.put(color, torchItem);

            // 3. Lantern items
            String lanternName = colorName + "_lantern";
            DeferredItem<BlockItem> lanternItem = ITEMS.registerSimpleBlockItem(lanternName, ModBlocks.getLantern(color));
            LANTERN_ITEMS.put(color, lanternItem);

            // 4. Campfire items
            String campfireName = colorName + "_campfire";
            DeferredItem<BlockItem> campfireItem = ITEMS.registerSimpleBlockItem(campfireName, ModBlocks.getCampfire(color));
            CAMPFIRE_ITEMS.put(color, campfireItem);

            // 5. Floor Light items
            String floorLightName = colorName + "_floor_light";
            DeferredItem<BlockItem> floorLightItem = ITEMS.registerSimpleBlockItem(floorLightName, ModBlocks.getFloorLight(color));
            FLOOR_LIGHT_ITEMS.put(color, floorLightItem);

            // 6. Chandelier items
            String chandelierName = colorName + "_chandelier";
            DeferredItem<BlockItem> chandelierItem = ITEMS.registerSimpleBlockItem(chandelierName, ModBlocks.getChandelier(color));
            CHANDELIER_ITEMS.put(color, chandelierItem);

            // 7. Jack o'Lantern items
            String jackName = colorName + "_jack_o_lantern";
            DeferredItem<BlockItem> jackItem = ITEMS.registerSimpleBlockItem(jackName, ModBlocks.getJackOLantern(color));
            JACK_O_LANTERN_ITEMS.put(color, jackItem);

            // 8. Underwater Torch items
            String uwTorchName = colorName + "_underwater_torch";
            DeferredItem<StandingAndWallBlockItem> uwTorchItem = ITEMS.register(uwTorchName, () -> new StandingAndWallBlockItem(
                    ModBlocks.getUnderwaterTorch(color).get(),
                    ModBlocks.getUnderwaterWallTorch(color).get(),
                    new Item.Properties(),
                    Direction.DOWN
            ));
            UNDERWATER_TORCH_ITEMS.put(color, uwTorchItem);
        }
    }

    public static DeferredItem<BlockItem> getLampItem(DyeColor color) {
        return LAMP_ITEMS.get(color);
    }

    public static DeferredItem<StandingAndWallBlockItem> getTorchItem(DyeColor color) {
        return TORCH_ITEMS.get(color);
    }

    public static DeferredItem<BlockItem> getLanternItem(DyeColor color) {
        return LANTERN_ITEMS.get(color);
    }

    public static DeferredItem<BlockItem> getCampfireItem(DyeColor color) {
        return CAMPFIRE_ITEMS.get(color);
    }

    public static DeferredItem<BlockItem> getFloorLightItem(DyeColor color) {
        return FLOOR_LIGHT_ITEMS.get(color);
    }

    public static DeferredItem<BlockItem> getChandelierItem(DyeColor color) {
        return CHANDELIER_ITEMS.get(color);
    }

    public static DeferredItem<BlockItem> getJackOLanternItem(DyeColor color) {
        return JACK_O_LANTERN_ITEMS.get(color);
    }

    public static DeferredItem<StandingAndWallBlockItem> getUnderwaterTorchItem(DyeColor color) {
        return UNDERWATER_TORCH_ITEMS.get(color);
    }
}
