package fr.chatmort.airain.fonderie;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.entity.IEntityWithComplexSpawn;
import net.neoforged.neoforge.event.entity.EntityMountEvent;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * La nacelle du téléphérique : une plateforme ouverte de 2 × 2, pendue à un chariot qui roule sur le brin droit du câble.
 * Elle garde sa route (les points d'attache du câble, de la gare de départ à celle d'arrivée) : elle n'a besoin d'aucun bloc
 * chargé pour rouler, et charge elle-même les tronçons qu'elle traverse. Jusqu'à quatre voyageurs, debout ; on monte d'un
 * clic droit, elle part deux secondes plus tard vers l'autre gare ; à l'arrivée, chacun descend. On ne peut pas sauter en route.
 */
public class Nacelle extends Entity implements IEntityWithComplexSpawn {
	private static final EntityDataAccessor<Float> S = SynchedEntityData.defineId(Nacelle.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> CIBLE = SynchedEntityData.defineId(Nacelle.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> V = SynchedEntityData.defineId(Nacelle.class, EntityDataSerializers.FLOAT);
	public static final int PLACES = 4, ATTENTE = 40;

	/** Les points d'attache du chariot (un par nœud), et le câble échantillonné entre eux. */
	private final List<Vec3> points = new ArrayList<>();
	private final List<Vec3> ech = new ArrayList<>();
	private final List<Integer> travee = new ArrayList<>();
	private double[] cumul = new double[0];
	private double longueur;
	private BlockPos gareA, gareB;
	/** Côté client : position sur le câble, lissée ; côté serveur : décompte avant le départ. */
	private double sLocal; private int depart = -1; private float vitesse;
	public float lacet, lacetChariot, lacetAvant, lacetChariotAvant;

	public Nacelle(EntityType<? extends Nacelle> t, Level l) { super(t, l); noPhysics = true; }

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) { b.define(S, 0f); b.define(CIBLE, 0f); b.define(V, 0f); }

	// ------------------------------------------------------------------ la route
	static Nacelle creer(Level l, List<BlockPos> ligne, int bout) {
		Nacelle n = new Nacelle(Telepherique.NACELLE.get(), l);
		n.gareA = ligne.get(0); n.gareB = ligne.get(ligne.size() - 1);
		n.points.addAll(Telepherique.brin(l, ligne, Telepherique.BRIN));
		n.echantillonner();
		float s0 = bout == 0 ? 0 : (float) n.longueur;
		n.entityData.set(S, s0); n.entityData.set(CIBLE, s0); n.sLocal = s0;
		n.placer(s0);
		n.setOldPosAndRot();
		l.addFreshEntity(n);
		return n;
	}
	private void echantillonner() {
		ech.clear(); travee.clear();
		for (int i = 0; i + 1 < points.size(); i++) {
			Vec3 a = points.get(i), b = points.get(i + 1);
			int n = Math.max(4, (int) (a.distanceTo(b) / 1.5));
			for (int k = (i == 0 ? 0 : 1); k <= n; k++) { ech.add(Telepherique.chainette(a, b, k / (double) n)); travee.add(i); }
		}
		cumul = new double[ech.size()];
		for (int i = 1; i < ech.size(); i++) cumul[i] = cumul[i - 1] + ech.get(i).distanceTo(ech.get(i - 1));
		longueur = cumul.length > 0 ? cumul[cumul.length - 1] : 0;
	}
	/** Le chariot à l'abscisse s ; renvoie aussi la direction de la travée (dans dir[0]). */
	private Vec3 chariot(double s, Vec3[] dir) {
		if (ech.isEmpty()) return position();
		s = Math.max(0, Math.min(longueur, s));
		int i = 1;
		while (i < cumul.length - 1 && cumul[i] < s) i++;
		double t = cumul[i] - cumul[i - 1] < 1e-6 ? 0 : (s - cumul[i - 1]) / (cumul[i] - cumul[i - 1]);
		int tr = travee.get(i);
		if (dir != null) dir[0] = points.get(tr + 1).subtract(points.get(tr));
		return ech.get(i - 1).lerp(ech.get(i), t);
	}
	private void placer(double s) {
		Vec3[] d = new Vec3[1];
		Vec3 c = chariot(s, d);
		setPos(c.x, c.y - Telepherique.SUSPENTE, c.z);
		if (d[0] != null) {
			lacetChariot = (float) Math.toDegrees(Math.atan2(-d[0].x, d[0].z));
			lacet = Math.round(lacetChariot / 90f) * 90f;           // la plateforme carrée, calée d'équerre (comme sa collision)
		}
	}
	public double abscisse() { return level().isClientSide ? sLocal : entityData.get(S); }
	public boolean enRoute() { return Math.abs(entityData.get(CIBLE) - entityData.get(S)) > 1e-3 || Math.abs(entityData.get(V)) > 0; }

	// ------------------------------------------------------------------ commandes
	/** Envoie la nacelle vers la gare g (appel depuis une gare ou départ avec des voyageurs). */
	boolean vers(BlockPos g, @Nullable Player qui) {
		float c = g.equals(gareA) ? 0 : (float) longueur;
		if (Math.abs(entityData.get(S) - c) < 1e-3) { if (qui != null) qui.displayClientMessage(Component.translatable("airain.telepherique.la").withStyle(ChatFormatting.GRAY), true); return false; }
		float v = vitesseLigne();
		if (v <= 0) { if (qui != null) qui.displayClientMessage(Component.translatable("airain.telepherique.immobile").withStyle(ChatFormatting.RED), true); return false; }
		vitesse = v;
		entityData.set(CIBLE, c);
		entityData.set(V, Math.signum(c - entityData.get(S)) * v);
		tournerGares(true);
		level().playSound(null, blockPosition(), SoundEvents.IRON_DOOR_CLOSE, SoundSource.BLOCKS, 0.7f, 0.7f);
		return true;
	}
	/** Vitesse donnée par les gares entraînées (en blocs par tick) : 256 tr/min → 0,35 bloc par tick (7 blocs/s). */
	private float vitesseLigne() {
		float rpm = 0;
		for (BlockPos g : new BlockPos[]{gareA, gareB})
			if (g != null && level().isLoaded(g) && level().getBlockEntity(g) instanceof Telepherique.GareBlockEntity ge) rpm = Math.max(rpm, ge.vitesse());
		if (rpm <= 0) return 0;
		return Math.max(0.04f, rpm / 256f * 0.35f);
	}
	private void tournerGares(boolean t) {
		for (BlockPos g : new BlockPos[]{gareA, gareB})
			if (g != null && level().isLoaded(g) && level().getBlockEntity(g) instanceof Telepherique.GareBlockEntity ge) ge.tourne(t);
	}

	@Override
	public InteractionResult interact(Player j, InteractionHand m) {
		if (j.isSecondaryUseActive()) return InteractionResult.PASS;
		if (enRoute()) return InteractionResult.PASS;
		if (!level().isClientSide) {
			if (getPassengers().size() >= PLACES) { j.displayClientMessage(Component.translatable("airain.telepherique.complet").withStyle(ChatFormatting.RED), true); return InteractionResult.CONSUME; }
			if (j.startRiding(this)) {
				if (depart < 0) depart = ATTENTE;
				j.displayClientMessage(Component.translatable("airain.telepherique.depart_proche").withStyle(ChatFormatting.GOLD), true);
			}
		}
		return InteractionResult.sidedSuccess(level().isClientSide);
	}
	/** Pas de descente en route. */
	public static void descente(EntityMountEvent e) {
		if (e.isDismounting() && e.getEntityBeingMounted() instanceof Nacelle n && n.enRoute()) e.setCanceled(true);
	}
	@Override protected boolean canAddPassenger(Entity e) { return getPassengers().size() < PLACES; }
	@Override public boolean shouldRiderSit() { return false; }
	@Override
	protected void positionRider(Entity e, MoveFunction f) {
		int i = Math.max(0, getPassengers().indexOf(e));
		double ox = (i % 2 == 0 ? -0.45 : 0.45), oz = (i < 2 ? -0.45 : 0.45);
		double a = Math.toRadians(lacet), c = Math.cos(a), sn = Math.sin(a);
		f.accept(e, getX() + ox * c - oz * sn, getY() + 0.125, getZ() + ox * sn + oz * c);
	}
	@Override public Vec3 getDismountLocationForPassenger(net.minecraft.world.entity.LivingEntity e) { return new Vec3(e.getX(), getY() + 0.13, e.getZ()); }

	@Override
	public boolean hurt(DamageSource src, float n) {
		if (level().isClientSide || isRemoved()) return true;
		if (src.getEntity() instanceof Player j && j.isShiftKeyDown() && !enRoute()) {
			if (!j.getAbilities().instabuild) spawnAtLocation(new ItemStack(Telepherique.NACELLE_ITEM.get()));
			oublier(); discard();
		}
		return true;
	}
	/** Les gares ne retiennent plus cette nacelle. */
	private void oublier() {
		for (BlockPos g : new BlockPos[]{gareA, gareB})
			if (g != null && level().isLoaded(g) && level().getBlockEntity(g) instanceof Telepherique.GareBlockEntity ge && getUUID().equals(ge.nacelle)) { ge.nacelle = null; ge.tourne(false); ge.setChanged(); }
	}
	/** Une gare ou un pylône de la ligne a été retiré : la nacelle redevient un objet. */
	static void retirerDe(Level l, BlockPos p) {
		if (!(l instanceof ServerLevel sl)) return;
		for (Nacelle n : sl.getEntities(Telepherique.NACELLE.get(), x -> x.passePar(p))) {
			n.ejectPassengers(); n.spawnAtLocation(new ItemStack(Telepherique.NACELLE_ITEM.get())); n.oublier(); n.discard();
		}
	}
	private boolean passePar(BlockPos p) {
		if (p.equals(gareA) || p.equals(gareB)) return true;
		for (Vec3 v : points) if (Math.abs(v.x - p.getX() - 0.5) < Telepherique.BRIN + 0.6 && Math.abs(v.z - p.getZ() - 0.5) < Telepherique.BRIN + 0.6 && Math.abs(v.y - p.getY()) < 2.5) return true;
		return false;
	}

	// ------------------------------------------------------------------ chaque tick
	@Override
	public void tick() {
		super.tick();
		lacetAvant = lacet; lacetChariotAvant = lacetChariot;
		if (ech.isEmpty()) { if (!level().isClientSide) discard(); return; }
		if (level().isClientSide) {
			// on roule à la vitesse annoncée, en se recalant doucement sur le serveur
			float v = entityData.get(V), cible = entityData.get(CIBLE);
			sLocal += v * lissage(sLocal, cible);
			sLocal += (entityData.get(S) - sLocal) * 0.15;
			if (v == 0) sLocal = entityData.get(S);
			placer(sLocal);
			return;
		}
		float s = entityData.get(S), cible = entityData.get(CIBLE);
		if (depart > 0 && --depart == 0) {
			depart = -1;
			if (!getPassengers().isEmpty()) vers(Math.abs(s) < 1e-3 ? gareB : gareA, getPassengers().get(0) instanceof Player p ? p : null);
		}
		if (Math.abs(cible - s) > 1e-3) {
			float v = vitesseLigne();
			if (v > 0) vitesse = v;                                   // une gare chargée et entraînée : on suit sa vitesse
			float pas = (float) (vitesse * lissage(s, cible));
			s = cible > s ? Math.min(cible, s + pas) : Math.max(cible, s - pas);
			entityData.set(S, s);
			entityData.set(V, Math.signum(cible - s) * vitesse);
			if (tickCount % 20 == 0 && level() instanceof ServerLevel sl)      // la nacelle garde chargé le tronçon qu'elle traverse
				sl.getChunkSource().addRegionTicket(TicketType.PORTAL, new ChunkPos(blockPosition()), 3, blockPosition());
			if (Math.abs(cible - s) < 1e-3) arrivee();
		}
		placer(s);
	}
	/** Démarrage et freinage en douceur près des gares. */
	private double lissage(double s, double cible) {
		double depuis = Math.min(Math.abs(s), Math.abs(longueur - s)), reste = Math.abs(cible - s);
		return Math.max(0.15, Math.min(1, Math.min(depuis / 3 + 0.25, reste / 3 + 0.15)));
	}
	private void arrivee() {
		entityData.set(V, 0f);
		tournerGares(false);
		level().playSound(null, blockPosition(), SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 0.7f, 0.8f);
		ejectPassengers();
	}

	// le client calcule lui-même sa position sur le câble : on ignore les recalages de position du serveur
	@Override public void lerpTo(double x, double y, double z, float yr, float xr, int n) { }
	@Override public boolean canBeCollidedWith() { return true; }
	@Override public boolean isPickable() { return !isRemoved(); }
	@Override public boolean isPushable() { return false; }
	@Override public boolean shouldBeSaved() { return true; }

	// ------------------------------------------------------------------ sauvegarde et apparition
	@Override
	protected void readAdditionalSaveData(CompoundTag t) {
		points.clear();
		for (Tag x : t.getList("points", Tag.TAG_COMPOUND)) { CompoundTag c = (CompoundTag) x; points.add(new Vec3(c.getDouble("x"), c.getDouble("y"), c.getDouble("z"))); }
		gareA = t.contains("a") ? BlockPos.of(t.getLong("a")) : null; gareB = t.contains("b") ? BlockPos.of(t.getLong("b")) : null;
		echantillonner();
		entityData.set(S, t.getFloat("s")); entityData.set(CIBLE, t.getFloat("cible")); vitesse = t.getFloat("vitesse");
		entityData.set(V, Math.abs(t.getFloat("cible") - t.getFloat("s")) > 1e-3 ? Math.signum(t.getFloat("cible") - t.getFloat("s")) * vitesse : 0f);
		sLocal = t.getFloat("s");
	}
	@Override
	protected void addAdditionalSaveData(CompoundTag t) {
		ListTag l = new ListTag();
		for (Vec3 v : points) { CompoundTag c = new CompoundTag(); c.putDouble("x", v.x); c.putDouble("y", v.y); c.putDouble("z", v.z); l.add(c); }
		t.put("points", l);
		if (gareA != null) t.putLong("a", gareA.asLong());
		if (gareB != null) t.putLong("b", gareB.asLong());
		t.putFloat("s", entityData.get(S)); t.putFloat("cible", entityData.get(CIBLE)); t.putFloat("vitesse", vitesse);
	}
	@Override
	public void writeSpawnData(RegistryFriendlyByteBuf b) {
		b.writeVarInt(points.size());
		for (Vec3 v : points) { b.writeDouble(v.x); b.writeDouble(v.y); b.writeDouble(v.z); }
		b.writeFloat(entityData.get(S));
	}
	@Override
	public void readSpawnData(RegistryFriendlyByteBuf b) {
		points.clear();
		int n = b.readVarInt();
		for (int i = 0; i < n; i++) points.add(new Vec3(b.readDouble(), b.readDouble(), b.readDouble()));
		echantillonner();
		sLocal = b.readFloat();
		placer(sLocal); setOldPosAndRot(); lacetAvant = lacet; lacetChariotAvant = lacetChariot;
	}
}
