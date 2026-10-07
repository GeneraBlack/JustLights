package net.justlights.block;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;

public class ColoredFloorLightBlock extends Block {
    public static final BooleanProperty LIT = BlockStateProperties.LIT;
    public static final IntegerProperty BRIGHTNESS = IntegerProperty.create("brightness", 1, 3);
    private final DyeColor color;

    public ColoredFloorLightBlock(DyeColor color) {
        super(BlockBehaviour.Properties.of()
                .strength(3.0F)
                .sound(SoundType.METAL)
                .lightLevel(ColoredFloorLightBlock::getLightValue)
        );
        this.color = color;
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(LIT, true)
                .setValue(BRIGHTNESS, 3));
    }

    public static int getLightValue(BlockState state) {
        if (!state.getValue(LIT)) return 0;
        int b = state.getValue(BRIGHTNESS);
        return switch (b) {
            case 1 -> 5;
            case 2 -> 10;
            default -> 15;
        };
    }

    public DyeColor getColor() {
        return this.color;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(LIT, BRIGHTNESS);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hitResult) {
        if (!level.isClientSide) {
            // Shift + Right-Click: Cycle Dimmable Brightness (15 -> 10 -> 5)
            if (player.isShiftKeyDown()) {
                int b = state.getValue(BRIGHTNESS);
                int nextB = (b == 3) ? 2 : ((b == 2) ? 1 : 3);
                level.setBlock(pos, state.setValue(BRIGHTNESS, nextB).setValue(LIT, true), Block.UPDATE_ALL);
                float pitch = (nextB == 3) ? 1.4F : ((nextB == 2) ? 1.1F : 0.8F);
                level.playSound(null, pos, SoundEvents.METAL_HIT, SoundSource.BLOCKS, 0.5F, pitch);

                Component msg = Component.translatable("message.justlights.brightness_" + nextB);
                player.displayClientMessage(msg, true);
                return InteractionResult.CONSUME;
            }

            // Normal Right-Click: ON / OFF
            boolean isLit = state.getValue(LIT);
            level.setBlock(pos, state.setValue(LIT, !isLit), Block.UPDATE_ALL);
            level.playSound(null, pos, SoundEvents.METAL_HIT, SoundSource.BLOCKS, 0.5F, !isLit ? 1.2F : 0.8F);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock, BlockPos fromPos, boolean isMoving) {
        if (!level.isClientSide) {
            boolean hasSignal = level.hasNeighborSignal(pos);
            if (hasSignal && !state.getValue(LIT)) {
                level.setBlock(pos, state.setValue(LIT, true), Block.UPDATE_ALL);
            }
        }
    }
}
