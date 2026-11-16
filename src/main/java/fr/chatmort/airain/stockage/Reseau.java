package fr.chatmort.airain.stockage;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.IItemHandler;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * L'inventaire d'un rayonnage entier, vu par Create (entonnoirs, bras, emballeurs…) depuis n'importe quel casier :
 * une case par casier. Ce qui entre est rangé où il faut, quelle que soit la case visée : d'abord le casier qui contient
 * déjà cet objet, puis un casier réservé à cet objet, puis un casier libre.
 */
public class Reseau implements IItemHandler {
	public static final int MAX = 512;
	private static int version;
	/** Un casier posé, cassé ou voisin changé : les rayonnages se recalculent. */
	static void changement() { version++; }

	private final CasierBlockEntity ici;
	private List<CasierBlockEntity> casiers = List.of();
	private int vu = -1;
	Reseau(CasierBlockEntity ici) { this.ici = ici; }

	public List<CasierBlockEntity> casiers() {
		if (vu != version || casiers.isEmpty()) {
			vu = version;
			List<CasierBlockEntity> l = new ArrayList<>();
			if (ici.getLevel() != null && !ici.isRemoved()) {
				Set<BlockPos> vus = new HashSet<>(); ArrayDeque<BlockPos> file = new ArrayDeque<>();
				file.add(ici.getBlockPos()); vus.add(ici.getBlockPos());
				while (!file.isEmpty() && l.size() < MAX) {
					BlockPos p = file.poll();
					if (!(ici.getLevel().getBlockEntity(p) instanceof CasierBlockEntity c)) continue;
					l.add(c);
					for (Direction d : Direction.values()) {
						BlockPos q = p.relative(d);
						if (vus.add(q) && ici.getLevel().isLoaded(q) && ici.getLevel().getBlockState(q).getBlock() instanceof CasierBlock) file.add(q);
					}
				}
				// ordre stable : de bas en haut, puis le long du rang
				l.sort((a, b) -> a.getBlockPos().getY() != b.getBlockPos().getY() ? Integer.compare(a.getBlockPos().getY(), b.getBlockPos().getY()) : Long.compare(a.getBlockPos().asLong(), b.getBlockPos().asLong()));
			}
			casiers = l;
		}
		return casiers;
	}

	@Override public int getSlots() { return Math.max(1, casiers().size()); }
	private CasierBlockEntity casier(int i) { List<CasierBlockEntity> l = casiers(); return i >= 0 && i < l.size() ? l.get(i) : null; }
	/** La pile montrée pour une case : l'objet et sa quantité réelle (qui peut dépasser une pile). */
	@Override
	public @NotNull ItemStack getStackInSlot(int i) {
		CasierBlockEntity c = casier(i);
		if (c == null || c.modele.isEmpty() || c.quantite <= 0) return ItemStack.EMPTY;
		return c.modele.copyWithCount((int) Math.min(Integer.MAX_VALUE, c.quantite));
	}
	@Override
	public @NotNull ItemStack insertItem(int i, @NotNull ItemStack s, boolean simuler) {
		if (s.isEmpty()) return s;
		long reste = s.getCount();
		List<CasierBlockEntity> l = casiers();
		for (int passe = 0; passe < 3 && reste > 0; passe++)
			for (CasierBlockEntity c : l) {
				boolean ok = switch (passe) {
					case 0 -> !c.modele.isEmpty() && c.quantite > 0 && c.accepte(s);
					case 1 -> !c.modele.isEmpty() && c.quantite <= 0 && c.accepte(s);
					default -> c.modele.isEmpty();
				};
				if (ok) reste -= c.ajouter(s, reste, simuler);
				if (reste <= 0) break;
			}
		return reste <= 0 ? ItemStack.EMPTY : s.copyWithCount((int) reste);
	}
	@Override
	public @NotNull ItemStack extractItem(int i, int n, boolean simuler) {
		CasierBlockEntity c = casier(i);
		return c == null ? ItemStack.EMPTY : c.retirer(n, simuler);
	}
	@Override
	public int getSlotLimit(int i) {
		CasierBlockEntity c = casier(i);
		return c == null ? 64 : (int) Math.min(Integer.MAX_VALUE, c.capacite());
	}
	@Override public boolean isItemValid(int i, @NotNull ItemStack s) { return true; }
}
