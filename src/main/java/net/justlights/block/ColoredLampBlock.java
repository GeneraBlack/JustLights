package net.justlights.block;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
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

public class ColoredLampBlock extends Block {
    public static final BooleanProperty LIT = BlockStateProperties.LIT;
    public static final BooleanProperty AUTO = BooleanProperty.create("auto");
    public static final IntegerProperty BRIGHTNESS = IntegerProperty.create("brightness", 1, 3);
    private final DyeColor color;

    public ColoredLampBlock(DyeColor color) {
        super(BlockBehaviour.Properties.of()
                .strength(0.3F)
                .sound(SoundType.GLASS)
                .lightLevel(ColoredLampBlock::getLightValue)
        );
        this.color = color;
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(LIT, true)
                .setValue(AUTO, false)
                .setValue(BRIGHTNESS, 3));
    }

    public static int getLightValue(BlockState state) {
        if (!state.getValue(LIT)) {
            return 0;
        }
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
        builder.add(LIT, AUTO, BRIGHTNESS);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hitResult) {
        if (!level.isClientSide) {
            // Shift + Right-Click: Cycle Dimmable Brightness (15 -> 10 -> 5 -> Streetlight Auto)
            if (player.isShiftKeyDown()) {
                boolean isAuto = state.getValue(AUTO);
                int brightness = state.getValue(BRIGHTNESS);

                boolean newAuto = false;
                int newBrightness = 3;
                Component msg;
                float pitch = 1.4F;

                if (isAuto) {
                    newAuto = false;
                    newBrightness = 3;
                    pitch = 1.4F;
                    msg = Component.translatable("message.justlights.brightness_3");
                } else if (brightness == 3) {
                    newAuto = false;
                    newBrightness = 2;
                    pitch = 1.1F;
                    msg = Component.translatable("message.justlights.brightness_2");
                } else if (brightness == 2) {
                    newAuto = false;
                    newBrightness = 1;
                    pitch = 0.8F;
                    msg = Component.translatable("message.justlights.brightness_1");
                } else {
                    newAuto = true;
                    newBrightness = 3;
                    pitch = 1.6F;
                    msg = Component.translatable("message.justlights.auto_on");
                }

                boolean shouldBeLit = newAuto ? level.isNight() : true;
                level.setBlock(pos, state.setValue(AUTO, newAuto).setValue(BRIGHTNESS, newBrightness).setValue(LIT, shouldBeLit), Block.UPDATE_ALL);
                level.playSound(null, pos, SoundEvents.LEVER_CLICK, SoundSource.BLOCKS, 0.4F, pitch);
                player.displayClientMessage(msg, true);

                if (newAuto) {
                    level.scheduleTick(pos, this, 40);
                }
                return InteractionResult.CONSUME;
            }

            // Normal Right-Click: Simple ON / OFF switch (remembers chosen brightness)
            boolean isLit = state.getValue(LIT);
            level.setBlock(pos, state.setValue(LIT, !isLit).setValue(AUTO, false), Block.UPDATE_ALL);
            level.playSound(null, pos, SoundEvents.LEVER_CLICK, SoundSource.BLOCKS, 0.4F, !isLit ? 0.6F : 0.5F);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected void onPlace(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean isMoving) {
        if (!level.isClientSide && state.getValue(AUTO)) {
            level.scheduleTick(pos, this, 40);
        }
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(AUTO)) {
            boolean isNight = level.isNight();
            if (state.getValue(LIT) != isNight) {
                level.setBlock(pos, state.setValue(LIT, isNight), Block.UPDATE_ALL);
            }
            level.scheduleTick(pos, this, 40);
        }
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock, BlockPos fromPos, boolean isMoving) {
        if (!level.isClientSide) {
            boolean hasSignal = level.hasNeighborSignal(pos);
            if (hasSignal && !state.getValue(LIT)) {
                level.setBlock(pos, state.setValue(LIT, true).setValue(AUTO, false), Block.UPDATE_ALL);
            }
        }
    }
}
