package fr.chatmort.airain.reliure;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/** La Reliure de l'ingénieur : neuf livres sous la main. Clic droit : lire ; accroupi + clic droit : ranger. */
public class ReliureItem extends Item {
	public ReliureItem(Properties p) { super(p); }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack pile = p.getItemInHand(main);
		int slot = main == InteractionHand.MAIN_HAND ? p.getInventory().selected : 40;   // 40 : main secondaire
		if (p instanceof ServerPlayer sp) {
			if (p.isShiftKeyDown())
				sp.openMenu(new SimpleMenuProvider((id, inv, j) -> new ReliureMenu(id, inv, slot), pile.getHoverName()), b -> b.writeVarInt(slot));
			else
				net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new Paquets.Ouvrir(Reliure.INVENTAIRE, slot, Reliure.livres(pile)));
		}
		level.playSound(p, p.blockPosition(), SoundEvents.ARMOR_EQUIP_LEATHER.value(), SoundSource.PLAYERS, 0.6f, 1.2f);
		return InteractionResultHolder.sidedSuccess(pile, level.isClientSide);
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		List<ItemStack> livres = Reliure.livres(s);
		if (livres.isEmpty()) l.add(Component.translatable("airain.reliure.vide").withStyle(ChatFormatting.GRAY));
		for (ItemStack b : livres) l.add(Component.literal("· ").append(b.getHoverName()).withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable("airain.reliure.aide").withStyle(ChatFormatting.DARK_GRAY));
	}
}
