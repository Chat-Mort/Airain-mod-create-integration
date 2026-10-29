package fr.chatmort.airain.trophee;

import fr.chatmort.airain.fondation.GabaritItem;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.fml.loading.FMLEnvironment;

/**
 * Piédestal de l'Empire : on y expose un trophée de boss ; tant qu'il y reste, son effet profite à toute l'équipe.
 * Clic droit avec un trophée : l'exposer ; main vide : le reprendre ; accroupi main vide : réglages.
 * Colonne haute : un second bloc au-dessus (HALF = UPPER), sans block entity.
 */
public class SocleBlock extends Block implements EntityBlock {
	public static final EnumProperty<DoubleBlockHalf> HALF = BlockStateProperties.DOUBLE_BLOCK_HALF;
	public static final BooleanProperty LUMIERE = BooleanProperty.create("lumiere");
	public static final net.minecraft.world.level.block.state.properties.DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	private static final VoxelShape FORME = Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(3, 4, 3, 13, 10, 13), Block.box(1, 10, 1, 15, 13, 15));
	private static final VoxelShape BAS_HAUT = Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(3, 4, 3, 13, 16, 13));
	private static final VoxelShape HAUT = Shapes.or(Block.box(3, 0, 3, 13, 10, 13), Block.box(1, 10, 1, 15, 13, 15));

	public SocleBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(HALF, DoubleBlockHalf.LOWER).setValue(LUMIERE, false).setValue(FACING, Direction.NORTH));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(HALF, LUMIERE, FACING);
	}

	/** La plaque gravée regarde le joueur qui pose le piédestal. */
	@Override
	public BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext ctx) {
		return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	protected BlockState rotate(BlockState state, net.minecraft.world.level.block.Rotation rot) {
		return state.setValue(FACING, rot.rotate(state.getValue(FACING)));
	}

	private static BlockPos bas(BlockState s, BlockPos pos) {
		return s.getValue(HALF) == DoubleBlockHalf.UPPER ? pos.below() : pos;
	}

	public static SocleBlockEntity socle(Level level, BlockPos pos) {
		BlockState s = level.getBlockState(pos);
		if (!(s.getBlock() instanceof SocleBlock)) return null;
		return level.getBlockEntity(bas(s, pos)) instanceof SocleBlockEntity e ? e : null;
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		if (state.getValue(HALF) == DoubleBlockHalf.UPPER) return HAUT;
		return level.getBlockState(pos.above()).getBlock() instanceof SocleBlock ? BAS_HAUT : FORME;
	}

	/** Colonne haute ou basse : pose ou retire le bloc du haut. Renvoie faux s'il n'y a pas la place. */
	public static boolean changerHauteur(Level level, BlockPos bas, boolean haute) {
		BlockState s = level.getBlockState(bas);
		if (!(s.getBlock() instanceof SocleBlock)) return false;
		BlockPos h = bas.above();
		boolean deja = level.getBlockState(h).getBlock() instanceof SocleBlock;
		if (haute == deja) return true;
		if (haute) {
			if (!level.getBlockState(h).canBeReplaced()) return false;
			level.setBlock(h, s.setValue(HALF, DoubleBlockHalf.UPPER).setValue(LUMIERE, false), 3);
		} else {
			level.setBlock(h, Blocks.AIR.defaultBlockState(), 3);
		}
		return true;
	}

	@Override
	protected BlockState updateShape(BlockState state, Direction dir, BlockState voisin, LevelAccessor level, BlockPos pos, BlockPos posVoisin) {
		if (state.getValue(HALF) == DoubleBlockHalf.UPPER && dir == Direction.DOWN
			&& !(voisin.getBlock() instanceof SocleBlock && voisin.getValue(HALF) == DoubleBlockHalf.LOWER))
			return Blocks.AIR.defaultBlockState();
		return super.updateShape(state, dir, voisin, level, pos, posVoisin);
	}

	@Override
	public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player joueur) {
		if (!level.isClientSide && state.getValue(HALF) == DoubleBlockHalf.UPPER && level.getBlockState(pos.below()).getBlock() instanceof SocleBlock)
			level.destroyBlock(pos.below(), !joueur.isCreative(), joueur);
		return super.playerWillDestroy(level, pos, state, joueur);
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return state.getValue(HALF) == DoubleBlockHalf.LOWER ? new SocleBlockEntity(pos, state) : null;
	}

	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
		return SocleBlockEntity.ticker(level, type);
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur, InteractionHand main, BlockHitResult hit) {
		if (pile.getItem() instanceof GabaritItem) return ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;
		SocleBlockEntity socle = socle(level, pos);
		if (socle == null || !socle.trophee().isEmpty())
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (!Trophees.estTrophee(pile)) {
			if (!level.isClientSide)
				joueur.displayClientMessage(Component.translatable("airain.socle.pas_trophee"), true);
			return ItemInteractionResult.CONSUME;
		}
		if (!level.isClientSide) {
			socle.exposer(pile);
			if (!joueur.getAbilities().instabuild) pile.shrink(1);
			BlockPos b = socle.getBlockPos();
			level.playSound(null, b, SoundEvents.ARMOR_EQUIP_GOLD.value(), SoundSource.BLOCKS, 1f, 0.8f);
			level.playSound(null, b, SoundEvents.NOTE_BLOCK_CHIME.value(), SoundSource.BLOCKS, 0.8f, 1.2f);   // carillon de la victoire
			joueur.displayClientMessage(Component.translatable("airain.socle.expose"), true);
		}
		return ItemInteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		SocleBlockEntity socle = socle(level, pos);
		if (socle == null) return InteractionResult.PASS;
		if (joueur.isShiftKeyDown()) {                          // réglages
			if (level.isClientSide && FMLEnvironment.dist.isClient())
				EcranSocleClient.ouvrir(socle.getBlockPos(), socle.apparence(), socle.plaque());
			return InteractionResult.sidedSuccess(level.isClientSide);
		}
		if (socle.trophee().isEmpty()) return InteractionResult.PASS;
		if (!level.isClientSide) {
			ItemStack p = socle.reprendre();
			if (!joueur.addItem(p)) joueur.drop(p, false);
			BlockPos b = socle.getBlockPos();
			level.playSound(null, b, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.6f, 1f);
			level.playSound(null, b, SoundEvents.NOTE_BLOCK_BASS.value(), SoundSource.BLOCKS, 0.9f, 0.5f);   // écho grave
		}
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	/** Comparateur : 0 sans trophée, sinon 11 à 15 selon les effets du trophée. */
	@Override
	protected boolean hasAnalogOutputSignal(BlockState state) {
		return state.getValue(HALF) == DoubleBlockHalf.LOWER;
	}

	@Override
	protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
		return level.getBlockEntity(pos) instanceof SocleBlockEntity s ? s.signal() : 0;
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && level.getBlockEntity(pos) instanceof SocleBlockEntity socle && level instanceof ServerLevel) {
			ItemStack p = socle.reprendre();
			if (!p.isEmpty()) Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, p);
			if (level.getBlockState(pos.above()).getBlock() instanceof SocleBlock) level.setBlock(pos.above(), Blocks.AIR.defaultBlockState(), 3);
		}
		super.onRemove(state, level, pos, neuf, deplace);
	}
}
