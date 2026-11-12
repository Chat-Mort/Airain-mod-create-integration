package fr.chatmort.airain.fusion;

import com.simibubi.create.content.kinetics.base.KineticBlockEntity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

/**
 * Sourcelink mécanique : {@link #PAR_TR} mB d'Écho liquide par seconde et par tr/min (128 tr/min → environ 10 mB/s),
 * dans sa cuve de 1 000 mB, à pomper avec les tuyaux de Create. Il consomme 8 de force par tr/min (réglé dans AirainMod).
 * Une turbine d'Écho qui l'entraînerait boirait plus qu'il ne rend : la boucle perd toujours de l'Écho.
 */
public class SourcelinkMecaBlockEntity extends KineticBlockEntity {
	public static final double PAR_TR = 0.08;
	public static final int CAPACITE = 1000;
	/** La cuve du socle (capacité enregistrée dans AirainMod). */
	public final FluidTank reservoir = new FluidTank(CAPACITE, f -> f.getFluid().isSame(EchoLiquide.SOURCE.get())) {
		@Override protected void onContentsChanged() { setChanged(); }
	};
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
		if (v == 0 || isOverStressed() || reservoir.getSpace() <= 0) return;   // cuve pleine : il tourne à vide
		cumul += v * PAR_TR / 20.0;
		if (cumul >= 1) {                                            // versé millibucket par millibucket
			int n = (int) cumul;
			cumul -= reservoir.fill(new FluidStack(EchoLiquide.SOURCE.get(), n), IFluidHandler.FluidAction.EXECUTE);
			if (cumul > 1) cumul = 1;
		}
	}

	@Override
	protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.write(t, r, client); t.putDouble("cumul", cumul); t.put("reservoir", reservoir.writeToNBT(r, new CompoundTag()));
	}

	@Override
	protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.read(t, r, client); cumul = t.getDouble("cumul"); reservoir.readFromNBT(r, t.getCompound("reservoir"));
	}
}
