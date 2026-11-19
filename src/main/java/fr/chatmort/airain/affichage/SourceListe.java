package fr.chatmort.airain.affichage;

import java.util.ArrayList;
import java.util.List;

import com.simibubi.create.api.behaviour.display.DisplaySource;
import com.simibubi.create.content.redstone.displayLink.DisplayLinkContext;
import com.simibubi.create.content.redstone.displayLink.target.DisplayTargetStats;
import com.simibubi.create.foundation.gui.ModularGuiLineBuilder;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;

/**
 * 1.66.4 : source de liaison d'affichage en liste « nom et quantité » (stock du rayonnage, contenu d'un coffre-fort, d'un
 * réservoir, d'un stockage Sophisticated…). Réglages dans l'écran de la liaison :
 * - affichage : nom et quantité, quantité seule, nom seul ;
 * - nombres : abrégés (1,2k) ou entiers ;
 * - filtre (facultatif) : seuls les éléments dont le nom ou l'identifiant contient ce texte, additionnés sur une ligne.
 */
public abstract class SourceListe extends DisplaySource {
	/** Un élément de la liste : son nom, son identifiant (pour le filtre), sa quantité, et l'unité affichée après le nombre. */
	public record Entree(Component nom, String id, long quantite, String unite) {}

	protected abstract List<Entree> entrees(DisplayLinkContext ctx);

	/** Formatage du nombre ; les fluides le remplacent (mB, seaux). */
	protected String nombre(Entree e, boolean abrege) {
		long n = e.quantite();
		String s = !abrege || n < 1000 ? String.valueOf(n) : n < 1_000_000 ? arrondi(n / 1000.0) + "k" : arrondi(n / 1_000_000.0) + "M";
		return e.unite().isEmpty() ? s : s + " " + e.unite();
	}
	protected static String arrondi(double v) { return v >= 100 ? String.valueOf((long) v) : String.format(java.util.Locale.ROOT, "%.1f", v).replace(".0", ""); }

	@Override
	public List<MutableComponent> provideText(DisplayLinkContext ctx, DisplayTargetStats stats) {
		var cfg = ctx.sourceConfig();
		int affichage = cfg.getInt("Affichage");             // 0 nom et quantité, 1 quantité seule, 2 nom seul
		boolean abrege = cfg.getInt("Format") == 0;
		String filtre = cfg.getString("Filtre").strip().toLowerCase(java.util.Locale.ROOT);
		List<Entree> l = new ArrayList<>(entrees(ctx));
		if (!filtre.isEmpty()) {
			// filtre : tout ce qui correspond, additionné en une seule ligne (sous le nom du premier élément trouvé)
			long total = 0; Entree premier = null;
			for (Entree e : l)
				if (e.nom().getString().toLowerCase(java.util.Locale.ROOT).contains(filtre) || e.id().toLowerCase(java.util.Locale.ROOT).contains(filtre)) {
					total += e.quantite(); if (premier == null) premier = e;
				}
			l = List.of(premier == null ? new Entree(Component.literal(filtre), filtre, 0, "") : new Entree(premier.nom(), premier.id(), total, premier.unite()));
		}
		l.sort((a, b) -> Long.compare(b.quantite(), a.quantite()));
		List<MutableComponent> r = new ArrayList<>();
		for (Entree e : l) {
			if (r.size() >= Math.max(1, stats.maxRows())) break;
			String n = nombre(e, abrege);
			r.add(switch (affichage) {
				case 1 -> Component.literal(n);
				case 2 -> e.nom().copy();
				default -> e.nom().copy().append(" ").append(n);
			});
		}
		return r.isEmpty() ? List.of(Component.literal("-")) : r;
	}

	@Override
	@OnlyIn(Dist.CLIENT)
	public void initConfigurationWidgets(DisplayLinkContext ctx, ModularGuiLineBuilder b, boolean premiere) {
		if (premiere) {
			b.addSelectionScrollInput(0, 85, (si, l) -> si.forOptions(List.of(Component.translatable("airain.display.affichage.0"),
				Component.translatable("airain.display.affichage.1"), Component.translatable("airain.display.affichage.2")))
				.titled(Component.translatable("airain.display.affichage")), "Affichage");
			b.addSelectionScrollInput(90, 50, (si, l) -> si.forOptions(List.of(Component.translatable("airain.display.format.0"),
				Component.translatable("airain.display.format.1"))).titled(Component.translatable("airain.display.format")), "Format");
		} else {
			b.addTextInput(0, 137, (e, t) -> {
				e.setValue("");
				t.withTooltip(com.google.common.collect.ImmutableList.of(Component.translatable("airain.display.filtre").withStyle(s -> s.withColor(0x5391E1)),
					Component.translatable("airain.display.filtre.aide").withStyle(net.minecraft.ChatFormatting.DARK_GRAY, net.minecraft.ChatFormatting.ITALIC)));
			}, "Filtre");
		}
	}
}
