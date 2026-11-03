package fr.chatmort.airain.armure;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/** Bonus d'ensemble : sacré (4 pièces sacrées ou mieux) et impérial (4 pièces impériales). */
public final class Armures {
	private Armures() {}
	private static final EquipmentSlot[] PIECES = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

	/** Palier de l'ensemble porté : le plus faible des quatre pièces. */
	public static int ensemble(LivingEntity e) {
		int min = 2;
		for (EquipmentSlot s : PIECES) min = Math.min(min, ArmureItem.palier(e.getItemBySlot(s)));
		return min;
	}

	public static void tick(PlayerTickEvent.Post ev) {
		if (!(ev.getEntity() instanceof ServerPlayer p) || p.tickCount % 10 != 0) return;
		int n = ensemble(p);
		if (n >= 1 && p.hasEffect(MobEffects.WITHER)) p.removeEffect(MobEffects.WITHER);          // ensemble sacré : pas de Wither
		if (n >= 2 && (!p.hasEffect(MobEffects.DAMAGE_RESISTANCE) || p.getEffect(MobEffects.DAMAGE_RESISTANCE).getDuration() < 100))
			p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 260, 0, true, false, true));   // impérial : Résistance I
	}
}
