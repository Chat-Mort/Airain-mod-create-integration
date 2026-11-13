package fr.chatmort.airain.atelier;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.PipeBlock;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.Map;

/** Tuyauterie décorative d'airain : tuyau qui se raccorde tout seul, et vanne à volant. */
public final class Tuyaux {
	private Tuyaux() {}

	static BooleanProperty bras(Direction d) { return PipeBlock.PROPERTY_BY_DIRECTION.get(d); }

	/** Boîte décrite pour un bras tourné vers le nord, tournée vers d. */
	static VoxelShape boite(Direction d, double x0, double y0, double z0, double x1, double y1, double z1) {
		return fr.chatmort.airain.fonderie.ConduitAir.boiteVers(d, x0, y0, z0, x1, y1, z1);
	}

	/** Un tuyau se raccorde aux tuyaux, aux vannes dans leur axe, et au tuyau logé dans un plancher technique. */
	static boolean raccorde(BlockGetter l, BlockPos p, Direction d) {
		BlockState n = l.getBlockState(p.relative(d));
		if (n.getBlock() instanceof Tuyau) return true;
		if (n.getBlock() instanceof Vanne) return n.getValue(BlockStateProperties.AXIS) == d.getAxis();
		if (n.getBlock() instanceof PlancherTechnique) return PlancherTechnique.loge(n, PlancherTechnique.Contenu.TUYAU, d.getAxis());
		return false;
	}

	// ====================================================================== le tuyau
	public static class Tuyau extends BlocPatine {
		private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();
		public Tuyau(WeatherState etat, Properties p) {
			super(etat, p);
			BlockState s = defaultBlockState();
			for (Direction d : Direction.values()) s = s.setValue(bras(d), false);
			registerDefaultState(s);
		}
		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			b.add(BlockStateProperties.NORTH, BlockStateProperties.SOUTH, BlockStateProperties.EAST, BlockStateProperties.WEST, BlockStateProperties.UP, BlockStateProperties.DOWN);
		}
		/**
		 * Bras affichés : les vrais raccords ; un seul raccord → le tuyau continue tout droit de l'autre côté ;
		 * aucun → on garde l'axe d'avant (ou celui de la face visée à la pose).
		 */
		private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p, Direction.Axis axeSiSeul) {
			int n = 0; Direction seul = null;
			BlockState r = s;
			for (Direction d : Direction.values()) {
				boolean c = raccorde(l, p, d);
				r = r.setValue(bras(d), c);
				if (c) { n++; seul = d; }
			}
			if (n == 1) return r.setValue(bras(seul.getOpposite()), true);
			if (n == 0) {
				if (axeSiSeul != null) {
					for (Direction d : Direction.values()) r = r.setValue(bras(d), d.getAxis() == axeSiSeul);
					return r;
				}
				return s;                                   // garde les bras d'avant
			}
			return r;
		}
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return ajuster(defaultBlockState(), c.getLevel(), c.getClickedPos(), c.getClickedFace().getAxis()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) { return ajuster(s, l, p, null); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.computeIfAbsent(s, Tuyau::forme); }
		private static VoxelShape forme(BlockState s) {
			VoxelShape v = Block.box(5, 5, 5, 11, 11, 11);
			for (Direction d : Direction.values()) if (s.getValue(bras(d))) v = Shapes.joinUnoptimized(v, boite(d, 5, 5, 0, 11, 11, 5), BooleanOp.OR);
			return v.optimize();
		}
	}

	// ====================================================================== la vanne (corps, volant ; clic droit : ouvre ou ferme)
	public static class Vanne extends BlocPatine {
		private static final Map<Direction.Axis, VoxelShape> FORMES = new java.util.EnumMap<>(Direction.Axis.class);
		static {
			FORMES.put(Direction.Axis.X, Shapes.or(Block.box(0, 5, 5, 16, 11, 11), Block.box(4, 4, 4, 12, 12, 12), Block.box(3, 12, 3, 13, 15, 13)));
			FORMES.put(Direction.Axis.Z, Shapes.or(Block.box(5, 5, 0, 11, 11, 16), Block.box(4, 4, 4, 12, 12, 12), Block.box(3, 12, 3, 13, 15, 13)));
			FORMES.put(Direction.Axis.Y, Shapes.or(Block.box(5, 0, 5, 11, 16, 11), Block.box(4, 4, 4, 12, 12, 12), Block.box(3, 3, 1, 13, 13, 4)));
		}
		public Vanne(WeatherState etat, Properties p) {
			super(etat, p);
			registerDefaultState(defaultBlockState().setValue(BlockStateProperties.AXIS, Direction.Axis.X).setValue(BlockStateProperties.OPEN, true));
		}
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.AXIS, BlockStateProperties.OPEN); }
		// l'axe suit le tuyau voisin s'il y en a un, sinon la face visée
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction.Axis a = c.getClickedFace().getAxis();
			for (Direction d : Direction.values())
				if (c.getLevel().getBlockState(c.getClickedPos().relative(d)).getBlock() instanceof Tuyau) { a = d.getAxis(); break; }
			return defaultBlockState().setValue(BlockStateProperties.AXIS, a);
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!l.isClientSide) {
				boolean o = !s.getValue(BlockStateProperties.OPEN);
				l.setBlock(p, s.setValue(BlockStateProperties.OPEN, o), Block.UPDATE_ALL);
				l.playSound(null, p, o ? SoundEvents.COPPER_TRAPDOOR_OPEN : SoundEvents.COPPER_TRAPDOOR_CLOSE, SoundSource.BLOCKS, 0.8f, 0.7f);
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(BlockStateProperties.AXIS)); }
	}
}
