package fr.chatmort.airain.fonderie;

import com.simibubi.create.api.equipment.goggles.IHaveGoggleInformation;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.content.processing.burner.BlazeBurnerBlock;
import com.simibubi.create.content.processing.burner.BlazeBurnerBlock.HeatLevel;
import fr.chatmort.airain.fonderie.FourneauBlocs.Partie;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.List;

/**
 * Le haut-fourneau impérial, porté par son trou de coulée.
 *
 * Structure (vue depuis le trou de coulée, qui est au milieu de la face avant, en bas) :
 *  - 3 × 3 au sol, 4 de haut, en briques réfractaires ;
 *  - au centre du sol : une grille d'airain, avec un brûleur à blaze de Create juste en dessous ;
 *  - au centre, deuxième et troisième rangs : vide (la cuve) ;
 *  - au centre du sommet : le gueulard, où l'on verse la charge ;
 *  - une tuyère au milieu d'un côté (rang 2 ou 3), avec un ventilateur de Create qui souffle dedans.
 *
 * Fonctionnement : chaleur du brûleur (chauffé : refonte ; surchauffé : refonte et alliage) et vitesse du ventilateur
 * (elle règle le débit). L'airain en fusion sort par le trou de coulée (tuyaux), le laitier aussi (entonnoir).
 */
public class HautFourneauBlockEntity extends BlockEntity implements IHaveGoggleInformation {
	public static final int CUVE = 4000, LINGOT = 90, TRAVAIL = 400;
	private static final TagKey<Item> CUIVRE = TagKey.create(net.minecraft.core.registries.Registries.ITEM, ResourceLocation.parse("c:ingots/copper"));
	private static final TagKey<Item> ZINC = TagKey.create(net.minecraft.core.registries.Registries.ITEM, ResourceLocation.parse("c:ingots/zinc"));

	/** La charge versée par le gueulard (4 emplacements). */
	public final ItemStackHandler charge = new ItemStackHandler(4) { @Override protected void onContentsChanged(int s) { setChanged(); } };
	/** Le laitier, à récupérer au trou de coulée. */
	public final ItemStackHandler laitier = new ItemStackHandler(1) { @Override protected void onContentsChanged(int s) { setChanged(); } };
	/** L'airain en fusion. */
	public final FluidTank cuve = new FluidTank(CUVE, f -> f.getFluid().isSame(MetalAirain.SOURCE.get())) {
		@Override protected void onContentsChanged() { setChanged(); change = true; }
	};

	private boolean forme, change;
	private HeatLevel chaleur = HeatLevel.NONE;
	private int air, progres, montrer;
	private BlockPos tuyere;
	private final List<BlockPos> manquants = new ArrayList<>();
	private final List<String> raisons = new ArrayList<>();

	public HautFourneauBlockEntity(BlockPos p, BlockState s) { super(Fourneau.BE.get(), p, s); }

	// ------------------------------------------------------------------ géométrie
	private Direction avant() { return getBlockState().getValue(FourneauBlocs.FACING); }
	/** Position locale : lx de -1 à 1 (gauche → droite vu de face), ly de 0 à 3, lz de 0 (avant) à 2 (arrière). */
	private BlockPos local(int lx, int ly, int lz) {
		Direction a = avant();
		return worldPosition.relative(a.getCounterClockWise(), lx).above(ly).relative(a.getOpposite(), lz);
	}
	public BlockPos centre(int ly) { return local(0, ly, 1); }

