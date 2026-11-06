package fr.chatmort.airain.manuel;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Un des deux manuels d'armes (camp 0 = Empire, 1 = Écho) : s'ouvre sur les pages déjà dévoilées par l'équipe. */
public class ManuelItem extends Item {
	public final int camp;

	public ManuelItem(int camp, Properties p) { super(p); this.camp = camp; }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		if (joueur instanceof ServerPlayer sp)
			net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new OuvrirManuel(camp, Manuel.de(sp.server).devoilees()));
		level.playSound(joueur, joueur.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.9f);
		return InteractionResultHolder.sidedSuccess(joueur.getItemInHand(main), level.isClientSide);
	}
}
