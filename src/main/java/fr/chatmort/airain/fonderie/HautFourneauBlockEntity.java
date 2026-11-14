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

	/** La charge versée par le gueulard : un emplacement par ingrédient (cuivre, zinc, fondant, ferraille, rouages brisés),
	 * pour qu'un ingrédient en trop ne prenne jamais la place d'un autre (1.56.1). */
	public static final int PLACES = 5;
	public final ItemStackHandler charge = new ItemStackHandler(PLACES) {
		@Override protected void onContentsChanged(int s) { setChanged(); }
		@Override public boolean isItemValid(int s, ItemStack st) { return place(st) == s; }
	};
	/** L'emplacement de cet ingrédient, ou -1 s'il n'entre pas dans le fourneau. */
	static int place(ItemStack s) {
		if (s.isEmpty()) return -1;
		if (estCuivre(s)) return 0;
		if (estZinc(s)) return 1;
		if (estFondant(s)) return 2;
		if (estFerraille(s)) return 3;
		if (estRouage(s)) return 4;
		return -1;
	}
	/** Charge d'une ancienne sauvegarde qui ne tient pas dans les nouveaux emplacements : rendue au prochain tick. */
	private final List<ItemStack> surplus = new ArrayList<>();
	/** Le laitier, à récupérer au trou de coulée. */
	public final ItemStackHandler laitier = new ItemStackHandler(1) { @Override protected void onContentsChanged(int s) { setChanged(); } };
	/** L'airain en fusion. */
	public final FluidTank cuve = new FluidTank(CUVE, f -> f.getFluid().isSame(MetalAirain.SOURCE.get())) {
		@Override protected void onContentsChanged() { setChanged(); change = true; }
	};

	private boolean forme, change;
	private HeatLevel chaleur = HeatLevel.NONE;
	private int air, souffle, progres;
	private final List<BlockPos> manquants = new ArrayList<>();
	private final List<String> raisons = new ArrayList<>();

	public HautFourneauBlockEntity(BlockPos p, BlockState s) { super(Fourneau.BE.get(), p, s); }

	// ------------------------------------------------------------------ géométrie (1.55 : creuset 5 × 5 à coins coupés, cuve 3 × 3, gueulard)
	/** Ce qu'attend une case du plan. TUYERE : une des trois places de tuyère (une brique y est acceptée aussi). */
	public enum Attendu { TROU, BRIQUE, TUYERE, GRILLE, VIDE, GUEULARD }
	/** Une case du plan, en coordonnées locales (lx -2..2 gauche → droite vu de face, ly 0..4, lz 0 avant → 4 arrière). */
	public record Case(int lx, int ly, int lz, Attendu quoi) {}
	public static final List<Case> PLAN = new ArrayList<>();
	/** Emprise d'une couche : le creuset (couches 0 et 1) ou la cuve (couches 2 à 4). */
	public static boolean dansEmprise(int lx, int ly, int lz) {
		if (ly <= 1) return Math.abs(lx) <= 2 && lz >= 0 && lz <= 4 && !(Math.abs(lx) == 2 && (lz == 0 || lz == 4));
		return Math.abs(lx) <= 1 && lz >= 1 && lz <= 3;
	}
	static {
		for (int ly = 0; ly < 5; ly++)
			for (int lx = -2; lx <= 2; lx++)
				for (int lz = 0; lz <= 4; lz++) {
					if (!dansEmprise(lx, ly, lz)) continue;
					boolean interieur = Math.abs(lx) <= 1 && lz >= 1 && lz <= 3;
					Attendu a = Attendu.BRIQUE;
					if (ly == 0 && lx == 0 && lz == 0) a = Attendu.TROU;
					else if (ly == 0 && lx == 0 && lz == 2) a = Attendu.GRILLE;
					else if (ly == 1 && interieur) a = Attendu.VIDE;
					else if (ly == 1 && ((Math.abs(lx) == 2 && lz == 2) || (lx == 0 && lz == 4))) a = Attendu.TUYERE;
					else if ((ly == 2 || ly == 3) && lx == 0 && lz == 2) a = Attendu.VIDE;
					else if (ly == 4 && lx == 0 && lz == 2) a = Attendu.GUEULARD;
					PLAN.add(new Case(lx, ly, lz, a));
				}
	}
	public Direction avant() { return getBlockState().getValue(FourneauBlocs.FACING); }
	public BlockPos local(int lx, int ly, int lz) { return local(worldPosition, avant(), lx, ly, lz); }
	public static BlockPos local(BlockPos trou, Direction a, int lx, int ly, int lz) {
		return trou.relative(a.getCounterClockWise(), lx).above(ly).relative(a.getOpposite(), lz);
	}
	public BlockPos centre(int ly) { return local(0, ly, 2); }
	/** Côtés extérieurs (dans le monde) d'une case : ceux qui donnent hors de l'emprise de sa couche. */
	public static List<Direction> dehors(Direction a, int lx, int ly, int lz) {
		List<Direction> r = new ArrayList<>();
		if (!dansEmprise(lx + 1, ly, lz)) r.add(a.getCounterClockWise());
		if (!dansEmprise(lx - 1, ly, lz)) r.add(a.getClockWise());
		if (!dansEmprise(lx, ly, lz - 1)) r.add(a);
		if (!dansEmprise(lx, ly, lz + 1)) r.add(a.getOpposite());
		return r;
	}
	public static boolean estGrille(BlockState s) { return s.is(TagKey.create(net.minecraft.core.registries.Registries.BLOCK, ResourceLocation.parse("airain:airain_grates"))); }
	/** La case est-elle conforme ? (une place de tuyère accepte une brique) */
	public static boolean conforme(Attendu a, BlockState s) {
		return switch (a) {
			case TROU -> true;
			case BRIQUE -> s.is(Fourneau.BRIQUES.get());
			case TUYERE -> s.is(Fourneau.TUYERE.get()) || s.is(Fourneau.BRIQUES.get());
			case GRILLE -> estGrille(s);
			case VIDE -> s.isAir();
			case GUEULARD -> s.is(Fourneau.GUEULARD.get());
		};
	}

	// ------------------------------------------------------------------ vérification de la structure
	private final List<BlockPos> tuyeres = new ArrayList<>();
	private boolean verifier() {
		manquants.clear(); raisons.clear(); tuyeres.clear();
		for (Case c : PLAN) {
			BlockPos p = local(c.lx(), c.ly(), c.lz());
			BlockState s = level.getBlockState(p);
			if (c.quoi() == Attendu.TUYERE && s.is(Fourneau.TUYERE.get())) tuyeres.add(p);
			if (!conforme(c.quoi(), s)) manque(p, switch (c.quoi()) {
				case GRILLE -> "grate"; case VIDE -> "hollow"; case GUEULARD -> "hopper"; default -> "bricks"; });
		}
		if (tuyeres.isEmpty()) raisons.add("tuyere");
		return manquants.isEmpty() && !tuyeres.isEmpty();
	}
	private void manque(BlockPos p, String quoi) { manquants.add(p); if (!raisons.contains(quoi)) raisons.add(quoi); }

	/** Habillage des briques une fois le fourneau monté (ou rendu nu s'il est démonté). */
	private void habiller(boolean monte) {
		Direction a = avant();
		for (Case c : PLAN) {
			BlockPos p = local(c.lx(), c.ly(), c.lz());
			BlockState s = level.getBlockState(p);
			List<Direction> ext = dehors(a, c.lx(), c.ly(), c.lz());
			if (s.is(Fourneau.BRIQUES.get())) {
				Partie part = Partie.AUCUNE; Direction d = Direction.NORTH;
				if (monte && !ext.isEmpty()) {
					boolean coin = ext.size() == 2 && ext.get(0).getAxis() != ext.get(1).getAxis();
					// creuset : socle puis corniche (l'épaulement) ; cuve : ceinture rivetée, corps (blason devant), couronne
					Partie droit = switch (c.ly()) { case 0, 2 -> Partie.SOCLE; case 3 -> Partie.CORPS; default -> Partie.COURONNE; };
					Partie angle = switch (c.ly()) { case 0, 2 -> Partie.SOCLE_COIN; case 3 -> Partie.CORPS_COIN; default -> Partie.COURONNE_COIN; };
					part = coin ? angle : droit;
					if (coin) d = orientationCoin(ext.get(0), ext.get(1));
					if (c.ly() == 3 && c.lx() == 0 && c.lz() == 1) { part = Partie.BLASON; d = a; }
				}
				BlockState n = s.setValue(FourneauBlocs.PARTIE, part).setValue(FourneauBlocs.FACING, d);
				if (n != s) level.setBlock(p, n, Block.UPDATE_CLIENTS);
			}
			if (monte && s.is(Fourneau.TUYERE.get()) && ext.size() == 1 && s.getValue(FourneauBlocs.FACING) != ext.get(0))   // la buse se tourne vers l'extérieur
				level.setBlock(p, s.setValue(FourneauBlocs.FACING, ext.get(0)), Block.UPDATE_CLIENTS);
		}
	}
	/** Les modèles de coin sont dessinés pour le coin nord-ouest, puis tournés : on choisit la rotation selon les deux côtés extérieurs. */
	private static Direction orientationCoin(Direction x, Direction y) {
		boolean n = x == Direction.NORTH || y == Direction.NORTH, s = x == Direction.SOUTH || y == Direction.SOUTH;
		boolean o = x == Direction.WEST || y == Direction.WEST;
		if (n) return o ? Direction.NORTH : Direction.EAST;   // NO : 0°, NE : 90°
		if (s) return o ? Direction.WEST : Direction.SOUTH;   // SO : 270°, SE : 180°
		return Direction.NORTH;
	}

	// ------------------------------------------------------------------ fonctionnement
	void tickServeur() {
		if (level == null) return;
		if (!surplus.isEmpty()) { for (ItemStack st : surplus) Block.popResource(level, worldPosition.relative(avant()), st); surplus.clear(); }
		if (level.getGameTime() % 20 == 0) {
			boolean f = verifier();
			if (f != forme) { forme = f; habiller(f); change = true; if (!f) allumer(false); }
			chaleur = forme ? BlazeBurnerBlock.getHeatLevelOf(level.getBlockState(centre(0).below())) : HeatLevel.NONE;
			// 1.55 : jusqu'à trois tuyères ; chaque ventilateur ajoute son débit
			air = 0; souffle = 0;
			if (forme) for (BlockPos t : tuyeres) {
				BlockPos ventilo = t.relative(level.getBlockState(t).getValue(FourneauBlocs.FACING));
				if (level.getBlockEntity(ventilo) instanceof KineticBlockEntity k
					&& BuiltInRegistries.BLOCK.getKey(level.getBlockState(ventilo).getBlock()).toString().equals("create:encased_fan")) {
					int v = (int) Math.abs(k.getSpeed());
					if (v > 0) { air += v; souffle += Math.max(1, Math.min(8, v / 32)); }
				}
			}
		}
		boolean marche = false;
		if (forme && air > 0 && chaleur.isAtLeast(HeatLevel.KINDLED)) {
			Recette r = recette();
			if (r != null && cuve.getSpace() >= r.mb) {
				marche = true;
				progres += souffle;            // par ventilateur : 32 tr/min = 1 par tick, 256 tr/min = 8 par tick
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
		BlockPos g = centre(4); BlockState gs = level.getBlockState(g);
		if (gs.is(Fourneau.GUEULARD.get()) && gs.getValue(FourneauBlocs.LIT) != oui) level.setBlock(g, gs.setValue(FourneauBlocs.LIT, oui), Block.UPDATE_ALL);
	}

	void tickClient() {
		if (level == null || !getBlockState().getValue(FourneauBlocs.LIT)) return;
		var r = level.random;
		BlockPos g = centre(4);
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
	/** Clic droit à main nue sur le trou de coulée : état du fourneau, ou hologramme des blocs manquants (allumé / éteint). */
	void clic(Player j) {
		if (!verifier()) {
			boolean allume = HologrammeFourneau.basculer(j, worldPosition, false);
			j.displayClientMessage(allume ? Component.translatable("airain.fourneau.hologramme", manquants.size() + (tuyeres.isEmpty() ? 1 : 0)).withStyle(ChatFormatting.GOLD)
				: Component.translatable("airain.fourneau.hologramme_off").withStyle(ChatFormatting.GRAY), true);
			return;
		}
		j.displayClientMessage(etat(), true);
	}
	private Component etat() {
		String c = chaleur == HeatLevel.SEETHING ? "surchauffe" : chaleur.isAtLeast(HeatLevel.KINDLED) ? "chaud" : "froid";
		return Component.translatable("airain.fourneau.etat", Component.translatable("airain.fourneau.chaleur." + c), air, cuve.getFluidAmount() / LINGOT);
	}
	/** Le trou de coulée est cassé : les briques redeviennent nues, le métal et la charge tombent. */
	void demonter() {
		if (level == null || level.isClientSide) return;
		if (forme) habiller(false);
		for (int i = 0; i < charge.getSlots(); i++) Block.popResource(level, worldPosition, charge.getStackInSlot(i));
		Block.popResource(level, worldPosition, laitier.getStackInSlot(0));
		BlockPos g = centre(4); BlockState gs = level.getBlockState(g);
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
		// chaque ingrédient va dans son emplacement, quel que soit celui que vise l'entonnoir
		@Override public ItemStack insertItem(int s, ItemStack st, boolean sim) { int p = place(st); return p < 0 ? st : charge.insertItem(p, st, sim); }
		@Override public ItemStack extractItem(int s, int n, boolean sim) { return ItemStack.EMPTY; }
		@Override public int getSlotLimit(int s) { return 64; }
		@Override public boolean isItemValid(int s, ItemStack st) { return accepte(st); }
	};
	private static boolean accepte(ItemStack s) { return estCuivre(s) || estZinc(s) || estFondant(s) || estFerraille(s) || estRouage(s); }

	/** Le trou de coulée dont dépend un gueulard (null si aucun fourneau monté autour). */
	public static HautFourneauBlockEntity depuisGueulard(net.minecraft.world.level.Level l, BlockPos gueulard) {
		for (Direction d : Direction.Plane.HORIZONTAL) {
			BlockPos p = gueulard.below(4).relative(d, 2);      // le gueulard est au centre de la cuve, deux blocs derrière le trou
			BlockState s = l.getBlockState(p);
			if (s.is(Fourneau.TROU.get()) && s.getValue(FourneauBlocs.FACING) == d && l.getBlockEntity(p) instanceof HautFourneauBlockEntity be) return be;
		}
		return null;
	}

	@Override
	public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
		t.add(Component.literal("    ").append(Component.translatable("block.airain.blast_furnace_taphole")).withStyle(ChatFormatting.GOLD));
		if (!forme) {
			t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.incomplet")).withStyle(ChatFormatting.RED));
			// ce qui manque, compté case par case (calculé ici, côté client)
			if (level != null) {
				int briques = 0, grille = 0, gueulard = 0, vide = 0, tuy = 0;
				for (Case c : PLAN) {
					BlockState s = level.getBlockState(local(c.lx(), c.ly(), c.lz()));
					if (c.quoi() == Attendu.TUYERE && s.is(Fourneau.TUYERE.get())) tuy++;
					if (conforme(c.quoi(), s)) continue;
					switch (c.quoi()) { case GRILLE -> grille++; case GUEULARD -> gueulard++; case VIDE -> vide++; default -> briques++; }
				}
				if (briques > 0) t.add(ligne("airain.fourneau.lunettes.briques", briques));
				if (tuy == 0) t.add(ligne("airain.fourneau.lunettes.tuyere", 1));
				if (grille > 0) t.add(ligne("airain.fourneau.lunettes.grille", grille));
				if (gueulard > 0) t.add(ligne("airain.fourneau.lunettes.gueulard", gueulard));
				if (vide > 0) t.add(ligne("airain.fourneau.lunettes.vide", vide));
				t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.astuce")).withStyle(ChatFormatting.DARK_GRAY));
			}
			return true;
		}
		String c = chaleur == HeatLevel.SEETHING ? "surchauffe" : chaleur.isAtLeast(HeatLevel.KINDLED) ? "chaud" : "froid";
		t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.chaleur", Component.translatable("airain.fourneau.chaleur." + c))).withStyle(ChatFormatting.GRAY));
		t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.air", air)).withStyle(ChatFormatting.GRAY));
		t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.cuve", cuve.getFluidAmount(), CUVE)).withStyle(ChatFormatting.GRAY));
		if (progres > 0) t.add(Component.literal("    ").append(Component.translatable("airain.fourneau.lunettes.progres", progres * 100 / TRAVAIL)).withStyle(ChatFormatting.DARK_GRAY));
		return true;
	}

	private static Component ligne(String cle, int n) { return Component.literal("     ").append(Component.translatable(cle, n)).withStyle(ChatFormatting.GRAY); }
	public List<BlockPos> tuyeresPosees() { return tuyeres; }

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
		// relu emplacement par emplacement : les anciennes sauvegardes (4 emplacements mélangés) sont rangées par ingrédient
		ItemStackHandler lu = new ItemStackHandler(PLACES); lu.deserializeNBT(r, t.getCompound("charge"));
		for (int i = 0; i < PLACES; i++) charge.setStackInSlot(i, ItemStack.EMPTY);
		for (int i = 0; i < lu.getSlots(); i++) {
			ItemStack st = lu.getStackInSlot(i).copy();
			if (st.isEmpty()) continue;
			int p = place(st);
			ItemStack reste = p < 0 ? st : charge.insertItem(p, st, false);
			if (!reste.isEmpty()) surplus.add(reste);
		} laitier.deserializeNBT(r, t.getCompound("laitier")); cuve.readFromNBT(r, t.getCompound("cuve"));
		progres = t.getInt("progres"); forme = t.getBoolean("forme"); air = t.getInt("air");
		for (HeatLevel h : HeatLevel.values()) if (h.getSerializedName().equals(t.getString("chaleur"))) chaleur = h;
	}
	@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
	@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
}
