package net.justlights.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WallTorchBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;

public class ColoredUnderwaterWallTorchBlock extends WallTorchBlock implements SimpleWaterloggedBlock {
    public static final BooleanProperty WATERLOGGED = BlockStateProperties.WATERLOGGED;
    private final DyeColor color;

    public ColoredUnderwaterWallTorchBlock(DyeColor color, SimpleParticleType particle) {
        super(particle, BlockBehaviour.Properties.of()
                .noCollission()
                .instabreak()
                .lightLevel(state -> 15)
                .sound(SoundType.WOOD)
        );
        this.color = color;
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(FACING, Direction.NORTH)
                .setValue(WATERLOGGED, false));
    }

    public DyeColor getColor() {
        return this.color;
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = super.getStateForPlacement(context);
        if (state == null) return null;
        FluidState fluidState = context.getLevel().getFluidState(context.getClickedPos());
        return state.setValue(WATERLOGGED, fluidState.getType() == Fluids.WATER);
    }

    @Override
    protected BlockState updateShape(BlockState state, Direction direction, BlockState neighborState, LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        if (state.getValue(WATERLOGGED)) {
            level.scheduleTick(pos, Fluids.WATER, Fluids.WATER.getTickDelay(level));
        }
        return super.updateShape(state, direction, neighborState, level, pos, neighborPos);
    }

    @Override
    public FluidState getFluidState(BlockState state) {
        return state.getValue(WATERLOGGED) ? Fluids.WATER.getSource(false) : super.getFluidState(state);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(WATERLOGGED);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        Direction direction = state.getValue(FACING);
        double x = (double) pos.getX() + 0.5D;
        double y = (double) pos.getY() + 0.7D;
        double z = (double) pos.getZ() + 0.5D;
        Direction opposite = direction.getOpposite();

        double px = x + 0.27D * (double) opposite.getStepX();
        double py = y + 0.22D;
        double pz = z + 0.27D * (double) opposite.getStepZ();

        if (state.getValue(WATERLOGGED)) {
            if (random.nextInt(3) == 0) {
                level.addParticle(ParticleTypes.BUBBLE, px, py, pz, 0.0D, 0.06D, 0.0D);
            }
        } else {
            super.animateTick(state, level, pos, random);
        }
    }
}
