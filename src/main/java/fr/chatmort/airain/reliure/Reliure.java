package fr.chatmort.airain.reliure;

import java.util.ArrayList;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.ItemContainerContents;
import net.neoforged.neoforge.capabilities.Capabilities;

/** Outils partagés de la Reliure : contenu, recherche, lecture d'un livre « comme s'il était en main ». */
public final class Reliure {
	private Reliure() {}

	public static final int CASES = 9;   // 9 livres : la rangée tient juste dans le panneau
	public static final TagKey<Item> LIVRES = TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("airain", "reliure"));
	/** D'où vient la Reliure : main / case d'inventaire, case du conteneur ouvert, recherche (touche). */
	public static final int INVENTAIRE = 0, CONTENEUR = 1, RECHERCHE = 2;

	public static boolean est(ItemStack s) { return s.is(AirainMod.RELIURE.get()); }

	public static List<ItemStack> livres(ItemStack reliure) {
		List<ItemStack> l = new ArrayList<>();
		ItemContainerContents c = reliure.getOrDefault(DataComponents.CONTAINER, ItemContainerContents.EMPTY);
		for (ItemStack s : c.nonEmptyItems()) l.add(s.copy());
		return l;
	}

	/** Toutes les cases, vides comprises (pour le menu). */
	public static List<ItemStack> cases(ItemStack reliure) {
		ItemContainerContents c = reliure.getOrDefault(DataComponents.CONTAINER, ItemContainerContents.EMPTY);
		net.minecraft.core.NonNullList<ItemStack> nl = net.minecraft.core.NonNullList.withSize(CASES, ItemStack.EMPTY);
		c.copyInto(nl);
		return new ArrayList<>(nl);
	}

	/** Cherche une Reliure : inventaire, puis à l'intérieur des objets à inventaire (sacs) de l'inventaire et du plastron. */
	public static ItemStack chercher(ServerPlayer p) {
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) if (est(inv.getItem(i))) return inv.getItem(i);
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.isEmpty()) continue;
			var h = s.getCapability(Capabilities.ItemHandler.ITEM);
			if (h == null) continue;
			for (int k = 0; k < h.getSlots(); k++) if (est(h.getStackInSlot(k))) return h.getStackInSlot(k);
		}
		return ItemStack.EMPTY;
	}

	public static ItemStack trouver(ServerPlayer p, int ou, int slot) {
		ItemStack r = switch (ou) {
			case INVENTAIRE -> slot >= 0 && slot < p.getInventory().getContainerSize() ? p.getInventory().getItem(slot) : ItemStack.EMPTY;
			case CONTENEUR -> slot >= 0 && slot < p.containerMenu.slots.size() ? p.containerMenu.getSlot(slot).getItem() : ItemStack.EMPTY;
			default -> chercher(p);
		};
		return est(r) ? r : ItemStack.EMPTY;
	}

	/** Utilise une copie du livre comme s'il était dans la main principale, puis rend la main telle qu'elle était. */
	public static void lire(net.minecraft.world.entity.player.Player p, ItemStack livre) {
		if (livre.isEmpty() || !livre.is(LIVRES)) return;
		var inv = p.getInventory();
		int sel = inv.selected;
		ItemStack main = inv.items.get(sel);
		ItemStack copie = livre.copy();
		inv.items.set(sel, copie);
		try {
			copie.getItem().use(p.level(), p, InteractionHand.MAIN_HAND);
		} finally {
			inv.items.set(sel, main);
		}
	}
}
