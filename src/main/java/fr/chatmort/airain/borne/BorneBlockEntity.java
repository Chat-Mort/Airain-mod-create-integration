package fr.chatmort.airain.borne;

import java.util.ArrayList;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.Containers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.network.PacketDistributor;

/** La commande en cours d'une borne : contenu, compte à rebours (barre de boss) puis livraison. */
public class BorneBlockEntity extends BlockEntity {
	public static final int DUREE = 1200;
	/** Empire : la caisse est larguée de haut, elle touche la zone à la fin du compte à rebours. */
	static final int LARGAGE = 120;
	static final double HAUTEUR = 24;
	private final List<ItemStack> commande = new ArrayList<>();
	private int restant;
	private ServerBossEvent barre;

	public BorneBlockEntity(BlockPos pos, BlockState s) { super(AirainMod.BORNE_BE.get(), pos, s); }

	private boolean empire() { return getBlockState().getBlock() instanceof BorneBlock b && b.empire; }
	private Direction facing() { return getBlockState().getValue(BorneBlock.FACING); }
	public BlockPos zone() { return BorneBlock.zone(worldPosition, facing()); }
	public boolean enCours() { return restant > 0; }

	public boolean zoneOccupee() {
		BlockPos z = zone();
		return level != null && !level.getEntitiesOfClass(CaisseEntity.class, new AABB(z).inflate(1.5, 2, 1.5)).isEmpty();
	}

	public void ouvrir(ServerPlayer p) {
		PacketDistributor.sendToPlayer(p, new PaquetsBorne.Ouvrir(worldPosition, empire(), restant, zoneOccupee()));
	}

	public void lancer(List<ItemStack> piles) {
		commande.clear();
		commande.addAll(piles);
		restant = DUREE;
		setChanged();
		if (level != null) level.playSound(null, worldPosition, empire() ? SoundEvents.UI_CARTOGRAPHY_TABLE_TAKE_RESULT : SoundEvents.AMETHYST_BLOCK_RESONATE,
			SoundSource.BLOCKS, 1f, empire() ? 0.8f : 1.2f);
	}

	public void tick() {
		if (!(level instanceof ServerLevel sl)) return;
		if (restant <= 0) { fermerBarre(); return; }
		restant--;
		if (restant % 10 == 0 || barre == null) majBarre(sl);
		BlockPos z = zone();
		Vec3 c = new Vec3(z.getX() + 0.5, z.getY() + 2 / 16.0, z.getZ() + 0.5);
		if (empire()) {
			if (restant == LARGAGE) {
				CaisseEntity e = CaisseEntity.creer(sl, c.add(0, HAUTEUR, 0), c.y, true, new ArrayList<>(commande));
				sl.addFreshEntity(e);
				commande.clear();
				sl.playSound(null, z, SoundEvents.ELYTRA_FLYING, SoundSource.BLOCKS, 0.6f, 1.4f);
			}
		} else {
			if (restant <= 80) {
				double a = restant * 0.35, r = 1.4 * restant / 80.0 + 0.2;
				for (int k = 0; k < 4; k++) {
					double b = a + k * Math.PI / 2;
					sl.sendParticles(ParticleTypes.REVERSE_PORTAL, c.x + Math.cos(b) * r, c.y + 0.2 + (80 - restant) * 0.012, c.z + Math.sin(b) * r, 1, 0, 0.05, 0, 0.01);
				}
				if (restant % 20 == 0) sl.playSound(null, z, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1f, 0.6f + (80 - restant) / 80f);
			}
			if (restant == 0) {
				sl.addFreshEntity(CaisseEntity.creer(sl, c, c.y, false, new ArrayList<>(commande)));
				commande.clear();
				sl.sendParticles(ParticleTypes.END_ROD, c.x, c.y + 0.5, c.z, 40, 0.4, 0.4, 0.4, 0.08);
				sl.sendParticles(ParticleTypes.PORTAL, c.x, c.y + 0.5, c.z, 80, 0.5, 0.6, 0.5, 0.6);
				sl.playSound(null, z, SoundEvents.ENDERMAN_TELEPORT, SoundSource.BLOCKS, 1f, 0.8f);
			}
		}
		if (restant == 0) fermerBarre();
		setChanged();
	}

	private void majBarre(ServerLevel sl) {
		boolean emp = empire();
		if (barre == null) {
			barre = new ServerBossEvent(Component.empty(), emp ? BossEvent.BossBarColor.YELLOW : BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS);
		}
		int s = (restant + 19) / 20;
		String temps = (s / 60) + ":" + String.format("%02d", s % 60);
		String cle = emp ? (restant <= LARGAGE ? "airain.borne.barre_largage" : "airain.borne.barre_empire")
			: (restant <= 80 ? "airain.borne.barre_passage" : "airain.borne.barre_echo");
		barre.setName(Component.translatable(cle, temps));
		barre.setProgress(Math.max(0f, Math.min(1f, restant / (float) DUREE)));
		Vec3 o = Vec3.atCenterOf(worldPosition);
		for (ServerPlayer p : sl.players()) {
			boolean pres = p.position().distanceToSqr(o) < 64 * 64;
			if (pres && !barre.getPlayers().contains(p)) barre.addPlayer(p);
			else if (!pres && barre.getPlayers().contains(p)) barre.removePlayer(p);
		}
		for (ServerPlayer p : new ArrayList<>(barre.getPlayers())) if (p.level() != sl || p.isRemoved()) barre.removePlayer(p);
	}

	private void fermerBarre() {
		if (barre != null) { barre.removeAllPlayers(); barre = null; }
	}

	/** Borne détruite pendant une commande : le contenu tombe sur place. */
	void rendre() {
		fermerBarre();
		if (level != null) for (ItemStack s : commande) Containers.dropItemStack(level, worldPosition.getX() + 0.5, worldPosition.getY() + 1, worldPosition.getZ() + 0.5, s);
		commande.clear();
		restant = 0;
	}

	@Override
	public void setRemoved() { fermerBarre(); super.setRemoved(); }

	@Override
	public void onChunkUnloaded() { fermerBarre(); super.onChunkUnloaded(); }

	@Override
	protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) {
		super.saveAdditional(t, r);
		t.putInt("restant", restant);
		ListTag l = new ListTag();
		for (ItemStack s : commande) if (!s.isEmpty()) l.add(s.save(r));
		t.put("commande", l);
	}

	@Override
	protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) {
		super.loadAdditional(t, r);
		restant = t.getInt("restant");
		commande.clear();
		for (Tag e : t.getList("commande", Tag.TAG_COMPOUND)) ItemStack.parse(r, e).ifPresent(commande::add);
	}
}
