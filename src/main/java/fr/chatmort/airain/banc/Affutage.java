package fr.chatmort.airain.banc;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.MaceItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/**
 * Affûtage : un outil ou une arme qui sort du banc d'entretien garde un bonus discret pendant quelques minutes
 * (+10 % de vitesse de minage pour un outil, +10 % de dégâts pour une arme). L'échéance est une date de jeu
 * rangée dans les données de l'objet.
 */
public final class Affutage {
	private static final String CLE = "airain_affute";
	public static final float BONUS = 1.10f;

	private Affutage() {}

	public static boolean outil(ItemStack s) {
		return s.has(DataComponents.TOOL) && !arme(s);
	}

	public static boolean arme(ItemStack s) {
		return s.getItem() instanceof SwordItem || s.getItem() instanceof TridentItem || s.getItem() instanceof MaceItem;
	}

	public static boolean affutable(ItemStack s) {
		return outil(s) || arme(s);
	}

	public static void marquer(ItemStack s, long fin) {
		CustomData.update(DataComponents.CUSTOM_DATA, s, t -> t.putLong(CLE, fin));
	}

	/** Ticks restants (0 si l'objet n'est pas affûté ou plus). */
	public static long restant(ItemStack s, Level level) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		if (d == null || level == null) return 0;
		CompoundTag t = d.copyTag();
		return t.contains(CLE) ? Math.max(0, t.getLong(CLE) - level.getGameTime()) : 0;
	}

	public static void vitesse(PlayerEvent.BreakSpeed e) {
		ItemStack s = e.getEntity().getMainHandItem();
		if (outil(s) && restant(s, e.getEntity().level()) > 0) e.setNewSpeed(e.getNewSpeed() * BONUS);
	}

	public static void degats(LivingIncomingDamageEvent e) {
		if (e.getSource().getEntity() instanceof Player p) {
			ItemStack s = p.getMainHandItem();
			if (arme(s) && restant(s, p.level()) > 0) e.setAmount(e.getAmount() * BONUS);
		}
	}

	public static void infobulle(ItemTooltipEvent e) {
		Level l = e.getEntity() != null ? e.getEntity().level() : null;
		long r = restant(e.getItemStack(), l);
		if (r <= 0) return;
		int minutes = (int) Math.max(1, (r + 1199) / 1200);
		e.getToolTip().add(1, Component.translatable(arme(e.getItemStack()) ? "airain.affute.arme" : "airain.affute.outil", minutes)
			.withStyle(ChatFormatting.GOLD));
	}
}
