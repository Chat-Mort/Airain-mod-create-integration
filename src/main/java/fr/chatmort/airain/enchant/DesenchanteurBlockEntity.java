package fr.chatmort.airain.enchant;

import java.util.ArrayList;
import java.util.List;

import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.foundation.item.ItemHelper;

import fr.chatmort.airain.banc.BancEntretienBlockEntity;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.EnchantedBookItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.EnchantmentInstance;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.FluidUtil;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;

/**
 * Désenchanteur. Cases : 0 = objet enchanté (détruit), 1 = livres vierges, 2 = livre enchanté obtenu.
 * Un enchantement est tiré au hasard parmi ceux de l'objet ; il coûte {@link #COUT_PAR_NIVEAU} mB d'huile par niveau
 * et {@link #TRAVAIL} points de travail par niveau (même pénalité de lenteur que le banc d'entretien).
 */
public class DesenchanteurBlockEntity extends KineticBlockEntity {

	public static final int CAPACITE = 8000;
	public static final int COUT_PAR_NIVEAU = 500;
	public static final float TRAVAIL = 200f;

	public final ItemStackHandler inventaire;
	public final FluidTank reservoir;
	public final IItemHandler automatisation;
	private float progres;
	private boolean travaille;
	private String choix = "";      // enchantement tiré pour l'objet en cours
	private int niveauChoisi;

	public DesenchanteurBlockEntity(BlockPos pos, BlockState state) {
		this(fr.chatmort.airain.AirainMod.DESENCH_BE.get(), pos, state);
	}

