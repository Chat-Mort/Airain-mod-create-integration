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

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player joueur, InteractionHand main) {
		ItemStack pile = joueur.getItemInHand(main);
		if (joueur instanceof ServerPlayer sp) {
			List<FondationRegistre.Fondation> liste = new ArrayList<>(FondationRegistre.de(sp.getServer()).toutes());
			liste.removeIf(FondationRegistre.Fondation::decorative);
			String dim = sp.level().dimension().location().toString();
			liste.sort(Comparator.comparing((FondationRegistre.Fondation f) -> !f.dim().toString().equals(dim))
				.thenComparingDouble(f -> f.distance(sp.getX(), sp.getZ())));
			List<Filterable<Component>> pages = new ArrayList<>();
			if (liste.isEmpty())
				pages.add(Filterable.passThrough(Component.translatable("airain.registre.vide")));
			for (int i = 0; i < liste.size(); i += PAR_PAGE) {
				MutableComponent page = Component.translatable("airain.registre.titre").withStyle(ChatFormatting.DARK_RED, ChatFormatting.BOLD);
				for (FondationRegistre.Fondation f : liste.subList(i, Math.min(liste.size(), i + PAR_PAGE))) {
					String nom = f.nom().isEmpty() ? Component.translatable("airain.fondation.sans_nom").getString() : f.nom();
					page.append(Component.literal("\n\n" + nom).withStyle(ChatFormatting.DARK_BLUE, ChatFormatting.BOLD));
					page.append(Component.literal("\n" + f.pos().getX() + " " + f.pos().getY() + " " + f.pos().getZ() + " · ").withStyle(ChatFormatting.BLACK).withStyle(s -> s.withBold(false)));
					page.append(Component.translatable("airain.registre.dim." + f.dim().getPath()).withStyle(s -> s.withBold(false).withColor(ChatFormatting.DARK_GRAY)));
					page.append(f.dim().toString().equals(dim)
						? Component.translatable("airain.registre.distance", (int) f.distance(sp.getX(), sp.getZ())).withStyle(s -> s.withBold(false).withColor(ChatFormatting.DARK_GRAY))
						: Component.literal(""));
				}
				pages.add(Filterable.passThrough(page));
			}
			// trophées de l'Empire : objet, effets, plaque gravée, base qui l'expose
			var trophees = fr.chatmort.airain.trophee.TropheeRegistre.de(sp.getServer()).entrees();
			FondationRegistre reg = FondationRegistre.de(sp.getServer());
			for (int i = 0; i < trophees.size(); i += 3) {
				MutableComponent page = Component.translatable("airain.registre.trophees").withStyle(ChatFormatting.DARK_RED, ChatFormatting.BOLD);
				for (var e : trophees.subList(i, Math.min(trophees.size(), i + 3))) {
					ItemStack objet = new ItemStack(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(e.getValue().objet()));
					page.append(Component.literal("\n\n").append(objet.getHoverName()).withStyle(s -> s.withBold(true).withColor(ChatFormatting.DARK_BLUE)));
					MutableComponent effets = Component.literal("\n");
					boolean premier = true;
					for (var ef : fr.chatmort.airain.trophee.Trophees.effetsDe(objet)) {
						if (!premier) effets.append(", ");
						effets.append(Component.translatable("airain.trophee.effet." + ef.name().toLowerCase()));
						premier = false;
					}
					page.append(effets.withStyle(s -> s.withBold(false).withColor(ChatFormatting.DARK_GREEN)));
					if (!e.getValue().plaque().isEmpty())
						page.append(Component.translatable("airain.registre.plaque", e.getValue().plaque(), e.getValue().jour())
							.withStyle(s -> s.withBold(false).withItalic(true).withColor(ChatFormatting.DARK_GRAY)));
					var pos = e.getKey().pos();
					FondationRegistre.Fondation base = reg.zone(e.getKey().dimension().location(), pos.getX() + 0.5, pos.getZ() + 0.5);
					page.append(Component.literal("\n").append(base != null && !base.nom().isEmpty() ? Component.literal(base.nom())
						: Component.translatable("airain.registre.hors_base")).withStyle(s -> s.withBold(false).withColor(ChatFormatting.BLACK)));
				}
				pages.add(Filterable.passThrough(page));
			}
			pile.set(DataComponents.WRITTEN_BOOK_CONTENT, new WrittenBookContent(
				Filterable.passThrough("Registre"), sp.getGameProfile().getName(), 0, pages, true));
			sp.openItemGui(pile, main);
		}
		return InteractionResultHolder.sidedSuccess(pile, level.isClientSide);
	}
}
