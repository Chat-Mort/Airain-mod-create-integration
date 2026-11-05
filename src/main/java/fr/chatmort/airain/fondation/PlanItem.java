package fr.chatmort.airain.fondation;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Plans d'une amélioration de capitale : à poser sur l'étendard d'une capitale, avec le prix en soleils. */
public class PlanItem extends Item {
	public final Ameliorations.Type type;

	public PlanItem(Ameliorations.Type type, Properties p) {
		super(p);
		this.type = type;
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.plan.usage").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
		for (int n = 0; n < type.max(); n++)
			l.add(Component.translatable("airain.plan.niveau", n + 1, type.prix[n],
				Component.translatable("airain.amelioration." + type.id + "." + (n + 1))).withStyle(ChatFormatting.GOLD));
	}
}
