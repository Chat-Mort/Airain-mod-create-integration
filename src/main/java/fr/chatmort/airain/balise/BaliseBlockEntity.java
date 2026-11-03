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
	/** Balise sacrée : pendant un assaut, elle foudroie elle-même les vagues. */
	private boolean sacree;
	public boolean sacree() { return sacree; }
	public void sacrer() {
		sacree = true; setChanged();
		if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
	}

	/** Toutes les 5 s d'alerte : un arc depuis le phare frappe jusqu'à 4 assaillants à 32 blocs. */
	private void foudroyer(net.minecraft.server.level.ServerLevel sl) {
		net.minecraft.world.phys.Vec3 de = net.minecraft.world.phys.Vec3.atCenterOf(worldPosition.above(5));
		var cibles = sl.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, new AABB(worldPosition).inflate(32),
			m -> m.isAlive() && m.getTags().contains("airain_vague"));
		if (cibles.isEmpty()) return;
		cibles.sort(java.util.Comparator.comparingDouble(m -> m.distanceToSqr(de)));
		for (var m : cibles.subList(0, Math.min(4, cibles.size()))) {
			m.hurt(sl.damageSources().magic(), 8f);
			m.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
			net.minecraft.world.phys.Vec3 a = m.position().add(0, m.getBbHeight() * 0.5, 0);
			int pas = (int) (de.distanceTo(a) * 2);
			for (int i = 1; i <= pas; i++) {
				net.minecraft.world.phys.Vec3 p = de.lerp(a, i / (double) pas);
				sl.sendParticles(net.minecraft.core.particles.ParticleTypes.ELECTRIC_SPARK, p.x + (sl.random.nextDouble() - 0.5) * 0.4,
					p.y + (sl.random.nextDouble() - 0.5) * 0.4, p.z + (sl.random.nextDouble() - 0.5) * 0.4, 1, 0, 0, 0, 0);
			}
		}
		sl.playSound(null, worldPosition.above(5), SoundEvents.LIGHTNING_BOLT_IMPACT, SoundSource.BLOCKS, 1.5f, 1.4f);
	}
	/** Côté client : temps (en ticks) depuis le changement d'état, pour la montée en régime de la sirène. */
	public float regime, oRegime, angle, oAngle;
	private boolean lumierePosee;

	public BaliseBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.BALISE_BE.get(), pos, state);
	}

	public boolean alerte() { return alerte; }

	public void tickServeur() {
		if (sacree && alerte && level instanceof net.minecraft.server.level.ServerLevel sl && level.getGameTime() % 100 == 0) foudroyer(sl);
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
		if (sacree && level != null && level.random.nextInt(alerte ? 4 : 30) == 0)   // éclats d'or autour du phare
			level.addParticle(net.minecraft.core.particles.ParticleTypes.END_ROD, worldPosition.getX() + 0.5 + (level.random.nextDouble() - 0.5) * 1.6,
				worldPosition.getY() + 5.5, worldPosition.getZ() + 0.5 + (level.random.nextDouble() - 0.5) * 1.6, 0, 0.02, 0);
		if (alerte && level != null && level.getGameTime() % 80 == 0)
			level.playLocalSound(worldPosition.getX() + 0.5, worldPosition.getY() + 3, worldPosition.getZ() + 0.5,
				SoundEvents.GOAT_HORN_SOUND_VARIANTS.get(6).value(), SoundSource.BLOCKS, 4f, 0.55f, false);
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.saveAdditional(tag, r);
		tag.putBoolean("alerte", alerte);
		tag.putBoolean("sacree", sacree);
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.loadAdditional(tag, r);
		alerte = tag.getBoolean("alerte");
		sacree = tag.getBoolean("sacree");
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
