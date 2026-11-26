package fr.chatmort.airain.fonderie;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;

/**
 * 1.70 : menu de la table du carreleur. Onglet 0 : création (4 rôles, carton vierge, carton imprimé) ;
 * onglets 1 à 3 : 36 cartons chacun (sols, murs, plafonds), un carton n'entre que dans l'onglet de son type.
 */
public class CarreleurMenu extends AbstractContainerMenu {
	public final Container table;
	private final DataSlot onglet = DataSlot.standalone();
	/** Côté client : rôles affichés selon le motif choisi (l'écran les règle). */
	public boolean accentVisible, bordVisible;
	public int premierJoueur;

	public CarreleurMenu(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
		this(id, inv, inv.player.level().getBlockEntity(buf.readBlockPos()) instanceof Carreleur.TableBE b ? b : new SimpleContainer(Carreleur.TAILLE));
	}

	public CarreleurMenu(int id, Inventory inv, Container t) {
		super(Carreleur.MENU.get(), id);
		this.table = t;
		addDataSlot(onglet);
		// rangement : 3 onglets de 4 rangées de 9
		for (int o = 0; o < 3; o++)
			for (int r = 0; r < 4; r++)
				for (int c = 0; c < 9; c++) {
					final int tab = o + 1;
					addSlot(new Slot(t, o * Carreleur.RANGEMENT + r * 9 + c, 52 + c * 18, 47 + r * 18) {
						@Override public boolean isActive() { return onglet.get() == tab; }
						@Override public boolean mayPlace(ItemStack s) { return Motif.enregistre(s) && Generateur.TYPES[tab - 1].equals(Motif.type(s)); }
					});
				}
		// rôles : A, B, accent, bordure (la case de bordure a deux places : 3e ligne si pas d'accent, sinon 4e)
		addSlot(role(Carreleur.ROLE_A, 0, () -> true));
		addSlot(role(Carreleur.ROLE_B, 1, () -> true));
		addSlot(role(Carreleur.ROLE_ACCENT, 2, () -> accentVisible));
		addSlot(role(Carreleur.ROLE_BORD, 2, () -> bordVisible && !accentVisible));
		addSlot(role(Carreleur.ROLE_BORD, 3, () -> bordVisible && accentVisible));
		addSlot(new Slot(t, Carreleur.ENTREE, 209, 123) {
			@Override public boolean isActive() { return onglet.get() == 0; }
			@Override public boolean mayPlace(ItemStack s) { return s.is(Motif.CARTON.get()) && !Motif.enregistre(s); }
		});
		addSlot(new Slot(t, Carreleur.SORTIE, 241, 123) {
			@Override public boolean isActive() { return onglet.get() == 0; }
			@Override public boolean mayPlace(ItemStack s) { return false; }
		});
		premierJoueur = slots.size();
		for (int r = 0; r < 3; r++)
			for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c + r * 9 + 9, 52 + c * 18, 191 + r * 18));
		for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c, 52 + c * 18, 249));
	}

	private Slot role(int k, int ligne, java.util.function.BooleanSupplier visible) {
		return new Slot(table, Carreleur.ROLES + k, 241, 32 + ligne * 22) {
			@Override public boolean isActive() { return onglet.get() == 0 && visible.getAsBoolean(); }
			@Override public boolean mayPlace(ItemStack s) { return s.getItem() instanceof BlockItem; }
			@Override public int getMaxStackSize() { return 1; }
		};
	}

	public int onglet() { return onglet.get(); }

	@Override
	public boolean clickMenuButton(Player p, int id) {
		if (id < 0 || id > 3) return false;
		onglet.set(id);
		return true;
	}

	@Override
	public ItemStack quickMoveStack(Player p, int i) {
		Slot s = slots.get(i);
		if (!s.hasItem()) return ItemStack.EMPTY;
		ItemStack st = s.getItem(), avant = st.copy();
		if (i < premierJoueur) {
			if (!moveItemStackTo(st, premierJoueur, slots.size(), true)) return ItemStack.EMPTY;
		} else {
			boolean ok = false;
			if (Motif.enregistre(st)) {
				String type = Motif.type(st);
				for (int o = 0; o < 3 && !ok; o++)
					if (Generateur.TYPES[o].equals(type)) ok = moveItemStackTo(st, o * 36, o * 36 + 36, false);
			} else if (st.is(Motif.CARTON.get())) ok = moveItemStackTo(st, 108 + 5, 108 + 6, false);
			else if (st.getItem() instanceof BlockItem && onglet.get() == 0) {
				for (int k = 108; k < 108 + 5 && !ok; k++) if (slots.get(k).isActive() && !slots.get(k).hasItem()) ok = moveItemStackTo(st, k, k + 1, false);
			}
			if (!ok) return ItemStack.EMPTY;
		}
		if (st.isEmpty()) s.setByPlayer(ItemStack.EMPTY); else s.setChanged();
		return avant;
	}

	@Override public boolean stillValid(Player p) { return table.stillValid(p); }
}
