package fr.chatmort.airain.armure;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.event.entity.player.CriticalHitEvent;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/** Effets des armes sacrées et impériales, et Filon de la pioche. */
public final class Armes {
	private Armes() {}

	/** Ce qu'une attaque de zone peut toucher : les monstres et ce qui vise le joueur, jamais un gardien ni un animal apprivoisé. */
	static boolean ennemi(Player p, LivingEntity e) {
		if (e == p || !e.isAlive() || e instanceof Player || e instanceof fr.chatmort.airain.gardien.GardienEntity) return false;
		if (e instanceof OwnableEntity o && o.getOwnerUUID() != null) return false;
		return e instanceof Enemy || (e instanceof Mob m && m.getTarget() == p);
	}

	static float degats(Player p) { return (float) p.getAttributeValue(Attributes.ATTACK_DAMAGE); }

	static void arc(ServerLevel sl, Vec3 de, Vec3 a) {
		int pas = Math.max(2, (int) (de.distanceTo(a) * 3));
		for (int i = 0; i <= pas; i++) {
			Vec3 q = de.lerp(a, i / (double) pas);
			sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, q.x + (sl.random.nextDouble() - .5) * .3, q.y + (sl.random.nextDouble() - .5) * .3,
				q.z + (sl.random.nextDouble() - .5) * .3, 1, 0, 0, 0, 0);
		}
	}

	static Vec3 centre(LivingEntity e) { return e.position().add(0, e.getBbHeight() * 0.55, 0); }

	// ------------------------------------------------------------ épée : Jugement
	static void jugement(ServerLevel sl, ServerPlayer p, LivingEntity cible, int palier) {
		var d = cible.getPersistentData();
		long t = sl.getGameTime();
		int n = (t - d.getLong("airain_jugement_t") > 100 ? 0 : d.getInt("airain_jugement")) + 1;
		d.putLong("airain_jugement_t", t);
		int seuil = palier == 2 ? 4 : 5;
		if (n < seuil) { d.putInt("airain_jugement", n); return; }
		d.putInt("airain_jugement", 0);
		float force = palier == 2 ? 8f : 5f;
		Vec3 haut = centre(cible).add(0, 2.5, 0);
		arc(sl, haut, centre(cible));
		cible.invulnerableTime = 0;
		cible.hurt(sl.damageSources().indirectMagic(p, p), force);
		if (palier == 2) {
			List<LivingEntity> voisins = sl.getEntitiesOfClass(LivingEntity.class, cible.getBoundingBox().inflate(6), e -> e != cible && ennemi(p, e));
			voisins.sort(java.util.Comparator.comparingDouble(cible::distanceToSqr));
			for (LivingEntity v : voisins.subList(0, Math.min(2, voisins.size()))) {
				arc(sl, centre(cible), centre(v));
				v.invulnerableTime = 0;
				v.hurt(sl.damageSources().indirectMagic(p, p), 6f);
			}
		}
		sl.playSound(null, cible.blockPosition(), SoundEvents.LIGHTNING_BOLT_IMPACT, SoundSource.PLAYERS, 0.7f, 1.7f);
	}

	// ------------------------------------------------------------ twinblade : second coup différé, tourbillon
	private record Coup(UUID joueur, LivingEntity cible, float degats, long quand) {}
	private static final List<Coup> COUPS = new ArrayList<>();

	static void doubleCoup(ServerPlayer p, LivingEntity cible, int palier) {
		COUPS.add(new Coup(p.getUUID(), cible, degats(p) * (palier == 2 ? 0.5f : 0.25f), cible.level().getGameTime() + 4));
	}

	static void tourbillon(ServerPlayer p, ArmeItem arme) {
		if (p.getCooldowns().isOnCooldown(arme)) return;
		ServerLevel sl = p.serverLevel();
		for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(3.5, 1, 3.5), e -> ennemi(p, e))) {
			e.invulnerableTime = 0;
			e.hurt(sl.damageSources().playerAttack(p), degats(p) * 0.8f);
			e.knockback(0.5, p.getX() - e.getX(), p.getZ() - e.getZ());
		}
		for (int k = 0; k < 12; k++) {
			double a = k * Math.PI / 6;
			sl.sendParticles(ParticleTypes.SWEEP_ATTACK, p.getX() + Math.cos(a) * 2.2, p.getY() + 1, p.getZ() + Math.sin(a) * 2.2, 1, 0, 0, 0, 0);
		}
		sl.playSound(null, p.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 1f, 0.7f);
		sl.playSound(null, p.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 1f, 1.2f);
		p.getCooldowns().addCooldown(arme, 80);
		p.swing(net.minecraft.world.InteractionHand.MAIN_HAND, true);
	}

	// ------------------------------------------------------------ katana : Iai (ruée) et Second souffle
	private static final Map<UUID, Long> RUEE = new HashMap<>();          // fin de la ruée
	private static final Map<UUID, Set<Integer>> TOUCHES = new HashMap<>();
	private static final Map<UUID, Long> CRITIQUE = new HashMap<>();      // coup critique garanti jusqu'à

	static void iai(ServerPlayer p, ArmeItem arme, int palier) {
		if (p.getCooldowns().isOnCooldown(arme)) return;
		Vec3 v = p.getLookAngle().multiply(1, 0, 1);
		if (v.lengthSqr() < 1e-4) return;
		v = v.normalize().scale(palier == 2 ? 1.9 : 1.3);
		p.setDeltaMovement(v.x, 0.12, v.z);
		p.hurtMarked = true;
		long t = p.serverLevel().getGameTime();
		RUEE.put(p.getUUID(), t + 8);
		TOUCHES.put(p.getUUID(), new HashSet<>());
		CRITIQUE.put(p.getUUID(), t + 8 + 60);
		p.getCooldowns().addCooldown(arme, palier == 2 ? 60 : 100);
		p.serverLevel().playSound(null, p.blockPosition(), SoundEvents.TRIDENT_RIPTIDE_1.value(), SoundSource.PLAYERS, 0.8f, 1.5f);
		p.swing(net.minecraft.world.InteractionHand.MAIN_HAND, true);
	}

	/** Pendant la ruée : tranche tout ce que le joueur traverse. */
	public static void joueur(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		Long fin = RUEE.get(p.getUUID());
		if (fin == null) return;
		ServerLevel sl = p.serverLevel();
		if (sl.getGameTime() > fin) { RUEE.remove(p.getUUID()); TOUCHES.remove(p.getUUID()); return; }
		ItemStack s = p.getMainHandItem();
		if (!(s.getItem() instanceof ArmeItem arme) || arme.type != ArmeItem.Type.KATANA) { RUEE.remove(p.getUUID()); return; }
		sl.sendParticles(ParticleTypes.SWEEP_ATTACK, p.getX(), p.getY() + 1, p.getZ(), 1, 0, 0, 0, 0);
		Set<Integer> deja = TOUCHES.get(p.getUUID());
		for (LivingEntity c : sl.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(1.2), c -> ennemi(p, c) && !deja.contains(c.getId()))) {
			deja.add(c.getId());
			c.invulnerableTime = 0;
			c.hurt(sl.damageSources().playerAttack(p), degats(p));
			sl.sendParticles(ParticleTypes.CRIT, c.getX(), c.getY() + c.getBbHeight() * .6, c.getZ(), 8, .3, .3, .3, .2);
			if (!c.isAlive() && arme.palier == 2) p.getCooldowns().removeCooldown(arme);    // achevé : on peut enchaîner
		}
	}

	/** Second souffle : le premier coup après une ruée est critique ; les critiques du katana frappent plus fort. */
	public static void critique(CriticalHitEvent e) {
		if (!(e.getEntity().getMainHandItem().getItem() instanceof ArmeItem arme) || arme.type != ArmeItem.Type.KATANA) return;
		Long jusqua = CRITIQUE.get(e.getEntity().getUUID());
		if (jusqua != null && e.getEntity().level().getGameTime() <= jusqua) {
			e.setCriticalHit(true);
			CRITIQUE.remove(e.getEntity().getUUID());
		}
		if (e.isCriticalHit()) e.setDamageMultiplier(arme.palier == 2 ? 2.0f : 1.75f);
	}

	// ------------------------------------------------------------ espadon : Fracas
	static void fracas(ServerPlayer p, ArmeItem arme, int palier) {
		if (p.getCooldowns().isOnCooldown(arme)) return;
		ServerLevel sl = p.serverLevel();
		double r = palier == 2 ? 6 : 4;
		float force = palier == 2 ? 10f : 6f;
		for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(r, 1.5, r), e -> ennemi(p, e) && e.distanceTo(p) <= r)) {
			e.invulnerableTime = 0;
			e.hurt(sl.damageSources().playerAttack(p), force);
			e.knockback(1.2, p.getX() - e.getX(), p.getZ() - e.getZ());
			e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
		}
		BlockState sol = sl.getBlockState(p.blockPosition().below());
		if (!sol.isAir())
			for (int k = 0; k < 40; k++) {
				double a = k * Math.PI * 2 / 40, d = r * (0.4 + sl.random.nextDouble() * 0.6);
				sl.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, sol), p.getX() + Math.cos(a) * d, p.getY() + 0.1, p.getZ() + Math.sin(a) * d, 4, 0.1, 0.3, 0.1, 0.2);
			}
		sl.sendParticles(ParticleTypes.EXPLOSION, p.getX(), p.getY() + 0.2, p.getZ(), 1, 0, 0, 0, 0);
		sl.playSound(null, p.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.PLAYERS, 0.8f, 0.6f);
		sl.playSound(null, p.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.6f, 0.5f);
		p.getCooldowns().addCooldown(arme, palier == 2 ? 100 : 140);
		p.swing(net.minecraft.world.InteractionHand.MAIN_HAND, true);
		p.getMainHandItem().hurtAndBreak(2, p, EquipmentSlot.MAINHAND);
	}

	// ------------------------------------------------------------ tick serveur : seconds coups de la twinblade
	public static void tick(ServerTickEvent.Post e) {
		if (COUPS.isEmpty()) return;
		Iterator<Coup> it = COUPS.iterator();
		while (it.hasNext()) {
			Coup c = it.next();
			if (!(c.cible().level() instanceof ServerLevel sl)) { it.remove(); continue; }
			if (sl.getGameTime() < c.quand()) continue;
			it.remove();
			if (!c.cible().isAlive()) continue;
			Player p = sl.getPlayerByUUID(c.joueur());
			if (p == null) continue;
			c.cible().invulnerableTime = 0;
			c.cible().hurt(sl.damageSources().playerAttack(p), c.degats());
			sl.sendParticles(ParticleTypes.SWEEP_ATTACK, c.cible().getX(), c.cible().getY() + c.cible().getBbHeight() * .6, c.cible().getZ(), 1, 0, 0, 0, 0);
			sl.playSound(null, c.cible().blockPosition(), SoundEvents.PLAYER_ATTACK_STRONG, SoundSource.PLAYERS, 0.7f, 1.4f);
		}
	}

	// ------------------------------------------------------------ pioche : Filon
	private static boolean filonEnCours;

	public static void filon(BlockEvent.BreakEvent e) {
		if (filonEnCours || !(e.getPlayer() instanceof ServerPlayer p) || !p.isShiftKeyDown()) return;
		ItemStack outil = p.getMainHandItem();
		if (!(outil.getItem() instanceof PiocheItem pioche) || !e.getState().is(Tags.Blocks.ORES)) return;
		if (!(e.getLevel() instanceof ServerLevel sl)) return;
		BlockState type = e.getState();
		ArrayDeque<BlockPos> file = new ArrayDeque<>();
		Set<BlockPos> vus = new HashSet<>();
		file.add(e.getPos()); vus.add(e.getPos());
		List<BlockPos> filon = new ArrayList<>();
		while (!file.isEmpty() && filon.size() < pioche.filon()) {
			BlockPos b = file.poll();
			for (int dx = -1; dx <= 1; dx++)
				for (int dy = -1; dy <= 1; dy++)
					for (int dz = -1; dz <= 1; dz++) {
						BlockPos v = b.offset(dx, dy, dz);
						if (vus.add(v) && sl.getBlockState(v).is(type.getBlock())) { file.add(v); if (filon.size() < pioche.filon()) filon.add(v); }
					}
		}
		filonEnCours = true;
		try {
			for (BlockPos b : filon) {
				if (outil.isEmpty() || !(outil.getItem() instanceof PiocheItem)) break;
				BlockState s = sl.getBlockState(b);
				if (!s.is(type.getBlock())) continue;
				var be = sl.getBlockEntity(b);
				net.minecraft.world.level.block.Block.dropResources(s, sl, b, be, p, outil);
				int xp = s.getExpDrop(sl, b, be, p, outil);
				sl.destroyBlock(b, false, p);
				if (xp > 0) s.getBlock().popExperience(sl, b, xp);
				sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, b.getX() + .5, b.getY() + .5, b.getZ() + .5, 3, .3, .3, .3, .05);
				outil.hurtAndBreak(1, p, EquipmentSlot.MAINHAND);
			}
		} finally { filonEnCours = false; }
		if (!filon.isEmpty()) sl.playSound(null, e.getPos(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1f, 0.8f);
	}

	/** Écart d'angle utile aux tests (non utilisé en jeu). */
	static float angle(float a) { return Mth.wrapDegrees(a); }
}
