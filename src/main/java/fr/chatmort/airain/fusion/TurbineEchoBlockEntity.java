package fr.chatmort.airain.fusion;

import com.simibubi.create.content.kinetics.base.GeneratingKineticBlockEntity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

/**
 * Turbine d'Écho : boit {@link #CONSO} mB d'Écho liquide par tick (20 mB/s), amené par les tuyaux de Create,
 * et fournit 64 tr/min (capacité réglée dans AirainMod : 16 par tr/min, soit 1 024 de force). Un signal de redstone l'arrête.
 */
public class TurbineEchoBlockEntity extends GeneratingKineticBlockEntity {
	public static final int VITESSE = 64, CONSO = 1, CAPACITE = 1000;
	/** La cuve arrière : n'accepte que l'Écho liquide (capacité enregistrée dans AirainMod). */
	public final FluidTank reservoir = new FluidTank(CAPACITE, f -> f.getFluid().isSame(EchoLiquide.SOURCE.get())) {
		@Override protected void onContentsChanged() { setChanged(); }
	};
	private boolean actif;

	public TurbineEchoBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) { super(type, pos, state); }

	public boolean actif() { return actif; }

	@Override
	public void tick() {
		super.tick();
		if (level == null) return;
		if (level.isClientSide) {                                    // lueur violette quand elle tourne
			if (actif && level.random.nextInt(2) == 0)                 // la cheminée évacue la vapeur d'Écho
				level.addParticle(ParticleTypes.WITCH, worldPosition.getX() + 0.5 + (level.random.nextDouble() - 0.5) * 0.4,
					worldPosition.getY() + 1.2, worldPosition.getZ() + 0.5 + (level.random.nextDouble() - 0.5) * 0.4, 0, 0.12, 0);
			return;
		}
		boolean marche = reservoir.getFluidAmount() >= CONSO && !level.hasNeighborSignal(worldPosition);
		if (marche) reservoir.drain(CONSO, IFluidHandler.FluidAction.EXECUTE);
		if (marche != actif) { actif = marche; updateGeneratedRotation(); setChanged(); sendData(); }
	}

	@Override
	public void initialize() {
		super.initialize();
		if (!hasSource() || getGeneratedSpeed() > getTheoreticalSpeed()) updateGeneratedRotation();
	}

	@Override
	public float getGeneratedSpeed() {
		return actif ? convertToDirection(VITESSE, getBlockState().getValue(TurbineEchoBlock.FACING)) : 0;
	}

	@Override
	protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.write(t, r, client);
		t.put("reservoir", reservoir.writeToNBT(r, new CompoundTag())); t.putBoolean("actif", actif);
	}

	@Override
	protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.read(t, r, client);
		reservoir.readFromNBT(r, t.getCompound("reservoir")); actif = t.getBoolean("actif");
	}
}
