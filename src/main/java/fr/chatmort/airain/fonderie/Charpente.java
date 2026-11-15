package fr.chatmort.airain.fonderie;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WeatheringCopper;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 1.59 : la charpente métallique d'airain, pour bâtir des halles d'usine. Poutrelle en I (poteau debout, poutre couchée,
 * platines posées toutes seules aux bouts qui butent sur quelque chose), jambe de force, chevron et verrière à 45°,
 * poutre treillis (diagonales alternées d'un bloc à l'autre), lanterneau, gouttière et descente.
 * Chaque pièce existe en quatre teintes qui se patinent, et en version cirée (etat == null), comme les passerelles.
 */
public final class Charpente {
	private Charpente() {}

	/** Platine au bout négatif (ouest, nord, bas) et au bout positif (est, sud, haut). */
	public static final BooleanProperty DEBUT = BooleanProperty.create("start");
	public static final BooleanProperty FIN = BooleanProperty.create("end");
	/** Profil tourné d'un quart de tour autour de l'axe (clé de Create). */
	public static final BooleanProperty TOURNE = BooleanProperty.create("turned");
	/** Treillis : sens de la diagonale, alterné d'un bloc à l'autre pour dessiner le zigzag. */
	public static final BooleanProperty ALT = BooleanProperty.create("alt");
	/** Gouttière : sortie vers la descente posée dessous. Descente : sabot au pied. */
	public static final BooleanProperty SORTIE = BooleanProperty.create("outlet");
	public static final EnumProperty<Direction.Axis> AXE = BlockStateProperties.AXIS;
	public static final EnumProperty<Direction.Axis> AXE_H = BlockStateProperties.HORIZONTAL_AXIS;
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;

	/** Boîte décrite pour une pièce le long de l'axe nord-sud (z), tournée vers l'axe a (x : vers l'ouest, y : vers le bas). */
	static VoxelShape boiteAxe(Direction.Axis a, double x0, double y0, double z0, double x1, double y1, double z1) {
		return switch (a) {
			case Z -> Block.box(x0, y0, z0, x1, y1, z1);
			case X -> Block.box(z0, y0, 16 - x1, z1, y1, 16 - x0);
			default -> Block.box(x0, z0, 16 - y1, x1, z1, 16 - y0);
		};
	}

	private static abstract class Piece extends Block implements Passerelle.Patinable {
		private final WeatherState etat;
		Piece(WeatherState etat, Properties p) { super(p); this.etat = etat; }
		@Override public WeatherState etat() { return etat; }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
	}

