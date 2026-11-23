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
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.entity.IEntityWithComplexSpawn;
import net.neoforged.neoforge.event.entity.EntityMountEvent;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * La nacelle du téléphérique : une plateforme ouverte de 2 × 2, pendue à un chariot qui roule sur le câble.
 * 1.68 : elle fait le tour complet de la boucle, toujours sur le brin de droite dans le sens de marche : brin droit à l'aller,
 * demi-tour autour de la poulie de la gare d'arrivée, l'autre brin au retour. Elle attend en gare du côté du départ (le
 * demi-tour se fait avant de s'arrêter), et son portillon disparaît tant qu'elle attend.
 * Elle garde sa route (les centres des nœuds de la ligne) : elle n'a besoin d'aucun bloc chargé pour rouler, et charge elle-même
 * les tronçons qu'elle traverse. Jusqu'à quatre voyageurs, debout ; on monte d'un clic droit, elle part deux secondes plus tard
 * vers l'autre gare ; à l'arrivée, chacun descend. On ne peut pas sauter en route.
 */
public class Nacelle extends Entity implements IEntityWithComplexSpawn {
	private static final EntityDataAccessor<Float> S = SynchedEntityData.defineId(Nacelle.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> CIBLE = SynchedEntityData.defineId(Nacelle.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> V = SynchedEntityData.defineId(Nacelle.class, EntityDataSerializers.FLOAT);
	public static final int PLACES = 4, ATTENTE = 40;
	/** 1.68 : 256 tr/min donnent 0,9 bloc par tick (18 blocs/s), proportionnellement en dessous. */
	public static final float VITESSE_256 = 0.9f;

	/** Les centres des nœuds de la ligne (gare A, têtes de pylône, gare B), et la boucle échantillonnée. */
	private final List<Vec3> centres = new ArrayList<>();
	private final List<Vec3> ech = new ArrayList<>();
	private double[] cumul = new double[0];
	/** Longueur de la boucle ; fin de l'aller (s1), fin du demi-tour en B = arrêt en B (s2), fin du retour (s3) ; arrêt en A : 0. */
	private double longueur, s1, s2, s3;
	/** Demi-tours : cap de la plateforme au début, et sens de rotation (+1 ou -1). */
	private float capB, capA; private int sensB = 1, sensA = 1;
	private BlockPos gareA, gareB;
	/** Côté client : position sur la boucle, lissée ; côté serveur : décompte avant le départ. */
	private double sLocal; private int depart = -1; private float vitesse, vitesseAnnoncee;
	public float lacet, lacetChariot, lacetAvant, lacetChariotAvant;

	public Nacelle(EntityType<? extends Nacelle> t, Level l) { super(t, l); noPhysics = true; }

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) { b.define(S, 0f); b.define(CIBLE, 0f); b.define(V, 0f); }

	// ------------------------------------------------------------------ la route
	static Nacelle creer(Level l, List<BlockPos> ligne, int bout) {
		Nacelle n = new Nacelle(Telepherique.NACELLE.get(), l);
		n.gareA = ligne.get(0); n.gareB = ligne.get(ligne.size() - 1);
		for (BlockPos p : ligne) n.centres.add(Telepherique.centre(l, p));
		n.echantillonner();
		float s0 = bout == 0 ? 0 : (float) n.s2;
		n.entityData.set(S, s0); n.entityData.set(CIBLE, s0); n.sLocal = s0;
		n.placer(s0);
		n.setOldPosAndRot();
		l.addFreshEntity(n);
		return n;
	}
	private static Vec3 plat(Vec3 v) { Vec3 h = new Vec3(v.x, 0, v.z); double n = h.length(); return n < 1e-6 ? new Vec3(1, 0, 0) : h.scale(1 / n); }
	private static float cap(Vec3 d) { return (float) Math.toDegrees(Math.atan2(-d.x, d.z)); }
	/** La boucle : brin droit de A à B, demi-tour en B, brin gauche de B à A, demi-tour en A (qui referme la boucle). */
	private void echantillonner() {
		ech.clear();
		int n = centres.size();
		if (n < 2) { cumul = new double[0]; longueur = 0; return; }
		double r = Telepherique.BRIN;
		List<Vec3> dr = new ArrayList<>();
		for (int i = 0; i < n; i++) dr.add(Telepherique.droite(i > 0 ? centres.get(i - 1) : null, centres.get(i), i + 1 < n ? centres.get(i + 1) : null));
		// aller, sur le brin droit
		for (int i = 0; i + 1 < n; i++) portee(centres.get(i).add(dr.get(i).scale(r)), centres.get(i + 1).add(dr.get(i + 1).scale(r)), i == 0);
		int iS1 = ech.size() - 1;
		// demi-tour autour de la poulie de B, par l'extérieur de la ligne
		Vec3 cB = centres.get(n - 1), rB = dr.get(n - 1), dB = plat(cB.subtract(centres.get(n - 2)));
		int k = 12;
		for (int j = 1; j <= k; j++) { double t = Math.PI * j / k; ech.add(cB.add(rB.scale(Math.cos(t) * r)).add(dB.scale(Math.sin(t) * r))); }
		int iS2 = ech.size() - 1;
		// retour, sur l'autre brin (à droite dans ce sens-là)
		for (int i = n - 1; i > 0; i--) portee(centres.get(i).subtract(dr.get(i).scale(r)), centres.get(i - 1).subtract(dr.get(i - 1).scale(r)), false);
		int iS3 = ech.size() - 1;
		Vec3 cA = centres.get(0), rA = dr.get(0), dA = plat(centres.get(1).subtract(cA));
		for (int j = 1; j <= k; j++) { double t = Math.PI * j / k; ech.add(cA.subtract(rA.scale(Math.cos(t) * r)).subtract(dA.scale(Math.sin(t) * r))); }
		cumul = new double[ech.size()];
		for (int i = 1; i < ech.size(); i++) cumul[i] = cumul[i - 1] + ech.get(i).distanceTo(ech.get(i - 1));
		longueur = cumul[cumul.length - 1]; s1 = cumul[iS1]; s2 = cumul[iS2]; s3 = cumul[iS3];
		// la plateforme tourne d'un demi-tour sur chaque poulie, dans le sens où tourne le chariot
		capB = Math.round(cap(dB) / 90f) * 90f; sensB = Mth.wrapDegrees(cap(rB.scale(-1)) - cap(dB)) >= 0 ? 1 : -1;
		capA = Math.round(cap(dA.scale(-1)) / 90f) * 90f; sensA = Mth.wrapDegrees(cap(rA) - cap(dA.scale(-1))) >= 0 ? 1 : -1;
	}
	/** Une travée de câble (avec son affaissement), échantillonnée comme le rendu. */
	private void portee(Vec3 a, Vec3 b, boolean premier) {
		int m = Math.max(4, (int) (a.distanceTo(b) / 1.5));
		for (int k = premier ? 0 : 1; k <= m; k++) ech.add(Telepherique.chainette(a, b, k / (double) m));
	}
	private double boucle(double s) { return longueur <= 0 ? 0 : ((s % longueur) + longueur) % longueur; }
	/** Distance à parcourir (toujours en avant sur la boucle) de s jusqu'à c. */
	private double avant(double s, double c) { return boucle(c - s); }
	/** Le chariot à l'abscisse s ; renvoie aussi la direction de marche (dans dir[0]). */
	private Vec3 chariot(double s, Vec3[] dir) {
		if (ech.size() < 2) return position();
		s = boucle(s);
		int i = 1;
		while (i < cumul.length - 1 && cumul[i] < s) i++;
		double t = cumul[i] - cumul[i - 1] < 1e-6 ? 0 : (s - cumul[i - 1]) / (cumul[i] - cumul[i - 1]);
		if (dir != null) dir[0] = ech.get(i).subtract(ech.get(i - 1));
		return ech.get(i - 1).lerp(ech.get(i), Math.max(0, Math.min(1, t)));
	}
	private void placer(double s) {
		Vec3[] d = new Vec3[1];
		Vec3 c = chariot(s, d);
		setPos(c.x, c.y - Telepherique.SUSPENTE, c.z);
		if (d[0] == null) return;
		lacetChariot = cap(d[0]);
		s = boucle(s);
		// sur les poulies, la plateforme pivote en douceur ; ailleurs, calée d'équerre (comme sa collision)
		if (s > s1 && s < s2) lacet = capB + sensB * 180f * (float) ((s - s1) / (s2 - s1));
		else if (s > s3) lacet = capA + sensA * 180f * (float) ((s - s3) / (longueur - s3));
		else lacet = Math.round(lacetChariot / 90f) * 90f;
	}
	public double abscisse() { return level().isClientSide ? sLocal : entityData.get(S); }
	public boolean enRoute() { return avant(entityData.get(S), entityData.get(CIBLE)) > 1e-3 || Math.abs(entityData.get(V)) > 0; }
	/** Arrêt de la gare g sur la boucle : 0 en A, fin du demi-tour en B. */
	private double arret(BlockPos g) { return g.equals(gareA) ? 0 : s2; }

	// ------------------------------------------------------------------ commandes
	/** Envoie la nacelle vers la gare g (appel depuis une gare ou départ avec des voyageurs). */
	boolean vers(BlockPos g, @Nullable Player qui) {
		float c = (float) arret(g);
		if (Math.abs(boucle(entityData.get(S)) - c) < 1e-3 || avant(entityData.get(S), c) > longueur - 1e-3) { if (qui != null) qui.displayClientMessage(Component.translatable("airain.telepherique.la").withStyle(ChatFormatting.GRAY), true); return false; }
		float v = vitesseLigne();
		if (v <= 0) { if (qui != null) qui.displayClientMessage(Component.translatable("airain.telepherique.immobile").withStyle(ChatFormatting.RED), true); return false; }
		vitesse = v;
		entityData.set(CIBLE, c);
		entityData.set(V, v);
		annoncer(v * (float) lissage(entityData.get(S), c, v));
		level().playSound(null, blockPosition(), SoundEvents.IRON_DOOR_CLOSE, SoundSource.BLOCKS, 0.7f, 0.7f);
		return true;
	}
	/** Vitesse donnée par les gares entraînées (en blocs par tick). */
	private float vitesseLigne() {
		float rpm = 0;
		for (BlockPos g : new BlockPos[]{gareA, gareB})
			if (g != null && level().isLoaded(g) && level().getBlockEntity(g) instanceof Telepherique.GareBlockEntity ge) rpm = Math.max(rpm, ge.vitesse());
		if (rpm <= 0) return 0;
		return Math.max(0.04f, rpm / 256f * VITESSE_256);
	}
	/** Les poulies tournent (et le câble défile) à la vitesse réelle de la nacelle ; prévenues seulement quand elle change. */
	private void annoncer(float v) {
		if (v > 0 && vitesseAnnoncee > 0 && Math.abs(v - vitesseAnnoncee) < 0.1f * Math.max(vitesse, 0.04f)) return;
		vitesseAnnoncee = v;
		for (BlockPos g : new BlockPos[]{gareA, gareB})
			if (g != null && level().isLoaded(g) && level().getBlockEntity(g) instanceof Telepherique.GareBlockEntity ge) ge.tourne(v > 0, v);
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
		// décidé par le serveur seul : côté client, l'arrivée n'est pas encore connue quand le serveur fait descendre les voyageurs
		if (e.isDismounting() && !e.getLevel().isClientSide() && e.getEntityBeingMounted() instanceof Nacelle n && n.enRoute()) e.setCanceled(true);
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
			if (g != null && level().isLoaded(g) && level().getBlockEntity(g) instanceof Telepherique.GareBlockEntity ge && getUUID().equals(ge.nacelle)) { ge.nacelle = null; ge.tourne(false, 0); ge.setChanged(); }
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
		for (Vec3 v : centres) if (Math.abs(v.x - p.getX() - 0.5) < Telepherique.BRIN + 0.6 && Math.abs(v.z - p.getZ() - 0.5) < Telepherique.BRIN + 0.6 && Math.abs(v.y - p.getY()) < 2.5) return true;
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
			if (v > 0) sLocal = boucle(sLocal + Math.min(avant(sLocal, cible), v * lissage(sLocal, cible, v)));
			double ecart = Mth.wrapDegrees((entityData.get(S) - sLocal) / longueur * 360) / 360 * longueur;
			sLocal = boucle(sLocal + ecart * 0.15);
			if (v == 0) sLocal = entityData.get(S);
			placer(sLocal);
			return;
		}
		// une nacelle que ses gares ne reconnaissent plus (une autre l'a remplacée) redevient un objet
		if (tickCount % 40 == 0 && gareA != null && level().isLoaded(gareA) && level().getBlockEntity(gareA) instanceof Telepherique.GareBlockEntity ge
			&& ge.nacelle != null && !ge.nacelle.equals(getUUID())) {
			ejectPassengers(); spawnAtLocation(new ItemStack(Telepherique.NACELLE_ITEM.get())); discard(); return;
		}
		float s = entityData.get(S), cible = entityData.get(CIBLE);
		if (depart > 0 && --depart == 0) {
			depart = -1;
			if (!getPassengers().isEmpty()) vers(Math.abs(s) < 1e-3 ? gareB : gareA, getPassengers().get(0) instanceof Player p ? p : null);
		}
		double reste = avant(s, cible);
		if (reste > 1e-3) {
			float v = vitesseLigne();
			if (v > 0) vitesse = v;                                   // une gare chargée et entraînée : on suit sa vitesse
			float pas = (float) (vitesse * lissage(s, cible, vitesse));
			s = pas >= reste ? cible : (float) boucle(s + pas);
			entityData.set(S, s);
			entityData.set(V, s == cible ? 0f : vitesse);
			annoncer(s == cible ? 0 : pas);
			if (tickCount % 20 == 0 && level() instanceof ServerLevel sl)      // la nacelle garde chargé le tronçon qu'elle traverse
				sl.getChunkSource().addRegionTicket(TicketType.PORTAL, new ChunkPos(blockPosition()), 3, blockPosition());
			if (s == cible) arrivee();
		}
		placer(s);
	}
	/** Démarrage et freinage en douceur près des gares (sur une distance qui grandit avec la vitesse). */
	private double lissage(double s, double cible, float v) {
		double rampe = 2 + 8 * v;
		double depuis = Math.min(avant(0, s), avant(s2, s)), reste = avant(s, cible);
		return Math.max(0.15, Math.min(1, Math.min(depuis / rampe + 0.25, reste / rampe + 0.15)));
	}
	private void arrivee() {
		entityData.set(V, 0f);
		annoncer(0);
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
		centres.clear();
		gareA = t.contains("a") ? BlockPos.of(t.getLong("a")) : null; gareB = t.contains("b") ? BlockPos.of(t.getLong("b")) : null;
		vitesse = t.getFloat("vitesse");
		if (t.contains("centres")) {
			for (Tag x : t.getList("centres", Tag.TAG_COMPOUND)) { CompoundTag c = (CompoundTag) x; centres.add(new Vec3(c.getDouble("x"), c.getDouble("y"), c.getDouble("z"))); }
			echantillonner();
			entityData.set(S, t.getFloat("s")); entityData.set(CIBLE, t.getFloat("cible"));
		} else {
			// nacelle d'avant la 1.68 : elle gardait les points du brin droit, et faisait la navette dessus (0 en A, la longueur en B)
			List<Vec3> brin = new ArrayList<>();
			for (Tag x : t.getList("points", Tag.TAG_COMPOUND)) { CompoundTag c = (CompoundTag) x; brin.add(new Vec3(c.getDouble("x"), c.getDouble("y"), c.getDouble("z"))); }
			for (int i = 0; i < brin.size(); i++)
				centres.add(brin.get(i).subtract(Telepherique.droite(i > 0 ? brin.get(i - 1) : null, brin.get(i), i + 1 < brin.size() ? brin.get(i + 1) : null).scale(Telepherique.BRIN)));
			echantillonner();
			float s = t.getFloat("s"), c = t.getFloat("cible");
			boolean versA = c < s - 1e-3;
			float ns = s < 1e-3 ? 0 : s > s1 - 1e-3 ? (float) s2 : versA ? (float) (s2 + (s1 - s)) : s;
			float nc = Math.abs(c - s) < 1e-3 ? ns : versA ? 0 : (float) s2;
			entityData.set(S, ns); entityData.set(CIBLE, nc);
		}
		float s = entityData.get(S), c = entityData.get(CIBLE);
		entityData.set(V, avant(s, c) > 1e-3 ? vitesse : 0f);
		sLocal = s;
	}
	@Override
	protected void addAdditionalSaveData(CompoundTag t) {
		ListTag l = new ListTag();
		for (Vec3 v : centres) { CompoundTag c = new CompoundTag(); c.putDouble("x", v.x); c.putDouble("y", v.y); c.putDouble("z", v.z); l.add(c); }
		t.put("centres", l);
		if (gareA != null) t.putLong("a", gareA.asLong());
		if (gareB != null) t.putLong("b", gareB.asLong());
		t.putFloat("s", entityData.get(S)); t.putFloat("cible", entityData.get(CIBLE)); t.putFloat("vitesse", vitesse);
	}
	@Override
	public void writeSpawnData(RegistryFriendlyByteBuf b) {
		b.writeVarInt(centres.size());
		for (Vec3 v : centres) { b.writeDouble(v.x); b.writeDouble(v.y); b.writeDouble(v.z); }
		b.writeFloat(entityData.get(S));
	}
	@Override
	public void readSpawnData(RegistryFriendlyByteBuf b) {
		centres.clear();
		int n = b.readVarInt();
		for (int i = 0; i < n; i++) centres.add(new Vec3(b.readDouble(), b.readDouble(), b.readDouble()));
		echantillonner();
		sLocal = b.readFloat();
		placer(sLocal); setOldPosAndRot(); lacetAvant = lacet; lacetChariotAvant = lacetChariot;
	}
}