	public DesenchanteurBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
		super(type, pos, state);
		inventaire = new ItemStackHandler(3) {
			@Override
			protected void onContentsChanged(int slot) {
				if (slot == 0) {
					choix = "";
					progres = 0;
				}
				setChanged();
				sendData();
			}
		};
		reservoir = new FluidTank(CAPACITE, f -> f.is(BancEntretienBlockEntity.HUILES)) {
			@Override
			protected void onContentsChanged() {
				setChanged();
				sendData();
			}
		};
		automatisation = new Automatisation();
	}

	public static ItemEnchantments enchantements(ItemStack s) {
		return EnchantmentHelper.getEnchantmentsForCrafting(s);
	}

	public static boolean desenchantable(ItemStack s) {
		return !s.isEmpty() && !enchantements(s).isEmpty();
	}

	// ------------------------------------------------------------------ travail
	@Override
	public void tick() {
		super.tick();
		if (level == null)
			return;
		if (level.isClientSide) {
			if (travaille && level.random.nextInt(2) == 0)
				level.addParticle(ParticleTypes.ENCHANT, worldPosition.getX() + 0.5, worldPosition.getY() + 1.3, worldPosition.getZ() + 0.4,
					level.random.nextGaussian() * 0.4, -0.3, level.random.nextGaussian() * 0.4);
			return;
		}
		boolean actif = etape();
		if (actif != travaille) {
			travaille = actif;
			sendData();
		}
	}

	private Holder<Enchantment> tirer(ItemStack a) {
		List<Object2IntMap.Entry<Holder<Enchantment>>> liste = new ArrayList<>(enchantements(a).entrySet());
		if (liste.isEmpty())
			return null;
		var e = liste.get(level.random.nextInt(liste.size()));
		niveauChoisi = Math.min(e.getIntValue(), e.getKey().value().getMaxLevel());   // jamais au-delà du maximum vanilla
		choix = e.getKey().unwrapKey().map(k -> k.location().toString()).orElse("");
		return e.getKey();
	}

	private Holder<Enchantment> choisi(ItemStack a) {
		for (var e : enchantements(a).entrySet())
			if (e.getKey().unwrapKey().map(k -> k.location().toString()).orElse("?").equals(choix))
				return e.getKey();
		return null;
	}

	private boolean etape() {
		ItemStack a = inventaire.getStackInSlot(0);
		if (!desenchantable(a) || !inventaire.getStackInSlot(1).is(Items.BOOK) || !inventaire.getStackInSlot(2).isEmpty())
			return false;
		Holder<Enchantment> h = choix.isEmpty() ? tirer(a) : choisi(a);
		if (h == null) {
			h = tirer(a);
			if (h == null)
				return false;
		}
		niveauChoisi = Math.max(1, Math.min(niveauChoisi, h.value().getMaxLevel()));
		if (reservoir.getFluidAmount() < COUT_PAR_NIVEAU * niveauChoisi)
			return false;
		float vitesse = Math.abs(getSpeed());
		if (vitesse < 16 || isOverStressed())
			return false;

		progres += BancEntretienBlockEntity.rythme(vitesse);
		if (progres < TRAVAIL * niveauChoisi)
			return true;

		ItemStack livre = EnchantedBookItem.createForEnchantment(new EnchantmentInstance(h, niveauChoisi));
		reservoir.drain(COUT_PAR_NIVEAU * niveauChoisi, IFluidHandler.FluidAction.EXECUTE);
		inventaire.extractItem(1, 1, false);
		inventaire.setStackInSlot(0, ItemStack.EMPTY);   // l'objet est détruit
		inventaire.setStackInSlot(2, livre);
		level.playSound(null, worldPosition, SoundEvents.GRINDSTONE_USE, SoundSource.BLOCKS, 0.6f, 0.8f);
		level.playSound(null, worldPosition, SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.BLOCKS, 0.6f, 1.2f);
		return true;
	}

	// ------------------------------------------------------------------ interactions
	public boolean utiliserObjet(Player player, InteractionHand hand, ItemStack tenu) {
		if (BancEntretienBlockEntity.BURETTE_ID.equals(BuiltInRegistries.ITEM.getKey(tenu.getItem()))) {
			Fluid huile = BuiltInRegistries.FLUID.get(BancEntretienBlockEntity.HUILE_ID);
			if (huile == Fluids.EMPTY)
				return false;
			int b = BancEntretienBlockEntity.BURETTE;
			if (reservoir.fill(new FluidStack(huile, b), IFluidHandler.FluidAction.SIMULATE) < b) {
				player.displayClientMessage(Component.translatable("airain.banc.plein").withStyle(ChatFormatting.GRAY), true);
				return true;
			}
			reservoir.fill(new FluidStack(huile, b), IFluidHandler.FluidAction.EXECUTE);
			if (!player.isCreative())
				tenu.shrink(1);
			player.displayClientMessage(Component.translatable("airain.banc.huile", reservoir.getFluidAmount(), CAPACITE).withStyle(ChatFormatting.GOLD), true);
			return true;
		}
		if (FluidUtil.getFluidHandler(tenu).isPresent())
			return FluidUtil.interactWithFluidHandler(player, hand, reservoir);
		ItemStack reste = automatisation.insertItem(0, tenu.copy(), false);
		if (reste.getCount() == tenu.getCount())
			reste = automatisation.insertItem(1, tenu.copy(), false);
		if (reste.getCount() == tenu.getCount())
			return false;
		player.setItemInHand(hand, reste);
		return true;
	}

	public void reprendre(Player player) {
		for (int slot : new int[] {2, 1, 0}) {
			ItemStack s = inventaire.getStackInSlot(slot);
			if (!s.isEmpty()) {
				player.getInventory().placeItemBackInInventory(s.copy());
				inventaire.setStackInSlot(slot, ItemStack.EMPTY);
				return;
			}
		}
	}

	private class Automatisation implements IItemHandler {
		@Override
		public int getSlots() {
			return 3;
		}

		@Override
		public ItemStack getStackInSlot(int slot) {
			return inventaire.getStackInSlot(slot);
		}

		@Override
		public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) {
			if (slot == 0) {
				if (!inventaire.getStackInSlot(0).isEmpty() || !desenchantable(stack))
					return stack;
				return inventaire.insertItem(0, stack.copyWithCount(1), simulate).isEmpty()
					? stack.copyWithCount(stack.getCount() - 1) : stack;
			}
			if (slot == 1)
				return stack.is(Items.BOOK) ? inventaire.insertItem(1, stack, simulate) : stack;
			return stack;
		}

		@Override
		public ItemStack extractItem(int slot, int amount, boolean simulate) {
			return slot == 2 ? inventaire.extractItem(2, amount, simulate) : ItemStack.EMPTY;
		}

		@Override
		public int getSlotLimit(int slot) {
			return slot == 0 ? 1 : 64;
		}

		@Override
		public boolean isItemValid(int slot, ItemStack stack) {
			return slot == 0 ? desenchantable(stack) : slot == 1 && stack.is(Items.BOOK);
		}
	}

	// ------------------------------------------------------------------ lunettes
	@Override
	public boolean addToGoggleTooltip(List<Component> tooltip, boolean isPlayerSneaking) {
		super.addToGoggleTooltip(tooltip, isPlayerSneaking);
		tooltip.add(Component.literal("    ").append(Component.translatable("airain.desench.lunettes.titre").withStyle(ChatFormatting.GRAY)));
		tooltip.add(Component.literal("     ").append(Component.translatable("airain.banc.huile", reservoir.getFluidAmount(), CAPACITE).withStyle(ChatFormatting.GOLD)));
		ItemStack a = inventaire.getStackInSlot(0);
		if (!a.isEmpty())
			tooltip.add(Component.literal("     ").append(a.getHoverName().copy().withStyle(ChatFormatting.WHITE))
				.append(Component.literal(" : " + enchantements(a).size()).withStyle(ChatFormatting.LIGHT_PURPLE))
				.append(Component.translatable("airain.desench.enchantements").withStyle(ChatFormatting.GRAY)));
		return true;
	}

	// ------------------------------------------------------------------ sauvegarde
	@Override
	protected void write(CompoundTag tag, HolderLookup.Provider registries, boolean clientPacket) {
		super.write(tag, registries, clientPacket);
		tag.put("Inventaire", inventaire.serializeNBT(registries));
		tag.put("Reservoir", reservoir.writeToNBT(registries, new CompoundTag()));
		tag.putFloat("Progres", progres);
		tag.putBoolean("Travaille", travaille);
		tag.putString("Choix", choix);
		tag.putInt("Niveau", niveauChoisi);
	}

	@Override
	protected void read(CompoundTag tag, HolderLookup.Provider registries, boolean clientPacket) {
		super.read(tag, registries, clientPacket);
		inventaire.deserializeNBT(registries, tag.getCompound("Inventaire"));
		reservoir.readFromNBT(registries, tag.getCompound("Reservoir"));
		progres = tag.getFloat("Progres");
		travaille = tag.getBoolean("Travaille");
		choix = tag.getString("Choix");
		niveauChoisi = tag.getInt("Niveau");
	}

	@Override
	public void invalidate() {
		super.invalidate();
		invalidateCapabilities();
	}

	@Override
	public void destroy() {
		super.destroy();
		ItemHelper.dropContents(level, worldPosition, inventaire);
	}
}
