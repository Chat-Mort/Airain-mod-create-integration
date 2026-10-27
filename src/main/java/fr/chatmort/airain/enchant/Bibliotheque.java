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

/**
 * Le répertoire de la table d'enchantement de l'Empire : les livres enchantés rangés dans les bibliothèques sculptées
 * autour de la table (jusqu'à 3 blocs à l'horizontale, d'un bloc en dessous à deux au-dessus).
 * Chaque enchantement est disponible jusqu'au plus haut niveau trouvé dans un livre.
 */
public final class Bibliotheque {
	public static final int RAYON = 3;

	public record Entree(Holder<Enchantment> enchantement, int niveauMax) {}

	private Bibliotheque() {}

	public static List<Entree> lire(Level level, BlockPos table) {
		Map<Holder<Enchantment>, Integer> trouve = new LinkedHashMap<>();
		for (BlockPos p : BlockPos.betweenClosed(table.offset(-RAYON, -1, -RAYON), table.offset(RAYON, 2, RAYON))) {
			if (!(level.getBlockEntity(p) instanceof ChiseledBookShelfBlockEntity etagere))
				continue;
			for (int i = 0; i < etagere.getContainerSize(); i++) {
				ItemStack livre = etagere.getItem(i);
				if (!livre.is(Items.ENCHANTED_BOOK))
					continue;
				ItemEnchantments ench = livre.getOrDefault(DataComponents.STORED_ENCHANTMENTS, ItemEnchantments.EMPTY);
				for (Object2IntMap.Entry<Holder<Enchantment>> e : ench.entrySet())
					trouve.merge(e.getKey(), e.getIntValue(), Math::max);
			}
		}
		List<Entree> liste = new ArrayList<>();
		trouve.forEach((h, n) -> liste.add(new Entree(h, n)));
		return liste;
	}

	/** Coût en niveaux d'expérience : 3 par niveau, plus deux fois le coût d'enclume de l'enchantement (30 au plus). */
	public static int coutXp(Holder<Enchantment> h, int niveau) {
		return Math.min(30, 3 * niveau + 2 * h.value().getAnvilCost());
	}

	/** Coût en lapis-lazuli : un par niveau. */
	public static int coutLapis(int niveau) {
		return niveau;
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
