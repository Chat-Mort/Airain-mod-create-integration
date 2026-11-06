package fr.chatmort.airain.enchant;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import it.unimi.dsi.fastutil.objects.Object2IntMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.ChiseledBookShelfBlockEntity;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import java.util.HashSet;
import java.util.Set;

/**
 * Le répertoire de la table d'enchantement de l'Empire : les livres enchantés rangés dans les bibliothèques sculptées
 * autour de la table (jusqu'à 3 blocs à l'horizontale, d'un bloc en dessous à deux au-dessus).
 * Chaque enchantement est disponible jusqu'au plus haut niveau trouvé dans un livre.
 */
public final class Bibliotheque {
	public static final int RAYON = 3;

	/** niveauMax : le plus haut niveau proposé ; tome : ce niveau-là vient d'un tome ancien (un seul compte par enchantement). */
	public record Entree(Holder<Enchantment> enchantement, int niveauMax, boolean tome) {}

	private Bibliotheque() {}

	/** Composant des tomes anciens de Quark (lu par son nom : pas de dépendance à la compilation). */
	private static final ResourceLocation TOME_ID = ResourceLocation.fromNamespaceAndPath("quark", "ancient_tome");
	private static final ResourceLocation TOME_COMPOSANT = ResourceLocation.fromNamespaceAndPath("quark", "tome_enchantments");

	/** Enchantement porté par un tome ancien de Quark, ou null. */
	@SuppressWarnings("unchecked")
	public static Holder<Enchantment> enchantementDuTome(ItemStack pile) {
		if (pile.isEmpty() || !BuiltInRegistries.ITEM.getKey(pile.getItem()).equals(TOME_ID))
			return null;
		DataComponentType<?> type = BuiltInRegistries.DATA_COMPONENT_TYPE.get(TOME_COMPOSANT);
		if (type == null || !(pile.get(type) instanceof ItemEnchantments ench) || ench.isEmpty())
			return null;
		return ench.keySet().iterator().next();
	}

	/** Au-delà du maximum vanilla : coût renforcé (40 niveaux, double lapis). */
	public static boolean depasse(Holder<Enchantment> h, int niveau) {
		return niveau > h.value().getMaxLevel();
	}

	public static List<Entree> lire(Level level, BlockPos table) {
		Map<Holder<Enchantment>, Integer> trouve = new LinkedHashMap<>();
		Set<Holder<Enchantment>> tomes = new HashSet<>();
		for (BlockPos p : BlockPos.betweenClosed(table.offset(-RAYON, -1, -RAYON), table.offset(RAYON, 2, RAYON))) {
			if (!(level.getBlockEntity(p) instanceof ChiseledBookShelfBlockEntity etagere))
				continue;
			for (int i = 0; i < etagere.getContainerSize(); i++) {
				ItemStack livre = etagere.getItem(i);
				Holder<Enchantment> tome = enchantementDuTome(livre);
				if (tome != null) {
					tomes.add(tome);
					continue;
				}
				if (!livre.is(Items.ENCHANTED_BOOK))
					continue;
				ItemEnchantments ench = livre.getOrDefault(DataComponents.STORED_ENCHANTMENTS, ItemEnchantments.EMPTY);
				// un livre au-delà du maximum compte comme un livre au maximum : seul le tome ouvre le niveau suivant
				for (Object2IntMap.Entry<Holder<Enchantment>> e : ench.entrySet())
					trouve.merge(e.getKey(), Math.min(e.getIntValue(), e.getKey().value().getMaxLevel()), Math::max);
			}
		}
		List<Entree> liste = new ArrayList<>();
		// un tome ancien ajoute UN niveau à celui du meilleur livre, quel qu'il soit ; plusieurs tomes du même enchantement ne comptent qu'une fois
		trouve.forEach((h, n) -> liste.add(tomes.contains(h) ? new Entree(h, n + 1, true) : new Entree(h, n, false)));
		return liste;
	}

	/** Coût plein en niveaux d'expérience : 3 par niveau, plus deux fois le coût d'enclume de l'enchantement (30 au plus) ; 40 au-delà du maximum. */
	public static int coutXp(Holder<Enchantment> h, int niveau) {
		if (depasse(h, niveau))
			return 40;
		return Math.min(30, 3 * niveau + 2 * h.value().getAnvilCost());
	}

	/** Coût plein en lapis-lazuli : un par niveau (le double au-delà du maximum). */
	public static int coutLapis(Holder<Enchantment> h, int niveau) {
		return depasse(h, niveau) ? 2 * niveau : niveau;
	}

	/** Niveau de cet enchantement déjà présent sur l'objet (0 s'il ne l'a pas). */
	public static int actuel(ItemStack objet, Holder<Enchantment> h) {
		return objet.isEmpty() ? 0 : objet.getOrDefault(DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY).getLevel(h);
	}

	/**
	 * Réduction d'un niveau ouvert par un tome (au-delà du maximum) quand l'objet porte déjà l'enchantement :
	 * 50 % au plus, soit (50 % / niveau maximum normal) par niveau déjà présent. Ex. Protection III → V : 3 × 12,5 % = 37,5 %.
	 */
	static double reductionTome(Holder<Enchantment> h, int actuel) {
		int max = Math.max(1, h.value().getMaxLevel());
		return Math.min(0.5, 0.5 / max * Math.min(actuel, max));
	}

	/**
	 * Coût en niveaux compte tenu de ce que l'objet porte déjà.
	 * Niveau normal : on ne paie que la différence avec le niveau déjà présent (1 au moins).
	 * Niveau de tome : prix plein moins la réduction de tome, arrondi au niveau inférieur.
	 */
	public static int coutXp(Holder<Enchantment> h, int niveau, int actuel) {
		if (actuel <= 0) return coutXp(h, niveau);
		if (depasse(h, niveau)) return (int) Math.floor(coutXp(h, niveau) * (1 - reductionTome(h, actuel)));
		return Math.max(1, coutXp(h, niveau) - coutXp(h, Math.min(actuel, niveau)));
	}

	/** Coût en lapis, même règle : la différence pour un niveau normal, la réduction de tome au-delà. */
	public static int coutLapis(Holder<Enchantment> h, int niveau, int actuel) {
		if (actuel <= 0) return coutLapis(h, niveau);
		if (depasse(h, niveau)) return Math.max(1, (int) Math.floor(coutLapis(h, niveau) * (1 - reductionTome(h, actuel))));
		return Math.max(1, niveau - actuel);
	}

	/** L'enchantement peut-il aller sur cet objet, compte tenu de ceux qu'il porte déjà ? */
	public static boolean applicable(ItemStack objet, Holder<Enchantment> h, int niveau) {
		if (objet.isEmpty() || objet.is(Items.BOOK) || objet.is(Items.ENCHANTED_BOOK))
			return false;
		if (!h.value().canEnchant(objet))
			return false;
		ItemEnchantments actuels = objet.getOrDefault(DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY);
		int deja = actuels.getLevel(h);
		if (deja > 0)
			return niveau > deja;
		return EnchantmentHelper.isEnchantmentCompatible(actuels.keySet(), h);
	}
}
