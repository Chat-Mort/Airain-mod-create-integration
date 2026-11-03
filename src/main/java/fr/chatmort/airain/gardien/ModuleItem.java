package fr.chatmort.airain.gardien;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Un module de gardien : clic droit sur un gardien en état de marche pour le monter. */
public class ModuleItem extends Item {
	public final Module module;
	public final int niveau;

	public ModuleItem(Module module, int niveau, Properties p) {
		super(p);
		this.module = module;
		this.niveau = niveau;
	}

	public int code() { return module.code(niveau); }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.module.emplacement", Component.translatable("airain.module.emplacement." + module.emplacement.nom()))
			.withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable("airain.module." + module.nom() + ".effet" + niveau).withStyle(ChatFormatting.GRAY));
		if (niveau == 1) l.add(Component.translatable("airain.module.ameliorable").withStyle(ChatFormatting.DARK_PURPLE));
		l.add(Component.translatable("airain.module.monter").withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
	}
}
