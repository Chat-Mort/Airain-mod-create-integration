package fr.chatmort.airain.tableau;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Tableau de service : un panneau de liège au mur, où l'on épingle des notes pour l'autre. */
public class TableauBlock extends Block {
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	private static final VoxelShape NORD = Block.box(0, 2, 14, 16, 14, 16), SUD = Block.box(0, 2, 0, 16, 14, 2),
		EST = Block.box(0, 2, 0, 2, 14, 16), OUEST = Block.box(14, 2, 0, 16, 14, 16);

	public TableauBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		Direction d = ctx.getClickedFace();
		if (!d.getAxis().isHorizontal()) d = ctx.getHorizontalDirection().getOpposite();
		BlockState s = defaultBlockState().setValue(FACING, d);
		return s.canSurvive(ctx.getLevel(), ctx.getClickedPos()) ? s : null;
	}

	@Override
	protected boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
		Direction d = state.getValue(FACING);
		BlockPos mur = pos.relative(d.getOpposite());
		return level.getBlockState(mur).isFaceSturdy(level, mur, d);
	}

	@Override
	protected BlockState updateShape(BlockState state, Direction dir, BlockState voisin, net.minecraft.world.level.LevelAccessor level, BlockPos pos, BlockPos vp) {
		return dir == state.getValue(FACING).getOpposite() && !state.canSurvive(level, pos)
			? net.minecraft.world.level.block.Blocks.AIR.defaultBlockState() : state;
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return switch (state.getValue(FACING)) {
			case SOUTH -> SUD;
			case EAST -> EST;
			case WEST -> OUEST;
			default -> NORD;
		};
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player p, BlockHitResult hit) {
		if (p instanceof ServerPlayer sp) PaquetsTableau.envoyer(sp, pos);
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && level instanceof net.minecraft.server.level.ServerLevel sl)
			Tableaux.de(sl.getServer()).retirer(sl.dimension().location(), pos);
		super.onRemove(state, level, pos, neuf, deplace);
	}
}
