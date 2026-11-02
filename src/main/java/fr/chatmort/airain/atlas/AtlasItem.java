package fr.chatmort.airain.atlas;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** L'atlas impérial : la carte de tout ce que l'équipe a parcouru. */
public class AtlasItem extends Item {
	public AtlasItem(Properties p) { super(p); }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		if (p instanceof ServerPlayer sp)
			net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new OuvrirAtlas(Atlas.de(sp.server).paquet(sp)));
		level.playSound(p, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.8f);
		return InteractionResultHolder.sidedSuccess(p.getItemInHand(main), level.isClientSide);
	}
}
