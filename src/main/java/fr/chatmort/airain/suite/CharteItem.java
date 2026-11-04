package fr.chatmort.airain.suite;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** La charte impériale : rallume un avant-poste (après « Rallumer le Cœur », couronne sur la tête). */
public class CharteItem extends Item {
	public CharteItem(Properties p) { super(p); }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack pile = p.getItemInHand(main);
		if (p instanceof ServerPlayer sp) {
			var r = Suites.charte(sp, pile);
			return r.consumesAction() ? InteractionResultHolder.consume(pile) : InteractionResultHolder.fail(pile);
		}
		return InteractionResultHolder.success(pile);
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, java.util.List<net.minecraft.network.chat.Component> l, net.minecraft.world.item.TooltipFlag f) {
		l.add(net.minecraft.network.chat.Component.translatable("item.airain.imperial_charter.aide").withStyle(net.minecraft.ChatFormatting.GRAY));
	}
}
