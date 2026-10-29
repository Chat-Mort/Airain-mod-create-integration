package fr.chatmort.airain.banc;

import fr.chatmort.airain.AirainMod;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.items.SlotItemHandler;

/**
 * Écran du banc d'entretien : objet abîmé, matériau (ou second objet), résultat, trois modules, inventaire.
 * Données suivies : avancement (‰), huile (mB), vitesse (tr/min), secondes restantes, travail en cours.
 */
public class BancMenu extends AbstractContainerMenu {
	public final BancEntretienBlockEntity banc;
	private final ContainerData donnees;

	public BancMenu(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
		this(id, inv, inv.player.level().getBlockEntity(buf.readBlockPos()) instanceof BancEntretienBlockEntity b ? b : null, new SimpleContainerData(5));
	}

	public BancMenu(int id, Inventory inv, BancEntretienBlockEntity b, ContainerData d) {
		super(AirainMod.BANC_MENU.get(), id);
		this.banc = b;
		this.donnees = d;
		IItemHandler objets = b != null ? b.inventaire : new ItemStackHandler(3);
		IItemHandler mods = b != null ? b.modules : new ItemStackHandler(3);
		addSlot(new SlotItemHandler(objets, 0, 36, 24) {
			@Override public boolean mayPlace(ItemStack s) { return BancEntretienBlockEntity.reparable(s); }
			@Override public int getMaxStackSize() { return 1; }
		});
		addSlot(new SlotItemHandler(objets, 1, 36, 52) {
			@Override public boolean mayPlace(ItemStack s) { return BancEntretienBlockEntity.accepteEnSecond(objets.getStackInSlot(0), s); }
		});
		addSlot(new SlotItemHandler(objets, 2, 110, 38) {
			@Override public boolean mayPlace(ItemStack s) { return false; }
		});
		for (int i = 0; i < 3; i++)
			addSlot(new SlotItemHandler(mods, i, 150, 18 + i * 20) {
				@Override public boolean mayPlace(ItemStack s) { return BancEntretienBlockEntity.Module.de(s) != null; }
				@Override public int getMaxStackSize() { return 1; }
			});
		for (int l = 0; l < 3; l++)
			for (int c = 0; c < 9; c++)
				addSlot(new Slot(inv, c + l * 9 + 9, 8 + c * 18, 104 + l * 18));
		for (int c = 0; c < 9; c++)
			addSlot(new Slot(inv, c, 8 + c * 18, 162));
		addDataSlots(d);
	}

	/** Données côté serveur, lues dans le banc à chaque synchronisation. */
	public static ContainerData donnees(BancEntretienBlockEntity b) {
		return new ContainerData() {
			@Override
			public int get(int i) {
				return switch (i) {
					case 0 -> Math.round(b.avancement() * 1000);
					case 1 -> b.reservoir.getFluidAmount();
					case 2 -> Math.round(Math.abs(b.getSpeed()));
					case 3 -> b.secondesRestantes();
					default -> b.travaille() ? 1 : 0;
				};
			}

			@Override public void set(int i, int v) {}
			@Override public int getCount() { return 5; }
		};
	}

	public float avancement() { return donnees.get(0) / 1000f; }
	public int huile() { return donnees.get(1); }
	public int vitesse() { return donnees.get(2); }
	public int secondes() { return donnees.get(3); }
	public boolean travaille() { return donnees.get(4) == 1; }

	@Override
	public ItemStack quickMoveStack(Player p, int index) {
		Slot slot = slots.get(index);
		if (!slot.hasItem()) return ItemStack.EMPTY;
		ItemStack s = slot.getItem(), copie = s.copy();
		if (index < 6) {
			if (!moveItemStackTo(s, 6, 42, true)) return ItemStack.EMPTY;
		} else if (BancEntretienBlockEntity.Module.de(s) != null) {
			if (!moveItemStackTo(s, 3, 6, false)) return ItemStack.EMPTY;
		} else if (BancEntretienBlockEntity.reparable(s) && !slots.get(0).hasItem()) {
			if (!moveItemStackTo(s, 0, 1, false)) return ItemStack.EMPTY;
		} else if (!moveItemStackTo(s, 1, 2, false)) return ItemStack.EMPTY;
		if (s.isEmpty()) slot.setByPlayer(ItemStack.EMPTY); else slot.setChanged();
		return copie;
	}

	@Override
	public boolean stillValid(Player p) {
		return banc != null && !banc.isRemoved() && p.distanceToSqr(banc.getBlockPos().getCenter()) <= 64;
	}
}
