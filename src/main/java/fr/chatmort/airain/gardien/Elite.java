package fr.chatmort.airain.gardien;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

import fr.chatmort.airain.AirainMod;

/**
 * Gardiens d'élite, un par base. Capitaine impérial (plaque impériale, fin Empire) : plus grand, deux modules par emplacement,
 * Force et Résistance aux gardiens proches. Gardien d'Écho (bloc d'écho primordial, fin Écho) : onde sonique à distance, soigne les gardiens proches.
 */
public final class Elite {
	private Elite() {}
	public static final int CAPITAINE = 1, ECHO = 2;
	private static final ResourceLocation TAILLE = ResourceLocation.fromNamespaceAndPath("airain", "capitaine_taille");
	private static final ResourceLocation PV = ResourceLocation.fromNamespaceAndPath("airain", "capitaine_pv");
	private static final double RAYON_CAPITAINE = 16, RAYON_SOIN = 12, PORTEE_ONDE = 16;

	static int insigne(ItemStack s) {
		if (s.is(AirainMod.PLAQUE_IMPERIALE.get())) return CAPITAINE;
		if (s.is(AirainMod.BLOC_ECHO_ITEM.get())) return ECHO;
		return 0;
	}

	static void promouvoir(GardienEntity g, Player p, ItemStack s) {
		int r = insigne(s);
		ServerLevel sl = (ServerLevel) g.level();
		Fin fin = Fin.de(sl.getServer());
		if (g.rang() != 0) { p.displayClientMessage(Component.translatable("airain.gardien.elite_deja_promu"), true); return; }
		if (r == CAPITAINE ? !fin.empire() : !fin.echo()) {
			p.displayClientMessage(Component.translatable(r == CAPITAINE ? "airain.gardien.elite_fin_empire" : "airain.gardien.elite_fin_echo"), true);
			return;
		}
		String base = g.fondation();
		if (base == null) { p.displayClientMessage(Component.translatable("airain.gardien.elite_base"), true); return; }
		Gardiens reg = Gardiens.de(sl.getServer());
		if (reg.elite(base) != null && !reg.elite(base).equals(g.getUUID())) {
			p.displayClientMessage(Component.translatable("airain.gardien.elite_unique"), true);
			return;
		}
		reg.designer(base, g.getUUID());
		g.promouvoir(r);
		g.setHealth(g.getMaxHealth());
		if (!p.getAbilities().instabuild) s.shrink(1);
		p.displayClientMessage(Component.translatable(r == CAPITAINE ? "airain.gardien.promu_capitaine" : "airain.gardien.promu_echo"), true);
		if (r == CAPITAINE) {
			sl.playSound(null, g.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.NEUTRAL, 1f, 0.8f);
			sl.playSound(null, g.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.NEUTRAL, 0.7f, 1.2f);
			sl.sendParticles(ParticleTypes.END_ROD, g.getX(), g.getY() + 2, g.getZ(), 40, 0.6, 1, 0.6, 0.05);
		} else {
			sl.playSound(null, g.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.NEUTRAL, 1.5f, 0.6f);
			sl.playSound(null, g.blockPosition(), SoundEvents.SCULK_SHRIEKER_SHRIEK, SoundSource.NEUTRAL, 0.6f, 1.4f);
			sl.sendParticles(ParticleTypes.SCULK_SOUL, g.getX(), g.getY() + 2, g.getZ(), 30, 0.6, 1, 0.6, 0.05);
		}
		GardienModules.etape(p, "airain_gardien_elite");
	}

	/** Le capitaine est plus grand (×1,2) et plus robuste. */
	static void attributs(GardienEntity g) {
		boolean cap = g.capitaine();
		modif(g.getAttribute(Attributes.SCALE), TAILLE, cap ? 0.2 : 0);
		modif(g.getAttribute(Attributes.MAX_HEALTH), PV, cap ? 60 : 0);
	}

	private static void modif(AttributeInstance a, ResourceLocation id, double v) {
		if (a == null) return;
		a.removeModifier(id);
		if (v != 0) a.addPermanentModifier(new AttributeModifier(id, v, AttributeModifier.Operation.ADD_VALUE));
	}

	static void tick(GardienEntity g) {
		if (g.rang() == 0) return;
		ServerLevel sl = (ServerLevel) g.level();
		if (g.capitaine() && g.tickCount % 20 == 0) {
			for (GardienEntity o : sl.getEntitiesOfClass(GardienEntity.class, g.getBoundingBox().inflate(RAYON_CAPITAINE), o -> o != g && !o.enPanne())) {
				o.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 60, 0, true, false));
				o.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
			}
		}
		if (!g.echo()) return;
		if (g.tickCount % 40 == 0) {                                                          // soin des gardiens proches
			for (GardienEntity o : sl.getEntitiesOfClass(GardienEntity.class, g.getBoundingBox().inflate(RAYON_SOIN), o -> !o.enPanne() && o.getHealth() < o.getMaxHealth())) {
				o.heal(4f);
				sl.sendParticles(ParticleTypes.SCULK_CHARGE_POP, o.getX(), o.getY() + 1.6, o.getZ(), 6, 0.4, 0.5, 0.4, 0.02);
			}
		}
		LivingEntity c = g.getTarget();
		if (g.tickCount % 60 == 0 && c != null && c.isAlive() && g.distanceTo(c) <= PORTEE_ONDE && g.hasLineOfSight(c)) {   // onde sonique
			Vec3 a = g.position().add(0, 1.8, 0), b = c.getEyePosition();
			Vec3 d = b.subtract(a);
			int n = Math.max(1, (int) d.length());
			for (int i = 1; i <= n; i++) {
				Vec3 q = a.add(d.scale(i / (double) n));
				sl.sendParticles(ParticleTypes.SONIC_BOOM, q.x, q.y, q.z, 1, 0, 0, 0, 0);
			}
			g.playSound(SoundEvents.WARDEN_SONIC_BOOM, 2.5f, 1.2f);
			c.hurt(sl.damageSources().sonicBoom(g), 10f);
			Vec3 pousse = d.normalize();
			c.push(pousse.x * 0.8, 0.3, pousse.z * 0.8);
		}
	}
}
