package fr.chatmort.airain.armure;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;

/** Pioche sacrée ou impériale : Filon (accroupi, tout le filon de minerai d'un coup). */
public class PiocheItem extends PickaxeItem {
	public final int palier;

	public PiocheItem(Tier tier, int palier, Properties p) {
		super(tier, p);
		this.palier = palier;
	}

	public int filon() { return palier == 2 ? 32 : 12; }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.arme.pioche.nom").withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable("airain.arme.pioche.effet", filon()).withStyle(ChatFormatting.GRAY));
	}
}
