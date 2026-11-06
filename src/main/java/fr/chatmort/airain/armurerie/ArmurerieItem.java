package fr.chatmort.airain.armurerie;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Un manuel des armes : clic droit pour le lire (Empire ou Écho). Rangeable dans la Reliure. */
public class ArmurerieItem extends Item {
	private final boolean echo;

	public ArmurerieItem(boolean echo, Properties p) { super(p); this.echo = echo; }

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		if (joueur instanceof ServerPlayer sp) {
			// les objets que l'équipe a déjà eus en main : les pages correspondantes se dévoilent
			ListTag l = new ListTag();
			for (String id : fr.chatmort.airain.chronique.Chronique.de(sp.server).armes()) l.add(StringTag.valueOf(id));
			CompoundTag t = new CompoundTag();
			t.put("vus", l);
			net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new OuvrirArmurerie(echo, t));
		}
		level.playSound(joueur, joueur.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.8f);
		return InteractionResultHolder.sidedSuccess(joueur.getItemInHand(main), level.isClientSide);
	}
}
