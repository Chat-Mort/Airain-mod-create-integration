package fr.chatmort.airain.enchant;

import java.util.ArrayList;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.Level;

/**
 * Écran de la table de l'Empire. Case 0 : l'objet ; case 1 : le lapis.
 * Le répertoire (enchantement + niveau maximal) est calculé côté serveur et envoyé au client par des DataSlot :
 * identifiant de l'enchantement dans le registre, puis niveau maximal. Bouton = index × 16 + niveau.
 */
public class TableEmpireMenu extends AbstractContainerMenu {
	public static final int MAX = 40;

	private final ContainerLevelAccess access;
	public final Container table;
	private final DataSlot nombre = DataSlot.standalone();
	private final DataSlot[] ids = new DataSlot[MAX];
	private final DataSlot[] niveaux = new DataSlot[MAX];
	private final Player joueur;
	private int attente;

	public TableEmpireMenu(int id, Inventory inv, RegistryFriendlyByteBuf buf) {
		this(id, inv, ContainerLevelAccess.NULL);
		buf.readBlockPos();
	}

	public TableEmpireMenu(int id, Inventory inv, ContainerLevelAccess access) {
		super(AirainMod.TABLE_MENU.get(), id);
		this.access = access;
		this.joueur = inv.player;
		this.table = new SimpleContainer(2) {
			@Override
			public void setChanged() {
				super.setChanged();
				slotsChanged(this);
			}
		};
		addSlot(new Slot(table, 0, 22, 35) {
			@Override
			public boolean mayPlace(ItemStack stack) {
				return !stack.is(Items.BOOK) && !stack.is(Items.ENCHANTED_BOOK);
			}

			@Override
			public int getMaxStackSize() {
				return 1;
			}
		});
		addSlot(new Slot(table, 1, 22, 60) {
			@Override
			public boolean mayPlace(ItemStack stack) {
				return stack.is(Items.LAPIS_LAZULI);
			}
		});
		for (int l = 0; l < 3; l++)
			for (int c = 0; c < 9; c++)
				addSlot(new Slot(inv, c + l * 9 + 9, 35 + c * 18, 140 + l * 18));
		for (int c = 0; c < 9; c++)
			addSlot(new Slot(inv, c, 35 + c * 18, 198));

		addDataSlot(nombre);
		for (int i = 0; i < MAX; i++) {
			ids[i] = addDataSlot(DataSlot.standalone());
			niveaux[i] = addDataSlot(DataSlot.standalone());
		}
		actualiser();
	}

	// ------------------------------------------------------------------ répertoire
	private void actualiser() {
		access.execute((level, pos) -> {
			List<Bibliotheque.Entree> liste = Bibliotheque.lire(level, pos);
			Registry<Enchantment> reg = level.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
			int n = Math.min(MAX, liste.size());
			nombre.set(n);
			for (int i = 0; i < n; i++) {
				ids[i].set(reg.getId(liste.get(i).enchantement().value()));
				niveaux[i].set(liste.get(i).niveauMax() + (liste.get(i).tome() ? 100 : 0));
			}
		});
	}

	public record Ligne(Holder<Enchantment> enchantement, int niveauMax, boolean tome) {
		/** Ce niveau est-il celui qu'ouvre le tome ancien (et qui le consomme) ? */
		public boolean parTome(int niveau) {
			return tome && niveau == niveauMax;
		}
	}

	/** Le répertoire tel que le voit ce côté (client ou serveur). */
	public List<Ligne> lignes(Level level) {
		List<Ligne> l = new ArrayList<>();
		Registry<Enchantment> reg = level.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
		for (int i = 0; i < nombre.get(); i++) {
			Enchantment e = reg.byId(ids[i].get());
			if (e != null)
				l.add(new Ligne(reg.wrapAsHolder(e), niveaux[i].get() % 100, niveaux[i].get() >= 100));
		}
		return l;
	}

	@Override
	public void broadcastChanges() {
		if (++attente >= 20) {         // les bibliothèques peuvent changer pendant que l'écran est ouvert
			attente = 0;
			actualiser();
		}
		super.broadcastChanges();
	}

	@Override
	public void slotsChanged(Container container) {
		super.slotsChanged(container);
		actualiser();
	}

	// ------------------------------------------------------------------ enchanter
	@Override
	public boolean clickMenuButton(Player player, int bouton) {
		int index = bouton / 16, niveau = bouton % 16;
		List<Ligne> l = lignes(player.level());
		if (index < 0 || index >= l.size() || niveau < 1 || niveau > l.get(index).niveauMax())
			return false;
		Holder<Enchantment> h = l.get(index).enchantement();
		boolean parTome = l.get(index).parTome(niveau);
		ItemStack objet = table.getItem(0);
		ItemStack lapis = table.getItem(1);
		if (!Bibliotheque.applicable(objet, h, niveau))
			return false;
		int xp = Bibliotheque.coutXp(h, niveau), nl = Bibliotheque.coutLapis(h, niveau);
		if (!player.getAbilities().instabuild && (player.experienceLevel < xp || lapis.getCount() < nl))
			return false;

		boolean[] ok = {true};
		access.execute((level, pos) -> {
			if (parTome && !Bibliotheque.consommerTome(level, pos, h)) {
				ok[0] = false;
				return;
			}
			EnchantmentHelper.updateEnchantments(objet, m -> m.set(h, niveau));
			if (!player.getAbilities().instabuild) {
				player.giveExperienceLevels(-xp);
				lapis.shrink(nl);
			}
			table.setChanged();
			level.playSound(null, pos, SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.BLOCKS, 1f, level.random.nextFloat() * 0.1f + 0.9f);
		});
		return ok[0];
	}

	// ------------------------------------------------------------------ divers
	@Override
	public void removed(Player player) {
		super.removed(player);
		access.execute((level, pos) -> clearContainer(player, table));
	}

	@Override
	public boolean stillValid(Player player) {
		return stillValid(access, player, AirainMod.TABLE.get());
	}

	@Override
	public ItemStack quickMoveStack(Player player, int index) {
		Slot slot = slots.get(index);
		if (!slot.hasItem())
			return ItemStack.EMPTY;
		ItemStack s = slot.getItem(), copie = s.copy();
		if (index < 2) {
			if (!moveItemStackTo(s, 2, slots.size(), true))
				return ItemStack.EMPTY;
		} else if (s.is(Items.LAPIS_LAZULI)) {
			if (!moveItemStackTo(s, 1, 2, false))
				return ItemStack.EMPTY;
		} else {
			if (slots.get(0).hasItem() || !slots.get(0).mayPlace(s))
				return ItemStack.EMPTY;
			slots.get(0).setByPlayer(s.split(1));
		}
		if (s.isEmpty())
			slot.setByPlayer(ItemStack.EMPTY);
		else
			slot.setChanged();
		return copie;
	}

	public ItemStack objet() {
		return table.getItem(0);
	}

	public int lapis() {
		return table.getItem(1).getCount();
	}
}
