package fr.chatmort.airain.chronique;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Les Chroniques oubliées : le livre de l'aventure, rempli au fil de la partie. */
public class ChroniquesItem extends Item {
	public ChroniquesItem(Properties p) { super(p); }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		if (joueur instanceof ServerPlayer sp) {
			Chronique.auteur(sp);
			net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new OuvrirChroniques(Chronique.de(sp.server).paquet(sp.server)));
		}
		level.playSound(joueur, joueur.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.9f);
		return InteractionResultHolder.sidedSuccess(joueur.getItemInHand(main), level.isClientSide);
	}
}
