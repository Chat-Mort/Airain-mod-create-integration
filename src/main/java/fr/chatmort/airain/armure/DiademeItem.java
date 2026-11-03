package fr.chatmort.airain.armure;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Le diadème d'Écho : récompense de la fin Écho, porté seul ou monté sur le casque runique. */
public class DiademeItem extends ArmorItem {
	public DiademeItem(Holder<ArmorMaterial> m, Properties p) { super(m, Type.HELMET, p); }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.lignee.echo").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
		l.add(Component.translatable("airain.diademe.l1").withStyle(ChatFormatting.LIGHT_PURPLE));
		l.add(Component.translatable("airain.diademe.effet").withStyle(ChatFormatting.GRAY));
	}
}
