package net.justlights.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;

public class ColoredCampfireBlock extends CampfireBlock {
    private final DyeColor color;
    private final SimpleParticleType flameParticle;

    public ColoredCampfireBlock(DyeColor color, Properties properties) {
        super(false, 2, properties);
        this.color = color;
        this.flameParticle = (color == DyeColor.BLUE || color == DyeColor.CYAN || color == DyeColor.LIGHT_BLUE)
                ? ParticleTypes.SOUL_FIRE_FLAME
                : ParticleTypes.FLAME;
    }

    public DyeColor getColor() {
        return color;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        super.animateTick(state, level, pos, random);
        if (state.getValue(LIT)) {
            if (random.nextInt(5) == 0) {
                for (int i = 0; i < random.nextInt(1) + 1; ++i) {
                    level.addParticle(
                            this.flameParticle,
                            (double) pos.getX() + 0.5D + (random.nextDouble() - 0.5D) * 0.4D,
                            (double) pos.getY() + 0.45D + (random.nextDouble() - 0.5D) * 0.2D,
                            (double) pos.getZ() + 0.5D + (random.nextDouble() - 0.5D) * 0.4D,
                            0.0D, 0.005D, 0.0D
                    );
                }
            }
        }
    }
}
