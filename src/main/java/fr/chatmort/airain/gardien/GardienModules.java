package fr.chatmort.airain.gardien;

import java.util.Comparator;
import java.util.List;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.targeting.TargetingConditions;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.Vec3;

/** Effets, montage et démontage des modules de gardien. */
public final class GardienModules {
	private GardienModules() {}

	private static final ResourceLocation ARMURE = ResourceLocation.fromNamespaceAndPath("airain", "module_blindage");
	private static final ResourceLocation FORCE = ResourceLocation.fromNamespaceAndPath("airain", "module_lunette");
	private static final ResourceLocation PORTEE = ResourceLocation.fromNamespaceAndPath("airain", "module_portee");

	/** Portées et puissances, par niveau (index 1 et 2). */
	static final int[] RAYON_LANTERNE = {0, 24, 48}, PORTEE_CANON = {0, 20, 40}, RAYON_TESLA = {0, 8, 16}, CIBLES_TESLA = {0, 3, 6};
	static final float[] DEGATS_CANON = {0, 7, 14}, DEGATS_TESLA = {0, 5, 10};

	public static ItemStack objet(int code) {
		Module m = Module.de(code);
		if (m == null) return ItemStack.EMPTY;
		return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("airain", m.id(Module.niveau(code)))));
	}

	// ------------------------------------------------------------ montage
	static void monter(GardienEntity g, Player p, ItemStack s, ModuleItem mi) {
		Module.Emplacement e = mi.module.emplacement;
		// le capitaine impérial porte les deux modules d'un emplacement : le second va dans la seconde case
		boolean second = g.capitaine() && Module.de(g.codeModule(e)) != null && Module.de(g.codeModule(e)) != mi.module;
		int avant = second ? g.codeModule2(e) : g.codeModule(e);
		if (avant == mi.code()) { p.displayClientMessage(Component.translatable("airain.gardien.module_deja"), true); return; }
		if (Module.de(avant) == Module.LANTERNE) eteindre(g);
		if (second) g.poserModule2(e, mi.code()); else g.poserModule(e, mi.code());
		ItemStack monte = s.copyWithCount(1);
		if (!p.getAbilities().instabuild) s.shrink(1);
		if (avant != 0) {
			ItemStack rendu = objet(avant);
			if (!p.getInventory().add(rendu)) p.drop(rendu, false);
			p.displayClientMessage(Component.translatable("airain.gardien.module_remplace", monte.getHoverName(), objet(avant).getHoverName()), true);
		} else p.displayClientMessage(Component.translatable("airain.gardien.module_monte", monte.getHoverName()), true);
		ServerLevel sl = (ServerLevel) g.level();
		etape(p, "airain_module_monte");
		if (mi.niveau == 2) etape(p, "airain_module_2");
		sl.playSound(null, g.blockPosition(), SoundEvents.SMITHING_TABLE_USE, SoundSource.NEUTRAL, 1f, 1.1f);
		sl.playSound(null, g.blockPosition(), SoundEvents.IRON_GOLEM_REPAIR, SoundSource.NEUTRAL, 0.8f, 1.3f);
		sl.sendParticles(ParticleTypes.WAX_ON, g.getX(), g.getY() + 1.8, g.getZ(), 10, 0.5, 0.6, 0.5, 0.1);
	}

	/** Étape de quête (FTB Quests, via KubeJS). */
	static void etape(Player p, String etape) {
		if (!(p instanceof net.minecraft.server.level.ServerPlayer sp)) return;
		var srv = sp.getServer();
		srv.getCommands().performPrefixedCommand(srv.createCommandSourceStack().withSuppressedOutput().withPermission(4),
			"kubejs stages add " + sp.getGameProfile().getName() + " " + etape);
	}

	static void demonter(GardienEntity g, Player p) {
		eteindre(g);
		for (Module.Emplacement e : Module.Emplacement.values()) {
			for (int c : new int[] {g.codeModule(e), g.codeModule2(e)}) {
				if (c == 0) continue;
				ItemStack rendu = objet(c);
				if (!p.getInventory().add(rendu)) p.drop(rendu, false);
			}
			g.poserModule(e, 0); g.poserModule2(e, 0);
		}
		p.displayClientMessage(Component.translatable("airain.gardien.modules_demontes"), true);
		g.level().playSound(null, g.blockPosition(), SoundEvents.CHAIN_BREAK, SoundSource.NEUTRAL, 1f, 0.8f);
	}

	/** À la destruction du gardien, ses modules tombent au sol. */
	static void lacher(GardienEntity g) {
		for (Module.Emplacement e : Module.Emplacement.values()) {
			int c = g.codeModule(e), c2 = g.codeModule2(e);
			if (c != 0) { g.spawnAtLocation(objet(c)); g.poserModule(e, 0); }
			if (c2 != 0) { g.spawnAtLocation(objet(c2)); g.poserModule2(e, 0); }
		}
	}

	static Component resume(GardienEntity g) {
		MutableComponent l = null;
		for (Module.Emplacement e : Module.Emplacement.values())
			for (int c : new int[] {g.codeModule(e), g.codeModule2(e)}) {
				if (c == 0) continue;
				Component n = objet(c).getHoverName();
				l = l == null ? n.copy() : l.append(", ").append(n);
			}
		return l == null ? Component.empty() : Component.translatable("airain.gardien.modules_resume", l);
	}

	// ------------------------------------------------------------ attributs (blindage, longue-vue, portée)
	static void attributs(GardienEntity g) {
		int bl = g.niveau(Module.BLINDAGE), lu = g.niveau(Module.LUNETTE), la = g.niveau(Module.LANTERNE), ca = g.niveau(Module.CANON);
		modif(g.getAttribute(Attributes.ARMOR), ARMURE, 10 * bl, AttributeModifier.Operation.ADD_VALUE);
		modif(g.getAttribute(Attributes.ATTACK_DAMAGE), FORCE, 0.3 * lu, AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
		double portee = Math.max(la * 8, ca > 0 ? PORTEE_CANON[ca] + 4 - 16 : 0);   // golem : 16 blocs de base
		modif(g.getAttribute(Attributes.FOLLOW_RANGE), PORTEE, portee, AttributeModifier.Operation.ADD_VALUE);
	}

	private static void modif(AttributeInstance a, ResourceLocation id, double v, AttributeModifier.Operation op) {
		if (a == null) return;
		a.removeModifier(id);
		if (v != 0) a.addTransientModifier(new AttributeModifier(id, v, op));
	}

	// ------------------------------------------------------------ chaudière de secours
	/** Au lieu d'être détruit, le gardien se relève (1 ou 2 fois par jour de jeu). */
	static boolean sauver(GardienEntity g) {
		int n = g.actif(Module.CHAUDIERE);
		if (n == 0) return false;
		long jour = g.level().getDayTime() / 24000L;
		if (jour != g.jourSauvetage) { g.jourSauvetage = jour; g.sauvetages = 0; }
		if (g.sauvetages >= n) return false;
		g.sauvetages++;
		g.setHealth(g.getMaxHealth() * 0.3f);
		ServerLevel sl = (ServerLevel) g.level();
		sl.sendParticles(ParticleTypes.CLOUD, g.getX(), g.getY() + 2, g.getZ(), 30, 0.6, 0.6, 0.6, 0.08);
		sl.sendParticles(ParticleTypes.LAVA, g.getX(), g.getY() + 1.6, g.getZ(), 6, 0.4, 0.3, 0.4, 0.1);
		sl.playSound(null, g.blockPosition(), SoundEvents.FIRECHARGE_USE, SoundSource.NEUTRAL, 1f, 0.6f);
		sl.playSound(null, g.blockPosition(), SoundEvents.IRON_GOLEM_REPAIR, SoundSource.NEUTRAL, 1f, 0.7f);
		return true;
	}

	// ------------------------------------------------------------ chaque tick (serveur, gardien en marche)
	static void tick(GardienEntity g) {
		ServerLevel sl = (ServerLevel) g.level();
		int la = g.niveau(Module.LANTERNE);
		if (la > 0) {
			if (g.tickCount % 10 == 0) allumer(g, la);
			if (g.tickCount % 20 == 0)
				for (Mob m : sl.getEntitiesOfClass(Mob.class, g.getBoundingBox().inflate(RAYON_LANTERNE[la]), GardienEntity::hostile))
					m.addEffect(new MobEffectInstance(MobEffects.GLOWING, 40, 0, false, false));
		}
		int ch = g.niveau(Module.CHAUDIERE);
		if (ch > 0 && g.tickCount % (ch == 2 ? 50 : 100) == 0 && g.getHealth() < g.getMaxHealth()) g.heal(1f);
		int ca = g.niveau(Module.CANON);
		if (ca > 0) {
			if (g.rechargeCanon > 0) g.rechargeCanon--;
			else tirer(g, sl, ca);
		}
		int te = g.niveau(Module.TESLA);
		if (te > 0) {
			if (g.rechargeTesla > 0) g.rechargeTesla--;
			else arc(g, sl, te);
		}
	}

	private static Vec3 bouche(GardienEntity g) {
		float r = g.yBodyRot * Mth.DEG_TO_RAD;
		Vec3 avant = new Vec3(-Mth.sin(r), 0, Mth.cos(r)), droite = new Vec3(-Mth.cos(r), 0, -Mth.sin(r));
		return g.position().add(0, 1.95, 0).add(droite.scale(0.69)).add(avant.scale(0.6));
	}

	private static void tirer(GardienEntity g, ServerLevel sl, int n) {
		LivingEntity t = g.getTarget();
		if (t == null || !t.isAlive()) return;
		double d = g.distanceTo(t);
		if (d > PORTEE_CANON[n] || d < 3 || !g.hasLineOfSight(t)) return;
		g.rechargeCanon = 60;
		Vec3 de = bouche(g), a = t.position().add(0, t.getBbHeight() * 0.5, 0);
		t.hurt(g.damageSources().mobAttack(g), DEGATS_CANON[n]);
		sl.broadcastEntityEvent(g, (byte) 60);
		sl.playSound(null, g.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.NEUTRAL, 0.7f, 1.5f);
		sl.sendParticles(ParticleTypes.LARGE_SMOKE, de.x, de.y, de.z, 6, 0.1, 0.1, 0.1, 0.02);
		int pas = (int) (d * 2);
		for (int i = 1; i < pas; i++) {
			Vec3 p = de.lerp(a, i / (double) pas);
			sl.sendParticles(ParticleTypes.SMOKE, p.x, p.y, p.z, 1, 0, 0, 0, 0);
		}
		sl.sendParticles(ParticleTypes.EXPLOSION, a.x, a.y, a.z, 1, 0, 0, 0, 0);
	}

	private static void arc(GardienEntity g, ServerLevel sl, int n) {
		List<Mob> proches = sl.getEntitiesOfClass(Mob.class, g.getBoundingBox().inflate(RAYON_TESLA[n]),
			m -> GardienEntity.hostile(m) && m.isAlive() && g.hasLineOfSight(m));
		if (proches.isEmpty()) { g.rechargeTesla = 20; return; }
		proches.sort(Comparator.comparingDouble(g::distanceToSqr));
		g.rechargeTesla = 160;
		Vec3 de = g.position().add(0, 2.9, 0);
		for (Mob m : proches.subList(0, Math.min(CIBLES_TESLA[n], proches.size()))) {
			m.hurt(g.damageSources().indirectMagic(g, g), DEGATS_TESLA[n]);
			m.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
			Vec3 a = m.position().add(0, m.getBbHeight() * 0.5, 0);
			int pas = (int) (de.distanceTo(a) * 3);
			for (int i = 1; i <= pas; i++) {
				Vec3 p = de.lerp(a, i / (double) pas).add((sl.random.nextDouble() - 0.5) * 0.3, (sl.random.nextDouble() - 0.5) * 0.3, (sl.random.nextDouble() - 0.5) * 0.3);
				sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, p.x, p.y, p.z, 1, 0, 0, 0, 0);
			}
		}
		sl.broadcastEntityEvent(g, (byte) 61);
		sl.playSound(null, g.blockPosition(), SoundEvents.LIGHTNING_BOLT_IMPACT, SoundSource.NEUTRAL, 0.6f, 1.8f);
	}

	// ------------------------------------------------------------ lumière de la tête-lanterne
	private static void allumer(GardienEntity g, int niveau) {
		ServerLevel sl = (ServerLevel) g.level();
		BlockPos cible = null;
		for (int dy : new int[] {2, 1}) {
			BlockPos p = g.blockPosition().above(dy);
			BlockState s = sl.getBlockState(p);
			if (s.is(Blocks.LIGHT) || s.isAir() || (s.is(Blocks.WATER) && s.getFluidState().isSource())) { cible = p; break; }
		}
		if (cible != null && cible.equals(g.lumiere) && sl.getBlockState(cible).is(Blocks.LIGHT)) return;
		eteindre(g);
		if (cible == null) return;
		boolean eau = sl.getFluidState(cible).is(Fluids.WATER);
		sl.setBlock(cible, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, niveau == 2 ? 15 : 12)
			.setValue(BlockStateProperties.WATERLOGGED, eau), 3);
		g.lumiere = cible;
	}

	/** Retire la lumière posée par la tête-lanterne. */
	static void eteindre(GardienEntity g) {
		if (g.lumiere == null || !(g.level() instanceof ServerLevel sl)) return;
		BlockState s = sl.getBlockState(g.lumiere);
		if (s.is(Blocks.LIGHT))
			sl.setBlock(g.lumiere, s.getValue(BlockStateProperties.WATERLOGGED) ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState(), 3);
		g.lumiere = null;
	}

	// ------------------------------------------------------------ côté client : vapeur, étincelles
	static void particules(GardienEntity g) {
		var lv = g.level();
		float r = g.yBodyRot * Mth.DEG_TO_RAD;
		double ax = -Mth.sin(r), az = Mth.cos(r);
		if (g.niveau(Module.CHAUDIERE) > 0 && g.getRandom().nextInt(8) == 0)
			lv.addParticle(ParticleTypes.CLOUD, g.getX() - ax * 0.62, g.getY() + 2.45, g.getZ() - az * 0.62, 0, 0.04, 0);
		if (g.niveau(Module.TESLA) > 0 && g.getRandom().nextInt(g.eclairTesla > 0 ? 1 : 14) == 0)
			lv.addParticle(ParticleTypes.ELECTRIC_SPARK, g.getX() - ax * 0.4 + (g.getRandom().nextDouble() - 0.5) * 0.4, g.getY() + 2.9,
				g.getZ() - az * 0.4 + (g.getRandom().nextDouble() - 0.5) * 0.4, 0, 0.05, 0);
		if (g.niveau(Module.LANTERNE) > 0 && g.getRandom().nextInt(40) == 0)
			lv.addParticle(ParticleTypes.SMALL_FLAME, g.getX(), g.getY() + 2.75, g.getZ(), 0, 0.01, 0);
	}

	// ------------------------------------------------------------ ciblage (la longue-vue voit les invisibles)
	static class Cibler extends NearestAttackableTargetGoal<Mob> {
		private final GardienEntity g;

		Cibler(GardienEntity g) {
			super(g, Mob.class, 5, false, false, GardienEntity::hostile);
			this.g = g;
		}

		@Override
		protected void findTarget() {
			TargetingConditions avant = targetConditions;
			if (g.actif(Module.LUNETTE) > 0) targetConditions = avant.copy().ignoreInvisibilityTesting();
			super.findTarget();
			targetConditions = avant;
		}
	}
}
