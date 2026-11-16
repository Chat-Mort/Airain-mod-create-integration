package fr.chatmort.airain.stockage;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Renfort de casier : clic droit sur un casier pour doubler sa capacité (dans l'ordre, du I au IV). */
public class RenfortItem extends Item {
	public final int niveau;
	public RenfortItem(int niveau, Properties p) { super(p); this.niveau = niveau; }
	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.renfort.aide", CasierBlockEntity.PILES << niveau).withStyle(ChatFormatting.GRAY));
	}
}
