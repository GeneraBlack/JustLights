package net.justlights.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public class ColoredChandelierBlock extends Block implements SimpleWaterloggedBlock {
    public static final BooleanProperty HANGING = BlockStateProperties.HANGING;
    public static final BooleanProperty WATERLOGGED = BlockStateProperties.WATERLOGGED;

    protected static final VoxelShape STANDING_SHAPE = Block.box(2.0D, 0.0D, 2.0D, 14.0D, 14.0D, 14.0D);
    protected static final VoxelShape HANGING_SHAPE = Block.box(2.0D, 2.0D, 2.0D, 14.0D, 16.0D, 14.0D);

    private final DyeColor color;
    private final SimpleParticleType flameParticle;

    public ColoredChandelierBlock(DyeColor color) {
        super(BlockBehaviour.Properties.of()
                .strength(3.5F)
                .sound(SoundType.LANTERN)
                .lightLevel(state -> 15)
                .noOcclusion()
        );
        this.color = color;
        this.flameParticle = (color == DyeColor.BLUE || color == DyeColor.CYAN || color == DyeColor.LIGHT_BLUE)
                ? ParticleTypes.SOUL_FIRE_FLAME
                : ParticleTypes.FLAME;

        this.registerDefaultState(this.stateDefinition.any()
                .setValue(HANGING, true)
                .setValue(WATERLOGGED, false));
    }

    public DyeColor getColor() {
        return this.color;
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(HANGING) ? HANGING_SHAPE : STANDING_SHAPE;
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        FluidState fluidState = context.getLevel().getFluidState(context.getClickedPos());
        boolean isHanging = context.getClickedFace() != Direction.UP;
        return this.defaultBlockState()
                .setValue(HANGING, isHanging)
                .setValue(WATERLOGGED, fluidState.getType() == Fluids.WATER);
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
        builder.add(HANGING, WATERLOGGED);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(WATERLOGGED)) return;

        double y = pos.getY() + (state.getValue(HANGING) ? 0.65D : 0.55D);
        double[][] flameOffsets = {
                {0.22D, 0.5D},
                {0.78D, 0.5D},
                {0.5D, 0.22D},
                {0.5D, 0.78D}
        };

        for (double[] offset : flameOffsets) {
            if (random.nextInt(3) == 0) {
                double x = pos.getX() + offset[0];
                double z = pos.getZ() + offset[1];
                level.addParticle(this.flameParticle, x, y, z, 0.0D, 0.0D, 0.0D);
            }
        }
    }
}
