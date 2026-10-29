package fr.chatmort.airain.fondation;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.fml.loading.FMLEnvironment;

/**
 * Bannière murale : une tringle scellée au mur, la bannière pend dessous. Mêmes réglages que les étendards
 * (couleurs, partitions, motif, usure, taille, franges, embouts, lanternes, vent), purement décorative.
 * Un signal de redstone l'enroule.
 */
public class BanniereMuraleBlock extends Block implements EntityBlock {
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	/** Longueur et largeur de la toile en pixels (2 à 4 blocs ; 1 à 2 blocs). */
	public static final int[] LONGUEURS = {32, 48, 64};
	public static final int[] LARGEURS = {16, 20, 24, 32};
	private static final VoxelShape NORD = Block.box(0, 10.5, 11, 16, 15.5, 16), SUD = Block.box(0, 10.5, 0, 16, 15.5, 5),
		EST = Block.box(0, 10.5, 0, 5, 15.5, 16), OUEST = Block.box(11, 10.5, 0, 16, 15.5, 16);

	public BanniereMuraleBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(FACING);
	}

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		Direction d = ctx.getClickedFace();
		return defaultBlockState().setValue(FACING, d.getAxis().isHorizontal() ? d : ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	protected RenderShape getRenderShape(BlockState state) {
		return RenderShape.MODEL;
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
	public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity qui, ItemStack pile) {
		if (level.isClientSide && FMLEnvironment.dist.isClient() && level.getBlockEntity(pos) instanceof FondationBlockEntity f)
			EcranClient.ouvrir(pos, f.nom(), f.devise(), f.apparence());
	}

	@Override
	protected net.minecraft.world.ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur,
			net.minecraft.world.InteractionHand main, BlockHitResult hit) {
		return pile.getItem() instanceof GabaritItem ? net.minecraft.world.ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION
			: net.minecraft.world.ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		if (level.isClientSide && FMLEnvironment.dist.isClient() && level.getBlockEntity(pos) instanceof FondationBlockEntity f)
			EcranClient.ouvrir(pos, f.nom(), f.devise(), f.apparence());
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block voisin, BlockPos posVoisin, boolean deplace) {
		super.neighborChanged(state, level, pos, voisin, posVoisin, deplace);
		if (!level.isClientSide && level.getBlockEntity(pos) instanceof FondationBlockEntity f)
			f.mettreEnBerne(level.hasNeighborSignal(pos));
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new FondationBlockEntity(pos, state);
	}

	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
		return FondationBlockEntity.ticker(level, type);
	}
}
