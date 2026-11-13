package fr.chatmort.airain.atelier;

import net.minecraft.core.NonNullList;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.protocol.game.ClientboundContainerSetSlotPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.StackedContents;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.inventory.ResultContainer;
import net.minecraft.world.inventory.ResultSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeType;

import java.util.List;
import java.util.Optional;

/** Écran de l'établi : comme une table de craft, mais la grille est celle de l'établi (elle garde ses objets). */
public class EtabliMenu extends AbstractContainerMenu {
	private final CraftingContainer grille;
	private final ResultContainer resultat = new ResultContainer();
	private final Player joueur;
	private final Etabli.EtabliBlockEntity etabli;

	public EtabliMenu(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
		this(id, inv, inv.player.level().getBlockEntity(buf.readBlockPos()) instanceof Etabli.EtabliBlockEntity b ? b : null);
	}
	public EtabliMenu(int id, Inventory inv, Etabli.EtabliBlockEntity b) {
		super(Atelier.ETABLI_MENU.get(), id);
		this.joueur = inv.player; this.etabli = b;
		this.grille = b != null ? b : new Grille(this);
		if (b != null && !joueur.level().isClientSide) b.ouverts.add(this);
		addSlot(new ResultSlot(joueur, grille, resultat, 0, 124, 35));
		for (int l = 0; l < 3; l++) for (int c = 0; c < 3; c++) addSlot(new Slot(grille, c + l * 3, 30 + c * 18, 17 + l * 18));
		for (int l = 0; l < 3; l++) for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c + l * 9 + 9, 8 + c * 18, 84 + l * 18));
		for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c, 8 + c * 18, 142));
		if (b != null) slotsChanged(grille);
	}

	// le résultat se recalcule (côté serveur) dès que la grille change
	@Override
	public void slotsChanged(Container c) {
		if (c != grille || joueur.level().isClientSide || !(joueur instanceof ServerPlayer sp)) return;
		CraftingInput in = grille.asCraftInput();
		ItemStack r = ItemStack.EMPTY;
		Optional<RecipeHolder<CraftingRecipe>> rec = sp.server.getRecipeManager().getRecipeFor(RecipeType.CRAFTING, in, joueur.level());
		if (rec.isPresent() && resultat.setRecipeUsed(joueur.level(), sp, rec.get())) {
			ItemStack x = rec.get().value().assemble(in, joueur.level().registryAccess());
			if (x.isItemEnabled(joueur.level().enabledFeatures())) r = x;
		}
		resultat.setItem(0, r);
		setRemoteSlot(0, r);
		sp.connection.send(new ClientboundContainerSetSlotPacket(containerId, incrementStateId(), 0, r));
	}

	@Override
	public void removed(Player j) {
		super.removed(j);
		if (etabli != null) etabli.ouverts.remove(this);
	}
	@Override public boolean stillValid(Player j) { return grille.stillValid(j); }
	@Override public boolean canTakeItemForPickAll(ItemStack s, Slot sl) { return sl.container != resultat && super.canTakeItemForPickAll(s, sl); }

	@Override
	public ItemStack quickMoveStack(Player j, int i) {
		ItemStack copie = ItemStack.EMPTY;
		Slot sl = slots.get(i);
		if (sl.hasItem()) {
			ItemStack st = sl.getItem(); copie = st.copy();
			if (i == 0) {                                     // résultat → inventaire (en boucle, comme la table)
				st.getItem().onCraftedBy(st, j.level(), j);
				if (!moveItemStackTo(st, 10, 46, true)) return ItemStack.EMPTY;
				sl.onQuickCraft(st, copie);
			} else if (i < 10) {                              // grille → inventaire
				if (!moveItemStackTo(st, 10, 46, false)) return ItemStack.EMPTY;
			} else if (!moveItemStackTo(st, 1, 10, false)) {  // inventaire → grille, sinon entre inventaire et barre
				if (i < 37 ? !moveItemStackTo(st, 37, 46, false) : !moveItemStackTo(st, 10, 37, false)) return ItemStack.EMPTY;
			}
			if (st.isEmpty()) sl.setByPlayer(ItemStack.EMPTY); else sl.setChanged();
			if (st.getCount() == copie.getCount()) return ItemStack.EMPTY;
			sl.onTake(j, st);
			if (i == 0) j.drop(st, false);
		}
		return copie;
	}

	/** Grille factice côté client (le vrai contenu arrive par la synchronisation des emplacements). */
	private static class Grille implements CraftingContainer {
		private final NonNullList<ItemStack> o = NonNullList.withSize(9, ItemStack.EMPTY);
		private final AbstractContainerMenu menu;
		Grille(AbstractContainerMenu m) { menu = m; }
		@Override public int getWidth() { return 3; }
		@Override public int getHeight() { return 3; }
		@Override public List<ItemStack> getItems() { return List.copyOf(o); }
		@Override public int getContainerSize() { return 9; }
		@Override public boolean isEmpty() { for (ItemStack s : o) if (!s.isEmpty()) return false; return true; }
		@Override public ItemStack getItem(int i) { return o.get(i); }
		@Override public ItemStack removeItem(int i, int n) { ItemStack r = ContainerHelper.removeItem(o, i, n); if (!r.isEmpty()) menu.slotsChanged(this); return r; }
		@Override public ItemStack removeItemNoUpdate(int i) { return ContainerHelper.takeItem(o, i); }
		@Override public void setItem(int i, ItemStack s) { o.set(i, s); menu.slotsChanged(this); }
		@Override public void setChanged() {}
		@Override public boolean stillValid(Player j) { return true; }
		@Override public void clearContent() { o.clear(); }
		@Override public void fillStackedContents(StackedContents c) { for (ItemStack s : o) c.accountSimpleStack(s); }
	}
}
