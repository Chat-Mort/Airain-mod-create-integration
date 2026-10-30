package fr.chatmort.airain.balise;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * La balise de défense : une tour-phare à sirène de 3 x 3 blocs de base et 8 de haut. Ce bloc-ci est le cœur, au centre
 * du socle (il porte le block entity et l'objet) ; les autres cases sont des {@link BalisePartieBlock}.
 * La logique des assauts reste dans le script KubeJS (airain_balise.js), qui allume l'alerte par « data merge ».
 */
public class BaliseBlock extends Block implements EntityBlock {
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;

	public BaliseBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }

	/** Toutes les cases occupées par la tour, en coordonnées du monde, sauf le cœur. */
	static void pourChaqueCase(BlockPos coeur, CaseVisiteur v) {
		for (float[] c : BaliseGeo.CASES) {
			int x = (int) c[0], y = (int) c[1], z = (int) c[2];
			if (x == 1 && y == 0 && z == 1) continue;
			v.visiter(x, y, z, coeur.offset(x - 1, y, z - 1));
		}
	}

	interface CaseVisiteur { void visiter(int x, int y, int z, BlockPos pos); }

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		Level level = ctx.getLevel();
		BlockPos pos = ctx.getClickedPos();
		if (pos.getY() + 8 > level.getMaxBuildHeight()) return refus(ctx);
		boolean[] ok = {true};
		pourChaqueCase(pos, (x, y, z, p) -> { if (!level.getBlockState(p).canBeReplaced(ctx)) ok[0] = false; });
		if (!ok[0]) return refus(ctx);
		return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	private BlockState refus(BlockPlaceContext ctx) {
		if (ctx.getPlayer() != null && !ctx.getLevel().isClientSide)
			ctx.getPlayer().displayClientMessage(Component.translatable("airain.balise.place"), true);
		return null;
	}

	@Override
	public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity qui, ItemStack pile) {
		if (level.isClientSide) return;
		pourChaqueCase(pos, (x, y, z, p) -> level.setBlock(p, AirainMod.BALISE_PARTIE.get().defaultBlockState()
			.setValue(BalisePartieBlock.PX, x).setValue(BalisePartieBlock.PY, y).setValue(BalisePartieBlock.PZ, z), 3));
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && !level.isClientSide)
			pourChaqueCase(pos, (x, y, z, p) -> {
				if (level.getBlockState(p).is(AirainMod.BALISE_PARTIE.get()))
					level.setBlock(p, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3 | Block.UPDATE_SUPPRESS_DROPS);
			});
		super.onRemove(state, level, pos, neuf, deplace);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		VoxelShape s = BaliseFormes.de(1, 0, 1);
		return s == null ? Shapes.block() : s;
	}

	@Override
	protected RenderShape getRenderShape(BlockState state) { return RenderShape.ENTITYBLOCK_ANIMATED; }

	@Override
	protected BlockState rotate(BlockState s, Rotation r) { return s.setValue(FACING, r.rotate(s.getValue(FACING))); }

	@Override
	protected BlockState mirror(BlockState s, Mirror m) { return s.rotate(m.getRotation(s.getValue(FACING))); }

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new BaliseBlockEntity(pos, state); }

	@Override
	@SuppressWarnings("unchecked")
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
		if (type != AirainMod.BALISE_BE.get()) return null;
		return level.isClientSide ? (l, p, s, be) -> ((BaliseBlockEntity) be).tickClient()
			: (l, p, s, be) -> ((BaliseBlockEntity) be).tickServeur();
	}
}
