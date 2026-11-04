package fr.chatmort.airain.borne;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/**
 * Le catalogue des bornes, entièrement piloté par étiquettes (data/airain/tags/item/borne/…) :
 * un objet est vendu s'il est dans un rayon et pas dans « exclus » ; son palier est le plus cher de ceux qui le citent
 * (par défaut : travaillé). Les prix sont en éperons (spur = 1).
 */
public final class Catalogue {
	private Catalogue() {}

	public static final int[] LOTS = {1, 32, 64};

	public enum Palier {
		COMMUN("commun", 0, 0, 8), COURANT("courant", 1, 8, 16), TRAVAILLE("travaille", 1, 16, 32), MINERAI("minerai", 2, 64, 128),
		PRECIEUX("precieux", 4, 128, 256), RARE("rare", 16, 512, 1024), TRES_RARE("tres_rare", 128, 4096, 8192);
		public final String cle;
		public final int[] prix;
		public final TagKey<Item> tag;
		Palier(String cle, int... prix) { this.cle = cle; this.prix = prix; this.tag = tag("borne/palier/" + cle); }
	}

	public enum Rayon {
		PIERRES("pierres", Items.COBBLESTONE), PLANTES("plantes", Items.OAK_SAPLING), METAUX("metaux", Items.IRON_INGOT),
		BUTIN("butin", Items.BONE), COULEURS("couleurs", Items.RED_DYE);
		public final String cle;
		public final Item icone;
		public final TagKey<Item> tag;
		Rayon(String cle, Item icone) { this.cle = cle; this.icone = icone; this.tag = tag("borne/" + cle); }
	}

	public static final TagKey<Item> EXCLUS = tag("borne/exclus");

	private static TagKey<Item> tag(String p) { return TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("airain", p)); }

	public static Palier palier(Item it) {
		Holder<Item> h = it.builtInRegistryHolder();
		Palier[] t = Palier.values();
		for (int i = t.length - 1; i >= 0; i--) if (h.is(t[i].tag)) return t[i];
		return Palier.TRAVAILLE;
	}

	public static boolean vendable(Item it) {
		if (it == Items.AIR) return false;
		String ns = BuiltInRegistries.ITEM.getKey(it).getNamespace();
		if (ns.equals("airain") || ns.equals("kubejs") || ns.equals("numismatics")) return false;
		Holder<Item> h = it.builtInRegistryHolder();
		if (h.is(EXCLUS)) return false;
		for (Rayon r : Rayon.values()) if (h.is(r.tag)) return true;
		return false;
	}

	/** Prix d'un lot (indice dans LOTS), 0 si ce lot n'est pas proposé. */
	public static int prix(Item it, int lot) {
		if (lot < 0 || lot >= LOTS.length) return 0;
		return palier(it).prix[lot];
	}

	public static List<Item> rayon(Rayon r) {
		Set<Item> s = new LinkedHashSet<>();
		for (Holder<Item> h : BuiltInRegistries.ITEM.getTagOrEmpty(r.tag)) {
			Item it = h.value();
			if (!vendable(it)) continue;
			Rayon premier = null;
			for (Rayon q : Rayon.values()) if (h.is(q.tag)) { premier = q; break; }
			if (premier == r) s.add(it);
		}
		List<Item> l = new ArrayList<>(s);
		l.sort(Comparator.comparing((Item it) -> palier(it).ordinal()).thenComparing(it -> BuiltInRegistries.ITEM.getKey(it).toString()));
		return l;
	}

	// ------------------------------------------------------------------ pièces (Create : Numismatics)
	public static final String[] PIECES = {"spur", "bevel", "sprocket", "cog", "crown", "sun"};
	public static final int[] VALEURS = {1, 8, 16, 64, 512, 4096};

	public static Item piece(int k) { return BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("numismatics", PIECES[k])); }

	private static int denomination(ItemStack s) {
		if (s.isEmpty()) return -1;
		ResourceLocation id = BuiltInRegistries.ITEM.getKey(s.getItem());
		if (!id.getNamespace().equals("numismatics")) return -1;
		for (int k = 0; k < PIECES.length; k++) if (PIECES[k].equals(id.getPath())) return k;
		return -1;
	}

	public static long solde(Player p) {
		long t = 0;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
			ItemStack s = p.getInventory().getItem(i);
			int k = denomination(s);
			if (k >= 0) t += (long) s.getCount() * VALEURS[k];
		}
		return t;
	}

	/** Décompose une somme en pièces (de la plus grosse à la plus petite). */
	public static int[] decomposer(long somme) {
		int[] n = new int[PIECES.length];
		for (int k = PIECES.length - 1; k >= 0; k--) { n[k] = (int) Math.min(Integer.MAX_VALUE, somme / VALEURS[k]); somme -= (long) n[k] * VALEURS[k]; }
		return n;
	}

	/** Prélève la somme dans l'inventaire (petites pièces d'abord) et rend la monnaie. */
	public static boolean payer(Player p, long prix) {
		if (prix <= 0) return true;
		if (solde(p) < prix) return false;
		long[] dispo = new long[PIECES.length];
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) { int k = denomination(inv.getItem(i)); if (k >= 0) dispo[k] += inv.getItem(i).getCount(); }
		long reste = prix;
		long[] prendre = new long[PIECES.length];
		for (int k = 0; k < PIECES.length && reste > 0; k++) {
			long t = Math.min(dispo[k], (reste + VALEURS[k] - 1) / VALEURS[k]);
			prendre[k] = t; reste -= t * VALEURS[k];
		}
		if (reste > 0) return false;
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			int k = denomination(s);
			if (k < 0 || prendre[k] == 0) continue;
			int t = (int) Math.min(prendre[k], s.getCount());
			s.shrink(t); prendre[k] -= t;
		}
		int[] monnaie = decomposer(-reste);
		for (int k = PIECES.length - 1; k >= 0; k--) {
			int n = monnaie[k];
			while (n > 0) {
				ItemStack st = new ItemStack(piece(k), Math.min(n, 64));
				n -= st.getCount();
				if (!inv.add(st)) p.drop(st, false);
			}
		}
		inv.setChanged();
		return true;
	}
}
