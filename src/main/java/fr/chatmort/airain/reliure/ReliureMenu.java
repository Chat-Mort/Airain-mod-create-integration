package fr.chatmort.airain.reliure;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.NonNullList;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.ItemContainerContents;

/** Ranger les livres de la Reliure : 8 cases, puis l'inventaire du joueur (la Reliure tenue ne bouge pas). */
public class ReliureMenu extends AbstractContainerMenu {
	private final int slotReliure;
	private final Player joueur;
	private final SimpleContainer livres = new SimpleContainer(Reliure.CASES) {
		@Override
		public void setChanged() { super.setChanged(); enregistrer(); }
	};

	public ReliureMenu(int id, Inventory inv, RegistryFriendlyByteBuf buf) { this(id, inv, buf.readVarInt()); }

	public ReliureMenu(int id, Inventory inv, int slotReliure) {
		super(AirainMod.RELIURE_MENU.get(), id);
		this.slotReliure = slotReliure;
		this.joueur = inv.player;
		var cases = Reliure.cases(reliure());
		for (int i = 0; i < Reliure.CASES; i++) livres.setItem(i, cases.get(i));
		for (int i = 0; i < Reliure.CASES; i++)
			addSlot(new Slot(livres, i, 17 + i * 18, 20) {
				@Override public boolean mayPlace(ItemStack s) { return s.is(Reliure.LIVRES) && !Reliure.est(s); }
				@Override public int getMaxStackSize() { return 1; }
			});
		for (int r = 0; r < 3; r++)
			for (int c = 0; c < 9; c++) {
				int k = c + r * 9 + 9;
				addSlot(slotJoueur(inv, k, 8 + c * 18, 52 + r * 18));
			}
		for (int c = 0; c < 9; c++) addSlot(slotJoueur(inv, c, 8 + c * 18, 110));
	}

	private Slot slotJoueur(Inventory inv, int k, int x, int y) {
		return new Slot(inv, k, x, y) {
			@Override public boolean mayPickup(Player p) { return k != slotReliure; }
		};
	}

	private ItemStack reliure() {
		ItemStack s = joueur.getInventory().getItem(slotReliure);
		return Reliure.est(s) ? s : ItemStack.EMPTY;
	}

	private void enregistrer() {
		ItemStack r = reliure();
		if (r.isEmpty()) return;
		NonNullList<ItemStack> l = NonNullList.withSize(Reliure.CASES, ItemStack.EMPTY);
		for (int i = 0; i < Reliure.CASES; i++) l.set(i, livres.getItem(i).copy());
		r.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(l));
	}

	@Override
	public boolean stillValid(Player p) { return !reliure().isEmpty(); }

	@Override
	public ItemStack quickMoveStack(Player p, int index) {
		Slot s = slots.get(index);
		if (!s.hasItem() || !s.mayPickup(p)) return ItemStack.EMPTY;
		ItemStack pile = s.getItem(), avant = pile.copy();
		if (index < Reliure.CASES) {
			if (!moveItemStackTo(pile, Reliure.CASES, slots.size(), true)) return ItemStack.EMPTY;
		} else {
			if (!pile.is(Reliure.LIVRES) || Reliure.est(pile) || !moveItemStackTo(pile, 0, Reliure.CASES, false)) return ItemStack.EMPTY;
		}
		if (pile.isEmpty()) s.set(ItemStack.EMPTY); else s.setChanged();
		return avant;
	}

	@Override
	public void removed(Player p) {
		super.removed(p);
		enregistrer();
	}

	public static Container vide() { return new SimpleContainer(0); }
}
