package fr.chatmort.airain.fondation;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.WrittenBookContent;
import net.minecraft.world.level.Level;

/** Registre des fondations : s'ouvre comme un livre et liste toutes les bases (nom, coordonnées, dimension, distance). */
public class RegistreItem extends Item {
	private static final int PAR_PAGE = 4;

	public RegistreItem(Properties p) {
		super(p);
	}

	/**
	 * Le registre s'ouvre dans son propre écran (un livre vanilla ne s'ouvre que pour un « livre écrit » :
	 * c'est pour ça que l'ancien registre ne répondait pas au clic droit).
	 */
	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		ItemStack pile = joueur.getItemInHand(main);
		if (joueur instanceof ServerPlayer sp) {
			List<FondationRegistre.Fondation> liste = new ArrayList<>(FondationRegistre.de(sp.getServer()).toutes());
			liste.removeIf(FondationRegistre.Fondation::decorative);
			String dim = sp.level().dimension().location().toString();
			liste.sort(Comparator.comparing((FondationRegistre.Fondation f) -> !f.dim().toString().equals(dim))
				.thenComparingDouble(f -> f.distance(sp.getX(), sp.getZ())));
			List<OuvrirRegistre.Base> bases = new ArrayList<>();
			for (FondationRegistre.Fondation f : liste)
				bases.add(new OuvrirRegistre.Base(f.nom(), f.devise(), f.pos(), f.dim(), f.apparence(), f.ext()));
			FondationRegistre reg = FondationRegistre.de(sp.getServer());
			List<OuvrirRegistre.Trophee> trophees = new ArrayList<>();
			for (var e : fr.chatmort.airain.trophee.TropheeRegistre.de(sp.getServer()).entrees()) {
				var pos = e.getKey().pos();
				FondationRegistre.Fondation base = reg.zone(e.getKey().dimension().location(), pos.getX() + 0.5, pos.getZ() + 0.5);
				int k = base == null ? -1 : liste.indexOf(base);
				trophees.add(new OuvrirRegistre.Trophee(e.getValue().objet(), e.getValue().plaque(), e.getValue().jour(), k));
			}
			net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(sp, new OuvrirRegistre(bases, trophees));
		}
		level.playSound(joueur, joueur.blockPosition(), net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, net.minecraft.sounds.SoundSource.PLAYERS, 1f, 1f);
		return InteractionResultHolder.sidedSuccess(pile, level.isClientSide);
	}
}
