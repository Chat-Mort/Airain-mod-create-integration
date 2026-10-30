package fr.chatmort.airain.codex;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Le Codex de l'Empire : s'ouvre dans son propre écran, avec les découvertes du joueur qui le tient. */
public class CodexItem extends Item {
	public CodexItem(Properties p) { super(p); }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		if (joueur instanceof ServerPlayer sp)
			net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new OuvrirCodex(Codex.donnees(sp).copy()));
		level.playSound(joueur, joueur.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.9f);
		return InteractionResultHolder.sidedSuccess(joueur.getItemInHand(main), level.isClientSide);
	}
}
