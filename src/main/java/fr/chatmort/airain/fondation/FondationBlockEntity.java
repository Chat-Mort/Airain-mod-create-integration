package fr.chatmort.airain.fondation;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class FondationBlockEntity extends BlockEntity {
	public static final int RAYON_MIN = 16, RAYON_MAX = 128, PAS = 16;
	private String nom = "";
	private int rayon = 48;

	public FondationBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.FONDATION_BE.get(), pos, state);
	}

	public String nom() { return nom; }
	public int rayon() { return rayon; }

	public void nommer(String n) {
		nom = n; enregistrer(); maj();
	}

	public void regler(int r) {
		rayon = Math.max(RAYON_MIN, Math.min(RAYON_MAX, r)); enregistrer(); maj();
	}

	public void enregistrer() {
		if (level instanceof ServerLevel sl)
			FondationRegistre.de(sl.getServer()).mettre(level, worldPosition, nom, rayon);
	}

	@Override
	public void onLoad() {
		super.onLoad();
		enregistrer();
	}

	private void maj() {
		setChanged();
		if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.saveAdditional(tag, r);
		tag.putString("nom", nom); tag.putInt("rayon", rayon);
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.loadAdditional(tag, r);
		nom = tag.getString("nom"); rayon = tag.contains("rayon") ? tag.getInt("rayon") : 48;
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
}
