package fr.chatmort.airain.fonderie;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.WeatheringCopper;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.HashMap;
import java.util.Map;

/**
 * Les passerelles d'airain (style industriel) : passerelle, escalier, rampe, poteau, échelle, et le portillon (un objet
 * qu'on pose sur un côté de passerelle).
 *
 * Hauteurs (en pixels) : plancher bas à 3, plancher haut à 11 (comme une dalle du haut). L'escalier monte de 3 à 19
 * (le plancher bas du bloc au-dessus, un cran plus loin) ; la rampe monte d'une dalle : de 3 à 11, ou de 11 à 19.
 * Les rambardes se posent seules sur les côtés qui ne se raccordent à rien ; la clé de Create en retire ou en remet une.
 * Chaque bloc existe en quatre teintes qui se patinent, et en version cirée (etat == null).
 */
public final class Passerelle {
	private Passerelle() {}

	public static final BooleanProperty HAUT = BooleanProperty.create("top");
	public static final BooleanProperty GAUCHE = BooleanProperty.create("left");
	public static final BooleanProperty DROITE = BooleanProperty.create("right");
	/** Plancher plein (tôle) au lieu du caillebotis : clé de Create sur le sol de la pièce. */
	public static final BooleanProperty PLEIN = BooleanProperty.create("solid");
	/** Ce qui entoure l'échelle : rien, une crinoline, ou un tunnel plein (clé de Create pour passer de l'un à l'autre). */
	public enum Entourage implements StringRepresentable {
		RIEN("none"), CRINOLINE("cage"), TUNNEL("full");
		private final String nom;
		Entourage(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public static final EnumProperty<Entourage> CAGE = EnumProperty.create("cage", Entourage.class);
	public static final BooleanProperty BAS = BooleanProperty.create("bottom");
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;

	/** Ce qu'il y a sur un côté de passerelle. */
	public enum Cote implements StringRepresentable {
		AUCUN("none"), RAMBARDE("railing"), PORTILLON("gate"), OUVERT("gate_open");
		private final String nom;
		Cote(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public static final EnumProperty<Cote> NORD = EnumProperty.create("north", Cote.class);
	public static final EnumProperty<Cote> SUD = EnumProperty.create("south", Cote.class);
	public static final EnumProperty<Cote> EST = EnumProperty.create("east", Cote.class);
	public static final EnumProperty<Cote> OUEST = EnumProperty.create("west", Cote.class);
	public static EnumProperty<Cote> cote(Direction d) {
		return switch (d) { case NORTH -> NORD; case SOUTH -> SUD; case EAST -> EST; default -> OUEST; };
	}

	private static double px(double v) { return v / 16.0; }
	private static VoxelShape boite(double x0, double y0, double z0, double x1, double y1, double z1) {
		return Block.box(Math.min(x0, x1), Math.max(0, Math.min(y0, y1)), Math.min(z0, z1), Math.max(x0, x1), Math.min(24, Math.max(y0, y1)), Math.max(z0, z1));
	}
	/** Une boîte décrite pour le côté nord, tournée vers le côté d. */
	private static VoxelShape tourner(Direction d, double x0, double y0, double z0, double x1, double y1, double z1) {
		return switch (d) {
			case NORTH -> boite(x0, y0, z0, x1, y1, z1);
			case SOUTH -> boite(16 - x1, y0, 16 - z1, 16 - x0, y1, 16 - z0);
			case EAST -> boite(16 - z1, y0, x0, 16 - z0, y1, x1);
			default -> boite(z0, y0, 16 - x1, z1, y1, 16 - x0);
		};
	}
	/** Côté le plus proche du point visé (en coordonnées locales du bloc). */
	static Direction coteVise(BlockPos pos, Vec3 visee) {
		double x = visee.x - pos.getX(), z = visee.z - pos.getZ();
		double n = z, s = 1 - z, o = x, e = 1 - x, m = Math.min(Math.min(n, s), Math.min(o, e));
		return m == n ? Direction.NORTH : m == s ? Direction.SOUTH : m == o ? Direction.WEST : Direction.EAST;
	}
	/** Hauteur du plancher d'une passerelle, d'un escalier ou d'une rampe, sur sa face d (en px), ou -1 si rien ne s'y raccorde. */
	static int niveauFace(BlockState s, Direction d) {
		if (s.getBlock() instanceof Plancher) return s.getValue(HAUT) ? 11 : 3;
		if (s.getBlock() instanceof Escalier) { Direction f = s.getValue(FACING); return d == f.getOpposite() ? 3 : d == f ? 19 : -1; }
		if (s.getBlock() instanceof Rampe) {
			Direction f = s.getValue(FACING); int bas = s.getValue(HAUT) ? 11 : 3;
			return d == f.getOpposite() ? bas : d == f ? bas + 8 : -1;
		}
		return -1;
	}

	// ====================================================================== mécanique commune de patine
	interface Patinable extends WeatheringCopper {
		WeatherState etat();
		@Override default WeatherState getAge() { return etat() == null ? WeatherState.UNAFFECTED : etat(); }
	}

	// ====================================================================== la passerelle
	public static class Plancher extends Block implements Patinable, IWrenchable {
		private final WeatherState etat;
		private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();
		public Plancher(WeatherState etat, Properties p) {
			super(p); this.etat = etat;
			registerDefaultState(defaultBlockState().setValue(HAUT, false).setValue(PLEIN, false).setValue(NORD, Cote.AUCUN).setValue(SUD, Cote.AUCUN).setValue(EST, Cote.AUCUN).setValue(OUEST, Cote.AUCUN));
		}
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(HAUT, PLEIN, NORD, SUD, EST, OUEST); }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }

		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction f = c.getClickedFace();
			double y = c.getClickLocation().y - c.getClickedPos().getY();
			BlockState s = defaultBlockState().setValue(HAUT, f == Direction.DOWN || (f != Direction.UP && y > 0.5));
			for (Direction d : Direction.Plane.HORIZONTAL) s = s.setValue(cote(d), raccorde(c.getLevel(), c.getClickedPos(), s, d) ? Cote.AUCUN : Cote.RAMBARDE);
			return s;
		}
		/** Le côté d se raccorde-t-il à une autre pièce de passerelle au même niveau ? */
		static boolean raccorde(BlockGetter l, BlockPos p, BlockState s, Direction d) {
			int niveau = s.getValue(HAUT) ? 11 : 3;
			BlockPos n = p.relative(d);
			if (niveauFace(l.getBlockState(n), d.getOpposite()) == niveau) return true;
			// escalier ou rampe en contrebas dont le haut arrive à notre plancher bas
			return niveau == 3 && niveauFace(l.getBlockState(n.below()), d.getOpposite()) == 19;
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState voisin, LevelAccessor l, BlockPos p, BlockPos np) {
			if (d.getAxis().isHorizontal()) {
				Cote c = s.getValue(cote(d));
				if (c == Cote.AUCUN || c == Cote.RAMBARDE) s = s.setValue(cote(d), raccorde(l, p, s, d) ? Cote.AUCUN : Cote.RAMBARDE);
			}
			return s;
		}
		/** Recalcule un côté (appelé par les escaliers et rampes posés en contrebas, qui ne déclenchent pas updateShape). */
		static void recalculer(Level l, BlockPos p, Direction d) {
			BlockState s = l.getBlockState(p);
			if (!(s.getBlock() instanceof Plancher)) return;
			Cote c = s.getValue(cote(d));
			if (c != Cote.AUCUN && c != Cote.RAMBARDE) return;
			BlockState n = s.setValue(cote(d), raccorde(l, p, s, d) ? Cote.AUCUN : Cote.RAMBARDE);
			if (n != s) l.setBlock(p, n, Block.UPDATE_ALL);
		}

		// portillon : le poser (objet), l'ouvrir et le fermer (main nue)
		@Override
		protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand h, BlockHitResult hit) {
			if (!st.is(Passerelles.PORTILLON.get())) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			Direction d = coteVise(p, hit.getLocation());
			if (s.getValue(cote(d)) == Cote.PORTILLON || s.getValue(cote(d)) == Cote.OUVERT) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			if (!l.isClientSide) {
				l.setBlock(p, s.setValue(cote(d), Cote.PORTILLON), Block.UPDATE_ALL);
				l.playSound(null, p, SoundEvents.COPPER_PLACE, SoundSource.BLOCKS, 1f, 1f);
				if (!j.getAbilities().instabuild) st.shrink(1);
			}
			return ItemInteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult hit) {
			Direction d = coteVise(p, hit.getLocation());
			Cote c = s.getValue(cote(d));
			if (c != Cote.PORTILLON && c != Cote.OUVERT) return InteractionResult.PASS;
			if (!l.isClientSide) {
				boolean ouvre = c == Cote.PORTILLON;
				l.setBlock(p, s.setValue(cote(d), ouvre ? Cote.OUVERT : Cote.PORTILLON), Block.UPDATE_ALL);
				l.playSound(null, p, ouvre ? SoundEvents.COPPER_TRAPDOOR_OPEN : SoundEvents.COPPER_TRAPDOOR_CLOSE, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		// clé de Create : sur le sol (loin des bords), plancher plein ou caillebotis ; sinon, enlève ou remet la rambarde du côté visé
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			Level l = c.getLevel(); BlockPos p = c.getClickedPos();
			Direction d = coteVise(p, c.getClickLocation());
			double x = c.getClickLocation().x - p.getX(), z = c.getClickLocation().z - p.getZ();
			double bord = Math.min(Math.min(x, 1 - x), Math.min(z, 1 - z));
			if (c.getClickedFace().getAxis() == Direction.Axis.Y && bord > 0.2) {
				if (!l.isClientSide) {
					l.setBlock(p, s.setValue(PLEIN, !s.getValue(PLEIN)), Block.UPDATE_ALL);
					l.playSound(null, p, SoundEvents.COPPER_PLACE, SoundSource.BLOCKS, 1f, 0.8f);
				}
				return InteractionResult.SUCCESS;
			}
			Cote cc = s.getValue(cote(d));
			if (!l.isClientSide) {
				if (cc == Cote.PORTILLON || cc == Cote.OUVERT) Block.popResource(l, p, new ItemStack(Passerelles.PORTILLON.get()));
				l.setBlock(p, s.setValue(cote(d), cc == Cote.AUCUN ? Cote.RAMBARDE : Cote.AUCUN), Block.UPDATE_ALL);
				l.playSound(null, p, SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!(n.getBlock() instanceof Plancher))      // le portillon tombe avec la passerelle (pas quand elle se patine)
				for (Direction d : Direction.Plane.HORIZONTAL)
					if (s.getValue(cote(d)) == Cote.PORTILLON || s.getValue(cote(d)) == Cote.OUVERT) Block.popResource(l, p, new ItemStack(Passerelles.PORTILLON.get()));
			super.onRemove(s, l, p, n, deplace);
		}

		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			return FORMES.computeIfAbsent(s, Plancher::forme);
		}
		private static VoxelShape forme(BlockState s) {
			int h = s.getValue(HAUT) ? 11 : 3;
			VoxelShape v = boite(0, h - 2, 0, 16, h, 16);
			for (Direction d : Direction.Plane.HORIZONTAL) {
				Cote c = s.getValue(cote(d));
				if (c == Cote.RAMBARDE || c == Cote.PORTILLON) v = Shapes.joinUnoptimized(v, tourner(d, 0, h, 0, 16, h + 13, 2), BooleanOp.OR);
			}
			return v.optimize();
		}
	}

	// ====================================================================== l'escalier (monte vers FACING)
	public static class Escalier extends Block implements Patinable, IWrenchable {
		private final WeatherState etat;
		private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();
		public Escalier(WeatherState etat, Properties p) {
			super(p); this.etat = etat;
			registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(GAUCHE, true).setValue(DROITE, true).setValue(PLEIN, false));
		}
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, GAUCHE, DROITE, PLEIN); }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection()); }
		@Override
		protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
			super.onPlace(s, l, p, ancien, deplace);
			Direction f = s.getValue(FACING); Plancher.recalculer(l, p.relative(f).above(), f.getOpposite());
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			super.onRemove(s, l, p, n, deplace);
			if (!(n.getBlock() instanceof Escalier)) { Direction f = s.getValue(FACING); Plancher.recalculer(l, p.relative(f).above(), f.getOpposite()); }
		}
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			Direction f = s.getValue(FACING), d = coteVise(c.getClickedPos(), c.getClickLocation());
			BooleanProperty r = d == f.getCounterClockWise() ? GAUCHE : d == f.getClockWise() ? DROITE : null;
			if (r == null || c.getClickedFace() == Direction.UP) r = PLEIN;     // sur les marches : plein ou caillebotis
			if (!c.getLevel().isClientSide) {
				c.getLevel().setBlock(c.getClickedPos(), s.setValue(r, !s.getValue(r)), Block.UPDATE_ALL);
				c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.computeIfAbsent(s, Escalier::forme); }
		private static VoxelShape forme(BlockState s) {
			Direction f = s.getValue(FACING);
			VoxelShape v = Shapes.empty();
			for (int i = 0; i < 4; i++) {        // décrit pour un escalier qui monte vers le nord (z décroissant)
				int top = 3 + 4 * (i + 1);
				v = Shapes.joinUnoptimized(v, tournerEsc(f, 1, top - 2, 16 - 4 * (i + 1), 15, top, 16 - 4 * i), BooleanOp.OR);
			}
			if (s.getValue(GAUCHE)) v = Shapes.joinUnoptimized(v, tournerEsc(f, 0, 3, 0, 1, 24, 16), BooleanOp.OR);
			if (s.getValue(DROITE)) v = Shapes.joinUnoptimized(v, tournerEsc(f, 15, 3, 0, 16, 24, 16), BooleanOp.OR);
			return v.optimize();
		}
	}
	/** Boîte décrite pour une pièce qui monte vers le nord, tournée selon f. */
	static VoxelShape tournerEsc(Direction f, double x0, double y0, double z0, double x1, double y1, double z1) {
		return switch (f) {
			case NORTH -> boite(x0, y0, z0, x1, y1, z1);
			case SOUTH -> boite(16 - x1, y0, 16 - z1, 16 - x0, y1, 16 - z0);
			case EAST -> boite(16 - z1, y0, x0, 16 - z0, y1, x1);
			default -> boite(z0, y0, 16 - x1, z1, y1, 16 - x0);
		};
	}

	// ====================================================================== la rampe (monte d'une dalle vers FACING)
	public static class Rampe extends Block implements Patinable, IWrenchable {
		private final WeatherState etat;
		private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();
		public Rampe(WeatherState etat, Properties p) {
			super(p); this.etat = etat;
			registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(HAUT, false).setValue(GAUCHE, true).setValue(DROITE, true).setValue(PLEIN, false));
		}
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, HAUT, GAUCHE, DROITE, PLEIN); }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction f = c.getClickedFace();
			double y = c.getClickLocation().y - c.getClickedPos().getY();
			return defaultBlockState().setValue(FACING, c.getHorizontalDirection()).setValue(HAUT, f == Direction.DOWN || (f != Direction.UP && y > 0.5));
		}
		@Override
		protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
			super.onPlace(s, l, p, ancien, deplace);
			if (s.getValue(HAUT)) { Direction f = s.getValue(FACING); Plancher.recalculer(l, p.relative(f).above(), f.getOpposite()); }
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			super.onRemove(s, l, p, n, deplace);
			if (!(n.getBlock() instanceof Rampe) && s.getValue(HAUT)) { Direction f = s.getValue(FACING); Plancher.recalculer(l, p.relative(f).above(), f.getOpposite()); }
		}
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			Direction f = s.getValue(FACING), d = coteVise(c.getClickedPos(), c.getClickLocation());
			BooleanProperty r = d == f.getCounterClockWise() ? GAUCHE : d == f.getClockWise() ? DROITE : null;
			if (r == null || c.getClickedFace() == Direction.UP) r = PLEIN;     // sur les marches : plein ou caillebotis
			if (!c.getLevel().isClientSide) {
				c.getLevel().setBlock(c.getClickedPos(), s.setValue(r, !s.getValue(r)), Block.UPDATE_ALL);
				c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.computeIfAbsent(s, Rampe::forme); }
		private static VoxelShape forme(BlockState s) {
			Direction f = s.getValue(FACING); int h0 = s.getValue(HAUT) ? 11 : 3;
			VoxelShape v = Shapes.empty();
			for (int i = 0; i < 8; i++) v = Shapes.joinUnoptimized(v, tournerEsc(f, 1, h0 - 2 + i, 14 - 2 * i, 15, h0 + i, 16 - 2 * i), BooleanOp.OR);
			if (s.getValue(GAUCHE)) v = Shapes.joinUnoptimized(v, tournerEsc(f, 0, h0, 0, 1, Math.min(24, h0 + 17), 16), BooleanOp.OR);
			if (s.getValue(DROITE)) v = Shapes.joinUnoptimized(v, tournerEsc(f, 15, h0, 0, 16, Math.min(24, h0 + 17), 16), BooleanOp.OR);
			return v.optimize();
		}
	}

	// ====================================================================== le poteau de soutien (s'évase au sol et sous la passerelle)
	public static class Poteau extends Block implements Patinable {
		private final WeatherState etat;
		private static final VoxelShape FUT = Block.box(5, 0, 5, 11, 16, 11);
		public Poteau(WeatherState etat, Properties p) { super(p); this.etat = etat; registerDefaultState(defaultBlockState().setValue(BAS, true).setValue(HAUT, true)); }
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BAS, HAUT); }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) {
			return s.setValue(BAS, !(l.getBlockState(p.below()).getBlock() instanceof Poteau)).setValue(HAUT, !(l.getBlockState(p.above()).getBlock() instanceof Poteau));
		}
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return ajuster(defaultBlockState(), c.getLevel(), c.getClickedPos()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			return d.getAxis() == Direction.Axis.Y ? ajuster(s, l, p) : s;
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FUT; }
	}

	// ====================================================================== l'échelle (crinoline à partir du 3e échelon)
	public static class Echelle extends LadderBlock implements Patinable, IWrenchable {
		private final WeatherState etat;
		public Echelle(WeatherState etat, Properties p) { super(p); this.etat = etat; registerDefaultState(defaultBlockState().setValue(CAGE, Entourage.RIEN)); }
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { super.createBlockStateDefinition(b); b.add(CAGE); }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		private static boolean cage(BlockGetter l, BlockPos p) {
			return l.getBlockState(p.below()).getBlock() instanceof Echelle && l.getBlockState(p.below(2)).getBlock() instanceof Echelle;
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			BlockState s = super.getStateForPlacement(c);
			return s == null ? null : s.setValue(CAGE, cage(c.getLevel(), c.getClickedPos()) ? Entourage.CRINOLINE : Entourage.RIEN);
		}
		// clé de Create : rien → crinoline → tunnel plein → rien
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			if (!c.getLevel().isClientSide) {
				Entourage e = s.getValue(CAGE);
				Entourage n = e == Entourage.RIEN ? Entourage.CRINOLINE : e == Entourage.CRINOLINE ? Entourage.TUNNEL : Entourage.RIEN;
				c.getLevel().setBlock(c.getClickedPos(), s.setValue(CAGE, n), Block.UPDATE_ALL);
				c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
	}

	@SuppressWarnings("unused") private static double inutile = px(0);
}
