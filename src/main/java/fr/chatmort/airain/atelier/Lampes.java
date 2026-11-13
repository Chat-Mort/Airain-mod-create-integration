package fr.chatmort.airain.atelier;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.Map;

/** Lampes d'atelier : suspension (sous un plafond ou une chaîne), applique murale à flamme rouge, gyrophare. */
public final class Lampes {
	private Lampes() {}

	// ====================================================================== la suspension (abat-jour, globe chaud)
	public static class Suspension extends BlocPatine {
		private static final VoxelShape FORME = Shapes.or(Block.box(2, 3.5, 2, 14, 12, 14), Block.box(7.5, 12, 7.5, 8.5, 16, 8.5));
		public Suspension(WeatherState etat, Properties p) { super(etat, p); }
		// accrochée sous un bloc : plafond plein, chaîne, suspente, ou ce qu'on veut tant qu'il y a quelque chose au-dessus
		@Override protected boolean canSurvive(BlockState s, LevelReader l, BlockPos p) { return !l.getBlockState(p.above()).isAir(); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			return d == Direction.UP && !canSurvive(s, l, p) ? Blocks.AIR.defaultBlockState() : s;
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	}

	// ====================================================================== l'applique (contre un mur ; FACING : vers la pièce)
	public static class Applique extends BlocPatine {
		private static final Map<Direction, VoxelShape> FORMES = new EnumMap<>(Direction.class);
		static {
			for (Direction d : Direction.Plane.HORIZONTAL)
				FORMES.put(d, Shapes.or(fr.chatmort.airain.fonderie.ConduitAir.boiteVers(d, 4, 3, 15, 12, 13, 16), fr.chatmort.airain.fonderie.ConduitAir.boiteVers(d, 5, 4, 10, 11, 12, 15)));
		}
		public Applique(WeatherState etat, Properties p) { super(etat, p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction f = c.getClickedFace().getAxis().isHorizontal() ? c.getClickedFace() : c.getHorizontalDirection().getOpposite();
			return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, f);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(BlockStateProperties.HORIZONTAL_FACING)); }
	}

	// ====================================================================== le gyrophare (redstone : s'allume, son réflecteur tourne)
	public static class Gyrophare extends BaseEntityBlock {
		public static final MapCodec<Gyrophare> CODEC = simpleCodec(Gyrophare::new);
		private static final VoxelShape FORME = Shapes.or(Block.box(4, 0, 4, 12, 2, 12), Block.box(5, 2, 5, 11, 9, 11));
		public Gyrophare(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.LIT, false)); }
		@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.LIT); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(BlockStateProperties.LIT, c.getLevel().hasNeighborSignal(c.getClickedPos())); }
		@Override
		protected void neighborChanged(BlockState s, Level l, BlockPos p, Block b, BlockPos np, boolean deplace) {
			if (l.isClientSide) return;
			boolean on = l.hasNeighborSignal(p);
			if (on != s.getValue(BlockStateProperties.LIT)) l.setBlock(p, s.setValue(BlockStateProperties.LIT, on), Block.UPDATE_CLIENTS);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new GyrophareBlockEntity(p, s); }
	}
	/** Bloc-entité vide : il ne sert qu'à faire tourner le réflecteur (rendu). */
	public static class GyrophareBlockEntity extends BlockEntity {
		public GyrophareBlockEntity(BlockPos p, BlockState s) { super(Atelier.GYROPHARE_BE.get(), p, s); }
	}
}
