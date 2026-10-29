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
	/** Encre runique : sert à purger les malédictions (une encre par malédiction). */
	public final ItemStackHandler encre;
	private float progres;
	private boolean purge;
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
		encre = new ItemStackHandler(1) {
			@Override
			protected void onContentsChanged(int slot) {
				setChanged();
				sendData();
			}
		};
		automatisation = new Automatisation();
	}

	public static boolean estEncre(ItemStack s) {
		return s.is(fr.chatmort.airain.AirainMod.ENCRE.get());
	}

	/** Première malédiction de l'objet, s'il en a. */
	public static Holder<Enchantment> malediction(ItemStack s) {
		for (var e : enchantements(s).entrySet())
			if (e.getKey().is(net.minecraft.tags.EnchantmentTags.CURSE)) return e.getKey();
		return null;
	}

	public boolean travaille() { return travaille; }
	public boolean enPurge() { return purge; }

	/** Avancement de l'opération en cours (0 à 1), pour le rendu et les lunettes. */
	public float avancement() {
		ItemStack a = inventaire.getStackInSlot(0);
		if (a.isEmpty()) return 0;
		float total = purge ? TRAVAIL : TRAVAIL * Math.max(1, niveauChoisi);
		return Math.min(1f, progres / total);
	}

	/** Position locale (devant = nord) → position dans le monde, selon l'orientation de la machine. */
	public net.minecraft.world.phys.Vec3 monde(double x, double y, double z) {
		double dx = x - 0.5, dz = z - 0.5, rx, rz;
		switch (getBlockState().getValue(DesenchanteurBlock.FACING)) {
			case EAST -> { rx = -dz; rz = dx; }
			case SOUTH -> { rx = -dx; rz = -dz; }
			case WEST -> { rx = dz; rz = -dx; }
			default -> { rx = dx; rz = dz; }
		}
		return new net.minecraft.world.phys.Vec3(worldPosition.getX() + 0.5 + rx, worldPosition.getY() + y, worldPosition.getZ() + 0.5 + rz);
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
			if (travaille) {
				var r = level.random;
				var objet = monde(0.33, 1.08, 0.3);
				if (purge) {                                  // la malédiction s'échappe en fumée sombre vers le cristal
					if (r.nextInt(2) == 0) level.addParticle(ParticleTypes.SMOKE, objet.x + r.nextGaussian() * 0.06, objet.y, objet.z + r.nextGaussian() * 0.06, 0, 0.04, 0);
					if (r.nextInt(4) == 0) level.addParticle(ParticleTypes.SOUL, objet.x, objet.y + 0.1, objet.z, 0, 0.03, 0);
				} else {                                      // des runes quittent l'objet et volent vers le livre
					var livre = monde(0.68, 1.1, 0.3);
					if (r.nextInt(2) == 0) level.addParticle(ParticleTypes.ENCHANT, livre.x, livre.y, livre.z,
						objet.x - livre.x + r.nextGaussian() * 0.05, 0.35 + r.nextDouble() * 0.2, objet.z - livre.z + r.nextGaussian() * 0.05);
					if (r.nextInt(3) == 0) level.addParticle(new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(0.62f, 0.32f, 0.9f), 0.6f),
						objet.x + r.nextGaussian() * 0.08, objet.y + r.nextDouble() * 0.2, objet.z + r.nextGaussian() * 0.08, 0, 0.02, 0);
				}
			}
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
		Holder<Enchantment> mal = a.isEmpty() ? null : malediction(a);
		if (mal != null && estEncre(encre.getStackInSlot(0)) && inventaire.getStackInSlot(2).isEmpty())
			return purger(a, mal);
		if (purge) { purge = false; progres = 0; }
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
		rayon(monde(0.5, 1.43, 11 / 16.0), monde(0.68, 1.06, 0.3), 0.62f, 0.32f, 0.9f);
		return true;
	}

	/**
	 * Purge : une malédiction disparaît par cycle, contre une encre runique et {@link #COUT_PAR_NIVEAU} mB d'huile.
	 * L'objet n'est pas détruit ; une fois purifié, il passe dans la case de sortie.
	 */
	private boolean purger(ItemStack a, Holder<Enchantment> mal) {
		if (!purge) { purge = true; progres = 0; choix = ""; }
		if (reservoir.getFluidAmount() < COUT_PAR_NIVEAU) return false;
		float vitesse = Math.abs(getSpeed());
		if (vitesse < 16 || isOverStressed()) return false;
		progres += BancEntretienBlockEntity.rythme(vitesse);
		if (progres < TRAVAIL) return true;
		progres = 0;
		ItemStack pur = a.copy();
		EnchantmentHelper.updateEnchantments(pur, m -> m.removeIf(h -> h.equals(mal)));
		encre.extractItem(0, 1, false);
		reservoir.drain(COUT_PAR_NIVEAU, IFluidHandler.FluidAction.EXECUTE);
		level.playSound(null, worldPosition, SoundEvents.BEACON_DEACTIVATE, SoundSource.BLOCKS, 0.7f, 1.4f);
		level.playSound(null, worldPosition, SoundEvents.SOUL_ESCAPE.value(), SoundSource.BLOCKS, 1f, 0.8f);
		rayon(monde(0.33, 1.06, 0.3), monde(0.5, 1.43, 11 / 16.0), 0.2f, 0.18f, 0.22f);
		if (malediction(pur) == null) {                         // purifié : il sort de la machine
			inventaire.setStackInSlot(0, ItemStack.EMPTY);
			inventaire.setStackInSlot(2, pur);
			purge = false;
		} else inventaire.setStackInSlot(0, pur);
		return true;
	}

	/** Trait de poussière colorée entre deux points (fin d'extraction ou de purge). */
	private void rayon(net.minecraft.world.phys.Vec3 de, net.minecraft.world.phys.Vec3 a, float r, float g, float b) {
		if (!(level instanceof net.minecraft.server.level.ServerLevel sl)) return;
		var poussiere = new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(r, g, b), 0.9f);
		for (int i = 0; i <= 12; i++) {
			var p = de.lerp(a, i / 12.0);
			sl.sendParticles(poussiere, p.x, p.y, p.z, 2, 0.01, 0.01, 0.01, 0);
		}
		sl.sendParticles(ParticleTypes.END_ROD, a.x, a.y, a.z, 6, 0.05, 0.05, 0.05, 0.02);
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
		if (estEncre(tenu)) {
			ItemStack r = encre.insertItem(0, tenu.copy(), false);
			if (r.getCount() == tenu.getCount()) return false;
			player.setItemInHand(hand, r);
			return true;
		}
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
		ItemStack e = encre.getStackInSlot(0);
		if (!e.isEmpty()) {
			player.getInventory().placeItemBackInInventory(e.copy());
			encre.setStackInSlot(0, ItemStack.EMPTY);
		}
	}

	private class Automatisation implements IItemHandler {
		@Override
		public int getSlots() {
			return 4;
		}

		@Override
		public ItemStack getStackInSlot(int slot) {
			return slot == 3 ? encre.getStackInSlot(0) : inventaire.getStackInSlot(slot);
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
			if (slot == 3)
				return estEncre(stack) ? encre.insertItem(0, stack, simulate) : stack;
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
			return slot == 0 ? desenchantable(stack) : slot == 1 ? stack.is(Items.BOOK) : slot == 3 && estEncre(stack);
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
		if (travaille) {
			Component op;
			if (purge) {
				Holder<Enchantment> m = malediction(a);
				op = Component.translatable("airain.desench.purge", m == null ? Component.literal("?") : m.value().description());
			} else {
				Holder<Enchantment> h = a.isEmpty() ? null : choisi(a);
				op = Component.translatable("airain.desench.extraction", h == null ? Component.literal("?") : Enchantment.getFullname(h, niveauChoisi));
			}
			tooltip.add(Component.literal("     ").append(op.copy().withStyle(ChatFormatting.LIGHT_PURPLE))
				.append(Component.literal(" · " + Math.round(avancement() * 100) + " %").withStyle(ChatFormatting.AQUA)));
		}
		ItemStack en = encre.getStackInSlot(0);
		tooltip.add(Component.literal("     ").append(Component.translatable("airain.desench.encre", en.getCount()).withStyle(ChatFormatting.DARK_PURPLE)));
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
		tag.put("Encre", encre.serializeNBT(registries));
		tag.putBoolean("Purge", purge);
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
		if (tag.contains("Encre")) encre.deserializeNBT(registries, tag.getCompound("Encre"));
		purge = tag.getBoolean("Purge");
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
		ItemHelper.dropContents(level, worldPosition, encre);
	}
}
