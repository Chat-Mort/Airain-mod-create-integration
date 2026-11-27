package fr.chatmort.airain.fonderie;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentEffectComponents;
import net.minecraft.world.item.enchantment.EnchantmentHelper;

/**
 * 1.71.1 : armoire impériale. 9 colonnes = 9 sets d'armure ; rangée 1 casques, 2 plastrons, 3 jambières, 4 bottes.
 * Bouton sous chaque colonne (clickMenuButton 0 à 8) : échange pièce par pièce l'armure portée et celle de la colonne.
 */
public class ArmoireMenu extends AbstractContainerMenu {
	public static final EquipmentSlot[] RANGEES = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
	private static final net.minecraft.resources.ResourceLocation[] GABARITS = {InventoryMenu.EMPTY_ARMOR_SLOT_HELMET,
		InventoryMenu.EMPTY_ARMOR_SLOT_CHESTPLATE, InventoryMenu.EMPTY_ARMOR_SLOT_LEGGINGS, InventoryMenu.EMPTY_ARMOR_SLOT_BOOTS};
	public static final int CASES = 36;
	final Container armoire;
	private final Player joueur;

	public ArmoireMenu(int id, Inventory inv) { this(id, inv, new SimpleContainer(CASES)); }

	public ArmoireMenu(int id, Inventory inv, Container c) {
		super(Mobilier.ARMOIRE_MENU.get(), id);
		checkContainerSize(c, CASES);
		armoire = c; joueur = inv.player;
		c.startOpen(joueur);
		for (int r = 0; r < 4; r++)
			for (int col = 0; col < 9; col++) {
				EquipmentSlot es = RANGEES[r];
				Slot s = new Slot(c, r * 9 + col, 8 + col * 18, 18 + r * 18) {
					@Override public boolean mayPlace(ItemStack st) { return accepte(st, es); }
					@Override public int getMaxStackSize() { return 1; }
				};
				s.setBackground(InventoryMenu.BLOCK_ATLAS, GABARITS[r]);   // silhouette de la pièce dans la case vide
				addSlot(s);
			}
		for (int r = 0; r < 3; r++)
			for (int col = 0; col < 9; col++) addSlot(new Slot(inv, 9 + r * 9 + col, 8 + col * 18, 122 + r * 18));
		for (int col = 0; col < 9; col++) addSlot(new Slot(inv, col, 8 + col * 18, 180));
	}

	/** La pièce va-t-elle dans cette rangée ? (même règle que les cases d'armure du joueur) */
	boolean accepte(ItemStack st, EquipmentSlot es) { return !st.isEmpty() && joueur.getEquipmentSlotForItem(st) == es; }

	/** Malédiction du lien : la pièce ne quitte pas le joueur (sauf en créatif), comme en vanilla. */
	private boolean liee(ItemStack st) {
		return !joueur.isCreative() && EnchantmentHelper.has(st, EnchantmentEffectComponents.PREVENT_ARMOR_CHANGE);
	}

	@Override
	public boolean clickMenuButton(Player p, int col) {
		if (col < 0 || col > 8) return false;
		boolean change = false;
		for (int r = 0; r < 4; r++) {
			EquipmentSlot es = RANGEES[r];
			int i = r * 9 + col;
			ItemStack porte = p.getItemBySlot(es), range = armoire.getItem(i);
			if (porte.isEmpty() && range.isEmpty()) continue;
			if (!porte.isEmpty() && liee(porte)) continue;
			if (!range.isEmpty() && !accepte(range, es)) continue;   // objet d'avant (ancienne armoire) : laissé en place
			p.setItemSlot(es, range.copy());
			armoire.setItem(i, porte.copy());
			change = true;
		}
		if (change) {
			armoire.setChanged();
			p.level().playSound(null, p.blockPosition(), SoundEvents.ARMOR_EQUIP_IRON.value(), SoundSource.PLAYERS, 0.8f, 1f);
		}
		return true;
	}

	@Override
	public ItemStack quickMoveStack(Player p, int index) {
		Slot s = slots.get(index);
		if (!s.hasItem()) return ItemStack.EMPTY;
		ItemStack st = s.getItem(), copie = st.copy();
		if (index < CASES) {
			if (!moveItemStackTo(st, CASES, slots.size(), true)) return ItemStack.EMPTY;
		} else {
			// une pièce d'armure va dans la première case libre de sa rangée
			int r = -1;
			for (int k = 0; k < 4; k++) if (accepte(st, RANGEES[k])) r = k;
			if (r < 0 || !moveItemStackTo(st, r * 9, r * 9 + 9, false)) return ItemStack.EMPTY;
		}
		if (st.isEmpty()) s.setByPlayer(ItemStack.EMPTY); else s.setChanged();
		return copie;
	}

	@Override public boolean stillValid(Player p) { return armoire.stillValid(p); }
	@Override public void removed(Player p) { super.removed(p); armoire.stopOpen(p); }
}
