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
	public final Lignee lignee;

	public PiocheItem(Tier tier, int palier, Properties p) { this(tier, palier, Lignee.EMPIRE, p); }

	public PiocheItem(Tier tier, int palier, Lignee lignee, Properties p) {
		super(tier, p);
		this.palier = palier;
		this.lignee = lignee;
	}

	/** Pioche de l'Écho : accroupi, clic droit dans le vide → écholocation des minerais. */
	@Override
	public net.minecraft.world.InteractionResultHolder<ItemStack> use(net.minecraft.world.level.Level level, net.minecraft.world.entity.player.Player p,
			net.minecraft.world.InteractionHand main) {
		ItemStack s = p.getItemInHand(main);
		if (lignee != Lignee.ECHO || !p.isShiftKeyDown()) return super.use(level, p, main);
		if (!level.isClientSide && Armes.autorise(p, lignee)) Armes.echolocation((net.minecraft.server.level.ServerPlayer) p, this);
		return net.minecraft.world.InteractionResultHolder.sidedSuccess(s, level.isClientSide);
	}

	public int rayonEcho() { return palier == 2 ? 16 : 8; }

	public int filon() { return palier == 2 ? 32 : 12; }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.lignee." + lignee.cle()).withStyle(ChatFormatting.DARK_RED, ChatFormatting.ITALIC));
		if (lignee == Lignee.ECHO) {
			l.add(Component.translatable("airain.arme.pioche_echo.nom").withStyle(ChatFormatting.GOLD));
			l.add(Component.translatable("airain.arme.pioche_echo.effet", rayonEcho()).withStyle(ChatFormatting.GRAY));
			return;
		}
		l.add(Component.translatable("airain.arme.pioche.nom").withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable("airain.arme.pioche.effet", filon()).withStyle(ChatFormatting.GRAY));
	}
}
