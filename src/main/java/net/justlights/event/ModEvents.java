package net.justlights.event;

import net.justlights.JustLights;
import net.justlights.block.ColoredCampfireBlock;
import net.justlights.block.ColoredChandelierBlock;
import net.justlights.block.ColoredFloorLightBlock;
import net.justlights.block.ColoredJackOLanternBlock;
import net.justlights.block.ColoredLampBlock;
import net.justlights.block.ColoredUnderwaterTorchBlock;
import net.justlights.block.ColoredUnderwaterWallTorchBlock;
import net.justlights.init.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.TorchBlock;
import net.minecraft.world.level.block.WallTorchBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

import java.util.Map;

@EventBusSubscriber(modid = JustLights.MODID)
public class ModEvents {

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        Level level = event.getLevel();
        BlockPos pos = event.getPos();
        Player player = event.getEntity();
        InteractionHand hand = event.getHand();
        ItemStack heldItem = player.getItemInHand(hand);

        if (!(heldItem.getItem() instanceof DyeItem dyeItem)) {
            return;
        }

        DyeColor newColor = dyeItem.getDyeColor();
        BlockState currentState = level.getBlockState(pos);
        Block currentBlock = currentState.getBlock();

        Block targetBlock = null;

        // 1. Lamp
        if (currentBlock instanceof ColoredLampBlock lampBlock) {
            if (lampBlock.getColor() != newColor) {
                targetBlock = ModBlocks.getLamp(newColor).get();
            }
        }
        // 2. Floor Light
        else if (currentBlock instanceof ColoredFloorLightBlock floorLight) {
            if (floorLight.getColor() != newColor) {
                targetBlock = ModBlocks.getFloorLight(newColor).get();
            }
        }
        // 3. Underwater Torch / Wall Torch
        else if (currentBlock instanceof ColoredUnderwaterTorchBlock uwTorch) {
            if (uwTorch.getColor() != newColor) {
                targetBlock = ModBlocks.getUnderwaterTorch(newColor).get();
            }
        }
        else if (currentBlock instanceof ColoredUnderwaterWallTorchBlock uwWallTorch) {
            if (uwWallTorch.getColor() != newColor) {
                targetBlock = ModBlocks.getUnderwaterWallTorch(newColor).get();
            }
        }
        // 4. Regular Torch / Wall Torch
        else if (currentBlock instanceof WallTorchBlock) {
            for (Map.Entry<DyeColor, ?> entry : ModBlocks.COLORED_WALL_TORCHES.entrySet()) {
                if (entry.getValue() != null && entry.getKey() != newColor) {
                    Block b = ModBlocks.getWallTorch(entry.getKey()).get();
                    if (b == currentBlock) {
                        targetBlock = ModBlocks.getWallTorch(newColor).get();
                        break;
                    }
                }
            }
        }
        else if (currentBlock instanceof TorchBlock) {
            for (Map.Entry<DyeColor, ?> entry : ModBlocks.COLORED_TORCHES.entrySet()) {
                if (entry.getValue() != null && entry.getKey() != newColor) {
                    Block b = ModBlocks.getTorch(entry.getKey()).get();
                    if (b == currentBlock) {
                        targetBlock = ModBlocks.getTorch(newColor).get();
                        break;
                    }
                }
            }
        }
        // 5. Lantern
        else if (currentBlock instanceof LanternBlock) {
            for (Map.Entry<DyeColor, ?> entry : ModBlocks.COLORED_LANTERNS.entrySet()) {
                if (entry.getValue() != null && entry.getKey() != newColor) {
                    Block b = ModBlocks.getLantern(entry.getKey()).get();
                    if (b == currentBlock) {
                        targetBlock = ModBlocks.getLantern(newColor).get();
                        break;
                    }
                }
            }
        }
        // 6. Campfire
        else if (currentBlock instanceof ColoredCampfireBlock campfireBlock) {
            if (campfireBlock.getColor() != newColor) {
                targetBlock = ModBlocks.getCampfire(newColor).get();
            }
        }
        // 7. Chandelier
        else if (currentBlock instanceof ColoredChandelierBlock chandelierBlock) {
            if (chandelierBlock.getColor() != newColor) {
                targetBlock = ModBlocks.getChandelier(newColor).get();
            }
        }
        // 8. Jack o'Lantern
        else if (currentBlock instanceof ColoredJackOLanternBlock jackBlock) {
            if (jackBlock.getColor() != newColor) {
                targetBlock = ModBlocks.getJackOLantern(newColor).get();
            }
        }

        if (targetBlock != null) {
            if (!level.isClientSide) {
                BlockState newState = targetBlock.defaultBlockState();
                for (Property<?> property : currentState.getProperties()) {
                    if (newState.hasProperty(property)) {
                        newState = copyProperty(currentState, newState, property);
                    }
                }
                level.setBlock(pos, newState, Block.UPDATE_ALL);
                level.playSound(null, pos, SoundEvents.DYE_USE, SoundSource.BLOCKS, 1.0F, 1.0F);

                if (!player.getAbilities().instabuild) {
                    heldItem.shrink(1);
                }
            }
            event.setCanceled(true);
            event.setCancellationResult(InteractionResult.sidedSuccess(level.isClientSide));
        }
    }

    @SuppressWarnings("unchecked")
    private static <T extends Comparable<T>> BlockState copyProperty(BlockState from, BlockState to, Property<T> property) {
        return to.setValue(property, from.getValue(property));
    }
}
