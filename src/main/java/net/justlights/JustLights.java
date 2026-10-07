package net.justlights;

import com.mojang.logging.LogUtils;
import net.justlights.init.ModBlocks;
import net.justlights.init.ModCreativeModeTabs;
import net.justlights.init.ModItems;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.BlockEntityTypeAddBlocksEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import org.slf4j.Logger;

@Mod(JustLights.MODID)
public class JustLights {
    public static final String MODID = "justlights";
    public static final Logger LOGGER = LogUtils.getLogger();

    public JustLights(IEventBus modEventBus) {
        LOGGER.info("Initializing JustLights Mod for 1.21.1!");

        ModBlocks.BLOCKS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModCreativeModeTabs.CREATIVE_MODE_TABS.register(modEventBus);

        modEventBus.addListener(this::onBlockEntityTypeAddBlocks);
        modEventBus.addListener(this::onClientSetup);
    }

    private void onClientSetup(net.neoforged.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            net.justlights.client.ShaderpackIntegrator.integrateShaderpacks();
        });
    }

    private void onBlockEntityTypeAddBlocks(BlockEntityTypeAddBlocksEvent event) {
        Block[] campfires = ModBlocks.COLORED_CAMPFIRES.values().stream()
                .map(DeferredBlock::get)
                .toArray(Block[]::new);
        event.modify(BlockEntityType.CAMPFIRE, campfires);
    }
}
