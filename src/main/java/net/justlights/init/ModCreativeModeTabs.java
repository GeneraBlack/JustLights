package net.justlights.init;

import net.justlights.JustLights;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.DyeColor;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModCreativeModeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, JustLights.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> JUST_LIGHTS_TAB =
            CREATIVE_MODE_TABS.register("just_lights_tab", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.justlights"))
                    .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
                    .icon(() -> ModItems.getLanternItem(DyeColor.CYAN).get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        // 1. All Lamps
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getLampItem(color).get());
                        }
                        // 2. All Torches
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getTorchItem(color).get());
                        }
                        // 3. All Lanterns
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getLanternItem(color).get());
                        }
                        // 4. All Campfires
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getCampfireItem(color).get());
                        }
                        // 5. All Floor Lights
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getFloorLightItem(color).get());
                        }
                        // 6. All Chandeliers
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getChandelierItem(color).get());
                        }
                        // 7. All Jack o'Lanterns
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getJackOLanternItem(color).get());
                        }
                        // 8. All Underwater Torches
                        for (DyeColor color : DyeColor.values()) {
                            output.accept(ModItems.getUnderwaterTorchItem(color).get());
                        }
                    })
                    .build());
}
