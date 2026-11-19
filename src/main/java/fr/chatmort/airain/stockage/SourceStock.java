package fr.chatmort.airain.stockage;

import com.simibubi.create.content.redstone.displayLink.DisplayLinkContext;

import fr.chatmort.airain.affichage.SourceListe;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/** Source de liaison d'affichage : le stock de tout le rayonnage, objets les plus nombreux d'abord (affichage et filtre réglables). */
public class SourceStock extends SourceListe {
	@Override
	protected List<Entree> entrees(DisplayLinkContext ctx) {
		if (!(ctx.getSourceBlockEntity() instanceof CasierBlockEntity c)) return List.of();
		List<ItemStack> vus = new ArrayList<>(); List<long[]> n = new ArrayList<>();
		for (CasierBlockEntity x : c.reseau.casiers()) {
			if (x.modele.isEmpty() || x.quantite <= 0) continue;
			int k = -1;
			for (int i = 0; i < vus.size(); i++) if (ItemStack.isSameItemSameComponents(vus.get(i), x.modele)) { k = i; break; }
			if (k < 0) { vus.add(x.modele); n.add(new long[] {x.quantite}); } else n.get(k)[0] += x.quantite;
		}
		List<Entree> l = new ArrayList<>();
		for (int i = 0; i < vus.size(); i++)
			l.add(new Entree(vus.get(i).getHoverName(), BuiltInRegistries.ITEM.getKey(vus.get(i).getItem()).toString(), n.get(i)[0], ""));
		return l;
	}
	@Override protected String getTranslationKey() { return "rack_stock"; }
}
