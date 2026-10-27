package fr.chatmort.airain.banc;

import java.util.List;

import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.foundation.item.ItemHelper;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
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
 * Répare comme une enclume, sans expérience :
 *  - chaque unité de matériau de réparation rend 25 % de la durabilité ;
 *  - deux objets identiques : durabilités additionnées, plus 12 % de bonus.
 * Chaque unité (ou fusion) coûte {@link #COUT} mB d'huile. Le travail avance avec la vitesse de rotation.
 * Cases : 0 = objet abîmé, 1 = matériau ou second objet, 2 = objet réparé.
 */
public class BancEntretienBlockEntity extends KineticBlockEntity {

	public static final int CAPACITE = 8000;
	public static final int COUT = 1000;
	public static final int BURETTE = 500;
	/**
	 * Travail par unité de réparation (25 %), en « points ». Chaque tick ajoute (vitesse / 16) / pénalité.
	 * Durée d'une réparation complète (4 unités) : 2,5 s à 256 tr/min, 7,5 s à 128, 20 s à 64, 50 s à 32, 2 min à 16.
	 */
	public static final float TRAVAIL = 200f;
	public static final TagKey<Fluid> HUILES = TagKey.create(Registries.FLUID, ResourceLocation.fromNamespaceAndPath("airain", "huile_entretien"));
	public static final ResourceLocation BURETTE_ID = ResourceLocation.fromNamespaceAndPath("kubejs", "huile_machine");
	public static final ResourceLocation HUILE_ID = ResourceLocation.fromNamespaceAndPath("kubejs", "huile");

	public final ItemStackHandler inventaire;
	public final FluidTank reservoir;
	public final IItemHandler automatisation;
	private float progres;
	private boolean travaille;

	public BancEntretienBlockEntity(BlockPos pos, BlockState state) {
		this(fr.chatmort.airain.AirainMod.BANC_BE.get(), pos, state);
	}

	public BancEntretienBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
		super(type, pos, state);
		inventaire = new ItemStackHandler(3) {
			@Override
			protected void onContentsChanged(int slot) {
				setChanged();
				sendData();
			}
		};
		reservoir = new FluidTank(CAPACITE, f -> f.is(HUILES)) {
			@Override
			protected void onContentsChanged() {
				setChanged();
				sendData();
			}
		};
		automatisation = new Automatisation();
	}

	// ------------------------------------------------------------------ règles
	public static boolean reparable(ItemStack a) {
		return !a.isEmpty() && a.isDamageableItem() && a.isDamaged();
	}

	public static boolean accepteEnSecond(ItemStack a, ItemStack b) {
		if (a.isEmpty() || b.isEmpty())
			return false;
		if (b.is(a.getItem()) && b.isDamageableItem())
			return true;
		return a.getItem().isValidRepairItem(a, b);
	}

	// ------------------------------------------------------------------ travail
	/** Points de travail pour une unité de réparation de cet objet. */
	public static float travailPour(ItemStack a) {
		return TRAVAIL;
	}

	/** Points de travail gagnés par tick à cette vitesse. */
	public static float rythme(float vitesse) {
		return vitesse / 16f / penalite(vitesse);
	}

	@Override
	public void tick() {
		super.tick();
		if (level == null)
			return;

		if (level.isClientSide) {
			if (travaille && level.random.nextInt(3) == 0)
				level.addParticle(ParticleTypes.CRIT, worldPosition.getX() + 0.3 + level.random.nextDouble() * 0.4,
					worldPosition.getY() + 1.05, worldPosition.getZ() + 0.3 + level.random.nextDouble() * 0.4, 0, 0.05, 0);
			return;
		}

		boolean actif = etape();
		if (actif != travaille) {
			travaille = actif;
			sendData();
		}
	}

	/** Une étape de travail ; renvoie vrai si le banc est en train de réparer. */
	private boolean etape() {
		ItemStack a = inventaire.getStackInSlot(0);
		if (a.isEmpty()) {
			progres = 0;
			return false;
		}
		if (!reparable(a)) {
			versSortie();
			return false;
		}
		ItemStack b = inventaire.getStackInSlot(1);
		if (!accepteEnSecond(a, b))
			return false;
		if (reservoir.getFluidAmount() < COUT)
			return false;
		float vitesse = Math.abs(getSpeed());
		if (vitesse < 16 || isOverStressed())
			return false;

		progres += rythme(vitesse);
		if (progres < travailPour(a))
			return true;
		progres = 0;

		ItemStack repare = a.copy();
		int max = repare.getMaxDamage();
		if (b.is(a.getItem()) && b.isDamageableItem()) {
			int reste = (max - a.getDamageValue()) + (max - b.getDamageValue()) + max * 12 / 100;
			repare.setDamageValue(Math.max(0, max - reste));
		} else {
			repare.setDamageValue(Math.max(0, a.getDamageValue() - max / 4));
		}
		inventaire.extractItem(1, 1, false);
		inventaire.setStackInSlot(0, repare);
		reservoir.drain(COUT, IFluidHandler.FluidAction.EXECUTE);
		level.playSound(null, worldPosition, SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 0.35f, 1.5f);
		if (!reparable(repare))
			versSortie();
		return true;
	}

	private void versSortie() {
		if (!inventaire.getStackInSlot(2).isEmpty())
			return;
		inventaire.setStackInSlot(2, inventaire.getStackInSlot(0).copy());
		inventaire.setStackInSlot(0, ItemStack.EMPTY);
		progres = 0;
	}

	/**
	 * Pénalité de lenteur, pour compenser l'absence de coût en expérience :
	 * ×1 à 256 tr/min, ×1,5 à 128, ×2 à 64, ×2,5 à 32, ×3 à 16 (chaque division par deux de la vitesse ajoute 0,5).
	 * Une réparation complète (4 unités) prend ainsi 2,5 s à 256 tr/min et 2 min à 16 tr/min.
	 */
	public static float penalite(float vitesse) {
		float v = Math.max(16f, Math.min(256f, vitesse));
		return 1f + 0.5f * (float) (Math.log(256f / v) / Math.log(2));
	}

	// ------------------------------------------------------------------ interactions à la main
	public boolean utiliserObjet(Player player, InteractionHand hand, ItemStack tenu) {
		// Burette d'huile (objet de KubeJS)
		if (BURETTE_ID.equals(BuiltInRegistries.ITEM.getKey(tenu.getItem()))) {
			Fluid huile = BuiltInRegistries.FLUID.get(HUILE_ID);
			if (huile == Fluids.EMPTY)
				return false;
			if (reservoir.fill(new FluidStack(huile, BURETTE), IFluidHandler.FluidAction.SIMULATE) < BURETTE) {
				player.displayClientMessage(Component.translatable("airain.banc.plein").withStyle(ChatFormatting.GRAY), true);
				return true;
			}
			reservoir.fill(new FluidStack(huile, BURETTE), IFluidHandler.FluidAction.EXECUTE);
			if (!player.isCreative())
				tenu.shrink(1);
			player.displayClientMessage(Component.translatable("airain.banc.huile", reservoir.getFluidAmount(), CAPACITE)
				.withStyle(ChatFormatting.GOLD), true);
			return true;
		}
		// Seau ou autre contenant de fluide
		if (FluidUtil.getFluidHandler(tenu).isPresent())
			return FluidUtil.interactWithFluidHandler(player, hand, reservoir);

		// Objet abîmé, puis matériau
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
		if (player.isShiftKeyDown())
			player.displayClientMessage(Component.translatable("airain.banc.huile", reservoir.getFluidAmount(), CAPACITE)
				.withStyle(ChatFormatting.GOLD), true);
	}

	// ------------------------------------------------------------------ automatisation (entonnoirs, tapis, trémies)
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
				if (!inventaire.getStackInSlot(0).isEmpty() || !reparable(stack))
					return stack;
				return inventaire.insertItem(0, stack.copyWithCount(1), simulate).isEmpty()
					? stack.copyWithCount(stack.getCount() - 1) : stack;
			}
			if (slot == 1) {
				if (!accepteEnSecond(inventaire.getStackInSlot(0), stack))
					return stack;
				return inventaire.insertItem(1, stack, simulate);
			}
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
			return slot == 0 ? reparable(stack) : slot == 1 && accepteEnSecond(inventaire.getStackInSlot(0), stack);
		}
	}

	// ------------------------------------------------------------------ lunettes d'ingénieur
	@Override
	public boolean addToGoggleTooltip(List<Component> tooltip, boolean isPlayerSneaking) {
		super.addToGoggleTooltip(tooltip, isPlayerSneaking);
		tooltip.add(Component.literal("    ").append(Component.translatable("airain.banc.lunettes.titre").withStyle(ChatFormatting.GRAY)));
		tooltip.add(Component.literal("     ").append(Component.translatable("airain.banc.huile", reservoir.getFluidAmount(), CAPACITE)
			.withStyle(ChatFormatting.GOLD)));
		ItemStack a = inventaire.getStackInSlot(0);
		if (!a.isEmpty() && a.isDamageableItem()) {
			int pct = 100 - a.getDamageValue() * 100 / Math.max(1, a.getMaxDamage());
			tooltip.add(Component.literal("     ").append(a.getHoverName().copy().withStyle(ChatFormatting.WHITE))
				.append(Component.literal(" : " + pct + " %").withStyle(ChatFormatting.AQUA)));
			float vitesse = Math.abs(getSpeed());
			if (vitesse >= 16) {
				int secondes = Math.round(travailPour(a) / rythme(vitesse) / 20f);
				tooltip.add(Component.literal("     ").append(Component.translatable("airain.banc.duree", secondes)
					.withStyle(ChatFormatting.GRAY)));
			}
		}
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
	}

	@Override
	protected void read(CompoundTag tag, HolderLookup.Provider registries, boolean clientPacket) {
		super.read(tag, registries, clientPacket);
		inventaire.deserializeNBT(registries, tag.getCompound("Inventaire"));
		reservoir.readFromNBT(registries, tag.getCompound("Reservoir"));
		progres = tag.getFloat("Progres");
		travaille = tag.getBoolean("Travaille");
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
