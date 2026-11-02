package fr.chatmort.airain.ingenieur;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.neoforged.fml.loading.FMLEnvironment;

/** Le livre de l'ingénieur : le manuel des machines de l'Empire. Il s'ouvre côté client, rien à demander au serveur. */
public class LivreIngenieurItem extends Item {
	public LivreIngenieurItem(Properties p) { super(p); }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		if (level.isClientSide && FMLEnvironment.dist.isClient()) Ouvrir.livre();
		level.playSound(joueur, joueur.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 1.1f);
		return InteractionResultHolder.sidedSuccess(joueur.getItemInHand(main), level.isClientSide);
	}
}
