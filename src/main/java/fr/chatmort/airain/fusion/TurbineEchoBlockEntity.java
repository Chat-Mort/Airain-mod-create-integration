package fr.chatmort.airain.fusion;

import com.simibubi.create.content.kinetics.base.GeneratingKineticBlockEntity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Turbine d'Écho : consomme {@link #CONSO} de source par tick et fournit 64 tr/min (capacité réglée dans AirainMod :
 * 16 par tr/min, soit 1 024 de force). Un signal de redstone l'arrête.
 */
public class TurbineEchoBlockEntity extends GeneratingKineticBlockEntity {
	public static final int VITESSE = 64, CONSO = 1, RESERVE_MAX = 200, RAYON = 6;
	private int reserve;
	private boolean actif;

	public TurbineEchoBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) { super(type, pos, state); }

	public boolean actif() { return actif; }

	@Override
	public void tick() {
		super.tick();
		if (level == null) return;
		if (level.isClientSide) {                                    // lueur violette quand elle tourne
			if (actif && level.random.nextInt(4) == 0)
				level.addParticle(ParticleTypes.WITCH, worldPosition.getX() + 0.5 + (level.random.nextDouble() - 0.5) * 0.6,
					worldPosition.getY() + 1.15, worldPosition.getZ() + 0.5 + (level.random.nextDouble() - 0.5) * 0.6, 0, 0.02, 0);
			return;
		}
		if (reserve < RESERVE_MAX / 2 && level.getGameTime() % 10 == 0) reserve += Source.prendre(level, worldPosition, RAYON, RESERVE_MAX - reserve);
		boolean marche = reserve >= CONSO && !level.hasNeighborSignal(worldPosition);
		if (marche) reserve -= CONSO;
		if (marche != actif) { actif = marche; updateGeneratedRotation(); setChanged(); }
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
		t.putInt("reserve", reserve); t.putBoolean("actif", actif);
	}

	@Override
	protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.read(t, r, client);
		reserve = t.getInt("reserve"); actif = t.getBoolean("actif");
	}
}
