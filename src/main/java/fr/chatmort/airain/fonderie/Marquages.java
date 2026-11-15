package fr.chatmort.airain.fonderie;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;

/**
 * 1.59 : les marquages au sol, une fine couche de peinture posée sur n'importe quel sol (pas de collision).
 * Lignes jaunes, blanches ou rouges qui se raccordent toutes seules (droite, angle, T, croix), hachures à motif continu,
 * flèches et passages piétons orientés.
 */
public final class Marquages {
	private Marquages() {}

	private static final VoxelShape FORME = Block.box(0, 0, 0, 16, 0.5, 16);

	/** Base : posée sur un dessus solide, sans collision, se casse d'un coup. */
	public static class Peinture extends Block {
		private final boolean oriente;
		public Peinture(Properties p, boolean oriente) {
			super(p); this.oriente = oriente;
			if (oriente) registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH));
		}
		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			// appelé par le constructeur de Block, avant que « oriente » soit affecté : on ajoute la propriété à toutes, les lignes l'ignorent
			b.add(BlockStateProperties.HORIZONTAL_FACING);
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, oriente ? c.getHorizontalDirection() : Direction.NORTH);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
		@Override protected VoxelShape getCollisionShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return Shapes.empty(); }
		@Override
		protected boolean canSurvive(BlockState s, LevelReader l, BlockPos p) {
			return l.getBlockState(p.below()).isFaceSturdy(l, p.below(), Direction.UP);
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			return d == Direction.DOWN && !canSurvive(s, l, p) ? Blocks.AIR.defaultBlockState() : s;
		}
		@Override
		protected BlockState rotate(BlockState s, Rotation r) {
			return oriente ? s.setValue(BlockStateProperties.HORIZONTAL_FACING, r.rotate(s.getValue(BlockStateProperties.HORIZONTAL_FACING))) : s;
		}
		@Override
		protected BlockState mirror(BlockState s, Mirror m) { return oriente ? s.rotate(m.getRotation(s.getValue(BlockStateProperties.HORIZONTAL_FACING))) : s; }
	}

	/** La ligne : un bras vers chaque ligne voisine ; un bout seul continue tout droit ; isolée, elle garde son sens. */
	public static class Ligne extends Peinture {
		public static final BooleanProperty N = BlockStateProperties.NORTH, S = BlockStateProperties.SOUTH, E = BlockStateProperties.EAST, O = BlockStateProperties.WEST;
		public Ligne(Properties p) {
			super(p, false);
			registerDefaultState(defaultBlockState().setValue(N, true).setValue(S, true).setValue(E, false).setValue(O, false));
		}
		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { super.createBlockStateDefinition(b); b.add(N, S, E, O); }
		static BooleanProperty bras(Direction d) { return switch (d) { case NORTH -> N; case SOUTH -> S; case EAST -> E; default -> O; }; }
		private static BlockState raccorder(BlockState s, LevelAccessor l, BlockPos p, Direction.Axis sens) {
			int n = 0; Direction seul = null;
			for (Direction d : Direction.Plane.HORIZONTAL) if (l.getBlockState(p.relative(d)).getBlock() instanceof Ligne) { n++; seul = d; }
			if (n == 0) {
				// isolée : on garde le sens donné (placement) ou celui qu'elle avait
				Direction.Axis a = sens != null ? sens : (s.getValue(E) || s.getValue(O)) && !(s.getValue(N) || s.getValue(S)) ? Direction.Axis.X : Direction.Axis.Z;
				return s.setValue(N, a == Direction.Axis.Z).setValue(S, a == Direction.Axis.Z).setValue(E, a == Direction.Axis.X).setValue(O, a == Direction.Axis.X);
			}
			for (Direction d : Direction.Plane.HORIZONTAL) {
				boolean v = l.getBlockState(p.relative(d)).getBlock() instanceof Ligne || (n == 1 && d == seul.getOpposite());
				s = s.setValue(bras(d), v);
			}
			return s;
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			return raccorder(defaultBlockState(), c.getLevel(), c.getClickedPos(), c.getHorizontalDirection().getAxis());
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			BlockState r = super.updateShape(s, d, v, l, p, np);
			if (r.isAir() || d.getAxis() == Direction.Axis.Y) return r;
			return raccorder(r, l, p, null);
		}
		@Override
		protected BlockState rotate(BlockState s, Rotation r) {
			BlockState t = s;
			for (Direction d : Direction.Plane.HORIZONTAL) t = t.setValue(bras(r.rotate(d)), s.getValue(bras(d)));
			return t;
		}
		@Override
		protected BlockState mirror(BlockState s, Mirror m) {
			BlockState t = s;
			for (Direction d : Direction.Plane.HORIZONTAL) t = t.setValue(bras(m.mirror(d)), s.getValue(bras(d)));
			return t;
		}
	}

	private static BlockBehaviour.Properties proprietes(MapColor c) {
		return BlockBehaviour.Properties.of().mapColor(c).instabreak().noCollission().sound(SoundType.WOOL).pushReaction(PushReaction.DESTROY);
	}
	private static void enregistrer(String id, java.util.function.Supplier<Block> f) {
		DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, f);
		AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
	}

	static {
		enregistrer("yellow_floor_line", () -> new Ligne(proprietes(MapColor.COLOR_YELLOW)));
		enregistrer("white_floor_line", () -> new Ligne(proprietes(MapColor.SNOW)));
		enregistrer("red_floor_line", () -> new Ligne(proprietes(MapColor.COLOR_RED)));
		enregistrer("yellow_hazard_stripes", () -> new Peinture(proprietes(MapColor.COLOR_YELLOW), false));
		enregistrer("red_hazard_stripes", () -> new Peinture(proprietes(MapColor.COLOR_RED), false));
		enregistrer("white_floor_arrow", () -> new Peinture(proprietes(MapColor.SNOW), true));
		enregistrer("yellow_floor_arrow", () -> new Peinture(proprietes(MapColor.COLOR_YELLOW), true));
		enregistrer("white_floor_crossing", () -> new Peinture(proprietes(MapColor.SNOW), true));
	}

	public static void charger() {}
}
