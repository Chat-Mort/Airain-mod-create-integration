package fr.chatmort.airain.trophee;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Trophée de boss créé pour le pack : son nom, l'effet qu'il donne sur un socle, et sa provenance. */
public class TropheeItem extends Item {
	private final String cle;

	public TropheeItem(String cle, Properties p) { super(p); this.cle = cle; }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("item.airain." + cle + ".l1").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
		for (Trophees.Effet e : Trophees.effetsDe(s))
			l.add(Component.translatable("airain.trophee.sur_socle", Component.translatable("airain.trophee.effet." + e.name().toLowerCase(java.util.Locale.ROOT))).withStyle(ChatFormatting.GOLD));
	}
}
