package fr.chatmort.airain.balise;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

/**
 * Cœur de la tour de défense. « alerte » est posé par le script des assauts (data merge block … {alerte:1b}) :
 * la sirène tourne, le phare s'embrase et ses faisceaux balaient la base, les hublots s'allument.
 */
public class BaliseBlockEntity extends BlockEntity {
	private boolean alerte;
	/** Côté client : temps (en ticks) depuis le changement d'état, pour la montée en régime de la sirène. */
	public float regime, oRegime, angle, oAngle;
	private boolean lumierePosee;

	public BaliseBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.BALISE_BE.get(), pos, state);
	}

	public boolean alerte() { return alerte; }

	public void tickServeur() {
		if (level == null || lumierePosee == alerte && level.getGameTime() % 40 != 0) return;
		BlockPos lampe = worldPosition.above(5);
		BlockState s = level.getBlockState(lampe);
		if (s.is(AirainMod.BALISE_PARTIE.get()) && s.getValue(BalisePartieBlock.LUMIERE) != alerte)
			level.setBlock(lampe, s.setValue(BalisePartieBlock.LUMIERE, alerte), 3);
		lumierePosee = alerte;
	}

	public void tickClient() {
		oRegime = regime; oAngle = angle;
		regime = alerte ? Math.min(1f, regime + 0.02f) : Math.max(0f, regime - 0.01f);
		angle += regime * 9f;                                         // degrés par tick à plein régime
		if (alerte && level != null && level.getGameTime() % 80 == 0)
			level.playLocalSound(worldPosition.getX() + 0.5, worldPosition.getY() + 3, worldPosition.getZ() + 0.5,
				SoundEvents.GOAT_HORN_SOUND_VARIANTS.get(6).value(), SoundSource.BLOCKS, 4f, 0.55f, false);
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.saveAdditional(tag, r);
		tag.putBoolean("alerte", alerte);
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.loadAdditional(tag, r);
		alerte = tag.getBoolean("alerte");
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider r) {
		CompoundTag t = saveWithoutMetadata(r);
		t.putBoolean("sync", true);
		return t;
	}

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }

	public AABB boite() { return new AABB(worldPosition).inflate(5, 0, 5).expandTowards(0, 9, 0); }
}
