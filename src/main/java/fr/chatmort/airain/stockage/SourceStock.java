package fr.chatmort.airain.stockage;

import com.simibubi.create.content.redstone.displayLink.DisplayLinkContext;
import com.simibubi.create.content.redstone.displayLink.source.ValueListDisplaySource;
import net.createmod.catnip.data.IntAttached;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

/** Source de liaison d'affichage : le stock de tout le rayonnage, objets les plus nombreux d'abord. */
public class SourceStock extends ValueListDisplaySource {
	@Override
	protected Stream<IntAttached<MutableComponent>> provideEntries(DisplayLinkContext ctx, int lignes) {
		if (!(ctx.getSourceBlockEntity() instanceof CasierBlockEntity c)) return Stream.empty();
		List<ItemStack> vus = new ArrayList<>(); List<long[]> n = new ArrayList<>();
		for (CasierBlockEntity x : c.reseau.casiers()) {
			if (x.modele.isEmpty() || x.quantite <= 0) continue;
			int k = -1;
			for (int i = 0; i < vus.size(); i++) if (ItemStack.isSameItemSameComponents(vus.get(i), x.modele)) { k = i; break; }
			if (k < 0) { vus.add(x.modele); n.add(new long[] {x.quantite}); } else n.get(k)[0] += x.quantite;
		}
		List<IntAttached<MutableComponent>> l = new ArrayList<>();
		for (int i = 0; i < vus.size(); i++) l.add(IntAttached.with((int) Math.min(Integer.MAX_VALUE, n.get(i)[0]), vus.get(i).getHoverName().copy()));
		l.sort((a, b) -> Integer.compare(b.getFirst(), a.getFirst()));
		return l.stream().limit(lignes);
	}
	@Override protected boolean valueFirst() { return false; }
	@Override protected String getTranslationKey() { return "rack_stock"; }
}