	// ====================================================================== la poutrelle en I
	public static class Poutrelle extends Piece implements IWrenchable {
		private static final Map<BlockState, VoxelShape> FORMES = new ConcurrentHashMap<>();
		public Poutrelle(WeatherState etat, Properties p) {
			super(etat, p);
			registerDefaultState(defaultBlockState().setValue(AXE, Direction.Axis.Y).setValue(DEBUT, false).setValue(FIN, false).setValue(TOURNE, false));
		}
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(AXE, DEBUT, FIN, TOURNE); }
		/** Une platine quand le bout bute sur un bloc qui n'est pas la suite de la poutrelle. */
		private static boolean platine(BlockGetter l, BlockPos p, Direction d, Direction.Axis a) {
			BlockState n = l.getBlockState(p.relative(d));
			if (n.isAir() || n.canBeReplaced()) return false;
			return !(n.getBlock() instanceof Poutrelle && n.getValue(AXE) == a);
		}
		private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) {
			Direction.Axis a = s.getValue(AXE);
			return s.setValue(DEBUT, platine(l, p, Direction.fromAxisAndDirection(a, Direction.AxisDirection.NEGATIVE), a))
				.setValue(FIN, platine(l, p, Direction.fromAxisAndDirection(a, Direction.AxisDirection.POSITIVE), a));
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			return ajuster(defaultBlockState().setValue(AXE, c.getClickedFace().getAxis()), c.getLevel(), c.getClickedPos());
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			return d.getAxis() == s.getValue(AXE) ? ajuster(s, l, p) : s;
		}
		@Override
		protected BlockState rotate(BlockState s, Rotation r) {
			Direction.Axis a = s.getValue(AXE);
			if (a == Direction.Axis.Y || r == Rotation.NONE || r == Rotation.CLOCKWISE_180) return s;
			return s.setValue(AXE, a == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.X);
		}
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			return FORMES.computeIfAbsent(s, e -> {
				Direction.Axis a = e.getValue(AXE);
				VoxelShape v = e.getValue(TOURNE) ? boiteAxe(a, 1, 3, 0, 15, 13, 16) : boiteAxe(a, 3, 1, 0, 13, 15, 16);
				if (e.getValue(DEBUT)) v = Shapes.or(v, boiteAxe(a, 1, 1, 0, 15, 15, 1));
				if (e.getValue(FIN)) v = Shapes.or(v, boiteAxe(a, 1, 1, 15, 15, 15, 16));
				return v.optimize();
			});
		}
		// clé de Create : le profil tourne d'un quart de tour autour de son axe
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			if (!c.getLevel().isClientSide) {
				c.getLevel().setBlock(c.getClickedPos(), s.cycle(TOURNE), Block.UPDATE_ALL);
				c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
	}

	// ====================================================================== pièces à 45° : jambe de force, chevron, verrière
	/** Pièce inclinée : monte vers FACING (le bas côté opposé), d'un coin du bloc à l'autre. */
	public static class Incline extends Piece implements IWrenchable {
		private final double x0, x1;
		private final Map<Direction, VoxelShape> formes = new ConcurrentHashMap<>();
		/** x0..x1 : largeur de la pièce (dessinée montant vers le nord). */
		public Incline(WeatherState etat, Properties p, double x0, double x1) {
			super(etat, p); this.x0 = x0; this.x1 = x1;
			registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH));
		}
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }
		/** Le haut de la pièce part devant soi. */
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection()); }
		@Override protected BlockState rotate(BlockState s, Rotation r) { return s.setValue(FACING, r.rotate(s.getValue(FACING))); }
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			return formes.computeIfAbsent(s.getValue(FACING), f -> {
				VoxelShape v = Shapes.empty();
				for (int i = 0; i < 4; i++) v = Shapes.or(v, ConduitAir.boiteVers(f, x0, i * 4, 12 - i * 4, x1, i * 4 + 4, 16 - i * 4));   // marches de 4 px
				return v.optimize();
			});
		}
		// clé de Create : un quart de tour
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			if (!c.getLevel().isClientSide) {
				c.getLevel().setBlock(c.getClickedPos(), s.setValue(FACING, s.getValue(FACING).getClockWise()), Block.UPDATE_ALL);
				c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
	}

	// ====================================================================== la poutre treillis
	public static class Treillis extends Piece {
		private static final Map<Direction.Axis, VoxelShape> FORMES = new ConcurrentHashMap<>();
		public Treillis(WeatherState etat, Properties p) {
			super(etat, p);
			registerDefaultState(defaultBlockState().setValue(AXE, Direction.Axis.X).setValue(ALT, false));
		}
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(AXE, ALT); }
		/** Diagonale alternée selon la position le long de l'axe : le zigzag se suit d'un bloc à l'autre. */
		private static BlockState ajuster(BlockState s, BlockPos p) { return s.setValue(ALT, (p.get(s.getValue(AXE)) & 1) == 1); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			// posée contre un côté : dans le prolongement de ce côté ; contre le dessus ou le dessous : dans le sens du regard
			Direction f = c.getClickedFace();
			Direction.Axis a = f.getAxis() == Direction.Axis.Y ? c.getHorizontalDirection().getAxis() : f.getAxis();
			if (c.getPlayer() != null && c.getPlayer().isShiftKeyDown()) a = Direction.Axis.Y;   // accroupi : en colonne
			return ajuster(defaultBlockState().setValue(AXE, a), c.getClickedPos());
		}
		@Override
		protected BlockState rotate(BlockState s, Rotation r) {
			Direction.Axis a = s.getValue(AXE);
			if (a == Direction.Axis.Y || r == Rotation.NONE || r == Rotation.CLOCKWISE_180) return s;
			return s.setValue(AXE, a == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.X);
		}
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			return FORMES.computeIfAbsent(s.getValue(AXE), a -> boiteAxe(a, 4, 0, 0, 12, 16, 16));
		}
	}

	// ====================================================================== le lanterneau (verrière à plat)
	public static class Lanterneau extends Piece {
		private static final VoxelShape FORME = Block.box(0, 0, 0, 16, 2, 16);
		public Lanterneau(WeatherState etat, Properties p) { super(etat, p); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	}

	// ====================================================================== la gouttière et sa descente
	public static class Gouttiere extends Piece {
		private static final Map<BlockState, VoxelShape> FORMES = new ConcurrentHashMap<>();
		public Gouttiere(WeatherState etat, Properties p) {
			super(etat, p);
			registerDefaultState(defaultBlockState().setValue(AXE_H, Direction.Axis.Z).setValue(DEBUT, true).setValue(FIN, true).setValue(SORTIE, false));
		}
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(AXE_H, DEBUT, FIN, SORTIE); }
		/** Les bouts se ferment s'il n'y a pas de gouttière dans le prolongement ; la sortie s'ouvre sur une descente. */
		private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) {
			Direction.Axis a = s.getValue(AXE_H);
			return s.setValue(DEBUT, !(l.getBlockState(p.relative(a, -1)).getBlock() instanceof Gouttiere))
				.setValue(FIN, !(l.getBlockState(p.relative(a, 1)).getBlock() instanceof Gouttiere))
				.setValue(SORTIE, l.getBlockState(p.below()).getBlock() instanceof Descente);
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			return ajuster(defaultBlockState().setValue(AXE_H, c.getHorizontalDirection().getClockWise().getAxis()), c.getLevel(), c.getClickedPos());
		}
		@Override protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) { return ajuster(s, l, p); }
		@Override
		protected BlockState rotate(BlockState s, Rotation r) {
			if (r == Rotation.NONE || r == Rotation.CLOCKWISE_180) return s;
			return s.setValue(AXE_H, s.getValue(AXE_H) == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.X);
		}
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			return FORMES.computeIfAbsent(s, e -> {
				VoxelShape v = boiteAxe(e.getValue(AXE_H), 3, 10, 0, 13, 15, 16);
				return e.getValue(SORTIE) ? Shapes.or(v, Block.box(6, 0, 6, 10, 10, 10)) : v;
			});
		}
	}
	public static class Descente extends Piece {
		private static final VoxelShape FORME = Block.box(5, 0, 5, 11, 16, 11);
		public Descente(WeatherState etat, Properties p) { super(etat, p); registerDefaultState(defaultBlockState().setValue(SORTIE, true)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(SORTIE); }
		private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) { return s.setValue(SORTIE, !(l.getBlockState(p.below()).getBlock() instanceof Descente)); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return ajuster(defaultBlockState(), c.getLevel(), c.getClickedPos()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			return d == Direction.DOWN ? ajuster(s, l, p) : s;
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	}

	// ====================================================================== enregistrement
	private static final WeatherState[] ETATS = {WeatherState.UNAFFECTED, WeatherState.EXPOSED, WeatherState.WEATHERED, WeatherState.OXIDIZED};
	private static final MapColor[] COULEURS = {MapColor.GOLD, MapColor.TERRACOTTA_YELLOW, MapColor.TERRACOTTA_ORANGE, MapColor.TERRACOTTA_RED};
	public static final Map<String, DeferredBlock<Block>[][]> FAMILLES = new LinkedHashMap<>();
	private interface Fabrique { Block creer(WeatherState etat, BlockBehaviour.Properties p); }

	@SuppressWarnings("unchecked")
	private static void famille(String nom, Fabrique f) {
		DeferredBlock<Block>[][] t = new DeferredBlock[4][2];
		for (int s = 0; s < 4; s++)
			for (int c = 0; c < 2; c++) {
				final int st = s; final boolean cire = c == 1;
				String id = (cire ? "waxed_" : "") + BlocsAirain.STADES[s] + nom;
				DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, () -> f.creer(cire ? null : ETATS[st],
					BlockBehaviour.Properties.of().mapColor(COULEURS[st]).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
						.isValidSpawn((a, bb, cc, dd) -> false).isRedstoneConductor((a, bb, cc) -> false).isSuffocating((a, bb, cc) -> false).isViewBlocking((a, bb, cc) -> false)));
				AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
				t[s][c] = b;
			}
		FAMILLES.put(nom, t);
	}

	static {
		famille("airain_beam", Poutrelle::new);
		famille("airain_knee_brace", (e, p) -> new Incline(e, p, 5, 11));
		famille("airain_rafter", (e, p) -> new Incline(e, p, 3, 13));
		famille("airain_lattice_girder", Treillis::new);
		famille("airain_glass_roof", (e, p) -> new Incline(e, p, 0, 16));
		famille("airain_skylight", Lanterneau::new);
		famille("airain_gutter", Gouttiere::new);
		famille("airain_downpipe", Descente::new);
	}

	public static void charger() { Marquages.charger(); }
}
