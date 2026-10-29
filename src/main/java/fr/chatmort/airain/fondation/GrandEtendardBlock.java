package fr.chatmort.airain.fondation;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
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
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.fml.loading.FMLEnvironment;

/**
 * Grand étendard de fondation : le même piédestal, surmonté d'un mât de six blocs.
 * PARTIE 0 = piédestal (porte le block entity), 1..6 = tronçons du mât. La bannière, plus grande, est réglable
 * en longueur et en largeur, et le vent se choisit.
 */
public class GrandEtendardBlock extends Block implements EntityBlock {
	public static final int MAT = 6, MAT_MIN = 5, MAT_MAX = 8;
	public static final IntegerProperty PARTIE = IntegerProperty.create("partie", 0, MAT_MAX);
	/** Dernier tronçon du mât : porte le collier du sommet, rien n'est attendu au-dessus. */
	public static final BooleanProperty SOMMET = BooleanProperty.create("sommet");
	private static final int SILENCIEUX = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	private static final VoxelShape SOCLE = Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(1, 4, 1, 15, 15, 15), Block.box(5.5, 15, 5.5, 10.5, 16, 10.5));
	private static final VoxelShape TRONCON = Block.box(6, 0, 6, 10, 16, 10);

	public GrandEtendardBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(PARTIE, 0).setValue(FACING, Direction.NORTH).setValue(SOMMET, false));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(PARTIE, FACING, SOMMET);
	}

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		BlockPos pos = ctx.getClickedPos();
		Level level = ctx.getLevel();
		if (pos.getY() + MAT >= level.getMaxBuildHeight())
			return null;
		for (int k = 1; k <= MAT; k++)
			if (!level.getBlockState(pos.above(k)).canBeReplaced(ctx))
				return null;
		return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity qui, ItemStack pile) {
		for (int k = 1; k <= MAT; k++)
			level.setBlock(pos.above(k), state.setValue(PARTIE, k).setValue(SOMMET, k == MAT), 3);
		if (level.getBlockEntity(pos) instanceof FondationBlockEntity f) {
			f.enregistrer();
			if (level.isClientSide && FMLEnvironment.dist.isClient())
				EcranClient.ouvrir(pos, f.nom(), f.devise(), f.apparence());
		}
	}

	private static BlockPos base(BlockState state, BlockPos pos) {
		return pos.below(state.getValue(PARTIE));
	}

	/** Chaque tronçon tient à ses voisins : si l'un disparaît, tout le mât tombe. */
	@Override
	protected BlockState updateShape(BlockState state, Direction dir, BlockState voisin, LevelAccessor level, BlockPos pos, BlockPos posVoisin) {
		int p = state.getValue(PARTIE);
		if (dir == Direction.UP && p < MAT_MAX && !state.getValue(SOMMET) && !(voisin.is(this) && voisin.getValue(PARTIE) == p + 1))
			return Blocks.AIR.defaultBlockState();
		if (dir == Direction.DOWN && p > 0 && !(voisin.is(this) && voisin.getValue(PARTIE) == p - 1))
			return Blocks.AIR.defaultBlockState();
		return super.updateShape(state, dir, voisin, level, pos, posVoisin);
	}

	/**
	 * Allonge ou raccourcit le mât. Pour l'allonger, toute la place au-dessus doit être libre.
	 * Les blocs sont posés sans mise à jour de forme, le sommet est marqué à la fin.
	 */
	public static boolean changerHauteur(Level level, BlockPos base, int avant, int apres) {
		apres = Math.max(MAT_MIN, Math.min(MAT_MAX, apres));
		BlockState socle = level.getBlockState(base);
		if (!(socle.getBlock() instanceof GrandEtendardBlock) || apres == avant) return true;
		if (apres > avant) {
			if (base.getY() + apres >= level.getMaxBuildHeight()) return false;
			for (int k = avant + 1; k <= apres; k++)
				if (!level.getBlockState(base.above(k)).canBeReplaced()) return false;
			for (int k = avant + 1; k <= apres; k++)
				level.setBlock(base.above(k), socle.setValue(PARTIE, k).setValue(SOMMET, k == apres), SILENCIEUX);
			level.setBlock(base.above(avant), socle.setValue(PARTIE, avant).setValue(SOMMET, false), SILENCIEUX);
		} else {
			level.setBlock(base.above(apres), socle.setValue(PARTIE, apres).setValue(SOMMET, true), SILENCIEUX);
			for (int k = avant; k > apres; k--)
				level.setBlock(base.above(k), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), SILENCIEUX);
		}
		if (level.getBlockEntity(base) instanceof FondationBlockEntity f) f.hauteur(apres);
		return true;
	}

	/** Remet le sommet au bon tronçon (étendards posés avant que la hauteur soit réglable). */
	public static void marquerSommet(Level level, BlockPos base, int hauteur) {
		BlockPos haut = base.above(hauteur);
		BlockState s = level.getBlockState(haut);
		if (s.getBlock() instanceof GrandEtendardBlock && s.getValue(PARTIE) == hauteur && !s.getValue(SOMMET))
			level.setBlock(haut, s.setValue(SOMMET, true), SILENCIEUX);
	}

	@Override
	public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player joueur) {
		if (!level.isClientSide && state.getValue(PARTIE) > 0) {
			BlockPos b = base(state, pos);
			if (level.getBlockState(b).is(this))
				level.destroyBlock(b, !joueur.isCreative(), joueur);   // le piédestal donne l'objet
		}
		return super.playerWillDestroy(level, pos, state, joueur);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return state.getValue(PARTIE) == 0 ? SOCLE : TRONCON;
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return state.getValue(PARTIE) == 0 ? new FondationBlockEntity(pos, state) : null;
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur, InteractionHand main, BlockHitResult hit) {
		if (pile.getItem() instanceof GabaritItem)
			return ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;   // le gabarit agit lui-même
		if (!BuiltInRegistries.ITEM.getKey(pile.getItem()).toString().equals("create:wrench"))
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		BlockPos b = base(state, pos);
		if (!(level.getBlockEntity(b) instanceof FondationBlockEntity f))
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		FondationBlock.reglerRayon(level, b, f, joueur);
		return ItemInteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		BlockPos b = base(state, pos);
		if (level.isClientSide && FMLEnvironment.dist.isClient() && level.getBlockEntity(b) instanceof FondationBlockEntity f)
			EcranClient.ouvrir(b, f.nom(), f.devise(), f.apparence());
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && state.getValue(PARTIE) == 0 && level instanceof ServerLevel sl)
			FondationRegistre.de(sl.getServer()).retirer(level, pos);
		super.onRemove(state, level, pos, neuf, deplace);
	}

	@Override
	public <T extends BlockEntity> net.minecraft.world.level.block.entity.BlockEntityTicker<T> getTicker(Level level, BlockState state,
			net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
		return FondationBlockEntity.ticker(level, type);
	}

	/** Signal de redstone sur le piédestal ou le premier tronçon : mise en berne. */
	@Override
	protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block voisin, BlockPos posVoisin, boolean deplace) {
		super.neighborChanged(state, level, pos, voisin, posVoisin, deplace);
		if (level.isClientSide) return;
		BlockPos b = base(state, pos);
		if (level.getBlockEntity(b) instanceof FondationBlockEntity f)
			f.mettreEnBerne(level.hasNeighborSignal(b) || level.hasNeighborSignal(b.above()));
	}

	/** Comparateur contre le piédestal : 15 tant qu'un joueur est dans la zone. */
	@Override
	protected boolean hasAnalogOutputSignal(BlockState state) {
		return state.getValue(PARTIE) == 0;
	}

	@Override
	protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
		return level instanceof ServerLevel sl && FondationRegistre.de(sl.getServer()).occupee(level.dimension().location(), pos) ? 15 : 0;
	}
}
