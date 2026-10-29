package fr.chatmort.airain.fondation;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.fml.loading.FMLEnvironment;

/**
 * Étendard de fondation : deux blocs de haut (piédestal + mât). Il nomme une base ; en entrant dans sa zone,
 * le nom s'affiche à l'écran. La bannière (style, couleurs, motif, forme) se règle dans le même écran que le nom.
 */
public class FondationBlock extends Block implements EntityBlock {
	public static final EnumProperty<DoubleBlockHalf> HALF = BlockStateProperties.DOUBLE_BLOCK_HALF;
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	public static final IntegerProperty STYLE = IntegerProperty.create("style", 0, 2);
	private static final VoxelShape SOCLE = Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(1, 4, 1, 15, 15, 15), Block.box(5.5, 15, 5.5, 10.5, 16, 10.5));
	private static final VoxelShape MAT = Block.box(6.5, 0, 6.5, 9.5, 16, 9.5);

	public FondationBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(HALF, DoubleBlockHalf.LOWER).setValue(FACING, Direction.NORTH).setValue(STYLE, 0));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(HALF, FACING, STYLE);
	}

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		BlockPos pos = ctx.getClickedPos();
		Level level = ctx.getLevel();
		if (pos.getY() >= level.getMaxBuildHeight() - 2 || !level.getBlockState(pos.above()).canBeReplaced(ctx)
			|| !level.getBlockState(pos.above(2)).canBeReplaced(ctx))   // le haut du mât et la bannière dépassent d'un bloc
			return null;
		return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity qui, ItemStack pile) {
		level.setBlock(pos.above(), state.setValue(HALF, DoubleBlockHalf.UPPER), 3);
		if (level.getBlockEntity(pos) instanceof FondationBlockEntity f) {
			f.enregistrer();
			if (level.isClientSide && FMLEnvironment.dist.isClient())
				EcranClient.ouvrir(pos, f.nom(), f.devise(), f.apparence());
		}
	}

	/** Le style choisi change le mât (bloc du haut) : on l'écrit dans les deux moitiés. */
	public static void appliquerStyle(Level level, BlockPos bas, int style) {
		for (BlockPos p : new BlockPos[] {bas, bas.above()}) {
			BlockState s = level.getBlockState(p);
			if (s.getBlock() instanceof FondationBlock && s.getValue(STYLE) != style)
				level.setBlock(p, s.setValue(STYLE, style), 3);
		}
	}

	private static BlockPos bas(BlockState state, BlockPos pos) {
		return state.getValue(HALF) == DoubleBlockHalf.UPPER ? pos.below() : pos;
	}

	@Override
	protected BlockState updateShape(BlockState state, Direction dir, BlockState voisin, LevelAccessor level, BlockPos pos, BlockPos posVoisin) {
		DoubleBlockHalf h = state.getValue(HALF);
		if (dir.getAxis() == Direction.Axis.Y && (h == DoubleBlockHalf.LOWER) == (dir == Direction.UP)) {
			if (!(voisin.getBlock() instanceof FondationBlock) || voisin.getValue(HALF) == h)
				return Blocks.AIR.defaultBlockState();
		}
		return super.updateShape(state, dir, voisin, level, pos, posVoisin);
	}

	@Override
	public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player joueur) {
		if (!level.isClientSide && state.getValue(HALF) == DoubleBlockHalf.UPPER) {
			BlockPos b = pos.below();
			if (level.getBlockState(b).getBlock() instanceof FondationBlock)
				level.destroyBlock(b, !joueur.isCreative(), joueur);   // le piédestal donne l'objet
		}
		return super.playerWillDestroy(level, pos, state, joueur);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return state.getValue(HALF) == DoubleBlockHalf.LOWER ? SOCLE : MAT;
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return state.getValue(HALF) == DoubleBlockHalf.LOWER ? new FondationBlockEntity(pos, state) : null;
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur, InteractionHand main, BlockHitResult hit) {
		if (pile.getItem() instanceof GabaritItem)
			return ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;   // le gabarit agit lui-même
		if (!BuiltInRegistries.ITEM.getKey(pile.getItem()).toString().equals("create:wrench"))
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		BlockPos b = bas(state, pos);
		if (!(level.getBlockEntity(b) instanceof FondationBlockEntity f))
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		reglerRayon(level, b, f, joueur);
		return ItemInteractionResult.sidedSuccess(level.isClientSide);
	}

	/** Clé de Create : agrandit (ou réduit en s'accroupissant) la zone, montre le cercle en particules. */
	public static void reglerRayon(Level level, BlockPos b, FondationBlockEntity f, Player joueur) {
		if (!level.isClientSide) {
			int r = f.rayon() + (joueur.isShiftKeyDown() ? -FondationBlockEntity.PAS : FondationBlockEntity.PAS);
			if (r > FondationBlockEntity.RAYON_MAX) r = FondationBlockEntity.RAYON_MIN;
			if (r < FondationBlockEntity.RAYON_MIN) r = FondationBlockEntity.RAYON_MAX;
			f.regler(r);
			joueur.displayClientMessage(Component.translatable("airain.fondation.rayon", f.rayon()), true);
			level.playSound(null, b, SoundEvents.UI_BUTTON_CLICK.value(), SoundSource.BLOCKS, 0.5f, 1.2f);
			if (level instanceof ServerLevel sl)
				for (int k = 0; k < 96; k++) {
				double a = k * Math.PI * 2 / 96;
				sl.sendParticles(ParticleTypes.END_ROD, b.getX() + 0.5 + Math.cos(a) * f.rayon(), b.getY() + 1.2,
				b.getZ() + 0.5 + Math.sin(a) * f.rayon(), 1, 0, 0.2, 0, 0);
			}
	}
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		BlockPos b = bas(state, pos);
		if (level.isClientSide && FMLEnvironment.dist.isClient() && level.getBlockEntity(b) instanceof FondationBlockEntity f)
			EcranClient.ouvrir(b, f.nom(), f.devise(), f.apparence());
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && state.getValue(HALF) == DoubleBlockHalf.LOWER && level instanceof ServerLevel sl)
			FondationRegistre.de(sl.getServer()).retirer(level, pos);
		super.onRemove(state, level, pos, neuf, deplace);
	}

	@Override
	public <T extends BlockEntity> net.minecraft.world.level.block.entity.BlockEntityTicker<T> getTicker(Level level, BlockState state,
			net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
		return FondationBlockEntity.ticker(level, type);
	}
}