	// ------------------------------------------------------------------ vérification de la structure
	private boolean verifier() {
		manquants.clear(); raisons.clear(); tuyere = null;
		int tuyeres = 0;
		for (int ly = 0; ly < 4; ly++)
			for (int lx = -1; lx <= 1; lx++)
				for (int lz = 0; lz <= 2; lz++) {
					if (lx == 0 && lz == 0 && ly == 0) continue;                   // le trou de coulée lui-même
					BlockPos p = local(lx, ly, lz);
					BlockState s = level.getBlockState(p);
					if (lx == 0 && lz == 1) {                                       // la colonne centrale
						if (ly == 0 && !s.is(net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.BLOCK, ResourceLocation.parse("airain:airain_grates")))) manque(p, "grate");
						if ((ly == 1 || ly == 2) && !s.isAir()) manque(p, "hollow");
						if (ly == 3 && !s.is(Fourneau.GUEULARD.get())) manque(p, "hopper");
						continue;
					}
					boolean milieu = (lx == 0) != (lz == 1) && !(lx == 0 && lz == 0);   // milieu d'un côté (pas l'avant)
					if (s.is(Fourneau.TUYERE.get()) && milieu && (ly == 1 || ly == 2)) { tuyeres++; tuyere = p; continue; }
					if (!s.is(Fourneau.BRIQUES.get())) manque(p, "bricks");
				}
		if (tuyeres == 0) raisons.add("tuyere");
		if (tuyeres > 1) raisons.add("tuyeres");
		return manquants.isEmpty() && tuyeres == 1;
	}
	private void manque(BlockPos p, String quoi) { manquants.add(p); if (!raisons.contains(quoi)) raisons.add(quoi); }

	/** Habillage des briques une fois le fourneau monté (ou rendu nu s'il est démonté). */
	private void habiller(boolean monte) {
		Direction a = avant();
		for (int ly = 0; ly < 4; ly++)
			for (int lx = -1; lx <= 1; lx++)
				for (int lz = 0; lz <= 2; lz++) {
					BlockPos p = local(lx, ly, lz);
					BlockState s = level.getBlockState(p);
					if (s.is(Fourneau.BRIQUES.get())) {
						boolean coin = lx != 0 && lz != 1;
						Partie part = Partie.AUCUNE; Direction d = Direction.NORTH;
						if (monte) {
							part = ly == 0 ? (coin ? Partie.SOCLE_COIN : Partie.SOCLE) : ly == 3 ? (coin ? Partie.COURONNE_COIN : Partie.COURONNE) : (coin ? Partie.CORPS_COIN : Partie.CORPS);
							if (ly == 2 && lx == 0 && lz == 0) { part = Partie.BLASON; d = a; }
							if (coin) d = orientationCoin(lx, lz);
						}
						BlockState n = s.setValue(FourneauBlocs.PARTIE, part).setValue(FourneauBlocs.FACING, d);
						if (n != s) level.setBlock(p, n, Block.UPDATE_CLIENTS);
					}
					if (monte && s.is(Fourneau.TUYERE.get())) {                // la buse se tourne vers l'extérieur
						Direction dehors = lz == 1 ? (lx > 0 ? a.getCounterClockWise() : a.getClockWise()) : a.getOpposite();   // lx > 0 : côté anti-horaire (voir local)
						if (s.getValue(FourneauBlocs.FACING) != dehors) level.setBlock(p, s.setValue(FourneauBlocs.FACING, dehors), Block.UPDATE_CLIENTS);
					}
				}
	}
	/** Les modèles de coin sont dessinés pour le coin nord-ouest, puis tournés : on choisit la rotation selon le coin réel. */
	private Direction orientationCoin(int lx, int lz) {
		Direction a = avant();
		Direction cote = lx > 0 ? a.getCounterClockWise() : a.getClockWise();     // face latérale extérieure (lx > 0 : côté anti-horaire)
		Direction fond = lz == 0 ? a : a.getOpposite();                           // face avant ou arrière
		boolean n = cote == Direction.NORTH || fond == Direction.NORTH, s = cote == Direction.SOUTH || fond == Direction.SOUTH;
		boolean o = cote == Direction.WEST || fond == Direction.WEST;
		if (n) return o ? Direction.NORTH : Direction.EAST;   // NO : 0°, NE : 90°
		if (s) return o ? Direction.WEST : Direction.SOUTH;   // SO : 270°, SE : 180°
		return Direction.NORTH;
	}

	// ------------------------------------------------------------------ fonctionnement
	void tickServeur() {
		if (level == null) return;
		if (level.getGameTime() % 20 == 0) {
			boolean f = verifier();
			if (f != forme) { forme = f; habiller(f); change = true; if (!f) allumer(false); }
			chaleur = forme ? BlazeBurnerBlock.getHeatLevelOf(level.getBlockState(centre(0).below())) : HeatLevel.NONE;
			air = 0;
			if (forme && tuyere != null) {
				BlockPos ventilo = tuyere.relative(level.getBlockState(tuyere).getValue(FourneauBlocs.FACING));
				if (level.getBlockEntity(ventilo) instanceof KineticBlockEntity k
					&& BuiltInRegistries.BLOCK.getKey(level.getBlockState(ventilo).getBlock()).toString().equals("create:encased_fan"))
					air = (int) Math.abs(k.getSpeed());
			}
		}
		if (montrer > 0) { montrer--; if (montrer % 10 == 0) montrerManquants(); }
		boolean marche = false;
		if (forme && air > 0 && chaleur.isAtLeast(HeatLevel.KINDLED)) {
			Recette r = recette();
			if (r != null && cuve.getSpace() >= r.mb) {
				marche = true;
				progres += Math.max(1, Math.min(8, air / 32));            // 32 tr/min : 1 par tick ; 256 tr/min : 8 par tick
				if (progres >= TRAVAIL) { progres = 0; produire(r); }
			}
		}
		if (!marche && progres > 0 && level.getGameTime() % 4 == 0) progres = Math.max(0, progres - 1);
		allumer(marche);
		if (marche && level.random.nextInt(60) == 0)
			level.playSound(null, worldPosition, SoundEvents.BLASTFURNACE_FIRE_CRACKLE, SoundSource.BLOCKS, 1f, 0.7f);
		if (change && level.getGameTime() % 10 == 0) { change = false; level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS); }
	}

	private void allumer(boolean oui) {
		BlockState s = getBlockState();
		if (s.getValue(FourneauBlocs.LIT) != oui) level.setBlock(worldPosition, s.setValue(FourneauBlocs.LIT, oui), Block.UPDATE_ALL);
		BlockPos g = centre(3); BlockState gs = level.getBlockState(g);
		if (gs.is(Fourneau.GUEULARD.get()) && gs.getValue(FourneauBlocs.LIT) != oui) level.setBlock(g, gs.setValue(FourneauBlocs.LIT, oui), Block.UPDATE_ALL);
	}

	void tickClient() {
		if (level == null || !getBlockState().getValue(FourneauBlocs.LIT)) return;
		var r = level.random;
		BlockPos g = centre(3);
		if (r.nextInt(3) == 0) level.addParticle(ParticleTypes.LARGE_SMOKE, g.getX() + 0.3 + r.nextDouble() * 0.4, g.getY() + 1.4, g.getZ() + 0.3 + r.nextDouble() * 0.4, 0, 0.07, 0);
		if (r.nextInt(4) == 0) level.addParticle(ParticleTypes.LAVA, g.getX() + 0.5, g.getY() + 1.2, g.getZ() + 0.5, 0, 0, 0);
		if (r.nextInt(6) == 0) {                                             // gouttes de métal dans la rigole
			Direction a = avant();
			double x = worldPosition.getX() + 0.5 + a.getStepX() * 0.75, z = worldPosition.getZ() + 0.5 + a.getStepZ() * 0.75;
			level.addParticle(ParticleTypes.DRIPPING_LAVA, x, worldPosition.getY() + 0.25, z, 0, 0, 0);
		}
	}

	// ------------------------------------------------------------------ recettes
	/** Refonte : le butin des automates redevient de l'airain. Alliage : cuivre + zinc + fondant, avec un brûleur surchauffé. */
	private record Recette(int cuivre, int zinc, int fondant, int ferraille, int rouages, int mb, boolean laitier) {}
	private static final Recette ALLIAGE = new Recette(3, 1, 1, 0, 0, 4 * LINGOT, true);
	private static final Recette REFONTE_FERRAILLE = new Recette(0, 0, 0, 6, 0, LINGOT, true);
	private static final Recette REFONTE_ROUAGES = new Recette(0, 0, 0, 0, 2, LINGOT, false);

	private static boolean estFerraille(ItemStack s) { return id(s).equals("kubejs:ferraille"); }
	private static boolean estRouage(ItemStack s) { return id(s).equals("kubejs:rouage_brise"); }
	private static boolean estCuivre(ItemStack s) { return s.is(CUIVRE) || id(s).equals("create:crushed_raw_copper"); }
	private static boolean estZinc(ItemStack s) { return s.is(ZINC) || id(s).equals("create:crushed_raw_zinc"); }
	private static boolean estFondant(ItemStack s) { return id(s).equals("minecraft:calcite") || id(s).equals("create:cinder_flour") || s.is(MetalAirain.LAITIER.get()); }
	private static String id(ItemStack s) { return BuiltInRegistries.ITEM.getKey(s.getItem()).toString(); }
	private int compter(java.util.function.Predicate<ItemStack> p) {
		int n = 0;
		for (int i = 0; i < charge.getSlots(); i++) if (p.test(charge.getStackInSlot(i))) n += charge.getStackInSlot(i).getCount();
		return n;
	}
	private Recette recette() {
		if (chaleur == HeatLevel.SEETHING && compter(HautFourneauBlockEntity::estCuivre) >= 3 && compter(HautFourneauBlockEntity::estZinc) >= 1
			&& compter(HautFourneauBlockEntity::estFondant) >= 1) return ALLIAGE;
		if (compter(HautFourneauBlockEntity::estFerraille) >= 6) return REFONTE_FERRAILLE;
		if (compter(HautFourneauBlockEntity::estRouage) >= 2) return REFONTE_ROUAGES;
		return null;
	}
	private void prendre(java.util.function.Predicate<ItemStack> p, int n) {
		for (int i = 0; i < charge.getSlots() && n > 0; i++) {
			ItemStack s = charge.getStackInSlot(i);
			if (p.test(s)) { int k = Math.min(n, s.getCount()); charge.extractItem(i, k, false); n -= k; }
		}
	}
	private void produire(Recette r) {
		if (r == ALLIAGE) {
			// le fondant est pris en dernier : s'il manque, on ne consomme rien
			prendre(HautFourneauBlockEntity::estCuivre, 3); prendre(HautFourneauBlockEntity::estZinc, 1); prendre(HautFourneauBlockEntity::estFondant, 1);
		} else if (r == REFONTE_FERRAILLE) prendre(HautFourneauBlockEntity::estFerraille, 6);
		else prendre(HautFourneauBlockEntity::estRouage, 2);
		cuve.fill(new FluidStack(MetalAirain.SOURCE.get(), r.mb), IFluidHandler.FluidAction.EXECUTE);
		if (r.laitier && level.random.nextFloat() < 0.6f) laitier.insertItem(0, new ItemStack(MetalAirain.LAITIER.get()), false);
		level.playSound(null, worldPosition, SoundEvents.LAVA_POP, SoundSource.BLOCKS, 1f, 0.8f);
	}

	// ------------------------------------------------------------------ interactions
	/** Clic droit à main nue sur le trou de coulée : état du fourneau, ou ce qui manque (montré en particules). */
	void clic(Player j) {
		boolean f = verifier();
		if (!f) {
			j.displayClientMessage(Component.translatable("airain.fourneau.incomplet").withStyle(ChatFormatting.GOLD), false);
			for (String r : raisons) j.displayClientMessage(Component.literal(" • ").append(Component.translatable("airain.fourneau.manque." + r)), false);
			montrer = 120;
			return;
		}
		j.displayClientMessage(etat(), true);
	}
	private Component etat() {
		String c = chaleur == HeatLevel.SEETHING ? "surchauffe" : chaleur.isAtLeast(HeatLevel.KINDLED) ? "chaud" : "froid";
		return Component.translatable("airain.fourneau.etat", Component.translatable("airain.fourneau.chaleur." + c), air, cuve.getFluidAmount() / LINGOT);
	}
	private void montrerManquants() {
		if (!(level instanceof ServerLevel sl)) return;
		var poussiere = new DustParticleOptions(new Vector3f(1f, 0.35f, 0.1f), 1.2f);
		for (BlockPos p : manquants) sl.sendParticles(poussiere, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0);
	}
	/** Le trou de coulée est cassé : les briques redeviennent nues, le métal et la charge tombent. */
	void demonter() {
		if (level == null || level.isClientSide) return;
		if (forme) habiller(false);
		for (int i = 0; i < charge.getSlots(); i++) Block.popResource(level, worldPosition, charge.getStackInSlot(i));
		Block.popResource(level, worldPosition, laitier.getStackInSlot(0));
		BlockPos g = centre(3); BlockState gs = level.getBlockState(g);
		if (gs.is(Fourneau.GUEULARD.get()) && gs.getValue(FourneauBlocs.LIT)) level.setBlock(g, gs.setValue(FourneauBlocs.LIT, false), Block.UPDATE_ALL);
	}
	public boolean forme() { return forme; }

	// ------------------------------------------------------------------ accès pour les tuyaux, entonnoirs et lunettes
	/** Ce que voient les tuyaux au trou de coulée : on peut seulement vider la cuve. */
	public final IFluidHandler sortie = new IFluidHandler() {
		@Override public int getTanks() { return 1; }
		@Override public FluidStack getFluidInTank(int t) { return cuve.getFluid(); }
		@Override public int getTankCapacity(int t) { return CUVE; }
		@Override public boolean isFluidValid(int t, FluidStack s) { return false; }
		@Override public int fill(FluidStack s, FluidAction a) { return 0; }
		@Override public FluidStack drain(FluidStack s, FluidAction a) { return cuve.drain(s, a); }
		@Override public FluidStack drain(int n, FluidAction a) { return cuve.drain(n, a); }
	};
	/** Ce que voient les entonnoirs au trou de coulée : le laitier, à sortir. */
	public final IItemHandler sortieLaitier = new IItemHandler() {
		@Override public int getSlots() { return 1; }
		@Override public ItemStack getStackInSlot(int s) { return laitier.getStackInSlot(0); }
		@Override public ItemStack insertItem(int s, ItemStack st, boolean sim) { return st; }
		@Override public ItemStack extractItem(int s, int n, boolean sim) { return laitier.extractItem(0, n, sim); }
		@Override public int getSlotLimit(int s) { return 64; }
		@Override public boolean isItemValid(int s, ItemStack st) { return false; }
	};
	/** Ce que voient les entonnoirs et goulottes au gueulard : on peut seulement verser la charge. */
	public final IItemHandler entree = new IItemHandler() {
		@Override public int getSlots() { return charge.getSlots(); }
		@Override public ItemStack getStackInSlot(int s) { return charge.getStackInSlot(s); }
		@Override public ItemStack insertItem(int s, ItemStack st, boolean sim) { return accepte(st) ? charge.insertItem(s, st, sim) : st; }
		@Override public ItemStack extractItem(int s, int n, boolean sim) { return ItemStack.EMPTY; }
		@Override public int getSlotLimit(int s) { return 64; }
		@Override public boolean isItemValid(int s, ItemStack st) { return accepte(st); }
	};
	private static boolean accepte(ItemStack s) { return estCuivre(s) || estZinc(s) || estFondant(s) || estFerraille(s) || estRouage(s); }

	/** Le trou de coulée dont dépend un gueulard (null si aucun fourneau monté autour). */
	public static HautFourneauBlockEntity depuisGueulard(net.minecraft.world.level.Level l, BlockPos gueulard) {
		for (Direction d : Direction.Plane.HORIZONTAL) {
			BlockPos p = gueulard.below(3).relative(d);
			BlockState s = l.getBlockState(p);
			if (s.is(Fourneau.TROU.get()) && s.getValue(FourneauBlocs.FACING) == d && l.getBlockEntity(p) instanceof HautFourneauBlockEntity be) return be;
		}
		return null;
	}

	@Override
	public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
		t.add(Component.literal("    ").append(Component.translatable("block.airain.blast_furnace_taphole")).withStyle(ChatFormatting.GOLD));
		if (!forme) { t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.incomplet")).withStyle(ChatFormatting.RED)); return true; }
		String c = chaleur == HeatLevel.SEETHING ? "surchauffe" : chaleur.isAtLeast(HeatLevel.KINDLED) ? "chaud" : "froid";
		t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.chaleur", Component.translatable("airain.fourneau.chaleur." + c))).withStyle(ChatFormatting.GRAY));
		t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.air", air)).withStyle(ChatFormatting.GRAY));
		t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.cuve", cuve.getFluidAmount(), CUVE)).withStyle(ChatFormatting.GRAY));
		if (progres > 0) t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.progres", progres * 100 / TRAVAIL)).withStyle(ChatFormatting.DARK_GRAY));
		return true;
	}

	// ------------------------------------------------------------------ sauvegarde et synchronisation (pour les lunettes)
	@Override
	protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) {
		super.saveAdditional(t, r);
		t.put("charge", charge.serializeNBT(r)); t.put("laitier", laitier.serializeNBT(r)); t.put("cuve", cuve.writeToNBT(r, new CompoundTag()));
		t.putInt("progres", progres); t.putBoolean("forme", forme); t.putInt("air", air); t.putString("chaleur", chaleur.getSerializedName());
	}
	@Override
	protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) {
		super.loadAdditional(t, r);
		charge.deserializeNBT(r, t.getCompound("charge")); laitier.deserializeNBT(r, t.getCompound("laitier")); cuve.readFromNBT(r, t.getCompound("cuve"));
		progres = t.getInt("progres"); forme = t.getBoolean("forme"); air = t.getInt("air");
		for (HeatLevel h : HeatLevel.values()) if (h.getSerializedName().equals(t.getString("chaleur"))) chaleur = h;
	}
	@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
	@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
}
