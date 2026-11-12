package fr.chatmort.airain.fusion;

import com.simibubi.create.content.kinetics.base.KineticBlockEntity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Sourcelink mécanique : {@link #PAR_TR} de source par seconde et par tr/min (128 tr/min → environ 10 de source par seconde).
 * Il consomme 8 de force par tr/min (réglé dans AirainMod). Une turbine d'Écho qui l'entraînerait produirait plus
 * qu'il ne rend : la boucle perd toujours de la source.
 */
public class SourcelinkMecaBlockEntity extends KineticBlockEntity {
	public static final double PAR_TR = 0.08;
	public static final int RAYON = 6;
	private double cumul;

	public SourcelinkMecaBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) { super(type, pos, state); }

	@Override
	public void tick() {
		super.tick();
		if (level == null) return;
		float v = Math.abs(getSpeed());
		if (level.isClientSide) {
			if (v > 0 && level.random.nextInt(Math.max(1, 40 - (int) (v / 8))) == 0)
				level.addParticle(ParticleTypes.ENCHANT, worldPosition.getX() + 0.5, worldPosition.getY() + 1.2, worldPosition.getZ() + 0.5,
					(level.random.nextDouble() - 0.5) * 0.4, 0.3, (level.random.nextDouble() - 0.5) * 0.4);
			return;
		}
		if (v == 0 || isOverStressed()) return;
		cumul += v * PAR_TR / 20.0;
		if (cumul >= 10) {                                           // versé par paquets de 10
			int n = (int) cumul;
			cumul -= Source.verser(level, worldPosition, RAYON, n);
			if (cumul > 200) cumul = 200;                            // jarres pleines : il n'accumule pas sans fin
		}
	}

	@Override
	protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) { super.write(t, r, client); t.putDouble("cumul", cumul); }

	@Override
	protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) { super.read(t, r, client); cumul = t.getDouble("cumul"); }
}
