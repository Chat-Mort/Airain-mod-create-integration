package fr.chatmort.airain.stockage;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.block.Block;

import java.util.List;

/** L'objet du casier : il rappelle ce qu'il contient quand on l'a cassé plein. */
public class CasierItem extends BlockItem {
	public CasierItem(Block b, Properties p) { super(b, p); }
	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		if (d == null) { l.add(Component.translatable("airain.casier.aide").withStyle(ChatFormatting.GRAY)); return; }
		CompoundTag t = d.copyTag();
		int r = t.getByte("renforts");
		if (t.contains("modele") && c.registries() != null) {
			ItemStack m = ItemStack.parse(c.registries(), t.getCompound("modele")).orElse(ItemStack.EMPTY);
			if (!m.isEmpty()) l.add(Component.translatable("airain.casier.objet", m.getHoverName(), t.getLong("quantite")).withStyle(ChatFormatting.GOLD));
		}
		if (r > 0) l.add(Component.translatable("airain.casier.renforts", r, CasierBlockEntity.PILES << r).withStyle(ChatFormatting.GRAY));
	}
}
