package fr.chatmort.airain.armure;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/** Bonus d'ensemble des deux lignées, réservation à la fin, diadème d'Écho. */
public final class Armures {
	private Armures() {}
	private static final EquipmentSlot[] PIECES = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

	/** Palier de l'ensemble porté dans cette lignée : le plus faible des quatre pièces. */
	public static int ensemble(LivingEntity e, Lignee l) {
		int min = 2;
		for (EquipmentSlot s : PIECES) min = Math.min(min, ArmureItem.palier(e.getItemBySlot(s), l));
		return min;
	}
	public static int ensemble(LivingEntity e) { return ensemble(e, Lignee.EMPIRE); }

	/** La lignée de cet objet sert-elle ce joueur (selon la fin choisie) ? */
	public static boolean autorise(Player p, Lignee l) {
		if (!(p.level() instanceof net.minecraft.server.level.ServerLevel sl)) return true;
		return l.autorisee(sl.getServer());
	}

	static Lignee lignee(ItemStack s) {
		if (s.getItem() instanceof ArmureItem a) return a.lignee;
		if (s.getItem() instanceof DiademeItem) return Lignee.ECHO;
		return null;
	}

	// ---- attributs d'Ars Nouveau (sans dépendance de compilation : on les cherche par leur nom)
	private static final ResourceLocation MANA_MAX = ResourceLocation.fromNamespaceAndPath("ars_nouveau", "ars_nouveau.perk.max_mana");
	private static final ResourceLocation MANA_REGEN = ResourceLocation.fromNamespaceAndPath("ars_nouveau", "ars_nouveau.perk.mana_regen");
	private static final ResourceLocation SORTS = ResourceLocation.fromNamespaceAndPath("ars_nouveau", "ars_nouveau.perk.spell_damage");
	private static final ResourceLocation ID_MANA = ResourceLocation.fromNamespaceAndPath("airain", "echo_mana"),
		ID_REGEN = ResourceLocation.fromNamespaceAndPath("airain", "echo_regen"), ID_SORTS = ResourceLocation.fromNamespaceAndPath("airain", "echo_sorts");

	private static void attribut(Player p, ResourceLocation attr, ResourceLocation id, double v) {
		var h = BuiltInRegistries.ATTRIBUTE.getHolder(attr);
		if (h.isEmpty()) return;
		var a = p.getAttribute(h.get());
		if (a == null) return;
		var m = a.getModifier(id);
		if (m != null && m.amount() == v) return;
		a.removeModifier(id);
		if (v != 0) a.addTransientModifier(new AttributeModifier(id, v, AttributeModifier.Operation.ADD_VALUE));
	}

	public static void tick(PlayerTickEvent.Post ev) {
		if (!(ev.getEntity() instanceof ServerPlayer p) || p.tickCount % 10 != 0) return;
		for (EquipmentSlot s : PIECES) {                                      // chaque lignée refuse de servir l'autre fin
			ItemStack pile = p.getItemBySlot(s);
			Lignee l = lignee(pile);
			if (l != null && !autorise(p, l)) {
				p.setItemSlot(s, ItemStack.EMPTY);
				if (!p.getInventory().add(pile)) p.drop(pile, false);
				p.displayClientMessage(Component.translatable("airain.lignee.refus_" + l.cle()), true);
			}
		}
		int n = ensemble(p, Lignee.EMPIRE);
		if (n >= 1 && p.hasEffect(MobEffects.WITHER)) p.removeEffect(MobEffects.WITHER);          // sacré : pas de Wither
		if (n >= 2 && (!p.hasEffect(MobEffects.DAMAGE_RESISTANCE) || p.getEffect(MobEffects.DAMAGE_RESISTANCE).getDuration() < 100))
			p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 260, 0, true, false, true));   // impérial : Résistance I
		// Écho : le diadème régénère le mana ; l'ensemble runique (puis arcanique) nourrit les sorts
		int e = ensemble(p, Lignee.ECHO);
		boolean diademe = ArmureItem.diademe(p.getItemBySlot(EquipmentSlot.HEAD));
		attribut(p, MANA_MAX, ID_MANA, e == 2 ? 500 : e == 1 ? 200 : 0);
		attribut(p, MANA_REGEN, ID_REGEN, (e == 2 ? 6 : e == 1 ? 3 : 0) + (diademe ? 1 : 0));
		attribut(p, SORTS, ID_SORTS, e == 2 ? 3 : e == 1 ? 1 : 0);
		if (e >= 1) {
			if (p.hasEffect(MobEffects.BLINDNESS)) p.removeEffect(MobEffects.BLINDNESS);
			if (p.hasEffect(MobEffects.DARKNESS)) p.removeEffect(MobEffects.DARKNESS);
		}
	}

	/** Diadème d'Écho : le Warden ne prend plus son porteur pour cible. */
	public static void cible(LivingChangeTargetEvent e) {
		if (e.getEntity() instanceof net.minecraft.world.entity.monster.warden.Warden && e.getNewAboutToBeSetTarget() instanceof Player p
			&& ArmureItem.diademe(p.getItemBySlot(EquipmentSlot.HEAD)))
			e.setCanceled(true);
	}
}
