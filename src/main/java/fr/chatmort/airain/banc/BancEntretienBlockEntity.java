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
	/**
	 * Chaque niveau d'enchantement de l'objet allonge le travail de 25 % (l'enclume, elle, coûterait plus d'expérience).
	 * Exemple : pioche Efficacité V, Solidité III, Fortune III, Raccommodage = 12 niveaux, soit ×4.
	 */
	public static final float PAR_NIVEAU = 0.25f;
	public static final TagKey<Fluid> HUILES = TagKey.create(Registries.FLUID, ResourceLocation.fromNamespaceAndPath("airain", "huile_entretien"));
	public static final ResourceLocation BURETTE_ID = ResourceLocation.fromNamespaceAndPath("kubejs", "huile_machine");
	public static final ResourceLocation HUILE_ID = ResourceLocation.fromNamespaceAndPath("kubejs", "huile");

	public final ItemStackHandler inventaire;
	public final FluidTank reservoir;
	public final IItemHandler automatisation;
	/** Trois emplacements de modules : meule fine, démultiplicateur, graisseur (un exemplaire de chaque compte). */
	public final ItemStackHandler modules;
	private float progres;
	private boolean travaille;
	/** Affûtage : durée du bonus d'un objet qui sort du banc (10 min, 15 si le réservoir est aux trois quarts). */
	public static final long AFFUTAGE = 12000, AFFUTAGE_HUILE = 18000;

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
		modules = new ItemStackHandler(3) {
			@Override
			protected void onContentsChanged(int slot) {
				setChanged();
				sendData();
				if (level != null && !level.isClientSide && hasNetwork())        // le démultiplicateur change le couple demandé
					getOrCreateNetwork().updateStressFor(BancEntretienBlockEntity.this, calculateStressApplied());
			}

			@Override
			public int getSlotLimit(int slot) {
				return 1;
			}

			@Override
			public boolean isItemValid(int slot, ItemStack stack) {
				return Module.de(stack) != null;
			}
		};
		automatisation = new Automatisation();
	}

	// ------------------------------------------------------------------ modules
	public enum Module { MEULE_FINE, DEMULTIPLICATEUR, GRAISSEUR;
		public static Module de(ItemStack s) {
			if (s.is(fr.chatmort.airain.AirainMod.MEULE_FINE.get())) return MEULE_FINE;
			if (s.is(fr.chatmort.airain.AirainMod.DEMULTIPLICATEUR.get())) return DEMULTIPLICATEUR;
			if (s.is(fr.chatmort.airain.AirainMod.GRAISSEUR.get())) return GRAISSEUR;
			return null;
		}
	}

	public boolean a(Module m) {
		for (int i = 0; i < modules.getSlots(); i++)
			if (Module.de(modules.getStackInSlot(i)) == m) return true;
		return false;
	}

	/** Huile par unité de réparation : 30 % de moins avec la meule fine. */
	public int cout() {
		return a(Module.MEULE_FINE) ? COUT * 7 / 10 : COUT;
	}

	/** Le démultiplicateur va 60 % plus vite mais demande deux fois plus de couple. */
	private float facteur() {
		return a(Module.DEMULTIPLICATEUR) ? 1.6f : 1f;
	}

	@Override
	public float calculateStressApplied() {
		float impact = super.calculateStressApplied() * (a(Module.DEMULTIPLICATEUR) ? 2f : 1f);
		this.lastStressApplied = impact;
		return impact;
	}

	public boolean travaille() { return travaille; }

	/** Avancement de l'unité en cours (0 à 1). */
	public float avancement() {
		ItemStack a = inventaire.getStackInSlot(0);
		return a.isEmpty() ? 0 : Math.min(1f, progres / travailPour(a));
	}

	/** Secondes restantes pour l'unité en cours à la vitesse actuelle (-1 si à l'arrêt). */
	public int secondesRestantes() {
		ItemStack a = inventaire.getStackInSlot(0);
		float v = Math.abs(getSpeed());
		if (a.isEmpty() || v < 16) return -1;
		return Math.round((travailPour(a) - progres) / (rythme(v) * facteur()) / 20f);
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
	public static int niveauxEnchantements(ItemStack a) {
		int total = 0;
		for (var e : a.getEnchantments().entrySet())
			total += e.getIntValue();
		return total;
	}

	/** Points de travail pour une unité de réparation de cet objet. */
	public static float travailPour(ItemStack a) {
		return TRAVAIL * (1 + PAR_NIVEAU * niveauxEnchantements(a));
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
			if (travaille) etincelles();
			return;
		}
		if (a(Module.GRAISSEUR) && level.getGameTime() % 20 == 0) graisser();
		if (travaille && level.getGameTime() % 10 == 0) level.updateNeighbourForOutputSignal(worldPosition, getBlockState().getBlock());

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
		if (reservoir.getFluidAmount() < cout())
			return false;
		float vitesse = Math.abs(getSpeed());
		if (vitesse < 16 || isOverStressed())
			return false;

		progres += rythme(vitesse) * facteur();
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
		reservoir.drain(cout(), IFluidHandler.FluidAction.EXECUTE);
		level.playSound(null, worldPosition, SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 0.35f, 1.5f);
		if (!reparable(repare)) {
			affuter(repare);
			inventaire.setStackInSlot(0, repare);
			versSortie();
		}
		return true;
	}

	/** Un outil ou une arme qui sort du banc est fraîchement affûté (bonus temporaire, voir {@link Affutage}). */
	private void affuter(ItemStack s) {
		if (!Affutage.affutable(s) || level == null) return;
		long duree = reservoir.getFluidAmount() >= CAPACITE * 3 / 4 ? AFFUTAGE_HUILE : AFFUTAGE;
		Affutage.marquer(s, level.getGameTime() + duree);
	}

	/** Le graisseur aspire l'huile d'un réservoir voisin (250 mB par seconde). */
	private void graisser() {
		int place = CAPACITE - reservoir.getFluidAmount();
		if (place < 250) return;
		for (net.minecraft.core.Direction d : net.minecraft.core.Direction.values()) {
			IFluidHandler h = level.getCapability(net.neoforged.neoforge.capabilities.Capabilities.FluidHandler.BLOCK, worldPosition.relative(d), d.getOpposite());
			if (h == null) continue;
			for (int t = 0; t < h.getTanks(); t++) {
				FluidStack f = h.getFluidInTank(t);
				if (f.isEmpty() || !f.is(HUILES)) continue;
				FluidStack pris = h.drain(f.copyWithAmount(Math.min(250, place)), IFluidHandler.FluidAction.EXECUTE);
				if (!pris.isEmpty()) { reservoir.fill(pris, IFluidHandler.FluidAction.EXECUTE); return; }
			}
		}
	}

	/** Position locale (devant = nord) → monde. */
	private net.minecraft.world.phys.Vec3 monde(double x, double y, double z) {
		double dx = x - 0.5, dz = z - 0.5, rx, rz;
		switch (getBlockState().getValue(BancEntretienBlock.FACING)) {
			case EAST -> { rx = -dz; rz = dx; }
			case SOUTH -> { rx = -dx; rz = -dz; }
			case WEST -> { rx = dz; rz = -dx; }
			default -> { rx = dx; rz = dz; }
		}
		return new net.minecraft.world.phys.Vec3(worldPosition.getX() + 0.5 + rx, worldPosition.getY() + y, worldPosition.getZ() + 0.5 + rz);
	}

	/** Étincelles là où l'objet touche la meule ; fumée à pleine vitesse. */
	private void etincelles() {
		var r = level.random;
		var p = monde(0.5, 18.6 / 16, 7.4 / 16);
		var avant = monde(0.5, 18.6 / 16, 4.0 / 16).subtract(p);
		if (r.nextInt(2) == 0)
			level.addParticle(ParticleTypes.ELECTRIC_SPARK, p.x + r.nextGaussian() * 0.03, p.y, p.z + r.nextGaussian() * 0.03,
				avant.x * 0.6 + r.nextGaussian() * 0.04, 0.05 + r.nextDouble() * 0.06, avant.z * 0.6 + r.nextGaussian() * 0.04);
		if (r.nextInt(3) == 0)
			level.addParticle(new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(1f, 0.62f, 0.2f), 0.5f),
				p.x, p.y, p.z, 0, 0, 0);
		if (Math.abs(getSpeed()) >= 128 && r.nextInt(6) == 0) {
			var f = monde(0.5, 1.55, 11 / 16.0);
			level.addParticle(ParticleTypes.SMOKE, f.x + r.nextGaussian() * 0.05, f.y, f.z + r.nextGaussian() * 0.05, 0, 0.03, 0);
		}
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
				int secondes = secondesRestantes();
				tooltip.add(Component.literal("     ").append(Component.translatable("airain.banc.duree", secondes)
					.withStyle(ChatFormatting.GRAY)));
			}
		}
		for (Module m : Module.values())
			if (a(m)) tooltip.add(Component.literal("     ").append(Component.translatable("airain.banc.module." + m.name().toLowerCase())
				.withStyle(ChatFormatting.DARK_AQUA)));
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
		tag.put("Modules", modules.serializeNBT(registries));
	}

	@Override
	protected void read(CompoundTag tag, HolderLookup.Provider registries, boolean clientPacket) {
		super.read(tag, registries, clientPacket);
		inventaire.deserializeNBT(registries, tag.getCompound("Inventaire"));
		reservoir.readFromNBT(registries, tag.getCompound("Reservoir"));
		progres = tag.getFloat("Progres");
		travaille = tag.getBoolean("Travaille");
		if (tag.contains("Modules")) modules.deserializeNBT(registries, tag.getCompound("Modules"));
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
		ItemHelper.dropContents(level, worldPosition, modules);
	}
}
