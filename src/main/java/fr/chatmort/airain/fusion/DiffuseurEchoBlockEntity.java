package fr.chatmort.airain.fusion;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Réserve de source du diffuseur : {@link #CONSO} par tick tant qu'il brûle (environ 40 par seconde). */
public class DiffuseurEchoBlockEntity extends BlockEntity {
	public static final int CONSO = 2, RESERVE_MAX = 400, RAYON = 6;
	private int reserve;

	public DiffuseurEchoBlockEntity(BlockPos pos, BlockState state) { super(AirainMod.DIFFUSEUR_ECHO_BE.get(), pos, state); }

	void tickServeur() {
		if (level == null) return;
		if (reserve < RESERVE_MAX / 2 && level.getGameTime() % 10 == 0) reserve += Source.prendre(level, worldPosition, RAYON, RESERVE_MAX - reserve);
		boolean brule = reserve >= CONSO && !level.hasNeighborSignal(worldPosition);
		if (brule) reserve -= CONSO;
		BlockState s = getBlockState();
		if (s.getValue(DiffuseurEchoBlock.ALLUME) != brule) level.setBlock(worldPosition, s.setValue(DiffuseurEchoBlock.ALLUME, brule), Block.UPDATE_ALL);
		setChanged();
	}

	@Override
	protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); t.putInt("reserve", reserve); }

	@Override
	protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); reserve = t.getInt("reserve"); }
}
