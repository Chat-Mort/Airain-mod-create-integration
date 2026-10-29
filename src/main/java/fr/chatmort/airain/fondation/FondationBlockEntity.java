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

/** Moitié basse de l'étendard : nom, rayon de la zone, apparence de la bannière. */
public class FondationBlockEntity extends BlockEntity {
	public static final int RAYON_MIN = 16, RAYON_MAX = 128, PAS = 16;
	private String nom = "";
	private String devise = "";
	private int rayon = 48;
	private Apparence apparence = Apparence.DEFAUT;

	public FondationBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.FONDATION_BE.get(), pos, state);
	}

	public String nom() { return nom; }
	public String devise() { return devise; }
	public int rayon() { return rayon; }
	public Apparence apparence() { return apparence; }

	public void configurer(String n, String d, Apparence a) {
		if (!(getBlockState().getBlock() instanceof GrandEtendardBlock) && a.estMasque()) {   // seul le grand peut être décoratif
			int[] v = a.valeurs(); v[12] = 0; a = Apparence.depuis(v);
		}
		nom = n; devise = d; apparence = a;
		if (level != null && !level.isClientSide) FondationBlock.appliquerStyle(level, worldPosition, a.style());
		enregistrer(); maj();
	}

	public void regler(int r) {
		rayon = Math.max(RAYON_MIN, Math.min(RAYON_MAX, r)); enregistrer(); maj();
	}

	public void enregistrer() {
		if (level instanceof ServerLevel sl)
			FondationRegistre.de(sl.getServer()).mettre(level, worldPosition, nom, rayon, devise, apparence.pack());
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
		tag.putString("nom", nom); tag.putString("devise", devise); tag.putInt("rayon", rayon); tag.putInt("apparence", apparence.pack());
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.loadAdditional(tag, r);
		nom = tag.getString("nom"); devise = tag.getString("devise"); rayon = tag.contains("rayon") ? tag.getInt("rayon") : 48;
		apparence = tag.contains("apparence") ? Apparence.unpack(tag.getInt("apparence")) : Apparence.DEFAUT;
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider r) { CompoundTag t = saveWithoutMetadata(r); t.putBoolean("sync", true); return t; }

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
}
